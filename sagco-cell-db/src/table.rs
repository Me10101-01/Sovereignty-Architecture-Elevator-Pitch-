/// Table — a named collection of cells with an attached index.
///
/// Table is the public API over StorageEngine + KeyIndex.
/// It keeps the index in sync automatically.

use std::io;
use std::path::Path;

use crate::cell::Cell;
use crate::index::KeyIndex;
use crate::query::Query;
use crate::storage::StorageEngine;

pub struct Table {
    pub name: String,
    engine: StorageEngine,
    index: KeyIndex,
}

impl Table {
    pub fn open(
        pages_dir: impl AsRef<Path>,
        indexes_dir: impl AsRef<Path>,
        name: &str,
    ) -> io::Result<Self> {
        let engine = StorageEngine::open(&pages_dir)?;
        engine.init_table(name)?;

        let mut index = KeyIndex::open(&indexes_dir, name)?;

        // If index is empty but page has data, rebuild
        if index.is_empty() {
            let name_clone = name.to_string();
            let engine_ref = StorageEngine::open(&pages_dir)?;
            index.rebuild_from_scan(|cb| {
                let _ = engine_ref.scan(&name_clone, |offset, cell| {
                    cb(offset, &cell.key);
                });
            })?;
        }

        Ok(Self { name: name.to_string(), engine, index })
    }

    /// Insert or update a record.
    pub fn put(&mut self, key: impl Into<Vec<u8>>, value: impl Into<Vec<u8>>) -> io::Result<u64> {
        let key = key.into();
        let cell = Cell::new(key.clone(), value.into());
        let offset = self.engine.put(&self.name, &cell)?;
        self.index.put(key, offset);
        self.index.flush()?;
        Ok(offset)
    }

    /// Get by key — uses index for O(1) lookup path.
    pub fn get(&self, key: &[u8]) -> io::Result<Option<Cell>> {
        if !self.index.contains(key) {
            return Ok(None); // not in index = definitely not in table
        }
        // Index hit → full scan to get actual cell (simple path; planner upgrades this)
        self.engine.get(&self.name, key)
    }

    /// Delete a key.
    pub fn delete(&mut self, key: &[u8]) -> io::Result<()> {
        self.engine.delete(&self.name, key)?;
        self.index.remove(key);
        self.index.flush()?;
        Ok(())
    }

    /// Run a query and return all matching cells.
    pub fn query(&self, q: &Query) -> io::Result<Vec<Cell>> {
        let mut results = vec![];
        self.engine.scan(&self.name, |_offset, cell| {
            if q.matches(cell) {
                results.push(cell.clone());
                if let Some(limit) = q.limit {
                    // Note: we can't break from the closure easily, so we just collect up to limit
                    let _ = limit; // planner will enforce limit after
                }
            }
        })?;
        if let Some(limit) = q.limit {
            results.truncate(limit);
        }
        Ok(results)
    }

    /// Full table scan — returns all live cells.
    pub fn scan_all(&self) -> io::Result<Vec<Cell>> {
        let mut cells = vec![];
        self.engine.scan(&self.name, |_, cell| cells.push(cell.clone()))?;
        Ok(cells)
    }

    /// Compact: rewrite without tombstones.
    pub fn compact(&self) -> io::Result<(usize, usize)> {
        self.engine.compact(&self.name)
    }

    pub fn cell_count(&self) -> usize {
        self.index.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::query::{Filter, Query};
    use tempfile::tempdir;

    #[test]
    fn put_get_delete() {
        let dir = tempdir().unwrap();
        let pages = dir.path().join("pages");
        let indexes = dir.path().join("indexes");
        let mut tbl = Table::open(&pages, &indexes, "MAT225").unwrap();

        tbl.put("PA8", "8*x^7*e^(x^8)").unwrap();
        let cell = tbl.get(b"PA8").unwrap().unwrap();
        assert_eq!(cell.value_str(), "8*x^7*e^(x^8)");

        tbl.delete(b"PA8").unwrap();
        assert!(tbl.get(b"PA8").unwrap().is_none());
    }

    #[test]
    fn query_by_value_contains() {
        let dir = tempdir().unwrap();
        let pages = dir.path().join("pages");
        let indexes = dir.path().join("indexes");
        let mut tbl = Table::open(&pages, &indexes, "notes").unwrap();

        tbl.put("concept_1", "chain_rule: d/dx[f(g(x))]").unwrap();
        tbl.put("concept_2", "product_rule: d/dx[f*g]").unwrap();
        tbl.put("hw_1", "MAT225 PA8 solution").unwrap();

        let f = Filter::parse("value~=chain").unwrap();
        let q = Query::new().filter(f);
        let results = tbl.query(&q).unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].key_str(), "concept_1");
    }
}
