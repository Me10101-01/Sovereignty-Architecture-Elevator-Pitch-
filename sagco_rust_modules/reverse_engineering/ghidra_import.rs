// SAGCO Ghidra Import — headless binary ingest automation
// License: SSL-1.0 — Strategickhaos DAO LLC

use std::path::PathBuf;
use std::process::Command;

pub struct GhidraConfig {
    pub ghidra_home: PathBuf,
    pub java_home:   PathBuf,
    pub project_dir: PathBuf,
    pub project_name: String,
}

impl Default for GhidraConfig {
    fn default() -> Self {
        let home = std::env::var("HOME").unwrap_or_default();
        let prefix = std::env::var("PREFIX")
            .unwrap_or_else(|_| format!("{}/usr", home));
        GhidraConfig {
            ghidra_home:  PathBuf::from(format!("{}/downloads/ghidra_12.1_PUBLIC", home)),
            java_home:    PathBuf::from(format!("{}/lib/jvm/java-21-openjdk", prefix)),
            project_dir:  PathBuf::from(format!("{}/ghidra_projects", home)),
            project_name: "SAGCO_FLAMETOKEN".to_string(),
        }
    }
}

pub struct ImportResult {
    pub success:  bool,
    pub log:      String,
    pub antibody: String,
}

pub fn run_import(binary: &PathBuf, cfg: &GhidraConfig) -> ImportResult {
    let analyze = cfg.ghidra_home.join("support/analyzeHeadless");

    if !analyze.exists() {
        return ImportResult {
            success: false,
            log: format!("analyzeHeadless not found at {}", analyze.display()),
            antibody: "PATH_DISCOVERY_ANTIBODY".to_string(),
        };
    }

    let mut cmd = Command::new(&analyze);
    cmd.env("JAVA_HOME", &cfg.java_home)
       .arg(&cfg.project_dir)
       .arg(&cfg.project_name)
       .arg("-import")
       .arg(binary)
       .arg("-overwrite");

    match cmd.output() {
        Ok(out) => {
            let log = String::from_utf8_lossy(&out.stdout).to_string()
                + &String::from_utf8_lossy(&out.stderr);
            let success = log.contains("Import succeeded");
            let antibody = if success {
                "PASS_IMMUNITY".to_string()
            } else if log.to_lowercase().contains("jdk 21") {
                "JDK_GATE_ANTIBODY".to_string()
            } else if log.to_lowercase().contains("decompiler") {
                "PLATFORM_LIMITATION_ANTIBODY".to_string()
            } else {
                "UNKNOWN_VARIANCE_ANTIBODY".to_string()
            };
            ImportResult { success, log, antibody }
        }
        Err(e) => ImportResult {
            success: false,
            log: e.to_string(),
            antibody: "DEPENDENCY_ANTIBODY".to_string(),
        },
    }
}
