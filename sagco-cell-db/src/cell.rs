/// One record — the atomic unit of the database.
///
/// Binary layout (on-disk):
///   [CELL][version:1][flags:1][key_len:2][val_len:4][checksum:4][ts:8][key...][val...]
///   Total header = 4+1+1+2+4+4+8 = 24 bytes
///
/// In memory: fully-owned key/value byte slices plus the metadata.

use std::io::{self, Read, Write};
use crc32fast::Hasher;

pub const CELL_MAGIC: &[u8; 4] = b"CELL";
pub const CELL_HEADER_SIZE: usize = 24;

/// Flags stored in the cell header.
pub mod flags {
    pub const DELETED: u8 = 0b0000_0001;
    pub const TOMBSTONE: u8 = 0b0000_0010;
}

#[derive(Debug, Clone, PartialEq)]
pub struct Cell {
    pub version: u8,
    pub flags: u8,
    pub timestamp: u64,
    pub key: Vec<u8>,
    pub value: Vec<u8>,
}

impl Cell {
    pub fn new(key: impl Into<Vec<u8>>, value: impl Into<Vec<u8>>) -> Self {
        Self {
            version: 1,
            flags: 0,
            timestamp: now_micros(),
            key: key.into(),
            value: value.into(),
        }
    }

    pub fn tombstone(key: impl Into<Vec<u8>>) -> Self {
        Self {
            version: 1,
            flags: flags::DELETED | flags::TOMBSTONE,
            timestamp: now_micros(),
            key: key.into(),
            value: vec![],
        }
    }

    pub fn is_deleted(&self) -> bool {
        self.flags & flags::DELETED != 0
    }

    pub fn key_str(&self) -> &str {
        std::str::from_utf8(&self.key).unwrap_or("<binary>")
    }

    pub fn value_str(&self) -> &str {
        std::str::from_utf8(&self.value).unwrap_or("<binary>")
    }

    /// Serialized size in bytes.
    pub fn byte_len(&self) -> usize {
        CELL_HEADER_SIZE + self.key.len() + self.value.len()
    }

    /// Write cell to any Write sink. Returns bytes written.
    pub fn write_to(&self, w: &mut impl Write) -> io::Result<usize> {
        let key_len = self.key.len() as u16;
        let val_len = self.value.len() as u32;

        // compute checksum over key + value
        let mut h = Hasher::new();
        h.update(&self.key);
        h.update(&self.value);
        let checksum = h.finalize();

        w.write_all(CELL_MAGIC)?;
        w.write_all(&[self.version, self.flags])?;
        w.write_all(&key_len.to_le_bytes())?;
        w.write_all(&val_len.to_le_bytes())?;
        w.write_all(&checksum.to_le_bytes())?;
        w.write_all(&self.timestamp.to_le_bytes())?;
        w.write_all(&self.key)?;
        w.write_all(&self.value)?;

        Ok(self.byte_len())
    }

    /// Read one cell from any Read source. Returns None at clean EOF.
    pub fn read_from(r: &mut impl Read) -> io::Result<Option<Self>> {
        let mut magic = [0u8; 4];
        match r.read_exact(&mut magic) {
            Ok(_) => {}
            Err(e) if e.kind() == io::ErrorKind::UnexpectedEof => return Ok(None),
            Err(e) => return Err(e),
        }
        if &magic != CELL_MAGIC {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                format!("bad cell magic: {:?}", magic),
            ));
        }

        let mut meta = [0u8; 20]; // version(1)+flags(1)+key_len(2)+val_len(4)+checksum(4)+ts(8)
        r.read_exact(&mut meta)?;

        let version   = meta[0];
        let flags     = meta[1];
        let key_len   = u16::from_le_bytes([meta[2], meta[3]]) as usize;
        let val_len   = u32::from_le_bytes([meta[4], meta[5], meta[6], meta[7]]) as usize;
        let stored_cs = u32::from_le_bytes([meta[8], meta[9], meta[10], meta[11]]);
        let timestamp = u64::from_le_bytes(meta[12..20].try_into().unwrap());

        let mut key = vec![0u8; key_len];
        r.read_exact(&mut key)?;
        let mut value = vec![0u8; val_len];
        r.read_exact(&mut value)?;

        // verify checksum
        let mut h = Hasher::new();
        h.update(&key);
        h.update(&value);
        let actual_cs = h.finalize();
        if actual_cs != stored_cs {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                format!(
                    "cell checksum mismatch for key {:?}: stored={:#010x} actual={:#010x}",
                    String::from_utf8_lossy(&key), stored_cs, actual_cs
                ),
            ));
        }

        Ok(Some(Cell { version, flags, timestamp, key, value }))
    }
}

fn now_micros() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_micros() as u64)
        .unwrap_or(0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trip() {
        let c = Cell::new(b"hello".to_vec(), b"world".to_vec());
        let mut buf = Vec::new();
        c.write_to(&mut buf).unwrap();
        assert_eq!(buf.len(), c.byte_len());

        let mut cursor = std::io::Cursor::new(&buf);
        let c2 = Cell::read_from(&mut cursor).unwrap().unwrap();
        assert_eq!(c.key, c2.key);
        assert_eq!(c.value, c2.value);
        assert_eq!(c.flags, c2.flags);
    }

    #[test]
    fn detects_corruption() {
        let c = Cell::new(b"key".to_vec(), b"val".to_vec());
        let mut buf = Vec::new();
        c.write_to(&mut buf).unwrap();

        // flip a byte in the value region
        let last = buf.len() - 1;
        buf[last] ^= 0xFF;

        let mut cursor = std::io::Cursor::new(&buf);
        assert!(Cell::read_from(&mut cursor).is_err());
    }

    #[test]
    fn tombstone_round_trip() {
        let t = Cell::tombstone(b"dead-key".to_vec());
        assert!(t.is_deleted());
        let mut buf = Vec::new();
        t.write_to(&mut buf).unwrap();
        let mut cursor = std::io::Cursor::new(&buf);
        let t2 = Cell::read_from(&mut cursor).unwrap().unwrap();
        assert!(t2.is_deleted());
    }
}
