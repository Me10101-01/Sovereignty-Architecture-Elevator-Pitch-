// SAGCO Polyglot Antibody — AI Engineering Bottleneck Classifier
// One EUR schema across: Shell | Rust | Python | SQL | Ghidra | AI | Academic
// License: SSL-1.0 — Strategickhaos DAO LLC

use super::types::{Antibody, Trajectory, EurScore};

#[derive(Debug, Clone, PartialEq)]
pub enum Domain {
    Shell,
    Rust,
    Python,
    Sql,
    Ghidra,
    Ai,
    Academic,
    Unknown,
}

impl Domain {
    pub fn from_str(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "shell" | "bash" | "sh"       => Domain::Shell,
            "rust" | "cargo"              => Domain::Rust,
            "python" | "py"               => Domain::Python,
            "sql" | "sqlite"              => Domain::Sql,
            "ghidra" | "binary" | "elf"   => Domain::Ghidra,
            "ai" | "llm" | "claude"       => Domain::Ai,
            "academic" | "snhu" | "course" => Domain::Academic,
            _                              => Domain::Unknown,
        }
    }
}

#[derive(Debug, Clone)]
pub struct PolyglotRow {
    pub domain:     Domain,
    pub name:       String,
    pub expected:   String,
    pub actual:     String,
    pub antibody:   Antibody,
    pub trajectory: Trajectory,
    pub score:      EurScore,
}

pub fn classify_polyglot(output: &str, exit_code: i32, domain: &Domain) -> (Antibody, Trajectory) {
    let text = output.to_lowercase();
    match domain {
        Domain::Shell => {
            if text.contains("no such file") || text.contains("cannot stat") {
                (Antibody::PathDiscovery, Trajectory::Adaptation)
            } else if text.contains("command not found") {
                (Antibody::Dependency, Trajectory::Adaptation)
            } else if exit_code == 0 {
                (Antibody::PassImmunity, Trajectory::Stabilized)
            } else {
                (Antibody::UnknownVariance, Trajectory::Mutation)
            }
        }
        Domain::Rust => {
            if text.contains("cannot find") && text.contains("cargo.toml") {
                (Antibody::ProjectRoot, Trajectory::Adaptation)
            } else if text.contains("borrow") || text.contains("does not live") {
                (Antibody::BorrowChecker, Trajectory::Evolution)
            } else if text.contains("error[e") {
                (Antibody::CompileError, Trajectory::Adaptation)
            } else if exit_code == 0 {
                (Antibody::PassImmunity, Trajectory::Stabilized)
            } else {
                (Antibody::UnknownVariance, Trajectory::Mutation)
            }
        }
        Domain::Python => {
            if text.contains("indentationerror") || text.contains("syntaxerror") {
                (Antibody::SyntaxError, Trajectory::Adaptation)
            } else if text.contains("modulenotfounderror") || text.contains("importerror") {
                (Antibody::ImportError, Trajectory::Adaptation)
            } else if exit_code == 0 {
                (Antibody::PassImmunity, Trajectory::Stabilized)
            } else {
                (Antibody::UnknownVariance, Trajectory::Mutation)
            }
        }
        Domain::Sql => {
            if text.contains("no such table") || text.contains("no such column") {
                (Antibody::SchemaError, Trajectory::Adaptation)
            } else if text.contains("unable to open") {
                (Antibody::Dependency, Trajectory::Adaptation)
            } else if exit_code == 0 {
                (Antibody::PassImmunity, Trajectory::Stabilized)
            } else {
                (Antibody::UnknownVariance, Trajectory::Mutation)
            }
        }
        Domain::Ghidra => {
            if text.contains("not a valid directory") || text.contains("invalidinputexception") {
                (Antibody::PathDiscovery, Trajectory::Adaptation)
            } else if text.contains("jdk 21") || text.contains("jdk") {
                (Antibody::JdkGate, Trajectory::Evolution)
            } else if text.contains("decompil") && text.contains("not exist") {
                (Antibody::PlatformLimitation, Trajectory::Evolution)
            } else if exit_code == 0 {
                (Antibody::PassImmunity, Trajectory::Stabilized)
            } else {
                (Antibody::UnknownVariance, Trajectory::Mutation)
            }
        }
        Domain::Ai => {
            if text.contains("context") && text.contains("limit") {
                (Antibody::ContextCollapse, Trajectory::Evolution)
            } else if text.contains("rate") && text.contains("limit") {
                (Antibody::RateLimit, Trajectory::Adaptation)
            } else if exit_code == 0 {
                (Antibody::PassImmunity, Trajectory::Stabilized)
            } else {
                (Antibody::UnknownVariance, Trajectory::Mutation)
            }
        }
        Domain::Academic => {
            if text.contains("prerequisite") || text.contains("not met") {
                (Antibody::PrerequisiteGate, Trajectory::Adaptation)
            } else if text.contains("bottleneck") || text.contains("blocked") {
                (Antibody::CurriculumBottleneck, Trajectory::Evolution)
            } else if exit_code == 0 {
                (Antibody::PassImmunity, Trajectory::Stabilized)
            } else {
                (Antibody::UnknownVariance, Trajectory::Mutation)
            }
        }
        Domain::Unknown => {
            if exit_code == 0 {
                (Antibody::PassImmunity, Trajectory::Stabilized)
            } else {
                (Antibody::UnknownVariance, Trajectory::Mutation)
            }
        }
    }
}
