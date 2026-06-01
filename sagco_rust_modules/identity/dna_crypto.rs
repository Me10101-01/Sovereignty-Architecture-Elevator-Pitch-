// SAGCO Identity — Command DNA verification and validation signatures
// License: SSL-1.0 — Strategickhaos DAO LLC

pub const KNOWN_DNA: &str = "a364ca9f90356c85";
pub const PAST_CHAIN_SHA: &str = "b8fa135d85b60795c36f07c5e77f163eeca2d05dca2510750cade34525a1ef0f";

pub struct DnaRecord {
    pub strand:    String,
    pub valid:     bool,
    pub source:    String,
}

pub fn verify_dna(candidate: &str) -> DnaRecord {
    let clean = candidate
        .trim()
        .trim_start_matches("SAGCO_COMMAND_DNA=");

    let valid = clean == KNOWN_DNA;
    DnaRecord {
        strand: clean.to_string(),
        valid,
        source: "sagco cmd dna".to_string(),
    }
}

pub fn fingerprint_stable(fp_a: &str, fp_b: &str) -> bool {
    // same source → same fingerprint across past and wave compilers
    fp_a == fp_b
}
