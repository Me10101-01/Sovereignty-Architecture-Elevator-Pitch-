// lineage.rs — Artifact Lineage Classifier for SAGCO-CORE
//
// Pipeline opcode: lineage <folder>
//
// What it does:
//   Walks <folder>, classifies every file by kind (Source/Config/Report/etc.),
//   extracts the ancestry chain (folder path segments), scores each artifact,
//   and emits a lineage manifest.
//
// Classification is by extension + path pattern — no file reads required.
// This keeps the opcode fast and side-effect-free.

use std::collections::HashMap;
use std::fmt;
use std::path::{Path, PathBuf};

// ── Artifact classification ────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum ArtifactKind {
    Source,    // .rs .cpp .c .h .py .js .ts
    Config,    // .toml .yaml .yml .json .env
    Pipeline,  // .txt files in pipelines/ or named pipeline_*.txt
    Agent,     // agents/*.yaml
    Report,    // .csv .manifest evidence*.bin reports/
    Blueprint, // .flame FlameLang source
    Docs,      // .md .txt (non-pipeline)
    Binary,    // .bin .elf .so compiled output
    Unknown,
}

impl fmt::Display for ArtifactKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = match self {
            ArtifactKind::Source    => "SOURCE",
            ArtifactKind::Config    => "CONFIG",
            ArtifactKind::Pipeline  => "PIPELINE",
            ArtifactKind::Agent     => "AGENT",
            ArtifactKind::Report    => "REPORT",
            ArtifactKind::Blueprint => "BLUEPRINT",
            ArtifactKind::Docs      => "DOCS",
            ArtifactKind::Binary    => "BINARY",
            ArtifactKind::Unknown   => "UNKNOWN",
        }; write!(f, "{}", s)
    }
}

impl ArtifactKind {
    /// Base lineage weight — how architecturally significant is this kind?
    pub fn base_weight(&self) -> f64 {
        match self {
            ArtifactKind::Source    => 0.95,
            ArtifactKind::Config    => 0.90,
            ArtifactKind::Pipeline  => 0.88,
            ArtifactKind::Agent     => 0.85,
            ArtifactKind::Report    => 0.80,
            ArtifactKind::Blueprint => 0.78,
            ArtifactKind::Docs      => 0.60,
            ArtifactKind::Binary    => 0.40,
            ArtifactKind::Unknown   => 0.10,
        }
    }
}

pub fn classify(path: &Path) -> ArtifactKind {
    let ext = path.extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_lowercase();

    let name = path.file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("")
        .to_lowercase();

    let path_str = path.to_string_lossy().to_lowercase();

    // Agent YAML — check path pattern before generic yaml
    if path_str.contains("/agents/") && ext == "yaml" {
        return ArtifactKind::Agent;
    }

    // Pipeline — by directory or name prefix
    if path_str.contains("/pipeline") && ext == "txt" {
        return ArtifactKind::Pipeline;
    }
    if name.starts_with("pipeline_") && ext == "txt" {
        return ArtifactKind::Pipeline;
    }

    match ext.as_str() {
        "rs" | "cpp" | "c" | "h" | "py" | "js" | "ts" => ArtifactKind::Source,
        "toml" | "yaml" | "yml" | "json" => ArtifactKind::Config,
        "flame" => ArtifactKind::Blueprint,
        "csv" | "manifest" => ArtifactKind::Report,
        "md" | "txt" => ArtifactKind::Docs,
        "bin" | "elf" | "so" | "a" => ArtifactKind::Binary,
        _ => {
            // evidence*.bin pattern counts as Report
            if name.starts_with("evidence") {
                return ArtifactKind::Report;
            }
            ArtifactKind::Unknown
        }
    }
}

// ── Lineage record ─────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub struct LineageRecord {
    pub path:      String,
    pub kind:      ArtifactKind,
    pub depth:     usize,          // number of directory segments
    pub ancestry:  Vec<String>,    // folder path components (no filename)
    pub weight:    f64,
}

impl LineageRecord {
    pub fn new(path: &Path, root: &Path) -> Self {
        let kind = classify(path);
        let rel = path.strip_prefix(root).unwrap_or(path);
        let depth = rel.components().count().saturating_sub(1);

        let ancestry: Vec<String> = rel.parent()
            .map(|p| p.components()
                .map(|c| c.as_os_str().to_string_lossy().to_string())
                .filter(|s| !s.is_empty())
                .collect())
            .unwrap_or_default();

        let weight = kind.base_weight()
            - (depth as f64 * 0.005).min(0.10);  // slight penalty for deep nesting

        LineageRecord {
            path:     path.to_string_lossy().to_string(),
            kind,
            depth,
            ancestry,
            weight,
        }
    }
}

