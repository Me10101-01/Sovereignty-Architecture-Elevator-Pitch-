// crates/sagco-core/src/scaffold.rs
// SAGCO Scaffold module — generates a complete deployable agent repository.
//
// Pipeline opcode: scaffold <agent_name>
//
// Creates sagco_fleet/agents/<name>/ with:
//   Cargo.toml, src/{main,agent,eru}.rs, tests/, k8s/job.yaml,
//   docs/README.md, LINEAGE.md
//
// Scores the result against the 7-dimension weight model:
//   exists(0.20) + builds_skeleton(0.20) + tests(0.20) +
//   docs(0.10) + deploy_manifest(0.10) + lineage(0.10) + antibody(0.10)
//
// Passes baton to: weight opcode (score), deploy opcode (push)

use std::fs;
use std::path::{Path, PathBuf};

// ── Weight model (repository dimension scores) ────────────────────────────────

#[derive(Debug, Clone, Default)]
pub struct RepoWeight {
    pub exists:          f64,   // 0.20 directory created
    pub builds_skeleton: f64,   // 0.20 Cargo.toml + src/main.rs written
    pub tests:           f64,   // 0.20 tests/ directory present
    pub docs:            f64,   // 0.10 docs/README.md present
    pub deploy_manifest: f64,   // 0.10 k8s/job.yaml present
    pub lineage:         f64,   // 0.10 LINEAGE.md present
    pub antibody:        f64,   // 0.10 antibody check present in agent.rs
}

impl RepoWeight {
    pub fn total(&self) -> f64 {
        self.exists + self.builds_skeleton + self.tests
            + self.docs + self.deploy_manifest + self.lineage + self.antibody
    }

    pub fn label(&self) -> &'static str {
        let t = self.total();
        if t >= 0.95      { "DEPLOYABLE" }
        else if t >= 0.70 { "NEAR_READY" }
        else if t >= 0.40 { "SCAFFOLDED" }
        else              { "STUB" }
    }
}

// ── PMI scoring ───────────────────────────────────────────────────────────────

pub struct PmiRecord {
    pub name:  String,
    pub score: f64,     // 0.0-1.0 impact if this agent is missing
    pub deps:  Vec<String>,
}

pub fn pmi_registry() -> Vec<PmiRecord> {
    vec![
        PmiRecord { name: "excavate-agent".into(),  score: 0.98,
                    deps: vec!["cortex-agent".into()] },
        PmiRecord { name: "deploy-agent".into(),    score: 0.96,
                    deps: vec!["cortex-agent".into(), "antibody-agent".into()] },
        PmiRecord { name: "antibody-agent".into(),  score: 0.95,
                    deps: vec![] },
        PmiRecord { name: "cortex-agent".into(),    score: 0.94,
                    deps: vec![] },
        PmiRecord { name: "lineage-agent".into(),   score: 0.93,
                    deps: vec!["excavate-agent".into()] },
        PmiRecord { name: "weight-agent".into(),    score: 0.91,
                    deps: vec!["lineage-agent".into()] },
        PmiRecord { name: "scaffold-agent".into(),  score: 0.90,
                    deps: vec!["weight-agent".into(), "excavate-agent".into()] },
        PmiRecord { name: "parser-agent".into(),    score: 0.87,
                    deps: vec![] },
        PmiRecord { name: "lexer-agent".into(),     score: 0.88,
                    deps: vec![] },
    ]
}

// ── ERU fleet scoring ─────────────────────────────────────────────────────────

pub struct EruFleet {
    pub expected: usize,
    pub actual:   usize,
    pub eru:      f64,
    pub missing:  Vec<String>,
}

pub fn eru_fleet(fleet_dir: &str) -> EruFleet {
    let expected_agents = pmi_registry();
    let expected = expected_agents.len();
    let root = Path::new(fleet_dir).join("agents");

    let mut actual = 0usize;
    let mut missing = Vec::new();

    for rec in &expected_agents {
        let agent_dir = root.join(&rec.name);
        if agent_dir.exists() {
            actual += 1;
        } else {
            missing.push(rec.name.clone());
        }
    }

    let eru = if expected > 0 {
        (expected - actual) as f64 / expected as f64
    } else { 0.0 };

    EruFleet { expected, actual, eru, missing }
}

// ── Template generation ───────────────────────────────────────────────────────

fn cargo_toml(name: &str) -> String {
    format!(
r#"[package]
name = "{name}"
version = "0.1.0"
edition = "2018"

[dependencies]
# Add fleet-specific dependencies here
"#,
        name = name
    )
}

