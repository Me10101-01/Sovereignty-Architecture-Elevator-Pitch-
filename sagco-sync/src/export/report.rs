use crate::calc::evm::EVMSnapshot;
use crate::calc::sim::SimResult;
use crate::ingest::ra_sheet::{Circuit, RASheet};

// ANSI color codes
const RESET: &str = "\x1b[0m";
const BOLD: &str = "\x1b[1m";
const RED: &str = "\x1b[31m";
const YELLOW: &str = "\x1b[33m";
const GREEN: &str = "\x1b[32m";
const CYAN: &str = "\x1b[36m";

fn status_color(cpi: f64) -> &'static str {
    if cpi >= 1.0 { GREEN } else if cpi >= 0.8 { YELLOW } else { RED }
}

pub fn print_report(ra: &RASheet) {
    let proj = EVMSnapshot::from_project(ra);
    let overrun = proj.eac - proj.pv;
    let overrun_str = if overrun > 0.0 {
        format!("+{:.0} overrun", overrun)
    } else {
        format!("{:.0} under", overrun.abs())
    };

    println!("{BOLD}══════════════════════════════════════════════════════════{RESET}");
    println!("  {BOLD}{CYAN}SAGCO-SYNC PRODUCTIVITY REPORT — EVM DASHBOARD{RESET}");
    println!("  Strategickhaos DAO LLC | Field Intelligence");
    println!("{BOLD}══════════════════════════════════════════════════════════{RESET}");
    println!();
    println!("  {BOLD}PROJECT:{RESET} {}", ra.project_name);
    println!("  ────────────────────────────────────────────────────────");
    println!("  Total PV  (Planned):  {:.1} hrs", proj.pv);
    println!("  Total AC  (Actual):   {:.1} hrs", proj.ac);
    println!("  Total EV  (Earned):   {:.1} hrs", proj.ev);
    let cpi_color = status_color(proj.cpi);
    println!("  Project CPI:          {cpi_color}{:.3}{RESET}", proj.cpi);
    println!("  Project SPI:          {:.3}", proj.spi);
    if proj.eac.is_infinite() {
        println!("  Project EAC:          ∞ hrs (CPI = 0)");
    } else {
        println!("  Project EAC:          {:.1} hrs ({})", proj.eac, overrun_str);
    }
    println!("  ────────────────────────────────────────────────────────");
    println!();
    println!("  {BOLD}CIRCUIT BREAKDOWN:{RESET}");
    println!(
        "  ┌─────────────────┬──────┬──────┬──────┬──────┬──────┬──────────────────────┐"
    );
    println!(
        "  │ {BOLD}Circuit         {RESET}│  PV  │  AC  │  EV  │  CPI │  EAC │ Status               │"
    );
    println!(
        "  ├─────────────────┼──────┼──────┼──────┼──────┼──────┼──────────────────────┤"
    );

    for circ in &ra.circuits {
        print_circuit_row(circ);
    }

    println!(
        "  └─────────────────┴──────┴──────┴──────┴──────┴──────┴──────────────────────┘"
    );
    println!();
}

pub fn print_circuit_row(circuit: &Circuit) {
    let snap = EVMSnapshot::from_circuit(circuit);
    let color = status_color(snap.cpi);
    let complete_tag = if snap.pct_complete >= 0.999 { " (complete)" } else { "" };
    let status_str = format!("{} {}{}", snap.status_icon(), snap.status(), complete_tag);

    let eac_str = if snap.eac.is_infinite() {
        "  ∞   ".to_string()
    } else {
        format!("{:>5.0} ", snap.eac)
    };

    println!(
        "  │ {:<15} │{:>5.0} │{:>5.0} │{:>5.0} │ {}{:.2}{} │{} │ {:<20} │",
        &circuit.id[..circuit.id.len().min(15)],
        snap.pv,
        snap.ac,
        snap.ev,
        color,
        snap.cpi,
        RESET,
        eac_str,
        status_str,
    );
}

pub fn print_circuit_detail(circuit: &Circuit) {
    let snap = EVMSnapshot::from_circuit(circuit);
    let color = status_color(snap.cpi);

    println!();
    println!("  {BOLD}Circuit: {}{RESET}", circuit.id);
    println!("  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄");
    println!("  PV:  {:.1}  AC: {:.1}  EV: {:.1}", snap.pv, snap.ac, snap.ev);
    println!(
        "  CPI: {}{:.3}{RESET}  SPI: {:.3}  TCPI: {:.3}",
        color, snap.cpi, snap.spi, snap.tcpi
    );
    println!("  CV:  {:.1}  SV: {:.1}", snap.cv, snap.sv);
    if snap.eac.is_infinite() {
        println!("  EAC: ∞");
    } else {
        println!("  EAC: {:.1}  ETC: {:.1}", snap.eac, snap.etc);
    }
    println!(
        "  % Complete (EV-based): {:.1}%   % Budget Spent: {:.1}%",
        snap.pct_complete * 100.0,
        snap.pct_spent * 100.0,
    );

    println!();
    println!("  Cuts:");
    for cut in &circuit.cuts {
        println!(
            "    [{:>3}] LNF {:.0}/{:.0}  E={:.1}h  U={:.1}h  CPI={:.2}  {}",
            cut.id,
            cut.lnf_done,
            cut.lnf_total,
            cut.estimate_hrs,
            cut.used_hrs,
            cut.cpi(),
            cut.access,
        );
    }
}

pub fn print_forecast(snap: &EVMSnapshot, sim: &SimResult) {
    println!("  {BOLD}FORECAST (Monte Carlo — {} simulations):{RESET}", sim.n_simulations);
    println!("  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄");
    println!("  Circuit: {}", snap.id);
    println!("  CPI std-dev (15% rule): {:.3}", sim.cpi_std);
    println!("  P20 EAC: {:.1} hrs", sim.p20_eac);
    println!("  P50 EAC: {:.1} hrs", sim.p50_eac);
    println!("  P80 EAC: {:.1} hrs", sim.p80_eac);
    println!("  Mean EAC: {:.1} hrs", sim.mean_eac);
    println!();
}
