use sagco_sync::ingest::csv_loader::load_demo;
use sagco_sync::calc::evm::EVMSnapshot;

/// The overrun circuit "E-1706-NA-2A" has:
///   lnf_total=120, lnf_done=120, estimate_hrs=491, used_hrs=1020.3
///   EV = (120/120) * 491 = 491
///   CPI = 491 / 1020.3 ≈ 0.4813
#[test]
fn overrun_circuit_cpi_approx_0_48() {
    let ra = load_demo();
    let overrun = ra
        .circuits
        .iter()
        .find(|c| c.id == "E-1706-NA-2A")
        .expect("E-1706-NA-2A should exist in demo data");

    let snap = EVMSnapshot::from_circuit(overrun);

    // CPI should be approximately 0.48
    let expected_cpi = 491.0 / 1020.3;
    let delta = (snap.cpi - expected_cpi).abs();
    assert!(
        delta < 0.001,
        "Expected CPI ≈ {:.4}, got {:.4} (delta={:.6})",
        expected_cpi,
        snap.cpi,
        delta,
    );

    // Must be OVERRUN status
    assert_eq!(snap.status(), "OVERRUN");

    // EV should equal PV (100% complete)
    let ev_delta = (snap.ev - 491.0).abs();
    assert!(ev_delta < 0.001, "EV should be 491.0, got {:.4}", snap.ev);
}

#[test]
fn demo_data_project_totals() {
    let ra = load_demo();

    // PV = 280+210+491+1080 = 2061
    let expected_pv = 2061.0_f64;
    let delta_pv = (ra.total_pv() - expected_pv).abs();
    assert!(delta_pv < 0.01, "PV mismatch: expected {}, got {:.2}", expected_pv, ra.total_pv());

    // AC = 40+427.5+1020.3+579.2 = 2067.0
    let expected_ac = 2067.0_f64;
    let delta_ac = (ra.total_ac() - expected_ac).abs();
    assert!(delta_ac < 0.01, "AC mismatch: expected {}, got {:.2}", expected_ac, ra.total_ac());

    assert_eq!(ra.circuits.len(), 3);
}

#[test]
fn early_high_cpi_cut1_circuit1a() {
    let ra = load_demo();
    let circ = ra
        .circuits
        .iter()
        .find(|c| c.id == "E-1706-NA-1A")
        .expect("E-1706-NA-1A should exist");

    let cut1 = circ.cuts.iter().find(|c| c.id == "1").expect("cut 1 should exist");

    // EV = (18/46) * 280 = 109.565...
    // CPI = 109.565 / 40 = 2.739...
    let ev = (18.0 / 46.0) * 280.0;
    let expected_cpi = ev / 40.0;
    let delta = (cut1.cpi() - expected_cpi).abs();
    assert!(
        delta < 0.001,
        "Cut 1 CPI should be ≈{:.4}, got {:.4}",
        expected_cpi,
        cut1.cpi()
    );
    // Should be well above 1.0 (front-loaded easy work)
    assert!(cut1.cpi() > 2.0, "Early CPI should be high (>2), got {:.3}", cut1.cpi());
}

#[test]
fn difficulty_weights_sum_to_nonzero() {
    let ra = load_demo();
    let weights = sagco_sync::calc::rates::extract_weights(&ra);
    assert!(weights.avg_rate > 0.0, "avg_rate should be positive");
    assert!(!weights.cuts.is_empty(), "should have cut weights");

    let adj_pct = sagco_sync::calc::rates::difficulty_adjusted_pct(&ra, &weights);
    assert!(adj_pct > 0.0 && adj_pct <= 1.0, "adj_pct should be in (0,1], got {}", adj_pct);
}