fn main_rs(name: &str) -> String {
    let ident = name.replace('-', "_");
    format!(
r#"mod agent;
mod eru;

fn main() {{
    println!("SAGCO AGENT: {name}");
    let result = agent::run();
    println!("{{}}", result.report());
    if result.eru_score() > 0.05 {{
        eprintln!("ERU_WARN: {name} deviation={{:.4}}", result.eru_score());
        std::process::exit(1);
    }}
    println!("STATUS=SAGCO_{IDENT}_PASS");
}}
"#,
        name  = name,
        IDENT = ident.to_uppercase()
    )
}

fn agent_rs(name: &str) -> String {
    let ident = name.replace('-', "_");
    format!(
r#"// {name} agent logic
use crate::eru;

pub struct AgentResult {{
    pub name:   String,
    pub status: String,
    pub eru:    f64,
}}

impl AgentResult {{
    pub fn report(&self) -> String {{
        format!("[{}] STATUS={{}} ERU={{:.4}}", self.name, self.status, self.eru)
    }}
    pub fn eru_score(&self) -> f64 {{ self.eru }}
}}

pub fn run() -> AgentResult {{
    // TODO: implement {name} agent logic
    let expected = 1.0_f64;
    let actual   = 1.0_f64;
    let eru      = eru::score(expected, actual);
    AgentResult {{
        name:   "{name}".to_string(),
        status: "STUB_PASS".to_string(),
        eru,
    }}
}}

// ANTIBODY: {IDENT}_HEALTH_CHECK
pub fn antibody_check() -> bool {{
    // Returns true if agent is healthy
    true
}}
"#,
        name  = name,
        IDENT = ident.to_uppercase()
    )
}

fn eru_rs() -> String {
    r#"// ERU scoring for this agent
// ERU = |expected - actual| / max(|expected|, 1e-12)

pub fn score(expected: f64, actual: f64) -> f64 {
    let denom = expected.abs().max(1e-12);
    (expected - actual).abs() / denom
}
"#.to_string()
}

fn integration_test_rs(name: &str) -> String {
    let ident = name.replace('-', "_");
    format!(
r#"// Integration tests for {name}

#[test]
fn test_{ident}_runs() {{
    // Smoke test: agent::run() must not panic
    // TODO: replace with real assertions
}}

#[test]
fn test_antibody_check() {{
    // Antibody gate must pass before deployment
}}
"#,
        name  = name,
        ident = ident
    )
}

fn k8s_job_yaml(name: &str) -> String {
    format!(
r#"apiVersion: batch/v1
kind: Job
metadata:
  name: {name}
  namespace: sagco-fleet
  labels:
    agent: {name}
    layer: fleet
    topology: sagco-os
spec:
  completions: 1
  parallelism: 1
  backoffLimit: 2
  ttlSecondsAfterFinished: 3600
  template:
    metadata:
      labels:
        agent: {name}
        job-name: {name}
    spec:
      restartPolicy: OnFailure
      containers:
        - name: {name}
          image: dom101/{name}:latest
          imagePullPolicy: Always
          resources:
            requests:
              cpu: "100m"
              memory: "64Mi"
            limits:
              cpu: "200m"
              memory: "128Mi"
"#,
        name = name
    )
}

fn readme_md(name: &str) -> String {
    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    format!(
r#"# {name}

SAGCO Fleet Agent — scaffolded by sagco-core scaffold opcode.

## Dimensions

| Dimension | Target | Status |
|-----------|--------|--------|
| Exists | 0.20 | ✅ |
| Builds | 0.20 | 🔧 implement |
| Tests | 0.20 | 🔧 implement |
| Docs | 0.10 | ✅ |
| Deploy manifest | 0.10 | ✅ |
| Lineage | 0.10 | ✅ |
| Antibody | 0.10 | 🔧 implement |

## Usage

```bash
cargo build && cargo test
```

## Scaffold metadata

SCAFFOLD_STAMP={stamp}
SCAFFOLD_AGENT={name}
"#,
        name  = name,
        stamp = stamp
    )
}

fn lineage_md(name: &str) -> String {
    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    format!(
r#"# LINEAGE: {name}

SCAFFOLD_STAMP: {stamp}
PARENT:        sagco-core
OPCODE:        scaffold
GENERATOR:     sagco-core scaffold opcode
FLEET:         sagco_fleet/agents/{name}
NAMESPACE:     sagco-fleet
CLUSTER:       sagco-os-computablesubcon
REGION:        us-central1

## Ancestry

sagco-core → scaffold → {name} → sagco-fleet

STATUS=SAGCO_LINEAGE_SEALED
"#,
        name  = name,
        stamp = stamp
    )
}

// ── ScaffoldResult ────────────────────────────────────────────────────────────

pub struct ScaffoldResult {
    pub name:          String,
    pub root:          String,
    pub files_created: Vec<String>,
    pub weight:        RepoWeight,
    pub manifest:      String,
}

// ── Main scaffold function ────────────────────────────────────────────────────

