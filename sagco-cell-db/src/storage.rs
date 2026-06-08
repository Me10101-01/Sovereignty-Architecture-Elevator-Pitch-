/// Page-based storage engine — brick 2.
///
/// A .sagco page file:
///   [PAGE_HEADER 64 bytes][cell_0][cell_1]...[cell_N]
///
/// Page header layout:
///   magic:      4 bytes  b"PAGE"
///   page_id:    4 bytes  u32 le
///   cell_count: 2 bytes  u16 le
///   flags:      2 bytes  u16 le
///   checksum:   4 bytes  u32 le  (crc32 of all cells in page)
///   created_at: 8 bytes  u64 le  microseconds
///   table:     32 bytes  ASCII name, null-padded
///   reserved:   8 bytes
///   ─────────────────────────────
///   total:     64 bytes
///
/// Pages grow by appending cells. No in-place update — only append + tombstone.

use std::fs::{self, File, OpenOptions};
use std::io::{self, BufReader, BufWriter, Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};

use crc32fast::Hasher;

use crate::cell::Cell;

pub const PAGE_MAGIC: &[u8; 4] = b"PAGE";
pub const PAGE_HEADER_SIZE: usize = 64;
pub const PAGE_MAX_CELLS: usize = 4096;

// ── Page header ────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub struct PageHeader {
    pub page_id: u32,
    pub cell_count: u16,
    pub flags: u16,
    pub checksum: u32,
    pub created_at: u64,
    pub table: String,
}

impl PageHeader {
    pub fn new(page_id: u32, table: &str) -> Self {
        use std::time::{SystemTime, UNIX_EPOCH};
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_micros() as u64)
            .unwrap_or(0);
        Self {
            page_id,
            cell_count: 0,
            flags: 0,
            checksum: 0,
            created_at: ts,
            table: table.to_string(),
        }
    }

    pub fn write_to(&self, w: &mut impl Write) -> io::Result<()> {
        w.write_all(PAGE_MAGIC)?;
        w.write_all(&self.page_id.to_le_bytes())?;
        w.write_all(&self.cell_count.to_le_bytes())?;
        w.write_all(&self.flags.to_le_bytes())?;
        w.write_all(&self.checksum.to_le_bytes())?;
        w.write_all(&self.created_at.to_le_bytes())?;

        // table name: 32 bytes, null-padded
        let mut name_bytes = [0u8; 32];
        let tb = self.table.as_bytes();
        let copy_len = tb.len().min(32);
        name_bytes[..copy_len].copy_from_slice(&tb[..copy_len]);
        w.write_all(&name_bytes)?;

        w.write_all(&[0u8; 8])?; // reserved
        Ok(())
    }

    pub fn read_from(r: &mut impl Read) -> io::Result<Self> {
        let mut magic = [0u8; 4];
        r.read_exact(&mut magic)?;
        if &magic != PAGE_MAGIC {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                format!("bad page magic: {:?}", magic),
            ));
        }
        let mut buf = [0u8; 60];
        r.read_exact(&mut buf)?;

        let page_id    = u32::from_le_bytes(buf[0..4].try_into().unwrap());
        let cell_count = u16::from_le_bytes(buf[4..6].try_into().unwrap());
        let flags      = u16::from_le_bytes(buf[6..8].try_into().unwrap());
        let checksum   = u32::from_le_bytes(buf[8..12].try_into().unwrap());
        let created_at = u64::from_le_bytes(buf[12..20].try_into().unwrap());
        let table_raw  = &buf[20..52];
        let table_end  = table_raw.iter().position(|&b| b == 0).unwrap_or(32);
        let table = String::from_utf8_lossy(&table_raw[..table_end]).to_string();

        Ok(PageHeader { page_id, cell_count, flags, checksum, created_at, table })
    }
}

// ── StorageEngine ──────────────────────────────────────────────────────────

pub struct StorageEngine {
    pub pages_dir: PathBuf,
}

impl StorageEngine {
    pub fn open(pages_dir: impl AsRef<Path>) -> io::Result<Self> {
        let pages_dir = pages_dir.as_ref().to_path_buf();
        fs::create_dir_all(&pages_dir)?;
        Ok(Self { pages_dir })
    }

    /// Path for a table's page file.
    fn page_path(&self, table: &str) -> PathBuf {
        self.pages_dir.join(format!("{}.sagco", table))
    }

