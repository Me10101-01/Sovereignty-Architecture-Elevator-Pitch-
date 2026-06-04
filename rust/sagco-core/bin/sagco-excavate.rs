//! SAGCO Excavate — ARTIFACT → TOKEN → EDGE → LINEAGE
//!
//! Combines treasure + past + dna into a unified archaeology report.
//! Usage: sagco-excavate [path]   (default: $HOME)

use std::collections::{HashMap, HashSet};
use std::env;
use std::fs;
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

// ── Artifact ─────────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
struct Artifact {
    path: PathBuf,
    name: String,
    ext:  String,
    kind: ArtifactKind,
    dna:  String,
    size: u64,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
enum ArtifactKind {
    Report,
    Wave,
    Evidence,
    CaseStudy,
    Attribution,
    Archive,
    RaceLog,
    Config,
    Source,
    Other,
}

impl ArtifactKind {
    fn from_path(p: &Path) -> Self {
        let name = p.file_name().unwrap_or_default().to_string_lossy().to_lowercase();
        let ext  = p.extension().unwrap_or_default().to_string_lossy().to_lowercase();
        if name.contains("report") || name.ends_with(".md") { return ArtifactKind::Report; }
        if ext == "wav"            { return ArtifactKind::Wave; }
        if name.contains("evidence") || name.contains("proof") { return ArtifactKind::Evidence; }
        if name.contains("case_study") { return ArtifactKind::CaseStudy; }
        if name.contains("attribution") { return ArtifactKind::Attribution; }
        if ext == "gz" || ext == "tar" || name.ends_with(".tar.gz") { return ArtifactKind::Archive; }
        if name.contains("race_log") || name.contains("race") { return ArtifactKind::RaceLog; }
        if ext == "yaml" || ext == "yml" || ext == "json" || ext == "toml" { return ArtifactKind::Config; }
        if ext == "rs" || ext == "py" || ext == "sh" { return ArtifactKind::Source; }
        ArtifactKind::Other
    }

    fn label(&self) -> &'static str {
        match self {
            ArtifactKind::Report      => "REPORT",
            ArtifactKind::Wave        => "WAVE",
            ArtifactKind::Evidence    => "EVIDENCE",
            ArtifactKind::CaseStudy   => "CASE_STUDY",
            ArtifactKind::Attribution => "ATTRIBUTION",
            ArtifactKind::Archive     => "ARCHIVE",
            ArtifactKind::RaceLog     => "RACE_LOG",
            ArtifactKind::Config      => "CONFIG",
            ArtifactKind::Source      => "SOURCE",
            ArtifactKind::Other       => "OTHER",
        }
    }
}

// ── Fingerprint ───────────────────────────────────────────────────────────────

fn dna_fingerprint(input: &str) -> String {
    let mut h = DefaultHasher::new();
    input.hash(&mut h);
    format!("{:016x}", h.finish())
}

// ── Token extraction ──────────────────────────────────────────────────────────

fn tokens_from_name(name: &str) -> Vec<String> {
    name.split(|c: char| !c.is_alphanumeric())
        .filter(|t| t.len() >= 3)
        .map(|t| t.to_lowercase())
        .filter(|t| !matches!(t.as_str(),
            "the"|"and"|"for"|"with"|"from"|"into"|"this"|"that"|"are"
            |"was"|"has"|"have"|"its"|"not"|"but"|"can"|"all"|"more"
            |"sagco"|"txt"|"csv"|"json"|"yaml"|"toml"|"md"|"wav"|"tar"|"gz"
        ))
        .collect()
}

// ── Discovery ─────────────────────────────────────────────────────────────────

