use anyhow::Result;
use sha2::{Digest, Sha256};
use std::io::Read;
use std::path::Path;

pub fn sha256_file(path: &Path) -> Result<String> {
    let mut file = std::fs::File::open(path)
        .map_err(|e| anyhow::anyhow!("Cannot open {}: {}", path.display(), e))?;
    let mut hasher = Sha256::new();
    let mut buf = [0u8; 65536];
    loop {
        let n = file.read(&mut buf)?;
        if n == 0 {
            break;
        }
        hasher.update(&buf[..n]);
    }
    Ok(hex::encode(hasher.finalize()))
}

pub fn sha256_bytes(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hex::encode(hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write as IoWrite;
    use tempfile::NamedTempFile;

    #[test]
    fn test_sha256_bytes_known() {
        // SHA-256("") = e3b0c44298...
        let hash = sha256_bytes(b"");
        assert!(hash.starts_with("e3b0c442"));
        assert_eq!(hash.len(), 64);
    }

    #[test]
    fn test_sha256_file_matches_bytes() {
        let mut f = NamedTempFile::new().unwrap();
        f.write_all(b"sagco test content").unwrap();
        let path = f.path().to_path_buf();
        let file_hash = sha256_file(&path).unwrap();
        let byte_hash = sha256_bytes(b"sagco test content");
        assert_eq!(file_hash, byte_hash);
    }
}
