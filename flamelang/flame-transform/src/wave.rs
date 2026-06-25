// L4 — Wave transform: map gematria values to Solfeggio Hz resonances
// The output sequence drives the DNA codon selection in L5.
//
// Mapping rule (sacred geometry):
//   gematria mod 6  →  Solfeggio frequency
//     0 → 432 Hz  (grounding / Schumann resonance)
//     1 → 528 Hz  (DNA repair / transformation)
//     2 → 639 Hz  (relationships / connection)
//     3 → 741 Hz  (expression / problem solving)
//     4 → 852 Hz  (intuition / spiritual order)
//     5 → 963 Hz  (oneness / crown chakra)

use anyhow::Result;

const SOLFEGGIO: [f64; 6] = [432.0, 528.0, 639.0, 741.0, 852.0, 963.0];

pub fn synthesise(gematria_map: &[(String, u32)]) -> Result<Vec<f64>> {
    let seq: Vec<f64> = gematria_map
        .iter()
        .map(|(_, g)| SOLFEGGIO[(g % 6) as usize])
        .collect();
    Ok(seq)
}