    /// Initialize a new table (creates the page file with header).
    /// No-op if the file already exists.
    pub fn init_table(&self, table: &str) -> io::Result<()> {
        let path = self.page_path(table);
        if path.exists() {
            return Ok(());
        }
        let f = File::create(&path)?;
        let mut w = BufWriter::new(f);
        let header = PageHeader::new(0, table);
        header.write_to(&mut w)?;
        w.flush()?;
        Ok(())
    }

    /// Append a cell to the table. Returns byte offset of written cell.
    pub fn put(&self, table: &str, cell: &Cell) -> io::Result<u64> {
        let path = self.page_path(table);
        if !path.exists() {
            self.init_table(table)?;
        }

        // Open for read+write to update header cell_count
        let mut f = OpenOptions::new().read(true).write(true).open(&path)?;

        // Read header
        let mut hdr = {
            let mut r = BufReader::new(&f);
            PageHeader::read_from(&mut r)?
        };

        // Seek to end to append
        let offset = f.seek(SeekFrom::End(0))?;

        {
            let mut w = BufWriter::new(&mut f);
            cell.write_to(&mut w)?;
            w.flush()?;
        }

        // Update cell_count in header (at byte 8, after magic+page_id)
        hdr.cell_count = hdr.cell_count.saturating_add(1);
        f.seek(SeekFrom::Start(4 + 4))?; // skip magic + page_id
        f.write_all(&hdr.cell_count.to_le_bytes())?;
        f.flush()?;

        Ok(offset)
    }

    /// Scan all cells in a table. Calls `f(offset, cell)` for each live cell.
    pub fn scan<F>(&self, table: &str, mut f: F) -> io::Result<()>
    where
        F: FnMut(u64, &Cell),
    {
        let path = self.page_path(table);
        if !path.exists() {
            return Ok(());
        }

        let file = File::open(&path)?;
        let mut r = BufReader::new(file);

        // Skip header
        PageHeader::read_from(&mut r)?;
        let mut offset = PAGE_HEADER_SIZE as u64;

        loop {
            match Cell::read_from(&mut r) {
                Ok(Some(cell)) => {
                    let cell_len = cell.byte_len() as u64;
                    if !cell.is_deleted() {
                        f(offset, &cell);
                    }
                    offset += cell_len;
                }
                Ok(None) => break,
                Err(e) => {
                    eprintln!("[storage] scan error at offset {}: {}", offset, e);
                    break;
                }
            }
        }
        Ok(())
    }

    /// Get the most recent value for a key (last writer wins, tombstone = deleted).
    pub fn get(&self, table: &str, key: &[u8]) -> io::Result<Option<Cell>> {
        let path = self.page_path(table);
        if !path.exists() {
            return Ok(None);
        }

        let file = File::open(&path)?;
        let mut r = BufReader::new(file);
        PageHeader::read_from(&mut r)?;

        // Raw scan — includes tombstones. Last cell for this key wins.
        let mut result: Option<Cell> = None;
        loop {
            match Cell::read_from(&mut r) {
                Ok(Some(cell)) if cell.key == key => result = Some(cell),
                Ok(Some(_))  => {}
                Ok(None)     => break,
                Err(e) => {
                    eprintln!("[storage] get scan error: {}", e);
                    break;
                }
            }
        }

        // If last write is a tombstone, key is deleted
        Ok(result.filter(|c| !c.is_deleted()))
    }

    /// Delete a key by appending a tombstone.
    pub fn delete(&self, table: &str, key: &[u8]) -> io::Result<()> {
        let tomb = Cell::tombstone(key.to_vec());
        self.put(table, &tomb)?;
        Ok(())
    }

