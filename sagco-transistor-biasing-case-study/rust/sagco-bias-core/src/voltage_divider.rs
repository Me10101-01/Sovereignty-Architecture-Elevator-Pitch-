// voltage_divider.rs — Voltage Divider Bias Calculator
//
// Circuit topology:
//
//   Vcc
//    |
//   Rc
//    |──── Vc
//    |
//   [BJT NPN]
//    |──── Vb ──── Rb1 ──── Vcc
//    |         \── Rb2 ──── GND
//    |
//   Re
//    |──── Ve
//    |
//   GND
//
// Method: Thevenin equivalent of Rb1/Rb2 divider, then KVL around base loop.
//
// Key equations:
//   Vth  = Vcc × Rb2 / (Rb1 + Rb2)
//   Rth  = Rb1 ‖ Rb2 = (Rb1 × Rb2) / (Rb1 + Rb2)
//   Ib   = (Vth − Vbe) / (Rth + (β+1)×Re)
//   Ic   = β × Ib
//   Ie   = (β+1) × Ib  [= Ic + Ib]
//   Vce  = Vcc − Ic×Rc − Ie×Re

use crate::units::Units;

const VCE_SAT: f64 = 0.2;   // saturation threshold (V)
const TINY:    f64 = 1e-12;  // prevents division by zero in ERU

#[derive(Debug, Clone)]
pub struct VoltageDividerInput {
    pub vcc:  f64,   // supply voltage (V)
    pub rc:   f64,   // collector resistor (Ω)
    pub re:   f64,   // emitter resistor (Ω)
    pub rb1:  f64,   // upper divider resistor (Ω)
    pub rb2:  f64,   // lower divider resistor (Ω)
    pub beta: f64,   // current gain hFE (dimensionless)
    pub vbe:  f64,   // base-emitter junction voltage (V), default 0.7
}

impl VoltageDividerInput {
    pub fn new(vcc: f64, rc: f64, re: f64, rb1: f64, rb2: f64, beta: f64) -> Self {
        Self { vcc, rc, re, rb1, rb2, beta, vbe: 0.7 }
    }

