/// Hash index — brick 4.
///
/// Maps key bytes → page file byte offset, so `get` doesn't need a full scan.
///
/// On-disk format (.sagco-idx):
///   [IDX_MAGIC 4][version 1][entry_count 4][reserved 3]
///   For each entry: [key_len 2][key ...][offset 8]
///
/// The index is loaded entirely into memory (suitable for millions of keys).
/// Writes go to the page file first, then the index is updated.

use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{self, BufReader, BufWriter, Read, Write};
use std::path::{Path, PathBuf};

pub const IDX_MAGIC: &[u8; 4] = b"SIDX";
pub const IDX_HEADER_SIZE: usize = 12;

pub struct KeyIndex {
    /// key → latest byte offset in the page file
    map: HashMap<Vec<u8>, u64>,
    path: PathBuf,
    dirty: bool,
}

impl KeyIndex {
    /// Open or create an index file for a table.
    pub fn open(index_dir: impl AsRef<Path>, table: &str) -> io::Result<Self> {
        let path = index_dir.as_ref().join(format!("{}.sagco-idx", table));
        let map = if path.exists() {
            Self::load_from(&path)?
        } else {
            HashMap::new()
        };
        Ok(Self { map, path, dirty: false })
    }

    fn load_from(path: &Path) -> io::Result<HashMap<Vec<u8>, u64>> {
        let f = File::open(path)?;
        let mut r = BufReader::new(f);

        let mut magic = [0u8; 4];
        r.read_exact(&mut magic)?;
        if &magic != IDX_MAGIC {
            return Err(io::Error::new(io::ErrorKind::InvalidData, "bad index magic"));
        }

        let mut header = [0u8; 8];
        r.read_exact(&mut header)?;
        let entry_count = u32::from_le_bytes(header[1..5].try_into().unwrap()) as usize;

        let mut map = HashMap::with_capacity(entry_count);
        for _ in 0..entry_count {
            let mut kl_buf = [0u8; 2];
            r.read_exact(&mut kl_buf)?;
            let key_len = u16::from_le_bytes(kl_buf) as usize;
            let mut key = vec![0u8; key_len];
            r.read_exact(&mut key)?;
            let mut off_buf = [0u8; 8];
            r.read_exact(&mut off_buf)?;
            let offset = u64::from_le_bytes(off_buf);
            map.insert(key, offset);
        }
        Ok(map)
    }

    /// Insert or update key → offset. Marks index dirty.
    pub fn put(&mut self, key: Vec<u8>, offset: u64) {
        self.map.insert(key, offset);
        self.dirty = true;
    }

    /// Remove a key (tombstone). Marks dirty.
    pub fn remove(&mut self, key: &[u8]) {
        if self.map.remove(key).is_some() {
            self.dirty = true;
        }
    }

    /// Look up offset for a key. O(1).
    pub fn get(&self, key: &[u8]) -> Option<u64> {
        self.map.get(key).copied()
    }

    pub fn contains(&self, key: &[u8]) -> bool {
        self.map.contains_key(key)
    }

    pub fn len(&self) -> usize {
        self.map.len()
    }

    pub fn is_empty(&self) -> bool {
        self.map.is_empty()
    }

    /// Flush index to disk if dirty.
    pub fn flush(&mut self) -> io::Result<()> {
        if !self.dirty {
            return Ok(());
        }

        if let Some(parent) = self.path.parent() {
            fs::create_dir_all(parent)?;
        }

        let f = File::create(&self.path)?;
        let mut w = BufWriter::new(f);

        w.write_all(IDX_MAGIC)?;
        w.write_all(&[1u8])?; // version
        w.write_all(&(self.map.len() as u32).to_le_bytes())?;
        w.write_all(&[0u8; 3])?; // reserved

        for (key, offset) in &self.map {
            w.write_all(&(key.len() as u16).to_le_bytes())?;
            w.write_all(key)?;
            w.write_all(&offset.to_le_bytes())?;
        }

        w.flush()?;
        self.dirty = false;
        Ok(())
    }

    /// Rebuild index from a full page scan (used after compact or corruption).
    pub fn rebuild_from_scan<F>(&mut self, mut scanner: F) -> io::Result<()>
    where
        F: FnMut(&mut dyn FnMut(u64, &[u8])),
    {
        self.map.clear();
        scanner(&mut |offset, key| {
            self.map.insert(key.to_vec(), offset);
        });
        self.dirty = true;
        self.flush()
    }
}

impl Drop for KeyIndex {
    fn drop(&mut self) {
        if self.dirty {
            let _ = self.flush();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn put_get_flush_reload() {
        let dir = tempdir().unwrap();
        let mut idx = KeyIndex::open(dir.path(), "test").unwrap();
        idx.put(b"PA8".to_vec(), 1024);
        idx.put(b"PA9".to_vec(), 2048);
        idx.flush().unwrap();

        let idx2 = KeyIndex::open(dir.path(), "test").unwrap();
        assert_eq!(idx2.get(b"PA8"), Some(1024));
        assert_eq!(idx2.get(b"PA9"), Some(2048));
        assert_eq!(idx2.get(b"PA10"), None);
    }

    #[test]
    fn remove_key() {
        let dir = tempdir().unwrap();
        let mut idx = KeyIndex::open(dir.path(), "test").unwrap();
        idx.put(b"key".to_vec(), 64);
        idx.remove(b"key");
        idx.flush().unwrap();

        let idx2 = KeyIndex::open(dir.path(), "test").unwrap();
        assert_eq!(idx2.get(b"key"), None);
    }
}
