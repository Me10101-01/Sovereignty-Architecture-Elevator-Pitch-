// crates/sagco-core/src/lexicon.rs
// SAGCO Lexicon — the unified artifact record.
//
// Merges sagco-wing output (TOKEN + RUST_CALL + BRICK_ID) with
// lineage output (ANCESTOR + KIND + WEIGHT) into one canonical entry
// per artifact.
//
// Pipeline opcode: lexicon <folder>
//
// Output per entry:
//   SAGCO_ID    — "SAGCO-0010"
//   TOKEN       — "sagco_lang"
//   TYPE        — SOURCE | CONFIG | PIPELINE | AGENT | REPORT | DOCS | BINARY
//   ANCESTOR    — ["bin", "sagco-lang"]        (folder path segments)
//   DESCENDANTS — ["program.sagco", "program.out"]  (derived from token name)
//   RUST_CALL   — "sagco_lang_brick()"
//   PATH        — "./bin/sagco-lang"
//   WEIGHT      — 0.95
//   STATUS      — LIVE | BUILT | PLANNED | COMPUTED

use std::collections::HashMap;
use std::fmt;
use std::path::{Path, PathBuf};
use std::fs;

// ── Artifact classification (mirrors lineage.rs) ──────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub enum ArtifactKind {
    Source, Config, Pipeline, Agent, Report, Docs, Binary, Unknown,
}

impl fmt::Display for ArtifactKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", match self {
            ArtifactKind::Source   => "SOURCE",
            ArtifactKind::Config   => "CONFIG",
            ArtifactKind::Pipeline => "PIPELINE",
            ArtifactKind::Agent    => "AGENT",
            ArtifactKind::Report   => "REPORT",
            ArtifactKind::Docs     => "DOCS",
            ArtifactKind::Binary   => "BINARY",
            ArtifactKind::Unknown  => "UNKNOWN",
        })
    }
}

impl ArtifactKind {
    pub fn base_weight(&self) -> f64 {
        match self {
            ArtifactKind::Source   => 0.95,
            ArtifactKind::Config   => 0.90,
            ArtifactKind::Pipeline => 0.88,
            ArtifactKind::Agent    => 0.85,
            ArtifactKind::Report   => 0.80,
            ArtifactKind::Docs     => 0.60,
            ArtifactKind::Binary   => 0.40,
            ArtifactKind::Unknown  => 0.10,
        }
    }
}

fn classify(path: &Path) -> ArtifactKind {
    let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("").to_lowercase();
    let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("").to_lowercase();
    let path_s = path.to_string_lossy().to_lowercase();

    if path_s.contains("/agents/") && ext == "yaml"          { return ArtifactKind::Agent; }
    if (path_s.contains("/pipeline") || name.starts_with("pipeline_")) && ext == "txt" {
        return ArtifactKind::Pipeline;
    }
    match ext.as_str() {
        "rs" | "py" | "js" | "ts" | "sh" | "cpp" | "c" | "h" => ArtifactKind::Source,
        "toml" | "yaml" | "yml" | "json" | "env"              => ArtifactKind::Config,
        "md" | "txt"                                           => ArtifactKind::Docs,
        "bin" | "elf" | "so"                                   => ArtifactKind::Binary,
        "csv" | "manifest"                                     => ArtifactKind::Report,
        _ => {
            if name.starts_with("evidence") || name.contains("report") {
                ArtifactKind::Report
            } else {
                ArtifactKind::Unknown
            }
        }
    }
}

// ── Token generation ──────────────────────────────────────────────────────────

fn tokenize(path: &Path) -> String {
    path.file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("unknown")
        .replace(['-', '.', ' '], "_")
        .to_lowercase()
}

fn rust_call(token: &str) -> String {
    format!("{}_brick()", token)
}

fn infer_descendants(token: &str, kind: &ArtifactKind) -> Vec<String> {
    match kind {
        ArtifactKind::Source => vec![
            format!("{}.o", token),
            format!("reports/sagco_{}.manifest", token),
        ],
        ArtifactKind::Pipeline => vec![
            format!("evidence_{}.bin", token),
            format!("reports/sagco_{}.manifest", token),
        ],
        ArtifactKind::Config => vec![
            format!("reports/sagco_{}.manifest", token),
        ],
        _ => vec![],
    }
}

// ── LexiconEntry ──────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub struct LexiconEntry {
    pub sagco_id:    String,
    pub token:       String,
    pub kind:        ArtifactKind,
    pub ancestor:    Vec<String>,
    pub descendants: Vec<String>,
    pub rust_call:   String,
    pub path:        String,
    pub weight:      f64,
    pub status:      String,
}

