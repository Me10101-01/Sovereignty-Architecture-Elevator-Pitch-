/// ERU Core — Expected Reality Unit
///
/// Don't measure projects. Measure claims.
/// Every SAGCO wing reduces to this same loop:
///   Claim → Expected → Actual → Variance → Verdict → BurnRate → Lineage
pub mod claim;
pub mod variance;
pub mod verdict;
pub mod burnrate;

pub use claim::{Claim, ClaimStatus, sagco_claims};
pub use variance::{Evidence, Variance};
pub use verdict::{Verdict, VerdictRecord};
pub use burnrate::BurnSnapshot;

/// Run a full ERU cycle for the SAGCO claim set.
pub fn run_sagco_eru() -> Vec<VerdictRecord> {
    // SAGCO knowledge graph
    let graph_v = Variance::compute(
        vec!["multiple interconnected projects", "shared registry", "cross-project lineage", "reusable architecture"],
        vec![
            ("multiple interconnected projects", "11 bricks registered"),
            ("shared registry",                  "registry.sagco.json"),
            ("cross-project lineage",             "topo sort + dep tree"),
            ("reusable architecture",             "ERU, antibodies, brick system"),
            ("trading simulator",                 "sagco-trade-simulator"),
            ("chess stack",                       "sagco-chess-stack 640 nodes"),
            ("KHAOS 72 elements",                 "sagco-true/khaos"),
            ("FlameLang VM",                      "sagco-true/language"),
            ("HP sovereign node",                 "sagco-node-hp"),
            ("Renko system",                      "renko-master"),
        ],
    );

    // Renko market valuation
    let renko_val_v = Variance::compute(
        vec!["users", "backtest metrics", "adoption data", "comparable sales", "revenue"],
        vec![],
    );

    // Renko portfolio signal
    let renko_portfolio_v = Variance::compute(
        vec!["C# codebase", "trading domain", "visualization", "AI integration", "automation"],
        vec![
            ("C# codebase",     "NinjaScript/NinjaTrader repo"),
            ("trading domain",  "Renko chart engine"),
            ("visualization",   "RenkoMasterVisualization"),
            ("AI integration",  "AI in project name + features"),
            ("automation",      "automated charting"),
        ],
    );

    vec![
        VerdictRecord::from_variance("SAGCO-GRAPH-001",      "SAGCO knowledge graph is the asset", &graph_v),
        VerdictRecord::from_variance("RENKO-VAL-001",         "Renko market value $55k+", &renko_val_v),
        VerdictRecord::from_variance("RENKO-PORTFOLIO-001",   "Renko is a strong portfolio signal", &renko_portfolio_v),
    ]
}
