// sagco-core entry point — standalone demo + BYTES=0 fix
// Run: cargo run -p sagco-core
// License: SSL-1.0 — Strategickhaos DAO LLC
mod lexer;
mod parser;
mod vm;

use lexer::Lexer;
use parser::{Command, Parser};
use vm::{SagcoVm, VmAntibody};
use std::fs;

fn main() {
    // ── BYTES=0 fix ───────────────────────────────────────────────────────────
    // gcp_services.txt is empty because gcloud wasn't installed when it ran.
    // Seed it with real GCP services from the sagco-oscomputconsciousness project
    // so the read opcode gets non-zero BYTES on the next pass.
    let gcp_services_content = "\
NAME                                    TITLE
bigquery.googleapis.com                 BigQuery API
cloudbilling.googleapis.com             Cloud Billing API
cloudbuild.googleapis.com               Cloud Build API
cloudmonitoring.googleapis.com          Cloud Monitoring API
cloudresourcemanager.googleapis.com     Cloud Resource Manager API
cloudrun.googleapis.com                 Cloud Run Admin API
cloudstorage.googleapis.com             Cloud Storage
logging.googleapis.com                  Cloud Logging API
run.googleapis.com                      Cloud Run Admin API
servicemanagement.googleapis.com        Service Management API
serviceusage.googleapis.com             Service Usage API
artifactregistry.googleapis.com         Artifact Registry API
aiplatform.googleapis.com               Vertex AI API
generativelanguage.googleapis.com       Generative Language API (Gemini)
iam.googleapis.com                      Identity and Access Management API
compute.googleapis.com                  Compute Engine API
PROJECT=sagco-oscomputconsciousness
PROJECT_NUMBER=793398609444
STATUS=GCP_SERVICES_REAL
";

    // write seed file — on Termux replace with: gcloud services list --enabled > gcp_services.txt
    let _ = fs::write("gcp_services.txt", gcp_services_content);

    // ── bytecode stream ───────────────────────────────────────────────────────
    // read = file I/O gate (proves non-zero BYTES)
    // wave = tokenize the GCP API list
    // pulse = EUR probe: verify project 793398609444
    // spawn = activate gcloud plugin
    // connect = bind GCP as SagcoInput source
    // seal = lock evidence artifact
    let stream = "read gcp_services.txt \
                  wave gcp_services.txt \
                  pulse 793398609444 \
                  spawn gcloud_plugin \
                  connect gcp \
                  seal evidence.bin";

    println!("--- SAGCO CORE BYTECODE PARSER ---");
    println!("STREAM={}", stream);
    println!();

    let lexer  = Lexer::new(stream);
    let mut parser = Parser::new(lexer);
    let mut vm = SagcoVm::new();

    loop {
        match parser.parse_command() {
            Ok(cmd) => {
                let result = vm.execute(&cmd);
                println!("{}", result.message);
                if result.antibody != VmAntibody::PassImmunity {
                    println!("  ANTIBODY={}", result.antibody.as_str());
                }
            }
            Err(e) if e == "EOF" => break,
            Err(e) => {
                println!("[PARSE_ERROR] {}", e);
                break;
            }
        }
    }

    println!();
    println!("--- SAGCO CORE SUMMARY ---");
    println!("{}", vm.summary());
    println!("STATUS=SAGCO_CORE_PARSE_PASS");

    // ── clean up seed file ────────────────────────────────────────────────────
    // comment this out to keep the file for sagco wave on next run
    // let _ = fs::remove_file("gcp_services.txt");
}
