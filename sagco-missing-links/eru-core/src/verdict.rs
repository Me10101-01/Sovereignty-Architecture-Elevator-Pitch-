/// Verdict: the output of one ERU cycle.
///
/// Don't measure projects. Measure claims.
/// Verdict is the seal on a claim — what the evidence actually says.
use serde::{Deserialize, Serialize};
use crate::variance::Variance;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum Verdict {
    Proven,     // ≥100% coverage — over-evidenced is fine
    Promising,  // 50–99% coverage — real signal, not yet sealed
    Unproven,   // 1–49%  — claim exists, evidence sparse
    Inflated,   // 0%     — claim made with zero evidence (antibody fires)
}

impl Verdict {
    pub fn from_variance(v: &Variance) -> Self {
        match v.coverage_pct as u32 {
            100.. => Self::Proven,
            50..  => Self::Promising,
            1..   => Self::Unproven,
            _     => Self::Inflated,
        }
    }

    pub fn label(&self) -> &'static str {
        match self {
            Self::Proven    => "PROVEN",
            Self::Promising => "PROMISING",
            Self::Unproven  => "UNPROVEN",
            Self::Inflated  => "INFLATED",
        }
    }

    pub fn icon(&self) -> &'static str {
        match self {
            Self::Proven    => "✓",
            Self::Promising => "~",
            Self::Unproven  => "·",
            Self::Inflated  => "✗",
        }
    }

    pub fn antibody_needed(&self) -> bool {
        matches!(self, Self::Inflated)
    }
}

impl std::fmt::Display for Verdict {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.label())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerdictRecord {
    pub claim_id:  String,
    pub claim_text: String,
    pub verdict:   Verdict,
    pub coverage:  f64,
    pub gaps:      Vec<String>,
    pub seal:      String,
    pub timestamp: String,
}

impl VerdictRecord {
    pub fn from_variance(claim_id: &str, claim_text: &str, v: &Variance) -> Self {
        use sha2::{Digest, Sha256};
        let verdict = Verdict::from_variance(v);
        let mut h = Sha256::new();
        h.update(claim_id.as_bytes());
        h.update(verdict.label().as_bytes());
        h.update(v.coverage_pct.to_bits().to_le_bytes());
        let seal = hex::encode(&h.finalize()[..8]);
        Self {
            claim_id:   claim_id.to_string(),
            claim_text: claim_text.to_string(),
            verdict,
            coverage:   v.coverage_pct,
            gaps:       v.gaps.clone(),
            seal,
            timestamp:  "2026-06-15T00:00:00Z".to_string(),
        }
    }

    pub fn one_line(&self) -> String {
        format!(
            "[{}] {:<40} {:.1}%  {}",
            self.verdict.icon(),
            &self.claim_id,
            self.coverage,
            self.verdict,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::variance::Variance;

    #[test]
    fn proven_when_full_coverage() {
        let v = Variance::compute(vec!["a"], vec![("a", "src")]);
        assert_eq!(Verdict::from_variance(&v), Verdict::Proven);
    }

    #[test]
    fn inflated_when_zero_coverage() {
        let v = Variance::compute(vec!["a", "b"], vec![]);
        assert_eq!(Verdict::from_variance(&v), Verdict::Inflated);
        assert!(Verdict::from_variance(&v).antibody_needed());
    }

    #[test]
    fn promising_at_half_coverage() {
        let v = Variance::compute(vec!["a", "b"], vec![("a", "src")]);
        assert_eq!(Verdict::from_variance(&v), Verdict::Promising);
    }
}
