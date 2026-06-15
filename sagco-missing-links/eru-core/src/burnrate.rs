/// BurnRate: how fast are claims being closed vs. time/effort consumed?
///
/// Low burnrate → claims pile up faster than they're proven
/// High burnrate → delivering faster than expected
/// Ideal burnrate → EV per claim is positive (mirrors trading EV)
use serde::{Deserialize, Serialize};
use crate::verdict::Verdict;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BurnSnapshot {
    pub claims_total:    usize,
    pub claims_proven:   usize,
    pub claims_promising: usize,
    pub claims_unproven: usize,
    pub claims_inflated: usize,
    pub burnrate:        f64,    // proven / total  (0.0–1.0)
    pub ev_per_claim:    f64,    // expected value: how much of each claim pays off
    pub verdict:         String,
}

impl BurnSnapshot {
    pub fn from_verdicts(verdicts: &[Verdict]) -> Self {
        let total     = verdicts.len();
        let proven    = verdicts.iter().filter(|v| **v == Verdict::Proven).count();
        let promising = verdicts.iter().filter(|v| **v == Verdict::Promising).count();
        let unproven  = verdicts.iter().filter(|v| **v == Verdict::Unproven).count();
        let inflated  = verdicts.iter().filter(|v| **v == Verdict::Inflated).count();

        let burnrate = if total == 0 { 0.0 } else { proven as f64 / total as f64 };

        // EV per claim: proven=1.0, promising=0.5, unproven=0.1, inflated=-0.5
        let ev = if total == 0 {
            0.0
        } else {
            (proven as f64 * 1.0
                + promising as f64 * 0.5
                + unproven as f64 * 0.1
                - inflated as f64 * 0.5)
                / total as f64
        };

        let verdict_str = if burnrate >= 0.8 {
            "STRONG — closing claims faster than opening"
        } else if burnrate >= 0.5 {
            "HEALTHY — majority of claims proven"
        } else if burnrate >= 0.3 {
            "LAGGING — more claims open than proven"
        } else {
            "CRITICAL — claims not being closed"
        };

        Self {
            claims_total:    total,
            claims_proven:   proven,
            claims_promising: promising,
            claims_unproven: unproven,
            claims_inflated: inflated,
            burnrate,
            ev_per_claim:    ev,
            verdict:         verdict_str.to_string(),
        }
    }

    pub fn report(&self) -> String {
        format!(
            "  BurnRate Report\n\n  Total claims:   {}\n  Proven:         {} ({:.1}%)\n  Promising:      {}\n  Unproven:       {}\n  Inflated:       {}\n\n  BurnRate:       {:.1}%\n  EV/claim:       {:.3}\n  Verdict:        {}\n",
            self.claims_total,
            self.claims_proven,
            self.burnrate * 100.0,
            self.claims_promising,
            self.claims_unproven,
            self.claims_inflated,
            self.burnrate * 100.0,
            self.ev_per_claim,
            self.verdict,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn burnrate_all_proven() {
        let v = vec![Verdict::Proven, Verdict::Proven];
        let s = BurnSnapshot::from_verdicts(&v);
        assert!((s.burnrate - 1.0).abs() < 0.001);
    }

    #[test]
    fn burnrate_mixed() {
        let v = vec![Verdict::Proven, Verdict::Promising, Verdict::Inflated, Verdict::Unproven];
        let s = BurnSnapshot::from_verdicts(&v);
        assert!((s.burnrate - 0.25).abs() < 0.001);
        assert!(s.ev_per_claim > 0.0);  // 1.0 + 0.5 + 0.1 - 0.5 = 1.1 / 4 = 0.275
    }

    #[test]
    fn sagco_graph_burnrate() {
        // From our real ERU results
        let verdicts = vec![
            Verdict::Proven,    // SAGCO-GRAPH-001
            Verdict::Unproven,  // RENKO-VAL-001
            Verdict::Proven,    // RENKO-PORTFOLIO-001
            Verdict::Proven,    // ERU-FOUNDATIONAL-001
            Verdict::Promising, // TRADE-SIM-001
            Verdict::Inflated,  // TRADE-SIM-002
            Verdict::Promising, // HP-NODE-001
            Verdict::Proven,    // CHESS-STACK-001
        ];
        let s = BurnSnapshot::from_verdicts(&verdicts);
        assert!(s.burnrate > 0.4);  // 4/8 = 50%
        assert!(s.ev_per_claim > 0.0);
    }
}
