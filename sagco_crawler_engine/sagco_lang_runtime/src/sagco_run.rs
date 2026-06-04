use std::env;
use std::fs;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: sagco-run <program.sagco>");
        std::process::exit(1);
    }

    let path = &args[1];
    let contents = fs::read_to_string(path).unwrap_or_else(|e| {
        eprintln!("ERROR: Cannot read {}: {}", path, e);
        std::process::exit(1);
    });

    println!("SAGCO_RUN: loading {}", path);
    println!();

    for line in contents.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        if line.starts_with("MISSION=") {
            println!(">> MISSION LOADED: {}", &line[8..]);
        } else if line.starts_with("BRICK=") {
            println!(">> BRICK: {}", &line[6..]);
        } else if line.starts_with("STATUS=") {
            println!(">> STATUS: {}", &line[7..]);
        } else if line.starts_with("ELEMENT_") {
            println!("   {}", line);
        }
    }

    println!();
    println!("SAGCO_RUN_COMPLETE");
}
