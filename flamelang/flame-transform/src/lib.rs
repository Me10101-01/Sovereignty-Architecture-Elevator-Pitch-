// flame-transform — L3 Hebrew  ·  L4 Wave  ·  L5 DNA
// Three-stage biological transform pipeline.
// Input:  flame_parser::Program (AST)
// Output: TransformOutput (gematria map, wave sequence, dna strand)

pub mod hebrew;
pub mod wave;
pub mod dna;

use anyhow::Result;
use flame_parser::Program;

#[derive(Debug, Clone)]
pub struct TransformOutput {
    pub gematria_map: Vec<(String, u32)>,
    pub wave_seq:     Vec<f64>,
    pub dna_strand:   String,
}

pub fn run(program: &Program) -> Result<TransformOutput> {
    let gematria_map = hebrew::extract(program)?;
    let wave_seq     = wave::synthesise(&gematria_map)?;
    let dna_strand   = dna::encode(&wave_seq)?;
    Ok(TransformOutput { gematria_map, wave_seq, dna_strand })
}
