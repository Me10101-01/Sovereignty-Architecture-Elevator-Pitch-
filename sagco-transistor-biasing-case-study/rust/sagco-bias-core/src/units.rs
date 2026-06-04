// units.rs — SI unit formatting helpers for bias report output

pub struct Units;

impl Units {
    pub fn volts(&self, v: f64) -> String {
        if v.abs() >= 1.0 {
            format!("{:.4} V", v)
        } else {
            format!("{:.4} mV", v * 1000.0)
        }
    }

    pub fn milliamps(&self, ma: f64) -> String {
        format!("{:.4} mA", ma)
    }

    pub fn ohms(&self, r: f64) -> String {
        if r >= 1_000_000.0 {
            format!("{:.3} MΩ", r / 1_000_000.0)
        } else if r >= 1_000.0 {
            format!("{:.3} kΩ", r / 1_000.0)
        } else {
            format!("{:.1} Ω", r)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_volts_above_one() {
        assert_eq!(Units.volts(5.0), "5.0000 V");
    }

    #[test]
    fn test_volts_millirange() {
        let s = Units.volts(0.0007);
        assert!(s.contains("mV"), "expected mV, got {}", s);
    }

    #[test]
    fn test_ohms_kilohms() {
        assert_eq!(Units.ohms(1000.0), "1.000 kΩ");
    }

    #[test]
    fn test_ohms_small() {
        assert_eq!(Units.ohms(100.0), "100.0 Ω");
    }
}
