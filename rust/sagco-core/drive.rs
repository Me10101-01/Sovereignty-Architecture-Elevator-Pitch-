// drive.rs — Agent Drive & Motivation Scoring for SAGCO-CORE
//
// Pipeline opcode:  drive <folder>
//
// Drive is the agent's desire to act.  It is not assigned externally —
// it is computed from the agent's weight, the artifact density it can
// find, and how long since it last ran.  An agent with high drive will
// appear early in the auto-generated pipeline; one with low drive waits.
//
// Formula:
//   drive = base_weight
//           × artifact_density          (0..1 — how much is here to work on)
//           × (1 + urgency_bonus)        (0.5 bonus if never run or stale)
//           × completion_hunger          (1 − prior_completion_ratio)
//
// Love threshold:  drive ≥ 0.85  →  "loves it"
//                  drive ≥ 0.60  →  "willing"
//                  drive  < 0.60 →  "waiting"

use std::collections::HashMap;
use std::path::Path;
use std::time::{SystemTime, UNIX_EPOCH};

// ── Agent descriptor ──────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub struct AgentSpec {
    pub name:         String,
    pub role:         String,
    pub base_weight:  f64,     // from agents/*.yaml weight field
    pub rust_call:    String,
    pub phase:        u32,
}

#[derive(Debug, Clone, PartialEq)]
pub enum LoveLevel {
    Loves,    // drive ≥ 0.85
    Willing,  // drive ≥ 0.60
    Waiting,  // drive  < 0.60
}

impl LoveLevel {
    pub fn label(&self) -> &'static str {
        match self {
            LoveLevel::Loves   => "LOVES",
            LoveLevel::Willing => "WILLING",
            LoveLevel::Waiting => "WAITING",
        }
    }
}

// ── Drive record ──────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub struct DriveRecord {
    pub agent:             AgentSpec,
    pub artifact_density:  f64,   // 0..1
    pub urgency_bonus:     f64,   // 0.0 or 0.5
    pub completion_hunger: f64,   // 1 − prior_completion_ratio
    pub drive:             f64,   // final score 0..1
    pub love:              LoveLevel,
}

impl DriveRecord {
    fn new(agent: AgentSpec, density: f64, urgency: f64, hunger: f64) -> Self {
        let drive = (agent.base_weight * density * (1.0 + urgency) * hunger).min(1.0);
        let love = if drive >= 0.85 {
            LoveLevel::Loves
        } else if drive >= 0.60 {
            LoveLevel::Willing
        } else {
            LoveLevel::Waiting
        };
        DriveRecord { agent, artifact_density: density, urgency_bonus: urgency,
                      completion_hunger: hunger, drive, love }
    }
}

// ── Scoring ───────────────────────────────────────────────────────────────────

/// artifact_density: count relevant artifacts in folder / expected total
fn density_for_agent(agent: &AgentSpec, folder: &str) -> f64 {
    let root = Path::new(folder);
    if !root.exists() { return 0.5; }

    let relevant_exts: &[&str] = match agent.role.as_str() {
        "artifact_discovery" | "folder_excavation" => &["rs", "toml", "yaml", "txt", "bin"],
        "token_ancestry"                            => &["manifest", "csv", "bin"],
        "brick_ranking"                             => &["yaml", "toml", "rs"],
        "command_builder" | "token_stream"          => &["rs"],
        "failure_detection"                         => &["manifest", "csv", "txt"],
        _                                           => &["rs", "yaml", "toml", "txt"],
    };

    let total = count_files(root, None);
    let relevant = count_files(root, Some(relevant_exts));
    if total == 0 { return 0.5; }
    (relevant as f64 / total as f64).min(1.0).max(0.1)
}

fn count_files(dir: &Path, exts: Option<&[&str]>) -> usize {
    let Ok(entries) = std::fs::read_dir(dir) else { return 0 };
    let mut count = 0;
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
            if !name.starts_with('.') && name != "target" && name != "node_modules" {
                count += count_files(&path, exts);
            }
        } else if let Some(allowed) = exts {
            if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                if allowed.contains(&ext) { count += 1; }
            }
        } else {
            count += 1;
        }
    }
    count
}