    /// List all tables (page files in the pages dir).
    pub fn list_tables(&self) -> io::Result<Vec<String>> {
        let mut tables = vec![];
        for entry in fs::read_dir(&self.pages_dir)? {
            let entry = entry?;
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) == Some("sagco") {
                if let Some(stem) = path.file_stem().and_then(|s| s.to_str()) {
                    tables.push(stem.to_string());
                }
            }
        }
        tables.sort();
        Ok(tables)
    }

    /// Read the page header for a table.
    pub fn page_header(&self, table: &str) -> io::Result<Option<PageHeader>> {
        let path = self.page_path(table);
        if !path.exists() {
            return Ok(None);
        }
        let f = File::open(&path)?;
        let mut r = BufReader::new(f);
        Ok(Some(PageHeader::read_from(&mut r)?))
    }

    /// Compact a table: rewrite without deleted cells.
    /// Returns (cells_kept, cells_removed).
    pub fn compact(&self, table: &str) -> io::Result<(usize, usize)> {
        let path = self.page_path(table);
        if !path.exists() {
            return Ok((0, 0));
        }

        let mut live: Vec<Cell> = vec![];
        let mut dead: Vec<Cell> = vec![];
        let mut seen_keys: std::collections::HashMap<Vec<u8>, usize> = Default::default();

        // Collect all cells, last-write-wins per key
        {
            let file = File::open(&path)?;
            let mut r = BufReader::new(file);
            PageHeader::read_from(&mut r)?;
            while let Ok(Some(cell)) = Cell::read_from(&mut r) {
                seen_keys.insert(cell.key.clone(), live.len());
                if cell.is_deleted() {
                    dead.push(cell);
                } else {
                    live.push(cell);
                }
            }
        }

        // Remove overwritten keys (keep only the latest version)
        // seen_keys maps key → index of latest in live; anything earlier is stale
        let mut final_live = vec![];
        let live_len = live.len();
        for (i, cell) in live.into_iter().enumerate() {
            if seen_keys.get(&cell.key) == Some(&i) {
                final_live.push(cell);
            } else {
                dead.push(cell); // stale version
            }
        }

        let removed = live_len - final_live.len() + dead.len();
        let kept = final_live.len();

        // Rewrite
        let tmp_path = path.with_extension("sagco.compact");
        {
            let f = File::create(&tmp_path)?;
            let mut w = BufWriter::new(f);
            let mut hdr = PageHeader::new(0, table);
            hdr.cell_count = kept as u16;
            hdr.write_to(&mut w)?;
            for cell in &final_live {
                cell.write_to(&mut w)?;
            }
            w.flush()?;
        }
        fs::rename(tmp_path, path)?;

        Ok((kept, removed))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cell::Cell;
    use tempfile::tempdir;

    #[test]
    fn init_put_get() {
        let dir = tempdir().unwrap();
        let engine = StorageEngine::open(dir.path().join("pages")).unwrap();

        engine.init_table("MAT225").unwrap();
        let c = Cell::new(b"PA8".to_vec(), b"8*x^7*e^(x^8)".to_vec());
        engine.put("MAT225", &c).unwrap();

        let found = engine.get("MAT225", b"PA8").unwrap();
        assert!(found.is_some());
        assert_eq!(found.unwrap().value_str(), "8*x^7*e^(x^8)");
    }

    #[test]
    fn missing_key_returns_none() {
        let dir = tempdir().unwrap();
        let engine = StorageEngine::open(dir.path().join("pages")).unwrap();
        engine.init_table("tbl").unwrap();
        assert!(engine.get("tbl", b"ghost").unwrap().is_none());
    }

    #[test]
    fn delete_hides_cell() {
        let dir = tempdir().unwrap();
        let engine = StorageEngine::open(dir.path().join("pages")).unwrap();
        engine.init_table("tbl").unwrap();
        engine.put("tbl", &Cell::new(b"k".to_vec(), b"v".to_vec())).unwrap();
        engine.delete("tbl", b"k").unwrap();
        assert!(engine.get("tbl", b"k").unwrap().is_none());
    }

    #[test]
    fn compact_removes_dead_cells() {
        let dir = tempdir().unwrap();
        let engine = StorageEngine::open(dir.path().join("pages")).unwrap();
        engine.init_table("tbl").unwrap();
        engine.put("tbl", &Cell::new(b"k1".to_vec(), b"v1".to_vec())).unwrap();
        engine.put("tbl", &Cell::new(b"k2".to_vec(), b"v2".to_vec())).unwrap();
        engine.delete("tbl", b"k1").unwrap();
        let (kept, removed) = engine.compact("tbl").unwrap();
        assert_eq!(kept, 1);
        assert!(removed >= 1);
        assert!(engine.get("tbl", b"k1").unwrap().is_none());
        assert_eq!(engine.get("tbl", b"k2").unwrap().unwrap().value_str(), "v2");
    }
}
