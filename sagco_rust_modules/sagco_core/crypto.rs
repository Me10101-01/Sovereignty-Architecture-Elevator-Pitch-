// SAGCO-Core crypto — pure Rust SHA-256, zero external dependencies
// [SEAL] stops being printed text and becomes a real cryptographic artifact.
// License: SSL-1.0 — Strategickhaos DAO LLC

use std::fs;
use std::io;

// ── SHA-256 constants ─────────────────────────────────────────────────────────
// First 32 bits of the fractional parts of the cube roots of the first 64 primes
#[rustfmt::skip]
const K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

// First 32 bits of the fractional parts of the square roots of the first 8 primes
const H0: [u32; 8] = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
];

// ── SHA-256 core ──────────────────────────────────────────────────────────────

pub fn sha256(data: &[u8]) -> [u8; 32] {
    let mut h = H0;
    let bit_len = (data.len() as u64).wrapping_mul(8);

    // pad: append 0x80, then zeros, then 64-bit big-endian bit length
    let mut padded = data.to_vec();
    padded.push(0x80);
    while padded.len() % 64 != 56 {
        padded.push(0);
    }
    padded.extend_from_slice(&bit_len.to_be_bytes());

    // process 512-bit (64-byte) blocks
    for block in padded.chunks(64) {
        let mut w = [0u32; 64];

        // fill first 16 words from block
        for i in 0..16 {
            w[i] = u32::from_be_bytes([block[i*4], block[i*4+1], block[i*4+2], block[i*4+3]]);
        }

        // extend to 64 words
        for i in 16..64 {
            let s0 = w[i-15].rotate_right(7) ^ w[i-15].rotate_right(18) ^ (w[i-15] >> 3);
            let s1 = w[i-2].rotate_right(17) ^ w[i-2].rotate_right(19) ^ (w[i-2] >> 10);
            w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1);
        }

        // compression — explicit assignments avoid any array-destructure ambiguity
        let mut a = h[0]; let mut b = h[1]; let mut c = h[2]; let mut d = h[3];
        let mut e = h[4]; let mut f = h[5]; let mut g = h[6]; let mut hh = h[7];

        for i in 0..64 {
            let s1  = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch  = (e & f) ^ ((!e) & g);
            let t1  = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0  = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2  = s0.wrapping_add(maj);

            hh = g; g = f; f = e;
            e  = d.wrapping_add(t1);
            d  = c; c = b; b = a;
            a  = t1.wrapping_add(t2);
        }

        h[0] = h[0].wrapping_add(a); h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c); h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e); h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g); h[7] = h[7].wrapping_add(hh);
    }

    // final hash → 32 bytes
    let mut out = [0u8; 32];
    for (i, word) in h.iter().enumerate() {
        out[i*4..(i+1)*4].copy_from_slice(&word.to_be_bytes());
    }
    out
}

pub fn sha256_hex(data: &[u8]) -> String {
    sha256(data).iter().map(|b| format!("{:02x}", b)).collect()
}

// ── Evidence sealing ──────────────────────────────────────────────────────────

#[derive(Debug)]
pub enum SealError {
    IoError(io::Error),
    EmptyPayload,
}

impl From<io::Error> for SealError {
    fn from(e: io::Error) -> Self { SealError::IoError(e) }
}

pub struct SealResult {
    pub path:   String,
    pub bytes:  usize,
    pub sha256: String,
}

/// Seal a file: read it, SHA-256 hash it, write a .sha256 sidecar.
/// Returns Err(EmptyPayload) if the file has zero bytes — EMPTY_PAYLOAD_ANTIBODY.
pub fn seal_file(path: &str) -> Result<SealResult, SealError> {
    let data = fs::read(path)?;
    if data.is_empty() {
        return Err(SealError::EmptyPayload);
    }
    let hex = sha256_hex(&data);

    // write sidecar: evidence.bin → evidence.bin.sha256
    let sidecar = format!("{}.sha256", path);
    fs::write(&sidecar, format!("SHA256({})={}\n", path, hex))?;

    Ok(SealResult { path: path.to_string(), bytes: data.len(), sha256: hex })
}

