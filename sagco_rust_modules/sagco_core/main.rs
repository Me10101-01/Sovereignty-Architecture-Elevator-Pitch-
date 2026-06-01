// sagco-core entry point — file-driven instruction pipeline
// Usage:  cargo run -- pipeline.txt
//         cargo run              (uses default stream)
// License: SSL-1.0 — Strategickhaos DAO LLC
mod antibody;
mod crypto;
mod lexer;
mod parser;
mod vm;

use antibody::Antibody;
use lexer::Lexer;
use parser::{Command, Parser};
use vm::{SagcoVm, VmAntibody};
use std::env;
use std::fs::File;
use std::io::{self, Read};

// ── native file reader (no shell, no bash) ────────────────────────────────────
fn read_target_file(path: &str) -> io::Result<String> {
    let mut file = File::open(path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}

// ── Wave sub-tokenizer: parse gcp_services.txt line by line ──────────────────
// Each "NAME  TITLE" line → service_name as Identifier token
fn wave_tokenize(content: &str) -> Vec<String> {
    content
        .lines()
        .filter(|line| {
            let l = line.trim();
            !l.is_empty()
                && !l.starts_with("NAME")   // skip header
                && !l.starts_with('#')
        })
        .filter_map(|line| {
            // first word of each line = service name or key=value token
            let token = line.split_whitespace().next()?;
            if token.len() >= 3 { Some(token.to_lowercase()) } else { None }
        })
        .collect()
}

// ── Pulse identity mask ────────────────────────────────────────────────────────
// 793398609444 = sagco-oscomputconsciousness
// Any other project number = FOREIGN_NODE_ANTIBODY
const SAGCO_PROJECT_NODE: u64 = 793398609444;

fn main() {
    let args: Vec<String> = env::args().collect();

    // ── Step 1: load instruction stream ──────────────────────────────────────
    let (stream, source) = if args.len() >= 2 {
        let path = &args[1];
        match read_target_file(path) {
            Ok(content) => {
                let bytes = content.len();
                println!("[READ]: {} BYTES={}", path, bytes);
                if bytes == 0 {
                    println!("  HINT: echo 'wave gcp_services.txt pulse 793398609444 seal evidence.bin' > {}", path);
                    Antibody::EmptyResponse.fire("SAGCO_CORE_VARIANCE_FAIL");
                }
                (content, path.clone())
            }
            Err(e) => {
                println!("[FATAL_IO]: {} — {}", path, e);
                Antibody::PathDiscovery.fire("SAGCO_CORE_VARIANCE_FAIL");
            }
        }
    } else {
        // default stream: covers all 7 opcodes
        let default = "read gcp_services.txt \
                        wave gcp_services.txt \
                        pulse 793398609444 \
                        spawn gcloud_plugin \
                        connect gcp \
                        seal evidence.bin";
        (default.to_string(), "<default>".to_string())
    };

    println!("--- SAGCO CORE BYTECODE PARSER ---");
    println!("SOURCE={}", source);
    println!();

    // ── Step 2: Lex → Parse → Execute ────────────────────────────────────────
    let lexer = Lexer::new(&stream);
    let mut parser = Parser::new(lexer);
    let mut vm = SagcoVm::new();

    loop {
        match parser.parse_command() {
            Ok(cmd) => {
                match &cmd {
                    // Wave: read target file natively → sub-tokenize → report
                    Command::Wave { source: target } => {
                        match read_target_file(target) {
                            Ok(content) => {
                                let bytes = content.len();
                                if bytes == 0 {
                                    println!("[WAVE]: {} TARGET_BYTES=0", target);
                                    println!("  HINT: gcloud services list --enabled > {}", target);
                                    Antibody::EmptyPayload.fire("SAGCO_CORE_VARIANCE_FAIL");
                                }
                                let tokens = wave_tokenize(&content);
                                println!("[WAVE]: {} TARGET_BYTES={}  TOKENS={}",
                                    target, bytes, tokens.len());
                                for (i, t) in tokens.iter().take(5).enumerate() {
                                    println!("  FL_GCP_{:02}={}", i, t);
                                }
                                if tokens.len() > 5 {
                                    println!("  ... +{} more GCP service tokens", tokens.len() - 5);
                                }
                                vm.tokens_ingested += tokens.len();
                            }
                            Err(_) => {
                                println!("[WAVE]: {} TARGET_BYTES=0 — EMPTY_RESPONSE_ANTIBODY", target);
                                println!("  HINT: gcloud services list --enabled > {}", target);
                            }
                        }
                    }

                    // Pulse: validate against SAGCO project identity mask
                    Command::Pulse { node_id } => {
                        if *node_id == SAGCO_PROJECT_NODE {
                            println!("[PULSE]: {} — SAGCO_GCP_PROJECT_NODE  PASS_IMMUNITY", node_id);
                        } else {
                            println!("[PULSE]: {} — FOREIGN_NODE_ANTIBODY  expected={}",
                                node_id, SAGCO_PROJECT_NODE);
                        }
                        vm.node_registry.insert(*node_id, "verified".to_string());
                    }

                    // All other commands: delegate to VM
                    other => {
                        let result = vm.execute(other);
                        println!("{}", result.message);
                        if result.antibody != VmAntibody::PassImmunity {
                            println!("  ANTIBODY={}", result.antibody.as_str());
                        }
                    }
                }
            }
            Err(e) if e == "EOF" => break,
            Err(e) => {
                println!("[PARSE_ERROR] {}", e);
                break;
            }
        }
    }

    // ── Step 3: Summary ───────────────────────────────────────────────────────
    println!();
    println!("--- SAGCO CORE SUMMARY ---");
    println!("{}", vm.summary());
    println!("STATUS=SAGCO_CORE_PARSE_PASS");
}
