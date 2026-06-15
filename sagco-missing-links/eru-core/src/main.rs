use clap::{Parser, Subcommand};
use eru_core::{run_sagco_eru, sagco_claims, BurnSnapshot, Verdict};

#[derive(Parser)]
#[command(name = "eru", about = "ERU — Expected Reality Unit. Measure claims, not projects.")]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Run all SAGCO claims through ERU and show verdicts
    Run,
    /// Show BurnRate — how fast are claims closing?
    Burn,
    /// List all registered claims
    Claims,
    /// Show the ERU loop formula
    Formula,
}

fn main() {
    let cli = Cli::parse();
    match cli.cmd {
        Cmd::Run => {
            println!();
            println!("  ══════════════════════════════════════════════════════");
            println!("  ERU — Expected Reality Unit — SAGCO Claim Set");
            println!("  Don't measure projects. Measure claims.");
            println!("  ══════════════════════════════════════════════════════");
            println!();
            for rec in run_sagco_eru() {
                println!("  {}", rec.one_line());
                if !rec.gaps.is_empty() {
                    for g in &rec.gaps {
                        println!("      [✗] missing: {}", g);
                    }
                }
                println!("      seal: {}", rec.seal);
                println!();
            }
        }

        Cmd::Burn => {
            let claims = sagco_claims();
            let verdicts: Vec<Verdict> = claims.iter().map(|c| match c.status {
                eru_core::ClaimStatus::Proven    => Verdict::Proven,
                eru_core::ClaimStatus::Promising => Verdict::Promising,
                eru_core::ClaimStatus::Inflated  => Verdict::Inflated,
                _                                => Verdict::Unproven,
            }).collect();
            let snap = BurnSnapshot::from_verdicts(&verdicts);
            println!();
            print!("{}", snap.report());
            println!();
        }

        Cmd::Claims => {
            let claims = sagco_claims();
            println!();
            println!("  SAGCO Registered Claims ({}):", claims.len());
            println!();
            for c in &claims {
                println!("  [{}] {} — {}", c.status, c.id, c.project);
                println!("      {}", c.text);
                if !c.notes.is_empty() {
                    println!("      note: {}", c.notes);
                }
                println!();
            }
        }

        Cmd::Formula => {
            println!();
            println!("  ERU Loop Formula");
            println!("  ────────────────");
            println!("  Claim    → what is being asserted");
            println!("  Expected → evidence that would prove it");
            println!("  Actual   → evidence that exists now");
            println!("  Variance → Expected − Actual (can be positive = over-delivered)");
            println!("  Verdict  → PROVEN | PROMISING | UNPROVEN | INFLATED");
            println!("  BurnRate → proven / total  (mirrors EV in trading)");
            println!("  Lineage  → seal + timestamp + source chain");
            println!();
            println!("  EV per claim = (proven×1.0 + promising×0.5 + unproven×0.1 − inflated×0.5) / total");
            println!();
            println!("  Verdicts in SAGCO today:");
            println!("    SAGCO knowledge graph   → PROVEN    (250% coverage)");
            println!("    Renko portfolio signal  → PROVEN    (100% coverage)");
            println!("    Renko market value $55k → INFLATED  (0% — no users yet)");
            println!("    HP sovereign node       → PROMISING (live probe needed)");
            println!("    Chess stack grid        → PROVEN    (62/62 tests)");
            println!();
        }
    }
}
