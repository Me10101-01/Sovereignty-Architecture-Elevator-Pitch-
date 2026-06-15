"""Trade simulator tests — 100 fake trades, real metrics."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulator import run_all, run_strategy
from src.metrics import compute_metrics
from src.eru_report import ab_overfit_check, metrics_to_eru


def test_all_strategies_produce_100_trades():
    for r in run_all(n_trades=100, seed=42):
        assert r.metrics.n_trades == 100, f"{r.strategy}: {r.metrics.n_trades} ≠ 100"


def test_wins_plus_losses_equals_n():
    for r in run_all(n_trades=100, seed=42):
        m = r.metrics
        assert m.n_wins + m.n_losses == m.n_trades


def test_final_equity_equals_starting_plus_sum_pnl():
    for r in run_all(n_trades=50, seed=7):
        total_pnl = sum(t.pnl for t in r.trades)
        expected  = r.metrics.starting_equity + total_pnl
        assert abs(r.metrics.final_equity - expected) < 0.01, \
            f"{r.strategy}: equity mismatch"


def test_max_drawdown_nonnegative():
    for r in run_all(seed=42):
        assert r.metrics.max_drawdown >= 0
        assert r.metrics.max_drawdown_pct >= 0


def test_profit_factor_positive_or_inf():
    for r in run_all(seed=42):
        assert r.metrics.profit_factor >= 0


def test_ev_formula_matches():
    for r in run_all(seed=42):
        m = r.metrics
        ev_check = (m.win_rate * m.avg_gain) - ((1 - m.win_rate) * m.avg_loss)
        assert abs(m.expected_value - ev_check) < 0.01, \
            f"{m.strategy}: EV mismatch {m.expected_value} vs {ev_check}"


def test_different_seeds_different_results():
    r1 = run_strategy("dividend", seed=1)
    r2 = run_strategy("dividend", seed=2)
    assert r1.metrics.final_equity != r2.metrics.final_equity


def test_ab_overfit_fires_correctly():
    # Construct a metrics object that should trigger AB-OVERFIT-001
    from src.metrics import Metrics
    bad = Metrics(
        strategy="test", n_trades=100, n_wins=65, n_losses=35,
        win_rate=0.65, avg_gain=50.0, avg_loss=120.0,
        profit_factor=0.80, expected_value=-9.50,
        max_drawdown=400, max_drawdown_pct=4.0,
        final_equity=9050, starting_equity=10000, total_return=-0.095,
    )
    result = ab_overfit_check(bad)
    assert result is not None
    assert "AB-OVERFIT-001" in result


def test_ab_overfit_clean_strategy():
    from src.metrics import Metrics
    good = Metrics(
        strategy="test", n_trades=100, n_wins=55, n_losses=45,
        win_rate=0.55, avg_gain=120.0, avg_loss=80.0,
        profit_factor=1.65, expected_value=30.0,
        max_drawdown=200, max_drawdown_pct=2.0,
        final_equity=13000, starting_equity=10000, total_return=0.30,
    )
    result = ab_overfit_check(good)
    assert result is None


def test_verdict_types():
    for r in run_all(seed=42):
        v = r.metrics.verdict()
        assert v in ("EDGE_DETECTED", "MARGINAL_EDGE", "BREAKEVEN", "NEGATIVE_EV"), \
            f"Unknown verdict: {v}"


def test_eru_coverage_range():
    """ERU coverage must be 0–100% (or above if over-evidenced)."""
    for r in run_all(seed=42):
        eru = metrics_to_eru(r.metrics)
        if eru:
            assert eru.coverage_pct() >= 0
