/// A Claim is the atomic unit of the ERU protocol.
///
/// Don't measure projects. Measure claims.
/// Every wild SAGCO wing reduces to this same loop:
///   Claim → Expected → Actual → Variance → Verdict → Lineage
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum ClaimStatus {
    /// No evidence yet — claim is open
    Open,
    /// Evidence being gathered
    InProgress,
    /// All expected evidence present → PROVEN
    Proven,
    /// Partial evidence → PROMISING
    Promising,
    /// Claim exists, no evidence → UNPROVEN
    Unproven,
    /// Win rate looks good but EV negative / numbers don't support it
    Inflated,
    /// Claim was superseded or withdrawn
    Retracted,
}

impl ClaimStatus {
    pub fn label(&self) -> &'static str {
        match self {
            Self::Open       => "OPEN",
            Self::InProgress => "IN_PROGRESS",
            Self::Proven     => "PROVEN",
            Self::Promising  => "PROMISING",
            Self::Unproven   => "UNPROVEN",
            Self::Inflated   => "INFLATED",
            Self::Retracted  => "RETRACTED",
        }
    }

    pub fn from_coverage(coverage_pct: f64) -> Self {
        if coverage_pct >= 100.0 { Self::Proven }
        else if coverage_pct >= 50.0 { Self::Promising }
        else if coverage_pct > 0.0  { Self::Unproven }
        else { Self::Inflated }
    }
}

impl std::fmt::Display for ClaimStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.label())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Claim {
    pub id:          String,        // e.g. "SAGCO-GRAPH-001"
    pub text:        String,        // "SAGCO knowledge graph exceeds value..."
    pub project:     String,        // which project owns this claim
    pub category:    String,        // "valuation" | "architecture" | "capability" | "market"
    pub status:      ClaimStatus,
    pub notes:       String,
    pub created_at:  String,        // ISO 8601
    pub seal:        String,        // SHA-256[:8] of id + text
}

impl Claim {
    pub fn new(
        id:       impl Into<String>,
        text:     impl Into<String>,
        project:  impl Into<String>,
        category: impl Into<String>,
    ) -> Self {
        let id   = id.into();
        let text = text.into();
        let seal = Self::compute_seal(&id, &text);
        Self {
            id,
            text,
            project:  project.into(),
            category: category.into(),
            status:   ClaimStatus::Open,
            notes:    String::new(),
            created_at: "2026-06-15".to_string(),
            seal,
        }
    }

    fn compute_seal(id: &str, text: &str) -> String {
        let mut h = Sha256::new();
        h.update(id.as_bytes());
        h.update(b"|");
        h.update(text.as_bytes());
        hex::encode(&h.finalize()[..8])
    }

    pub fn with_status(mut self, s: ClaimStatus) -> Self {
        self.status = s;
        self
    }

    pub fn with_notes(mut self, n: impl Into<String>) -> Self {
        self.notes = n.into();
        self
    }
}

/// The built-in claim set — every major SAGCO assertion encoded.
pub fn sagco_claims() -> Vec<Claim> {
    vec![
        Claim::new(
            "SAGCO-GRAPH-001",
            "SAGCO knowledge graph exceeds value of any single component",
            "sagco-organism",
            "architecture",
        ).with_status(ClaimStatus::Proven)
         .with_notes("10 components vs 4 expected = 250% coverage"),

        Claim::new(
            "RENKO-VAL-001",
            "RenkoMasterVisualization_AI market value = $55,000+",
            "renko-master",
            "valuation",
        ).with_status(ClaimStatus::Unproven)
         .with_notes("Dev=$4k Replacement=$40k Business=$10k-50k Market=unproven"),

        Claim::new(
            "RENKO-PORTFOLIO-001",
            "RenkoMasterVisualization_AI is a strong portfolio signal",
            "renko-master",
            "market",
        ).with_status(ClaimStatus::Proven)
         .with_notes("Trading+Viz+Automation+C#+AI in one repo = strong hiring signal"),

        Claim::new(
            "ERU-FOUNDATIONAL-001",
            "ERU is a universal comparator applicable across all SAGCO wings",
            "sagco-organism",
            "architecture",
        ).with_status(ClaimStatus::Proven)
         .with_notes("Same loop: Claim→Expected→Actual→Variance→Verdict works for valuation, trading, hardware, build order"),

        Claim::new(
            "TRADE-SIM-001",
            "Renko trend following has positive expected value",
            "sagco-trade-simulator",
            "capability",
        ).with_status(ClaimStatus::Promising)
         .with_notes("Simulated: WR=73% EV=+$1527/trade PF=10.64 — needs real market validation"),

        Claim::new(
            "TRADE-SIM-002",
            "Renko mean reversion is profitable",
            "sagco-trade-simulator",
            "capability",
        ).with_status(ClaimStatus::Inflated)
         .with_notes("AB-OVERFIT-001 fired: WR=48% EV=-$11.23 PF=0.76 — strategy destroys capital"),

        Claim::new(
            "HP-NODE-001",
            "HP node (192.168.1.98) is a sovereign local compute node",
            "sagco-node-hp",
            "capability",
        ).with_status(ClaimStatus::Promising)
         .with_notes("Observed via Task Manager. Needs live probe verification: sagco node hp probe"),

        Claim::new(
            "CHESS-STACK-001",
            "640-node chess stack models a complete callable execution grid",
            "sagco-chess-stack",
            "architecture",
        ).with_status(ClaimStatus::Proven)
         .with_notes("62/62 tests pass. 10×64=640 cells. 2040 hidden patterns. Loop closer: QED."),
    ]
}
