// main.rs — sagco-bias-core CLI entry point
//
// Runs the Omni reference example (Vcc=5V Rc=100Ω Re=250Ω Rb1=200Ω Rb2=50Ω β=65)
// then verifies against known values using ERU scoring.
//
// Usage:  cargo run --bin sagco-bias-core

use sagco_bias_core::voltage_divider::{self, VoltageDividerInput};
use sagco_bias_core::eru;

fn main() {
    println!("SAGCO TRANSISTOR BIAS CALCULATOR — VOLTAGE DIVIDER TOPOLOGY");
    println!("================================================================");

    // ── Omni reference example ────────────────────────────────────────────────
    let input = VoltageDividerInput::new(5.0, 100.0, 250.0, 200.0, 50.0, 65.0);

    let result = match voltage_divider::solve(&input) {
        Ok(r)  => r,
        Err(e) => { eprintln!("ERROR: {}", e); std::process::exit(1); }
    };

    println!("{}", result.report(&input));
    println!("{}", result.status_line());

    // ── ERU validation against Omni reference values ──────────────────────────
    println!("\n================================================================");
    let records = vec![
        eru::compare("Ib_mA",  0.018,  result.ib * 1000.0,  0.01),
        eru::compare("Ic_mA",  1.179,  result.ic * 1000.0,  0.01),
        eru::compare("Ie_mA",  1.197,  result.ie * 1000.0,  0.01),
        eru::compare("Vce_V",  4.583,  result.vce,          0.01),
        eru::compare("Vb_V",   0.999,  result.vb,           0.01),
    ];

    print!("{}", eru::report(&records));

    let all_pass = records.iter().all(|r| r.pass);
    if all_pass {
        println!("STATUS=SAGCO_BIAS_ERU_PASS");
    } else {
        println!("STATUS=SAGCO_BIAS_ERU_FAIL");
        std::process::exit(2);
    }
}
