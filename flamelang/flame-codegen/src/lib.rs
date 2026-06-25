// flame-codegen — L6 LLVM IR generation
// Consumes TransformOutput + the parsed AST and emits LLVM IR text.
// This is a stub — full LLVM integration requires inkwell + llvm17 toolchain.
// The stub produces human-readable pseudo-IR for inspection / testing.

use anyhow::Result;
use flame_transform::TransformOutput;
use flame_parser::Program;

pub struct CodegenOutput {
    pub ir:         String,
    pub dna_strand: String,
}

pub fn emit(program: &Program, transform: &TransformOutput) -> Result<CodegenOutput> {
    let mut ir = String::new();

    ir.push_str("; FlameLang v2.0 — SAGCO-Organism LLVM IR\n");
    ir.push_str("; DNA strand: ");
    ir.push_str(&transform.dna_strand);
    ir.push_str("\n\n");
    ir.push_str("define void @flame_main() {\n");
    ir.push_str("entry:\n");

    for (label, weight) in &transform.gematria_map {
        ir.push_str(&format!("  ; gematria [{label}] = {weight}\n"));
    }

    for (i, hz) in transform.wave_seq.iter().enumerate() {
        ir.push_str(&format!("  %wave_{i} = fadd double 0.0, {hz:.1}\n"));
    }

    ir.push_str("  ret void\n}\n");

    Ok(CodegenOutput {
        ir,
        dna_strand: transform.dna_strand.clone(),
    })
}
