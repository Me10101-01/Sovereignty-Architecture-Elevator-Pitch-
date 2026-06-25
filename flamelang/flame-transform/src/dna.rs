// L5 — DNA transform: map wave sequence → AGTC codon strand
// Integrates with quantum_dna_splicer.rs (sibling file at repo root).
//
// Encoding table (Hz → primary codon):
//   432 Hz → ATG  (start codon / methionine — grounding anchor)
//   528 Hz → GAT  (aspartate — repair signal)
//   639 Hz → CGA  (arginine — connectivity)
//   741 Hz → TAC  (tyrosine — expression)
//   852 Hz → AAG  (lysine — intuition)
//   963 Hz → GGC  (glycine — unity / crown)
//   other  → TAG  (stop codon — unresolved frequency)

use anyhow::Result;

const ATG: &str = "ATG";
const GAT: &str = "GAT";
const CGA: &str = "CGA";
const TAC: &str = "TAC";
const AAG: &str = "AAG";
const GGC: &str = "GGC";
const TAG: &str = "TAG";

fn hz_to_codon(hz: f64) -> &'static str {
    match hz as u32 {
        432 => ATG,
        528 => GAT,
        639 => CGA,
        741 => TAC,
        852 => AAG,
        963 => GGC,
        _   => TAG,
    }
}

pub fn encode(wave_seq: &[f64]) -> Result<String> {
    let strand: String = wave_seq.iter().map(|hz| hz_to_codon(*hz)).collect::<Vec<_>>().join("-");
    Ok(strand)
}