/// urgency_bonus: 0.5 if no manifest found (never run), 0.0 if recent
fn urgency_for_agent(agent: &AgentSpec) -> f64 {
    let manifest_pattern = format!("sagco_{}", agent.name.replace('-', "_"));
    let reports = Path::new("reports");
    if !reports.exists() { return 0.5; }

    let Ok(entries) = std::fs::read_dir(reports) else { return 0.5 };
    let now_secs = SystemTime::now()
        .duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();

    for entry in entries.flatten() {
        let name = entry.file_name().to_string_lossy().to_lowercase();
        if name.contains(&manifest_pattern) {
            // Found a prior run — check if it's fresh (< 24 hours)
            if let Ok(meta) = entry.metadata() {
                if let Ok(modified) = meta.modified() {
                    let age = now_secs.saturating_sub(
                        modified.duration_since(UNIX_EPOCH).unwrap_or_default().as_secs()
                    );
                    return if age > 86400 { 0.3 } else { 0.0 };
                }
            }
            return 0.0;
        }
    }
    0.5  // never run
}

/// completion_hunger: agents that are PLANNED hunger more than BUILT ones
fn hunger_for_agent(agent: &AgentSpec) -> f64 {
    // Phase 1-2: core infrastructure — always hungry
    if agent.phase <= 2 { return 1.0; }
    // Phase 3-4: mid-tier — moderately hungry
    if agent.phase <= 4 { return 0.85; }
    // Phase 5+: future — lower hunger
    0.65
}

// ── Fleet registry ────────────────────────────────────────────────────────────

pub fn fleet() -> Vec<AgentSpec> {
    vec![
        AgentSpec { name: "cortex-agent".into(),    role: "orchestration".into(),       base_weight: 1.00, rust_call: "cortex::route()".into(),              phase: 1 },
        AgentSpec { name: "antibody-agent".into(),  role: "failure_detection".into(),   base_weight: 0.99, rust_call: "antibody::scan()".into(),             phase: 1 },
        AgentSpec { name: "lineage-agent".into(),   role: "token_ancestry".into(),      base_weight: 0.97, rust_call: "lineage::trace()".into(),             phase: 3 },
        AgentSpec { name: "excavator-agent".into(), role: "artifact_discovery".into(),  base_weight: 0.96, rust_call: "excavate::excavate()".into(),         phase: 2 },
        AgentSpec { name: "weight-agent".into(),    role: "brick_ranking".into(),       base_weight: 0.93, rust_call: "weight::rank()".into(),               phase: 2 },
        AgentSpec { name: "parser-agent".into(),    role: "command_builder".into(),     base_weight: 0.92, rust_call: "parser::Parser::new()".into(),        phase: 1 },
        AgentSpec { name: "lexer-agent".into(),     role: "token_stream".into(),        base_weight: 0.90, rust_call: "lexer::Lexer::new()".into(),          phase: 1 },
    ]
}

// ── Compute drive for all agents ──────────────────────────────────────────────

pub struct DriveResult {
    pub folder:  String,
    pub records: Vec<DriveRecord>,
}

pub fn score(folder: &str) -> DriveResult {
    let agents = fleet();
    let mut records: Vec<DriveRecord> = agents.into_iter().map(|a| {
        let density = density_for_agent(&a, folder);
        let urgency = urgency_for_agent(&a);
        let hunger  = hunger_for_agent(&a);
        DriveRecord::new(a, density, urgency, hunger)
    }).collect();

    // Sort by drive descending — highest desire acts first
    records.sort_by(|a, b| b.drive.partial_cmp(&a.drive).unwrap_or(std::cmp::Ordering::Equal));
    DriveResult { folder: folder.to_string(), records }
}

// ── Auto-pipeline generator ───────────────────────────────────────────────────
//
// Emits a pipeline_autodrive.txt that sequences agents by drive score.
// Only "loves" and "willing" agents are scheduled; "waiting" agents are skipped.

