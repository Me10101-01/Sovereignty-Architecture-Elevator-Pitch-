/// Variance: the gap between Expected and Actual evidence.
///
/// Variance is not always negative.
/// Positive variance = over-delivered (more than expected).
/// Negative variance = gap remaining.
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Evidence {
    pub text:     String,
    pub present:  bool,
    pub source:   String,   // where this evidence comes from
}

impl Evidence {
    pub fn present(text: impl Into<String>, source: impl Into<String>) -> Self {
        Self { text: text.into(), present: true, source: source.into() }
    }
    pub fn missing(text: impl Into<String>) -> Self {
        Self { text: text.into(), present: false, source: String::new() }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Variance {
    pub expected: Vec<Evidence>,   // what would prove the claim
    pub actual:   Vec<Evidence>,   // what currently exists
    pub gaps:     Vec<String>,     // items in expected but not in actual
    pub surplus:  Vec<String>,     // items in actual but not in expected (bonus)
    pub coverage_pct: f64,         // actual / expected × 100
}

impl Variance {
    pub fn compute(
        expected: Vec<&str>,
        actual:   Vec<(&str, &str)>,   // (text, source)
    ) -> Self {
        let expected_texts: Vec<String> = expected.iter().map(|s| s.to_string()).collect();
        let actual_texts: Vec<String>   = actual.iter().map(|(s, _)| s.to_string()).collect();

        let gaps: Vec<String> = expected_texts.iter()
            .filter(|e| !actual_texts.iter().any(|a| a == *e))
            .cloned().collect();

        let surplus: Vec<String> = actual_texts.iter()
            .filter(|a| !expected_texts.iter().any(|e| e == *a))
            .cloned().collect();

        let coverage = if expected_texts.is_empty() {
            0.0
        } else {
            let matched = expected_texts.iter().filter(|e| actual_texts.iter().any(|a| a == *e)).count();
            matched as f64 / expected_texts.len() as f64 * 100.0
        };

        Self {
            expected: expected_texts.iter()
                .map(|t| Evidence {
                    text:    t.clone(),
                    present: actual_texts.iter().any(|a| a == t),
                    source:  actual.iter().find(|(a, _)| *a == t.as_str())
                                .map(|(_, s)| s.to_string())
                                .unwrap_or_default(),
                })
                .collect(),
            actual: actual.iter()
                .map(|(t, s)| Evidence::present(*t, *s))
                .collect(),
            gaps,
            surplus,
            coverage_pct: coverage,
        }
    }

    pub fn is_positive(&self) -> bool {
        self.coverage_pct >= 100.0
    }

    pub fn summary(&self) -> String {
        format!(
            "{:.1}% coverage | {} gaps | {} surplus",
            self.coverage_pct,
            self.gaps.len(),
            self.surplus.len(),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn positive_variance_over_delivered() {
        let v = Variance::compute(
            vec!["a", "b"],
            vec![("a", "src1"), ("b", "src2"), ("c", "src3")],
        );
        assert!(v.coverage_pct >= 100.0);
        assert_eq!(v.surplus, vec!["c"]);
    }

    #[test]
    fn gap_detected() {
        let v = Variance::compute(
            vec!["a", "b", "c"],
            vec![("a", "src1")],
        );
        assert!(v.coverage_pct < 100.0);
        assert_eq!(v.gaps.len(), 2);
    }
}