fn walk(dir: &Path, depth: usize, out: &mut Vec<Artifact>) {
    if depth == 0 { return; }
    let entries = match fs::read_dir(dir) {
        Ok(e) => e,
        Err(_) => return,
    };
    for entry in entries.flatten() {
        let path = entry.path();
        let name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
        // Skip noise
        if name.starts_with('.') && name != ".sagco_device" { continue; }
        if matches!(name.as_str(), "target"|"node_modules"|".git"|"__pycache__") { continue; }
        if path.is_dir() {
            walk(&path, depth - 1, out);
        } else {
            let ext = path.extension()
                .unwrap_or_default()
                .to_string_lossy()
                .to_string();
            // Only collect known SAGCO artifact types
            let keep = matches!(ext.as_str(),
                "md"|"csv"|"yaml"|"yml"|"json"|"toml"|"wav"|"sh"|"py"|"rs"|"txt"
            ) || name.contains(".tar.gz");
            if !keep { continue; }
            let size = fs::metadata(&path).map(|m| m.len()).unwrap_or(0);
            let dna  = dna_fingerprint(&path.to_string_lossy());
            let kind = ArtifactKind::from_path(&path);
            out.push(Artifact {
                path: path.clone(),
                name: name.clone(),
                ext,
                kind,
                dna,
                size,
            });
        }
    }
}

// ── Token map ─────────────────────────────────────────────────────────────────

fn build_token_map(artifacts: &[Artifact]) -> HashMap<String, Vec<usize>> {
    let mut map: HashMap<String, Vec<usize>> = HashMap::new();
    for (i, art) in artifacts.iter().enumerate() {
        for tok in tokens_from_name(&art.name) {
            map.entry(tok).or_default().push(i);
        }
    }
    // Keep only tokens that appear more than once (real edges)
    map.retain(|_, v| v.len() > 1);
    map
}

// ── Edge map ──────────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
struct Edge {
    from: usize,
    to:   usize,
    token: String,
}

fn build_edges(token_map: &HashMap<String, Vec<usize>>) -> Vec<Edge> {
    let mut edges: Vec<Edge> = Vec::new();
    let mut seen: HashSet<(usize, usize)> = HashSet::new();
    for (tok, idxs) in token_map {
        for i in 0..idxs.len() {
            for j in (i+1)..idxs.len() {
                let (a, b) = (idxs[i].min(idxs[j]), idxs[i].max(idxs[j]));
                if seen.insert((a, b)) {
                    edges.push(Edge { from: a, to: b, token: tok.clone() });
                }
            }
        }
    }
    edges
}

// ── Lineage ───────────────────────────────────────────────────────────────────

// Build a lineage chain by grouping artifacts by kind and ordering by creation
// Heuristic: archive → evidence → report → wave is the typical SAGCO flow
fn trace_lineage(artifacts: &[Artifact]) -> Vec<(ArtifactKind, Vec<usize>)> {
    let order = [
        ArtifactKind::RaceLog,
        ArtifactKind::Attribution,
        ArtifactKind::Evidence,
        ArtifactKind::CaseStudy,
        ArtifactKind::Archive,
        ArtifactKind::Report,
        ArtifactKind::Wave,
        ArtifactKind::Config,
        ArtifactKind::Source,
        ArtifactKind::Other,
    ];
    let mut lineage: Vec<(ArtifactKind, Vec<usize>)> = Vec::new();
    for kind in &order {
        let idxs: Vec<usize> = artifacts.iter().enumerate()
            .filter(|(_, a)| &a.kind == kind)
            .map(|(i, _)| i)
            .collect();
        if !idxs.is_empty() {
            lineage.push((kind.clone(), idxs));
        }
    }
    lineage
}

// ── Report ────────────────────────────────────────────────────────────────────

