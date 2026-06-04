// sagco-eru: ERU variance engine
// Usage: sagco-eru <wafer.csv> <capture.csv> [CASE_ID]

#[path = "../../src/eru/wafer.rs"]    mod wafer;
#[path = "../../src/eru/variance.rs"] mod variance;

use wafer::load_wafer;
use variance::{load_captures, compute_eru};
use std::env;
use std::fs;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: sagco-eru <wafer.csv> <capture.csv> [CASE_ID]");
        std::process::exit(1);
    }

    let wafer_path   = &args[1];
    let capture_path = &args[2];
    let case_id      = args.get(3).map(|s| s.as_str()).unwrap_or("DEFAULT");

    let wafer_csv   = fs::read_to_string(wafer_path).unwrap_or_else(|e| {
        eprintln!("ERROR reading wafer: {}", e); std::process::exit(1);
    });
    let capture_csv = fs::read_to_string(capture_path).unwrap_or_else(|e| {
        eprintln!("ERROR reading capture: {}", e); std::process::exit(1);
    });

    let wafer    = load_wafer(&wafer_csv);
    let captures = load_captures(&capture_csv, case_id);
    let records  = compute_eru(&wafer, &captures);

    println!("SAGCO ERU VARIANCE REPORT");
    println!("CASE={}", case_id);
    println!("WAFER_ROWS={}", wafer.len());
    println!("CAPTURE_ROWS={}", captures.len());
    println!();
    println!("{:<20} {:<12} {:<12} {:>9}  STATUS", "TOKEN_TYPE", "EXPECTED", "ACTUAL", "VARIANCE");
    println!("{}", "─".repeat(65));

    let mut green = 0; let mut yellow = 0; let mut red = 0;
    for r in &records {
        println!("{:<20} {:<12} {:<12} {:>+9}  {}",
            r.token_type, r.expected, r.actual, r.variance, r.status);
        match r.status.as_str() {
            "GREEN"  => green  += 1,
            "YELLOW" => yellow += 1,
            _        => red    += 1,
        }
    }

    println!("{}", "─".repeat(65));
    println!("GREEN={} YELLOW={} RED={}", green, yellow, red);

    let overall = if red > 0 { "RED" } else if yellow > 0 { "YELLOW" } else { "GREEN" };
    println!("STATUS=ERU_COMPLETE  OVERALL={}", overall);
}