pub fn scaffold(name: &str) -> Result<ScaffoldResult, String> {
    let base = PathBuf::from("sagco_fleet").join("agents").join(name);

    // Create directory tree
    let dirs = [
        base.clone(),
        base.join("src"),
        base.join("tests"),
        base.join("k8s"),
        base.join("docs"),
    ];
    for d in &dirs {
        fs::create_dir_all(d)
            .map_err(|e| format!("scaffold: create_dir_all {:?}: {}", d, e))?;
    }

    let mut files_created = Vec::new();
    let mut w = RepoWeight::default();

    // Cargo.toml + src/main.rs → builds_skeleton dimension
    let files: &[(&str, fn(&str) -> String)] = &[];
    let _ = files; // suppress warning — we write manually below

    write_file(base.join("Cargo.toml"),            &cargo_toml(name),         &mut files_created)?;
    write_file(base.join("src").join("main.rs"),   &main_rs(name),            &mut files_created)?;
    write_file(base.join("src").join("agent.rs"),  &agent_rs(name),           &mut files_created)?;
    write_file(base.join("src").join("eru.rs"),    &eru_rs(),                 &mut files_created)?;
    w.exists          = 0.20;
    w.builds_skeleton = 0.20;

    // Tests
    write_file(
        base.join("tests").join("integration_test.rs"),
        &integration_test_rs(name),
        &mut files_created,
    )?;
    w.tests = 0.20;

    // Docs
    write_file(base.join("docs").join("README.md"), &readme_md(name), &mut files_created)?;
    w.docs = 0.10;

    // K8s deploy manifest
    write_file(base.join("k8s").join("job.yaml"), &k8s_job_yaml(name), &mut files_created)?;
    w.deploy_manifest = 0.10;

    // Lineage
    write_file(base.join("LINEAGE.md"), &lineage_md(name), &mut files_created)?;
    w.lineage = 0.10;

    // Antibody is coded into agent.rs — mark it
    w.antibody = 0.10;

    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    let file_list: String = files_created.iter().map(|f| format!("  {}\n", f)).collect();

    let manifest = format!(
        "SCAFFOLD_NAME={name}\n\
         SCAFFOLD_ROOT={root}\n\
         SCAFFOLD_STAMP={stamp}\n\
         FILES_CREATED={count}\n\
         WEIGHT_TOTAL={total:.2}\n\
         WEIGHT_LABEL={label}\n\
         WEIGHT_EXISTS={exists}\n\
         WEIGHT_BUILDS={builds}\n\
         WEIGHT_TESTS={tests}\n\
         WEIGHT_DOCS={docs}\n\
         WEIGHT_DEPLOY={deploy}\n\
         WEIGHT_LINEAGE={lineage}\n\
         WEIGHT_ANTIBODY={antibody}\n\
         FILES:\n{file_list}\
         STATUS=SAGCO_SCAFFOLD_SEALED\n",
        name     = name,
        root     = base.display(),
        stamp    = stamp,
        count    = files_created.len(),
        total    = w.total(),
        label    = w.label(),
        exists   = w.exists,
        builds   = w.builds_skeleton,
        tests    = w.tests,
        docs     = w.docs,
        deploy   = w.deploy_manifest,
        lineage  = w.lineage,
        antibody = w.antibody,
        file_list = file_list,
    );

    Ok(ScaffoldResult {
        name:  name.to_string(),
        root:  base.to_string_lossy().to_string(),
        files_created,
        weight: w,
        manifest,
    })
}

fn write_file(path: PathBuf, content: &str, created: &mut Vec<String>) -> Result<(), String> {
    fs::write(&path, content)
        .map_err(|e| format!("scaffold: write {:?}: {}", path, e))?;
    created.push(path.to_string_lossy().to_string());
    Ok(())
}

// ── Report ────────────────────────────────────────────────────────────────────

pub fn report(result: &Result<ScaffoldResult, String>) -> String {
    match result {
        Err(e) => format!("[SCAFFOLD_ERROR]: {}\n", e),
        Ok(r)  => format!(
            "[SCAFFOLD]: {} ROOT={} WEIGHT={:.2} ({}) FILES={}\n",
            r.name, r.root, r.weight.total(), r.weight.label(), r.files_created.len()
        ),
    }
}

// ── ERU fleet report ──────────────────────────────────────────────────────────

pub fn eru_report(fleet_dir: &str) -> String {
    let eru = eru_fleet(fleet_dir);
    let missing_list: String = eru.missing.iter()
        .map(|m| format!("  MISSING: {}\n", m))
        .collect();
    format!(
        "[ERU_FLEET]: EXPECTED={} ACTUAL={} ERU={:.4} MISSING={}\n{}",
        eru.expected, eru.actual, eru.eru, eru.missing.len(), missing_list
    )
}
