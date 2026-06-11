use sagco_sync::calc;
use sagco_sync::export;
use sagco_sync::ingest;
use sagco_sync::lang;

mod cli;

use clap::Parser;
use cli::{Cli, Commands};

fn load_ra(file: &Option<String>) -> ingest::ra_sheet::RASheet {
    match file {
        Some(path) => match ingest::csv_loader::load_csv(path) {
            Ok(ra) => ra,
            Err(e) => {
                eprintln!("Error loading CSV '{}': {}", path, e);
                eprintln!("Falling back to demo data.");
                ingest::csv_loader::load_demo()
            }
        },
        None => ingest::csv_loader::load_demo(),
    }
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Productivity { file, json } => {
            let ra = load_ra(&file);

            if json {
                let snap = calc::evm::EVMSnapshot::from_project(&ra);
                let circuit_snaps: Vec<_> = ra
                    .circuits
                    .iter()
                    .map(calc::evm::EVMSnapshot::from_circuit)
                    .collect();
                let output = serde_json::json!({
                    "project": snap,
                    "circuits": circuit_snaps,
                });
                println!("{}", serde_json::to_string_pretty(&output).unwrap_or_default());
            } else {
                export::report::print_report(&ra);

                println!("  CIRCUIT DETAILS:");
                for circ in &ra.circuits {
                    export::report::print_circuit_detail(circ);
                }

                println!();
                println!("  FORECASTS (Monte Carlo):");
                println!("  ────────────────────────────────────────────────────────");
                let proj_snap = calc::evm::EVMSnapshot::from_project(&ra);
                let proj_sim = calc::sim::simulate(&proj_snap, 10_000);
                export::report::print_forecast(&proj_snap, &proj_sim);

                for circ in &ra.circuits {
                    let snap = calc::evm::EVMSnapshot::from_circuit(circ);
                    if snap.ac > 0.0 {
                        let sim = calc::sim::simulate(&snap, 10_000);
                        export::report::print_forecast(&snap, &sim);
                    }
                }
            }
        }

        Commands::Rates { file } => {
            let ra = load_ra(&file);
            let weights = calc::rates::extract_weights(&ra);
            let adj_pct = calc::rates::difficulty_adjusted_pct(&ra, &weights);

            println!("SAGCO-SYNC | Difficulty Rate Analysis — {}", ra.project_name);
            println!("Average implied rate: {:.4} hrs/LNF", weights.avg_rate);
            println!("Difficulty-adjusted % complete: {:.1}%", adj_pct * 100.0);
            println!();
            println!("{:<12} {:>10} {:>12} {:>14} {:>8}", "Cut ID", "LNF", "Est hrs", "Implied Rate", "Weight");
            println!("{}", "-".repeat(60));
            for cw in &weights.cuts {
                println!(
                    "{:<12} {:>10.1} {:>12.1} {:>14.4} {:>8.3}",
                    cw.cut_id, cw.lnf, cw.estimate_hrs, cw.implied_rate, cw.weight
                );
            }
        }

        Commands::Simulate { file, n } => {
            let ra = load_ra(&file);
            let proj_snap = calc::evm::EVMSnapshot::from_project(&ra);
            let sim = calc::sim::simulate(&proj_snap, n);

            println!("SAGCO-SYNC | Monte Carlo EAC Simulation — {}", ra.project_name);
            println!("Simulations: {}", sim.n_simulations);
            println!("Current CPI: {:.4}", proj_snap.cpi);
            println!("CPI std-dev:  {:.4} (15% rule of thumb)", sim.cpi_std);
            println!();
            println!("  P20 EAC: {:>10.1} hrs  (optimistic)", sim.p20_eac);
            println!("  P50 EAC: {:>10.1} hrs  (median)", sim.p50_eac);
            println!("  P80 EAC: {:>10.1} hrs  (conservative)", sim.p80_eac);
            println!("  Mean EAC:{:>10.1} hrs", sim.mean_eac);
            println!("  Planned: {:>10.1} hrs", proj_snap.pv);
        }

        Commands::Export { file, out } => {
            let ra = load_ra(&file);
            match export::excel::export_excel(&ra, &out) {
                Ok(()) => println!("Exported Excel workbook → {}", out),
                Err(e) => eprintln!("Export failed: {}", e),
            }
        }

        Commands::Parse { file } => {
            let content = match std::fs::read_to_string(&file) {
                Ok(s) => s,
                Err(e) => {
                    eprintln!("Cannot read '{}': {}", file, e);
                    return;
                }
            };

            println!("=== Lexer Tokens ===");
            let mut lexer = lang::lexer::Lexer::new(&content);
            let tokens = lexer.tokenize();
            for tok in &tokens {
                println!("  {:?}", tok);
            }

            println!();
            println!("=== AST ===");
            let mut parser = lang::parser::Parser::new(tokens);
            match parser.parse() {
                Ok(ast) => println!("{:#?}", ast),
                Err(e) => eprintln!("Parse error: {}", e),
            }
        }

        Commands::Status => {
            println!("SAGCO-SYNC v{}", env!("CARGO_PKG_VERSION"));
            println!("Description: {}", env!("CARGO_PKG_DESCRIPTION"));
            println!();
            println!("Modules:");
            println!("  [✓] lang     — .sagcoplan DSL lexer + parser");
            println!("  [✓] ingest   — CSV loader + RA sheet types");
            println!("  [✓] calc     — EVM, rates, Monte Carlo, CPI trend");
            println!("  [✓] export   — terminal report + Excel workbook");
            println!("  [✓] cli      — clap subcommand interface");
            println!();
            println!("Demo data summary (Stratford-Job-1):");
            let ra = ingest::csv_loader::load_demo();
            let proj = calc::evm::EVMSnapshot::from_project(&ra);
            println!("  Project:   {}", ra.project_name);
            println!("  Circuits:  {}", ra.circuits.len());
            println!("  Total PV:  {:.1} hrs", proj.pv);
            println!("  Total AC:  {:.1} hrs", proj.ac);
            println!("  Total EV:  {:.1} hrs", proj.ev);
            println!("  Project CPI: {:.3}", proj.cpi);
            if proj.eac.is_finite() {
                println!("  Project EAC: {:.1} hrs", proj.eac);
            } else {
                println!("  Project EAC: ∞");
            }
            println!("  Status: {} {}", proj.status_icon(), proj.status());
        }
    }
}