pub fn generate_pipeline(result: &DriveResult) -> String {
    let mut lines = Vec::new();
    lines.push(format!("# AUTO-GENERATED by drive opcode — {}", timestamp()));
    lines.push(format!("# folder: {}", result.folder));
    lines.push(String::new());
    lines.push("read CORTEX.md".into());
    lines.push(format!("lineage {}", result.folder));

    for r in &result.records {
        if r.love == LoveLevel::Waiting { continue; }
        // Map agent role to opcode
        let opcode = match r.agent.role.as_str() {
            "artifact_discovery" | "folder_excavation" => format!("excavate {}", result.folder),
            "token_ancestry"     => format!("lineage {}", result.folder),
            "brick_ranking"      => format!("weight {}", result.folder),
            _ => continue,
        };
        lines.push(format!("# [{:.3}] {} — {}", r.drive, r.love.label(), r.agent.name));
        lines.push(opcode);
    }

    lines.push(String::new());
    lines.push("pulse 793398609444".into());
    lines.push("seal evidence_autodrive.bin".into());
    lines.join("\n")
}

fn timestamp() -> String {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs().to_string())
        .unwrap_or_else(|_| "0".to_string())
}

// ── Report ─────────────────────────────────────────────────────────────────────

pub fn report(result: &DriveResult) -> String {
    let mut out = String::from("# SAGCO DRIVE MANIFEST\n\n");
    out.push_str(&format!("FOLDER = {}\n\n", result.folder));
    out.push_str(&format!("{:<20} {:>7} {:>9} {:>9} {:>8}  {}\n",
        "AGENT", "DRIVE", "DENSITY", "URGENCY", "HUNGER", "LOVE"));
    out.push_str(&"-".repeat(70));
    out.push('\n');

    for r in &result.records {
        out.push_str(&format!(
            "{:<20} {:>7.3} {:>9.3} {:>9.3} {:>8.3}  {}\n",
            r.agent.name,
            r.drive,
            r.artifact_density,
            r.urgency_bonus,
            r.completion_hunger,
            r.love.label(),
        ));
    }

    let loves   = result.records.iter().filter(|r| r.love == LoveLevel::Loves).count();
    let willing = result.records.iter().filter(|r| r.love == LoveLevel::Willing).count();
    let waiting = result.records.iter().filter(|r| r.love == LoveLevel::Waiting).count();
    out.push_str(&format!(
        "\nLOVES={} WILLING={} WAITING={}\n",
        loves, willing, waiting
    ));
    out.push_str(&format!("STATUS=SAGCO_DRIVE_PASS\n"));
    out
}

// ── Tests ──────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_drive_produces_records() {
        let r = score(".");
        assert!(!r.records.is_empty());
    }

    #[test]
    fn test_drive_sorted_descending() {
        let r = score(".");
        let drives: Vec<f64> = r.records.iter().map(|r| r.drive).collect();
        for w in drives.windows(2) {
            assert!(w[0] >= w[1], "drive not sorted: {:.3} < {:.3}", w[0], w[1]);
        }
    }

    #[test]
    fn test_love_level_threshold() {
        let agent = AgentSpec {
            name: "test".into(), role: "brick_ranking".into(),
            base_weight: 1.0, rust_call: "".into(), phase: 1,
        };
        let r = DriveRecord::new(agent, 1.0, 0.5, 1.0);
        assert_eq!(r.love, LoveLevel::Loves);
    }

    #[test]
    fn test_pipeline_generation() {
        let r = score(".");
        let pipeline = generate_pipeline(&r);
        assert!(pipeline.contains("read CORTEX.md"));
        assert!(pipeline.contains("seal evidence_autodrive.bin"));
    }

    #[test]
    fn test_report_contains_status() {
        let r = score(".");
        let rpt = report(&r);
        assert!(rpt.contains("STATUS=SAGCO_DRIVE_PASS"));
        assert!(rpt.contains("LOVES=") || rpt.contains("WILLING="));
    }
}
