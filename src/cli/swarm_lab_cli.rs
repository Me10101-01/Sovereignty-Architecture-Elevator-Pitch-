//! Swarm Lab CLI
//! 
//! Command-line interface for the Sovereign Black Ops Lab.
//! Provides tools for running experiments, parsing logs, and managing the swarm.

use std::env;
use std::process;

mod commands;

/// Entry point for the Swarm Lab CLI
fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        print_usage();
        process::exit(1);
    }

    match args[1].as_str() {
        "parse" => commands::parse::run(&args[2..]),
        "analyze" => commands::analyze::run(&args[2..]),
        "experiment" => commands::experiment::run(&args[2..]),
        "handshake" => commands::handshake::run(&args[2..]),
        "help" | "--help" | "-h" => print_usage(),
        _ => {
            eprintln!("Unknown command: {}", args[1]);
            print_usage();
            process::exit(1);
        }
    }
}

fn print_usage() {
    println!(r#"
Swarm Lab CLI - Sovereign Black Ops Lab

USAGE:
    swarm_lab_cli <COMMAND> [OPTIONS]

COMMANDS:
    parse       Parse raw logs (GKE audit, leases, autoscaler)
    analyze     Run analyzers on parsed data
    experiment  Manage experiment lifecycle
    handshake   Execute SWARM-HS protocol phases
    help        Show this help message

OPTIONS:
    -h, --help     Show help for a specific command
    -v, --verbose  Enable verbose output

EXAMPLES:
    # Parse GKE audit logs
    swarm_lab_cli parse --input logs/raw_gke_audit/audit.json --parser gke_audit

    # Analyze lease churn
    swarm_lab_cli analyze --type lease_churn --input logs/derived/events.csv

    # Start a new experiment
    swarm_lab_cli experiment new --name "lease-analysis"

    # Execute SYN phase
    swarm_lab_cli handshake syn --context context.md --agent claude

For more information, see docs/BLACK_OPS_LAB.md
"#);
}

/// Placeholder module for subcommands
mod commands {
    pub mod parse {
        pub fn run(_args: &[String]) {
            println!("Parse command - TODO: Implement");
        }
    }
    
    pub mod analyze {
        pub fn run(_args: &[String]) {
            println!("Analyze command - TODO: Implement");
        }
    }
    
    pub mod experiment {
        pub fn run(_args: &[String]) {
            println!("Experiment command - TODO: Implement");
        }
    }
    
    pub mod handshake {
        pub fn run(_args: &[String]) {
            println!("Handshake command - TODO: Implement");
        }
    }
}
