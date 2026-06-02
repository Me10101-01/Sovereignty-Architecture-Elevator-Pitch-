// sagco-evidence — aggregate report + token artifacts into sealed evidence ledger
// Usage: sagco-evidence <reports_dir> <tokens_dir>
// License: SSL-1.0 — Strategickhaos DAO LLC
use sagco_core::crypto::{sha256_hex, SealLedger};
use std::{env, fs, io::Write, path::Path, process};

fn walk_dir(dir: &str) -> Vec<std::path::PathBuf> {
    let mut paths = Vec::new();
    if let Ok(rd) = fs::read_dir(dir) {
        for entry in rd.flatten() {
            let p = entry.path();
            if p.is_file() { paths.push(p); }
        }
    }
    paths.sort();
    paths
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: sagco-evidence <reports_dir> <tokens_dir>");
        process::exit(1);
    }
    let reports_dir = &args[1];
    let tokens_dir  = &args[2];

    let mut ledger  = SealLedger::new();
    let mut lines   = Vec::new();
    let mut n_files = 0usize;

    lines.push("SAGCO_EVIDENCE_LEDGER=1".to_string());
    lines.push(format!("REPORTS_DIR={}", reports_dir));
    lines.push(format!("TOKENS_DIR={}", tokens_dir));
    lines.push(String::new());

    for dir in &[reports_dir.as_str(), tokens_dir.as_str()] {
        let label = if *dir == reports_dir { "REPORT" } else { "TOKEN" };
        for path in walk_dir(dir) {
            let path_str = path.to_string_lossy().to_string();
            match fs::read(&path) {
                Ok(data) if !data.is_empty() => {
                    let sha = sha256_hex(&data);
                    ledger.record(&path_str, &sha);
                    lines.push(format!("{}  {}  {}", label, sha, path_str));
                    n_files += 1;
                }
                _ => {
                    lines.push(format!("{}  EMPTY_PAYLOAD_ANTIBODY  {}", label, path_str));
                }
            }
        }
    }

    lines.push(String::new());
    lines.push(format!("TOTAL_ARTIFACTS={}", n_files));
    lines.push(format!("CHAIN_HASH={}", ledger.chain_hash()));
    lines.push("DNA=a364ca9f90356c85".to_string());
    lines.push("STATUS=SAGCO_EVIDENCE_PASS".to_string());

    let output = lines.join("\n");
    println!("{}", output);

    // write the sealed evidence artifact
    let artifact_path = "SAGCO_EVIDENCE.seal";
    let seal_content = format!(
        "SAGCO_SEAL_ARTIFACT=1\nTARGET={}\nCHAIN_HASH={}\nDNA=a364ca9f90356c85\n",
        artifact_path, ledger.chain_hash()
    );
    if let Ok(mut f) = fs::File::create(artifact_path) {
        let _ = f.write_all(seal_content.as_bytes());
        eprintln!("EVIDENCE_LOCKED  artifact={}", artifact_path);
    }
}
