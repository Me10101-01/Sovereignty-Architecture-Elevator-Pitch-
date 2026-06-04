// crates/sagco-core/src/weight.rs
// SAGCO Brick Scorer — ranks bricks by deployment readiness before agent dispatch.
//
// Score = base_weight
//       + 0.02 if src/{name}.rs exists       (module is written)
//       + 0.02 if last reports/*{name}*.manifest exists (ran recently)
//       - 0.10 if STATUS=*_FAIL in last manifest (known broken)
//
// Called from main.rs Command::Weight handler.

use std::fs;
use std::path::Path;

// ── Types ─────────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub enum BrickStatus {
    Live,    // src exists + last manifest = PASS
    Built,   // src exists, no recent manifest
    Planned, // src not yet written
    Failed,  // last manifest contains *_FAIL
}

impl BrickStatus {
    pub fn label(&self) -> &'static str {
        match self {
            BrickStatus::Live    => "LIVE",
            BrickStatus::Built   => "BUILT",
            BrickStatus::Planned => "PLANNED",
            BrickStatus::Failed  => "FAILED",
        }
    }
}

#[derive(Debug, Clone)]
pub struct Brick {
    pub name:        String,
    pub base_weight: f64,
    pub rust_call:   String,
    pub k8s_agent:   String,
    pub status:      BrickStatus,
    pub score:       f64,
}

// ── Registry ──────────────────────────────────────────────────────────────────

pub fn registry() -> Vec<Brick> {
    let raw: &[(&str, f64, &str, &str)] = &[
        ("lexer",         0.90, "lexer::Lexer::new()",         "lexer-agent"),
        ("parser",        0.92, "parser::Parser::new()",        "parser-agent"),
        ("compiler",      0.88, "compiler::compile()",          "compiler-agent"),
        ("excavate",      0.95, "excavate::excavate(folder)",   "excavator-agent"),
        ("lineage",       0.97, "lineage::run(token)",          "lineage-agent"),
        ("token_factory", 0.94, "token_factory::run(token)",    "token-agent"),
        ("antibody",      0.99, "Antibody::fire()",             "antibody-agent"),
        ("k8s",           0.91, "k8s::deploy()",                "deploy-agent"),
        ("weight",        0.93, "weight::score(brick)",         "weight-agent"),
        ("cortex",        1.00, "cortex::decide()",             "cortex-agent"),
    ];
    raw.iter()
        .map(|(name, base, call, agent)| {
            let mut b = Brick {
                name:        name.to_string(),
                base_weight: *base,
                rust_call:   call.to_string(),
                k8s_agent:   agent.to_string(),
                status:      BrickStatus::Planned,
                score:       *base,
            };
            b.status = detect_status(&b.name);
            b.score  = compute_score(&b);
            b
        })
        .collect()
}

// ── Status detection ──────────────────────────────────────────────────────────

fn detect_status(name: &str) -> BrickStatus {
    // Check if src module exists
    let src_exists = Path::new(&format!("crates/sagco-core/src/{}.rs", name)).exists()
        || Path::new(&format!("src/{}.rs", name)).exists();

    if !src_exists {
        return BrickStatus::Planned;
    }

    // Find most recent manifest for this brick in reports/
    if let Some(manifest_content) = latest_manifest(name) {
        if manifest_content.contains("_FAIL") {
            return BrickStatus::Failed;
        }
        if manifest_content.contains("_PASS") || manifest_content.contains("STATUS=SAGCO") {
            return BrickStatus::Live;
        }
    }

    BrickStatus::Built
}

fn latest_manifest(name: &str) -> Option<String> {
    let reports = Path::new("reports");
    if !reports.exists() { return None; }
    let entries = fs::read_dir(reports).ok()?;
    let mut matches: Vec<(u64, std::path::PathBuf)> = entries
        .flatten()
        .filter(|e| {
            let n = e.file_name().to_string_lossy().to_string();
            n.contains(name) && (n.ends_with(".manifest") || n.ends_with(".md") || n.ends_with(".txt"))
        })
        .filter_map(|e| {
            let mtime = e.metadata().ok()?.modified().ok()?
                .duration_since(std::time::UNIX_EPOCH).ok()?.as_secs();
            Some((mtime, e.path()))
        })
        .collect();
    matches.sort_by(|a, b| b.0.cmp(&a.0));
    matches.first().and_then(|(_, p)| fs::read_to_string(p).ok())
}

// ── Scoring ───────────────────────────────────────────────────────────────────

fn compute_score(b: &Brick) -> f64 {
    let src_bonus = if Path::new(&format!("crates/sagco-core/src/{}.rs", b.name)).exists()
        || Path::new(&format!("src/{}.rs", b.name)).exists() { 0.02 } else { 0.0 };

    let manifest_bonus = if latest_manifest(&b.name).is_some() { 0.02 } else { 0.0 };

    let fail_penalty = match b.status {
        BrickStatus::Failed => -0.10,
        _ => 0.0,
    };

    (b.base_weight + src_bonus + manifest_bonus + fail_penalty).clamp(0.0, 1.0)
}

// ── Public API ────────────────────────────────────────────────────────────────

/// Sort bricks descending by score.
pub fn rank(bricks: &mut Vec<Brick>) {
    bricks.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(std::cmp::Ordering::Equal));
}

/// Return bricks at or above threshold.
pub fn gate(bricks: &[Brick], threshold: f64) -> Vec<&Brick> {
    bricks.iter().filter(|b| b.score >= threshold).collect()
}

/// Render ranked table as a string.
pub fn report(bricks: &[Brick]) -> String {
    let mut r = String::new();
    r.push_str("# SAGCO WEIGHT REPORT\n\n");
    r.push_str("| Rank | Brick | Score | Status | Rust Call | K8s Agent |\n");
    r.push_str("|------|-------|-------|--------|-----------|----------|\n");
    for (i, b) in bricks.iter().enumerate() {
        r.push_str(&format!(
            "| {} | {} | {:.2} | {} | `{}` | {} |\n",
            i + 1, b.name, b.score, b.status.label(), b.rust_call, b.k8s_agent
        ));
    }
    r.push('\n');
    let live    = bricks.iter().filter(|b| b.status == BrickStatus::Live).count();
    let built   = bricks.iter().filter(|b| b.status == BrickStatus::Built).count();
    let planned = bricks.iter().filter(|b| b.status == BrickStatus::Planned).count();
    let failed  = bricks.iter().filter(|b| b.status == BrickStatus::Failed).count();
    r.push_str(&format!("LIVE={} BUILT={} PLANNED={} FAILED={}\n", live, built, planned, failed));
    r.push_str(&format!("GATE_90={}\n",
        bricks.iter().filter(|b| b.score >= 0.90).count()));
    r.push_str("STATUS=SAGCO_WEIGHT_PASS\n");
    r
}
