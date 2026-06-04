// eru.rs — ERU (Expected-vs-Real Uncertainty) variance scoring
//
// Formula:  score = |expected − actual| / max(|expected|, ε)
//
// A score < 0.01 means <1% deviation.  Used to compare calculator output
// against textbook / Omni reference values and rank portfolio confidence.

const TINY: f64 = 1e-12;

#[derive(Debug, Clone)]
pub struct EruRecord {
    pub label:    String,
    pub expected: f64,
    pub actual:   f64,
    pub score:    f64,   // 0.0 = perfect, 1.0 = 100% error
    pub pass:     bool,  // true if score < threshold
}

pub fn score(expected: f64, actual: f64) -> f64 {
    (expected - actual).abs() / expected.abs().max(TINY)
}

pub fn compare(label: &str, expected: f64, actual: f64, threshold: f64) -> EruRecord {
    let s = score(expected, actual);
    EruRecord {
        label:    label.to_string(),
        expected,
        actual,
        score:    s,
        pass:     s < threshold,
    }
}

pub fn report(records: &[EruRecord]) -> String {
    let mut out = String::from("# ERU VARIANCE REPORT\n\n");
    out.push_str(&format!("{:<16} {:>12} {:>12} {:>10} {}\n",
        "LABEL", "EXPECTED", "ACTUAL", "ERU%", "PASS"));
    out.push_str(&"-".repeat(58));
    out.push('\n');
    for r in records {
        out.push_str(&format!(
            "{:<16} {:>12.6} {:>12.6} {:>9.2}% {}\n",
            r.label, r.expected, r.actual,
            r.score * 100.0,
            if r.pass { "✓" } else { "✗" },
        ));
    }
    let pass_count = records.iter().filter(|r| r.pass).count();
    out.push_str(&format!("\nPASS {}/{}\n", pass_count, records.len()));
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_zero_variance() {
        assert!(score(1.179, 1.179) < 1e-9);
    }

    #[test]
    fn test_known_variance() {
        let s = score(1.179, 1.200);
        assert!(s < 0.02, "ERU {:.4} should be <2%", s);
    }

    #[test]
    fn test_compare_pass() {
        let r = compare("Ic_mA", 1.179, 1.180, 0.01);
        assert!(r.pass, "should pass at 1% threshold");
    }

    #[test]
    fn test_compare_fail() {
        let r = compare("Ic_mA", 1.179, 1.300, 0.01);
        assert!(!r.pass, "should fail at 1% threshold with 10% error");
    }

    #[test]
    fn test_report_formatting() {
        let records = vec![
            compare("Ib_mA",  0.018, 0.0181, 0.01),
            compare("Ic_mA",  1.179, 1.179,  0.01),
        ];
        let rpt = report(&records);
        assert!(rpt.contains("ERU VARIANCE REPORT"));
        assert!(rpt.contains("PASS 2/2"));
    }
}
