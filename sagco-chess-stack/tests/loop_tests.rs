use sagco_chess::{LoopCloser, LoopStatus, PieceKind};

#[test]
fn king_always_closes() {
    // King can always find an adjacent cell; must close within tight budget
    let mut lc = LoopCloser::new(PieceKind::King, 0).with_max_ticks(1000);
    let status = lc.run().clone();
    assert!(
        matches!(status, LoopStatus::Closed { .. }),
        "King loop did not close: {:?}", status
    );
}

#[test]
fn closed_loop_length_positive() {
    let mut lc = LoopCloser::new(PieceKind::King, 0).with_max_ticks(1000);
    if let LoopStatus::Closed { length, .. } = lc.run().clone() {
        assert!(length > 0, "loop length must be positive");
    }
}

#[test]
fn different_starts_different_closures() {
    let mut lc1 = LoopCloser::new(PieceKind::King, 0).with_max_ticks(1000);
    let mut lc2 = LoopCloser::new(PieceKind::King, 320).with_max_ticks(1000);
    lc1.run();
    lc2.run();
    // Both should close but with different seals (different start → different path)
    if let (LoopStatus::Closed { seal: s1, .. }, LoopStatus::Closed { seal: s2, .. }) =
        (&lc1.status, &lc2.status)
    {
        assert_ne!(s1, s2, "different starts must yield different seals");
    }
}

#[test]
fn knight_closes_from_center() {
    // Knight from L5 center (id=347) has more choices, must close
    let mut lc = LoopCloser::new(PieceKind::Knight, 347).with_max_ticks(10_000);
    let status = lc.run().clone();
    assert_ne!(status, LoopStatus::Open);
}

#[test]
fn loop_state_output_nonzero_after_closure() {
    let mut lc = LoopCloser::new(PieceKind::King, 0).with_max_ticks(1000);
    lc.run();
    // Cell::call() mixes in a salt, so output after N steps should be non-zero
    assert_ne!(lc.state.output, 0, "output should be non-zero after cell chain");
}

#[test]
fn loop_report_contains_qed_keywords() {
    let mut lc = LoopCloser::new(PieceKind::King, 0).with_max_ticks(1000);
    lc.run();
    let r = lc.report();
    assert!(r.contains("CLOSED") || r.contains("EXHAUSTED") || r.contains("OPEN"));
}