fn build_report(
    root: &str,
    artifacts: &[Artifact],
    token_map: &HashMap<String, Vec<usize>>,
    edges: &[Edge],
    lineage: &[(ArtifactKind, Vec<usize>)],
) -> String {
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    let node = fs::read_to_string(
        format!("{}/.sagco_device", std::env::var("HOME").unwrap_or_default())
    ).unwrap_or_else(|_| "unknown".into()).trim().to_string();

    let mut r = String::new();
    r.push_str("# SAGCO EXCAVATION REPORT\n");
    r.push_str(&format!("STAMP={}\n", stamp));
    r.push_str(&format!("NODE={}\n", node));
    r.push_str(&format!("ROOT={}\n", root));
    r.push_str(&format!("TREASURES={}\n", artifacts.len()));
    r.push_str(&format!("TOKENS={}\n", token_map.len()));
    r.push_str(&format!("EDGES={}\n\n", edges.len()));

    // Phase 1: Artifacts
    r.push_str("## PHASE 1 — ARTIFACTS\n\n");
    r.push_str("| # | Kind | DNA | Name | Size |\n");
    r.push_str("|---|------|-----|------|------|\n");
    for (i, a) in artifacts.iter().enumerate() {
        r.push_str(&format!("| {} | {} | `{}` | {} | {} |\n",
            i + 1,
            a.kind.label(),
            &a.dna[..8],
            a.name,
            a.size,
        ));
    }

    // Phase 2: Tokens (top 30 by frequency)
    r.push_str("\n## PHASE 2 — TOKENS\n\n");
    r.push_str("| Token | Frequency | Artifact Indices |\n");
    r.push_str("|-------|-----------|------------------|\n");
    let mut tok_vec: Vec<(&String, &Vec<usize>)> = token_map.iter().collect();
    tok_vec.sort_by(|a, b| b.1.len().cmp(&a.1.len()));
    for (tok, idxs) in tok_vec.iter().take(30) {
        let idx_str = idxs.iter().map(|i| (i+1).to_string()).collect::<Vec<_>>().join(",");
        r.push_str(&format!("| {} | {} | {} |\n", tok, idxs.len(), idx_str));
    }

    // Phase 3: Edges (top 40)
    r.push_str("\n## PHASE 3 — EDGES\n\n");
    r.push_str("| From | To | Via Token |\n");
    r.push_str("|------|----|-----------|\n");
    for e in edges.iter().take(40) {
        let from_name = artifacts.get(e.from).map(|a| a.name.as_str()).unwrap_or("?");
        let to_name   = artifacts.get(e.to).map(|a| a.name.as_str()).unwrap_or("?");
        r.push_str(&format!("| {} | {} | `{}` |\n",
            from_name, to_name, e.token));
    }

    // Phase 4: Lineage
    r.push_str("\n## PHASE 4 — LINEAGE\n\n");
    r.push_str("```\n");
    let mut prev: Option<&ArtifactKind> = None;
    for (kind, idxs) in lineage {
        if let Some(p) = prev {
            let _ = p; // suppress warning
            r.push_str("  ↓\n");
        }
        r.push_str(&format!("{} (n={})\n", kind.label(), idxs.len()));
        for idx in idxs.iter().take(5) {
            if let Some(a) = artifacts.get(*idx) {
                r.push_str(&format!("  · {}\n", a.name));
            }
        }
        if idxs.len() > 5 {
            r.push_str(&format!("  · ... +{} more\n", idxs.len() - 5));
        }
        prev = Some(kind);
    }
    r.push_str("```\n");

    r.push_str("\n---\n");
    r.push_str("STATUS=SAGCO_EXCAVATE_PASS\n");
    r
}

// ── Main ──────────────────────────────────────────────────────────────────────

fn main() {
    let root = env::args().nth(1)
        .or_else(|| env::var("HOME").ok())
        .unwrap_or_else(|| ".".to_string());

    let root_path = Path::new(&root);

    eprintln!("SAGCO EXCAVATE");
    eprintln!("ROOT={}", root);

    // Phase 1
    let mut artifacts: Vec<Artifact> = Vec::new();
    walk(root_path, 4, &mut artifacts);
    artifacts.sort_by(|a, b| a.kind.label().cmp(b.kind.label()).then(a.name.cmp(&b.name)));

    eprintln!("ARTIFACTS={}", artifacts.len());

    // Phase 2
    let token_map = build_token_map(&artifacts);
    eprintln!("TOKENS={}", token_map.len());

    // Phase 3
    let edges = build_edges(&token_map);
    eprintln!("EDGES={}", edges.len());

    // Phase 4
    let lineage = trace_lineage(&artifacts);

    // Report
    let report = build_report(&root, &artifacts, &token_map, &edges, &lineage);

    let fp = dna_fingerprint(&report);
    fs::create_dir_all("reports").unwrap_or(());
    let out_path = format!("reports/sagco_excavate_{}.md", fp);
    fs::write(&out_path, &report).unwrap_or(());

    println!("{}", report);
    println!("\nREPORT={}", out_path);
    println!("DNA={}", fp);
    println!("STATUS=SAGCO_EXCAVATE_PASS");
}