impl LexiconEntry {
    fn new(sagco_id: usize, path: &Path, root: &Path) -> Self {
        let kind  = classify(path);
        let token = tokenize(path);
        let rc    = rust_call(&token);
        let desc  = infer_descendants(&token, &kind);
        let weight = kind.base_weight();

        let rel = path.strip_prefix(root).unwrap_or(path);
        let ancestor: Vec<String> = rel.parent()
            .map(|p| p.components()
                .map(|c| c.as_os_str().to_string_lossy().to_string())
                .filter(|s| !s.is_empty())
                .collect())
            .unwrap_or_default();

        // Status: does the file exist and is it non-empty?
        let status = if path.exists() {
            if path.metadata().map(|m| m.len()).unwrap_or(0) > 0 {
                "COMPUTED".to_string()
            } else {
                "EMPTY".to_string()
            }
        } else {
            "PLANNED".to_string()
        };

        LexiconEntry {
            sagco_id: format!("SAGCO-{:04}", sagco_id),
            token,
            kind,
            ancestor,
            descendants: desc,
            rust_call: rc,
            path: path.to_string_lossy().to_string(),
            weight,
            status,
        }
    }

    pub fn format_record(&self) -> String {
        let ancestors = if self.ancestor.is_empty() {
            "root".to_string()
        } else {
            self.ancestor.join("/")
        };
        let desc = if self.descendants.is_empty() {
            "none".to_string()
        } else {
            self.descendants.join(", ")
        };
        format!(
            "{id}\n  TOKEN:       {tok}\n  TYPE:        {kind}\n  ANCESTOR:    {anc}\n  DESCENDANTS: {desc}\n  RUST_CALL:   {call}\n  PATH:        {path}\n  WEIGHT:      {w:.3}\n  STATUS:      {st}\n",
            id   = self.sagco_id,
            tok  = self.token,
            kind = self.kind,
            anc  = ancestors,
            desc = desc,
            call = self.rust_call,
            path = self.path,
            w    = self.weight,
            st   = self.status,
        )
    }
}

// ── LexiconResult ─────────────────────────────────────────────────────────────

pub struct LexiconResult {
    pub folder:   String,
    pub total:    usize,
    pub entries:  Vec<LexiconEntry>,
    pub by_kind:  HashMap<String, usize>,
    pub manifest: String,
}

// ── Walker ────────────────────────────────────────────────────────────────────

fn walk(dir: &Path, root: &Path, counter: &mut usize, out: &mut Vec<LexiconEntry>) {
    let entries = match fs::read_dir(dir) { Ok(e) => e, Err(_) => return };
    let mut paths: Vec<PathBuf> = entries.flatten().map(|e| e.path()).collect();
    paths.sort();  // deterministic SAGCO IDs

    for path in paths {
        let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        if name.starts_with('.') || name == "target" || name == "node_modules" { continue; }

        if path.is_dir() {
            walk(&path, root, counter, out);
        } else if path.is_file() {
            *counter += 1;
            out.push(LexiconEntry::new(*counter, &path, root));
        }
    }
}

// ── Main entry point ──────────────────────────────────────────────────────────

pub fn build(folder: &str) -> Result<LexiconResult, String> {
    let root = PathBuf::from(folder);
    if !root.exists() {
        return Err(format!("lexicon: not found: {}", folder));
    }

    let mut entries = Vec::new();
    let mut counter = 0usize;
    walk(&root, &root, &mut counter, &mut entries);

    let total = entries.len();
    let mut by_kind: HashMap<String, usize> = HashMap::new();
    for e in &entries { *by_kind.entry(e.kind.to_string()).or_insert(0) += 1; }

    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    // Full lexicon text
    let records: String = entries.iter().map(|e| e.format_record()).collect::<Vec<_>>().join("\n");

    // Rust brick registry (wing-style)
    let rust_calls: String = entries.iter().map(|e| {
        format!("fn {}() {{ println!(\"{} {}\"); }}\n",
            e.token.replace(['-', '.'], "_"),
            e.sagco_id,
            e.path)
    }).collect();

    let manifest = format!(
        "# SAGCO LEXICON\nFOLDER={folder}\nSTAMP={stamp}\nTOTAL={total}\n\n\
         ## KIND SUMMARY\n{kinds}\n\
         ## RECORDS\n{records}\n\
         ## RUST BRICK REGISTRY\n```rust\n{rust_calls}```\n\
         STATUS=SAGCO_LEXICON_SEALED\n",
        folder     = folder,
        stamp      = stamp,
        total      = total,
        kinds      = {
            let mut k: Vec<_> = by_kind.iter().collect();
            k.sort_by(|a, b| b.1.cmp(a.1));
            k.iter().map(|(k, n)| format!("  {:<12} {}\n", k, n)).collect::<String>()
        },
        records    = records,
        rust_calls = rust_calls,
    );

    Ok(LexiconResult { folder: folder.to_string(), total, entries, by_kind, manifest })
}

// ── Report (one-line summary for pipeline output) ─────────────────────────────

pub fn report(result: &Result<LexiconResult, String>) -> String {
    match result {
        Err(e) => format!("[LEXICON_ERROR]: {}\n", e),
        Ok(r)  => format!(
            "[LEXICON]: {} TOTAL={} SOURCE={} CONFIG={} PIPELINE={} AGENT={}\n",
            r.folder,
            r.total,
            r.by_kind.get("SOURCE").unwrap_or(&0),
            r.by_kind.get("CONFIG").unwrap_or(&0),
            r.by_kind.get("PIPELINE").unwrap_or(&0),
            r.by_kind.get("AGENT").unwrap_or(&0),
        ),
    }
}