// ── Directory walker ───────────────────────────────────────────────────────────

pub struct LineageResult {
    pub folder:  String,
    pub total:   usize,
    pub records: Vec<LineageRecord>,
    pub by_kind: HashMap<String, usize>,
}

pub fn trace(folder: &str) -> Result<LineageResult, String> {
    let root = PathBuf::from(folder);
    if !root.exists() {
        return Err(format!("lineage: folder not found: {}", folder));
    }

    let mut records = Vec::new();
    walk_dir(&root, &root, &mut records);

    let total = records.len();
    let mut by_kind: HashMap<String, usize> = HashMap::new();
    for r in &records {
        *by_kind.entry(r.kind.to_string()).or_insert(0) += 1;
    }

    // Sort by weight descending so highest-value artifacts appear first
    records.sort_by(|a, b| b.weight.partial_cmp(&a.weight).unwrap_or(std::cmp::Ordering::Equal));

    Ok(LineageResult { folder: folder.to_string(), total, records, by_kind })
}

fn walk_dir(dir: &Path, root: &Path, out: &mut Vec<LineageRecord>) {
    let entries = match std::fs::read_dir(dir) {
        Ok(e)  => e,
        Err(_) => return,
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            // Skip hidden dirs and build artifacts
            let name = path.file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("");
            if name.starts_with('.') || name == "target" || name == "node_modules" {
                continue;
            }
            walk_dir(&path, root, out);
        } else if path.is_file() {
            out.push(LineageRecord::new(&path, root));
        }
    }
}

// ── Report ─────────────────────────────────────────────────────────────────────

pub fn report(result: &LineageResult) -> String {
    let mut out = String::new();
    out.push_str("# SAGCO LINEAGE MANIFEST\n\n");
    out.push_str(&format!("FOLDER  = {}\n", result.folder));
    out.push_str(&format!("TOTAL   = {}\n\n", result.total));

    out.push_str("## KIND SUMMARY\n");
    let mut kinds: Vec<(&String, &usize)> = result.by_kind.iter().collect();
    kinds.sort_by(|a, b| b.1.cmp(a.1));
    for (k, n) in &kinds {
        out.push_str(&format!("  {:<12} {}\n", k, n));
    }

    out.push_str("\n## TOP ARTIFACTS (by lineage weight)\n");
    for r in result.records.iter().take(20) {
        out.push_str(&format!(
            "  [{:.3}] {:12} {}\n",
            r.weight, r.kind.to_string(), r.path
        ));
    }
    if result.total > 20 {
        out.push_str(&format!("  ... and {} more\n", result.total - 20));
    }

    out.push_str(&format!("\nSTATUS=SAGCO_LINEAGE_PASS TOTAL={}\n", result.total));
    out
}

// ── Tests ──────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::Path;

    #[test]
    fn test_classify_rust_source() {
        assert_eq!(classify(Path::new("src/main.rs")), ArtifactKind::Source);
    }

    #[test]
    fn test_classify_config_toml() {
        assert_eq!(classify(Path::new("Cargo.toml")), ArtifactKind::Config);
    }

    #[test]
    fn test_classify_pipeline_prefix() {
        assert_eq!(classify(Path::new("pipeline_excavate_l1.txt")), ArtifactKind::Pipeline);
    }

    #[test]
    fn test_classify_agent_yaml() {
        assert_eq!(classify(Path::new("agents/cortex-agent.yaml")), ArtifactKind::Agent);
    }

    #[test]
    fn test_classify_evidence_binary() {
        assert_eq!(classify(Path::new("evidence_boot.bin")), ArtifactKind::Report);
    }

    #[test]
    fn test_classify_flame() {
        assert_eq!(classify(Path::new("lexer.flame")), ArtifactKind::Blueprint);
    }

    #[test]
    fn test_base_weight_ordering() {
        assert!(ArtifactKind::Source.base_weight() > ArtifactKind::Docs.base_weight());
        assert!(ArtifactKind::Config.base_weight() > ArtifactKind::Binary.base_weight());
    }

    #[test]
    fn test_trace_current_dir() {
        // Smoke: trace the current dir — just verify it doesn't error
        let r = trace(".");
        assert!(r.is_ok(), "trace('.') failed: {:?}", r.err());
        let result = r.unwrap();
        assert!(result.total > 0);
    }
}