    pub fn validate(&self) -> Result<(), String> {
        if self.vcc <= 0.0    { return Err("Vcc must be positive".into()); }
        if self.rc  < 0.0     { return Err("Rc must be non-negative".into()); }
        if self.re  < 0.0     { return Err("Re must be non-negative".into()); }
        if self.rb1 <= 0.0    { return Err("Rb1 must be positive".into()); }
        if self.rb2 <= 0.0    { return Err("Rb2 must be positive".into()); }
        if self.beta <= 0.0   { return Err("β must be positive".into()); }
        if self.vbe < 0.0 || self.vbe > 1.5 {
            return Err(format!("Vbe={:.3} outside valid range 0–1.5V", self.vbe));
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum BiasRegion {
    Active,     // normal operating region
    Saturated,  // Vce < Vce_sat — transistor fully on
    Cutoff,     // Ib <= 0 — transistor off
}

impl BiasRegion {
    pub fn label(&self) -> &'static str {
        match self {
            BiasRegion::Active    => "ACTIVE",
            BiasRegion::Saturated => "SATURATED",
            BiasRegion::Cutoff    => "CUTOFF",
        }
    }
}

#[derive(Debug, Clone)]
pub struct VoltageDividerResult {
    // Thevenin intermediate values
    pub vth: f64,   // Thevenin voltage (V)
    pub rth: f64,   // Thevenin resistance (Ω)
    // Currents
    pub ib:  f64,   // base current (A)
    pub ic:  f64,   // collector current (A)
    pub ie:  f64,   // emitter current (A)
    // Node voltages (relative to GND)
    pub vb:  f64,   // base voltage (V)
    pub ve:  f64,   // emitter voltage (V)
    pub vc:  f64,   // collector voltage (V)
    pub vce: f64,   // collector-emitter voltage (V)
    pub vbc: f64,   // base-collector voltage (V)
    // Operating region
    pub region: BiasRegion,
}

impl VoltageDividerResult {
    pub fn status_line(&self) -> String {
        format!("STATUS=SAGCO_BIAS_PASS REGION={}", self.region.label())
    }

    pub fn report(&self, input: &VoltageDividerInput) -> String {
        let u = Units;
        format!(
            "# SAGCO TRANSISTOR BIAS — VOLTAGE DIVIDER\n\
             \n\
             ## INPUTS\n\
             Vcc  = {}\n\
             Rc   = {}\n\
             Re   = {}\n\
             Rb1  = {}\n\
             Rb2  = {}\n\
             β    = {:.0}\n\
             Vbe  = {}\n\
             \n\
             ## THEVENIN EQUIVALENT\n\
             Vth  = {}\n\
             Rth  = {}\n\
             \n\
             ## Q-POINT\n\
             Ib   = {}\n\
             Ic   = {}\n\
             Ie   = {}\n\
             Vce  = {}\n\
             \n\
             ## NODE VOLTAGES\n\
             Vb   = {}\n\
             Ve   = {}\n\
             Vc   = {}\n\
             Vbc  = {}\n\
             \n\
             ## BIAS REGION\n\
             {}\n",
            u.volts(input.vcc), u.ohms(input.rc), u.ohms(input.re),
            u.ohms(input.rb1), u.ohms(input.rb2),
            input.beta, u.volts(input.vbe),
            u.volts(self.vth), u.ohms(self.rth),
            u.milliamps(self.ib * 1000.0),
            u.milliamps(self.ic * 1000.0),
            u.milliamps(self.ie * 1000.0),
            u.volts(self.vce),
            u.volts(self.vb), u.volts(self.ve), u.volts(self.vc),
            u.volts(self.vbc),
            self.region.label(),
        )
    }
}

pub fn solve(input: &VoltageDividerInput) -> Result<VoltageDividerResult, String> {
    input.validate()?;

    // Step 1: Thevenin equivalent
    let vth = input.vcc * input.rb2 / (input.rb1 + input.rb2);
    let rth = (input.rb1 * input.rb2) / (input.rb1 + input.rb2);

    // Step 2: Check if circuit can even turn on
    if vth <= input.vbe {
        return Ok(VoltageDividerResult {
            vth, rth,
            ib: 0.0, ic: 0.0, ie: 0.0,
            vb: vth, ve: 0.0, vc: input.vcc, vce: input.vcc, vbc: vth - input.vcc,
            region: BiasRegion::Cutoff,
        });
    }

    // Step 3: KVL around base-emitter loop
    // Vth = Ib×Rth + Vbe + (β+1)×Ib×Re
    // Ib  = (Vth - Vbe) / (Rth + (β+1)×Re)
    let ib = (vth - input.vbe) / (rth + (input.beta + 1.0) * input.re);

    if ib <= 0.0 {
        return Ok(VoltageDividerResult {
            vth, rth,
            ib: 0.0, ic: 0.0, ie: 0.0,
            vb: vth, ve: 0.0, vc: input.vcc, vce: input.vcc, vbc: vth - input.vcc,
            region: BiasRegion::Cutoff,
        });
    }

    // Step 4: Derived currents
    let ic = input.beta * ib;
    let ie = (input.beta + 1.0) * ib;   // Ie = Ic + Ib

    // Step 5: Node voltages
    let ve  = ie * input.re;
    let vb  = ve + input.vbe;
    let vc  = input.vcc - ic * input.rc;
    let vce = vc - ve;
    let vbc = vb - vc;

    // Step 6: Operating region
    let region = if vce < VCE_SAT {
        BiasRegion::Saturated
    } else {
        BiasRegion::Active
    };

    Ok(VoltageDividerResult { vth, rth, ib, ic, ie, vb, ve, vc, vce, vbc, region })
}

/// ERU variance score: |expected - actual| / max(expected, TINY)
pub fn eru_score(expected: f64, actual: f64) -> f64 {
    (expected - actual).abs() / expected.abs().max(TINY)
}

#[cfg(test)]
mod tests {
    use super::*;

    // Omni example: Vcc=5V Rc=100Ω Re=250Ω Rb1=200Ω Rb2=50Ω β=65
    fn omni_input() -> VoltageDividerInput {
        VoltageDividerInput::new(5.0, 100.0, 250.0, 200.0, 50.0, 65.0)
    }

    #[test]
    fn test_omni_ib() {
        let r = solve(&omni_input()).unwrap();
        let ib_ma = r.ib * 1000.0;
        assert!((ib_ma - 0.018).abs() < 0.001,
            "Ib={:.4} mA, expected ≈0.018 mA", ib_ma);
    }

    #[test]
    fn test_omni_ic() {
        let r = solve(&omni_input()).unwrap();
        let ic_ma = r.ic * 1000.0;
        assert!((ic_ma - 1.179).abs() < 0.002,
            "Ic={:.4} mA, expected ≈1.179 mA", ic_ma);
    }

    #[test]
    fn test_omni_region() {
        let r = solve(&omni_input()).unwrap();
        assert_eq!(r.region, BiasRegion::Active);
    }

    #[test]
    fn test_cutoff_when_vth_lt_vbe() {
        // Rb1 >> Rb2 so Vth << Vbe
        let input = VoltageDividerInput::new(5.0, 100.0, 250.0, 10000.0, 1.0, 65.0);
        let r = solve(&input).unwrap();
        assert_eq!(r.region, BiasRegion::Cutoff);
    }

    #[test]
    fn test_saturation_low_re() {
        // No emitter resistor, low Rc → Vce collapses
        let input = VoltageDividerInput::new(1.0, 1.0, 0.0, 10.0, 10.0, 200.0);
        let r = solve(&input).unwrap();
        assert_eq!(r.region, BiasRegion::Saturated);
    }

    #[test]
    fn test_eru_zero_variance() {
        assert!(eru_score(1.179, 1.179) < 1e-9);
    }

    #[test]
    fn test_eru_known_variance() {
        let score = eru_score(1.179, 1.200);
        assert!(score < 0.02, "ERU score {:.4} should be <2%", score);
    }
}