/// Seal raw bytes — used for in-memory evidence artifacts.
pub fn seal_bytes(label: &str, data: &[u8]) -> Result<SealResult, SealError> {
    if data.is_empty() {
        return Err(SealError::EmptyPayload);
    }
    Ok(SealResult {
        path:   label.to_string(),
        bytes:  data.len(),
        sha256: sha256_hex(data),
    })
}

/// Verify a seal: recompute SHA-256 and compare against stored sidecar.
pub fn verify_seal(path: &str) -> bool {
    let sidecar = format!("{}.sha256", path);
    let expected = fs::read_to_string(&sidecar)
        .unwrap_or_default()
        .trim()
        .to_string();
    let data = match fs::read(path) {
        Ok(d) => d,
        Err(_) => return false,
    };
    let actual = format!("SHA256({})={}", path, sha256_hex(&data));
    expected == actual
}

// ── SealLedger: cryptographic audit chain ────────────────────────────────────

pub struct SealLedger {
    entries: Vec<(String, String)>,  // (label, sha256_hex)
}

impl SealLedger {
    pub fn new() -> Self { SealLedger { entries: Vec::new() } }

    pub fn record(&mut self, label: &str, sha256: &str) {
        self.entries.push((label.to_string(), sha256.to_string()));
    }

    pub fn chain_hash(&self) -> String {
        // hash of all recorded seals in order — the ledger fingerprint
        let combined: String = self.entries
            .iter()
            .map(|(l, h)| format!("{}:{}", l, h))
            .collect::<Vec<_>>()
            .join("|");
        sha256_hex(combined.as_bytes())
    }

    pub fn len(&self) -> usize { self.entries.len() }
    pub fn is_empty(&self) -> bool { self.entries.is_empty() }
    pub fn entries(&self) -> &[(String, String)] { &self.entries }

    pub fn export(&self) -> String {
        self.entries.iter()
            .map(|(l, h)| format!("{}  {}", h, l))
            .collect::<Vec<_>>()
            .join("\n")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sha256_empty_string() {
        // known SHA-256 of empty string
        let h = sha256_hex(b"");
        assert_eq!(h, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    }

    #[test]
    fn sha256_abc() {
        assert_eq!(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        );
    }

    #[test]
    fn sha256_sagco_dna() {
        // SAGCO_COMMAND_DNA fingerprint must be deterministic
        let h = sha256_hex(b"SAGCO_COMMAND_DNA=a364ca9f90356c85");
        assert!(!h.is_empty());
        assert_eq!(h.len(), 64);
    }

    #[test]
    fn seal_bytes_rejects_empty() {
        let r = seal_bytes("test", b"");
        assert!(matches!(r, Err(SealError::EmptyPayload)));
    }

    #[test]
    fn seal_bytes_real_data() {
        let data = b"wave gcp_services.txt pulse 793398609444 seal evidence.bin";
        let r = seal_bytes("pipeline.txt", data).unwrap();
        assert_eq!(r.bytes, data.len());
        assert_eq!(r.sha256.len(), 64);
        assert!(!r.sha256.starts_with("00000000"));
    }

    #[test]
    fn ledger_chain_hash_deterministic() {
        let mut l = SealLedger::new();
        l.record("evidence.bin", "abc123");
        l.record("pipeline.txt", "def456");
        let h1 = l.chain_hash();
        let h2 = l.chain_hash();
        assert_eq!(h1, h2);   // deterministic
        assert_eq!(h1.len(), 64);
    }

    #[test]
    fn ledger_chain_hash_changes_with_order() {
        let mut l1 = SealLedger::new();
        l1.record("a", "111"); l1.record("b", "222");

        let mut l2 = SealLedger::new();
        l2.record("b", "222"); l2.record("a", "111");

        assert_ne!(l1.chain_hash(), l2.chain_hash());
    }
}
