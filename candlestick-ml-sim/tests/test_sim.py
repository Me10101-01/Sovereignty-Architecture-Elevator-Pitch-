"""
candlestick-ml-sim test suite

Run: python -m pytest tests/ -v
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.candle_generator.generator import generate, bars_to_arrays
from src.feature_engine.features import (
    compute_atr, compute_all, body_ratio, relative_volume,
    trend_score, detect_doji, detect_hammer, FeatureParams,
)
from src.renko_bridge.renko import build_renko, renko_context_per_bar, renko_summary
from src.ml_probability.scorer import score_all, ScorerParams, burn_rate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_bars():
    return generate(n_bars=100, seed=42)

@pytest.fixture
def sample_arrays(sample_bars):
    return bars_to_arrays(sample_bars)


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class TestGenerator:
    def test_correct_length(self):
        bars = generate(n_bars=50, seed=1)
        assert len(bars) == 50

    def test_ohlcv_valid(self, sample_bars):
        for b in sample_bars:
            assert b.high >= b.open
            assert b.high >= b.close
            assert b.low  <= b.open
            assert b.low  <= b.close
            assert b.high >= b.low
            assert b.volume > 0

    def test_deterministic_with_seed(self):
        b1 = generate(n_bars=50, seed=99)
        b2 = generate(n_bars=50, seed=99)
        assert all(b1[i].close == b2[i].close for i in range(50))

    def test_different_seed_different_data(self):
        b1 = generate(n_bars=50, seed=1)
        b2 = generate(n_bars=50, seed=2)
        assert any(b1[i].close != b2[i].close for i in range(50))

    def test_bars_to_arrays_shapes(self, sample_arrays):
        for k in ("open", "high", "low", "close", "volume"):
            assert len(sample_arrays[k]) == 100


# ---------------------------------------------------------------------------
# Feature Engine
# ---------------------------------------------------------------------------

class TestFeatureEngine:
    def test_atr_shape(self, sample_arrays):
        atr = compute_atr(sample_arrays["high"], sample_arrays["low"], sample_arrays["close"], 14)
        assert len(atr) == 100

    def test_atr_nan_before_period(self, sample_arrays):
        atr = compute_atr(sample_arrays["high"], sample_arrays["low"], sample_arrays["close"], 14)
        assert np.isnan(atr[0])
        assert not np.isnan(atr[13])

    def test_atr_positive_after_warmup(self, sample_arrays):
        atr = compute_atr(sample_arrays["high"], sample_arrays["low"], sample_arrays["close"], 14)
        valid = atr[~np.isnan(atr)]
        assert np.all(valid > 0)

    def test_body_ratio_range(self, sample_arrays):
        br = body_ratio(sample_arrays["open"], sample_arrays["high"],
                        sample_arrays["low"], sample_arrays["close"])
        assert np.all((br >= 0) & (br <= 1))

    def test_rel_volume_positive(self, sample_arrays):
        rv = relative_volume(sample_arrays["volume"], 20)
        valid = rv[~np.isnan(rv)]
        assert np.all(valid > 0)

    def test_trend_score_range(self, sample_arrays):
        atr = compute_atr(sample_arrays["high"], sample_arrays["low"], sample_arrays["close"], 14)
        ts = trend_score(sample_arrays["close"], atr, 20)
        valid = ts[~np.isnan(ts)]
        assert np.all((valid >= 0) & (valid <= 1))

    def test_compute_all_returns_frame(self, sample_arrays):
        feats = compute_all(
            open_=sample_arrays["open"], high=sample_arrays["high"],
            low=sample_arrays["low"], close=sample_arrays["close"],
            volume=sample_arrays["volume"],
        )
        assert feats.atr is not None
        assert len(feats.body_ratio) == 100

    def test_doji_on_flat_bar(self):
        open_  = np.array([100.0, 100.0])
        close  = np.array([100.0, 100.0])
        high   = np.array([101.0, 101.0])
        low    = np.array([99.0,  99.0])
        result = detect_doji(open_, high, low, close)
        assert result[0] == True

    def test_hammer_detected(self):
        # Long lower wick, small body, tiny upper wick
        open_  = np.array([100.0])
        close  = np.array([100.5])
        high   = np.array([100.6])
        low    = np.array([97.0])
        result = detect_hammer(open_, high, low, close)
        assert result[0] == True


# ---------------------------------------------------------------------------
# Renko Bridge
# ---------------------------------------------------------------------------

class TestRenko:
    def test_bricks_nonempty(self, sample_arrays):
        feats = compute_all(
            open_=sample_arrays["open"], high=sample_arrays["high"],
            low=sample_arrays["low"], close=sample_arrays["close"],
            volume=sample_arrays["volume"],
        )
        bricks = build_renko(sample_arrays["close"], feats.atr, 1.0)
        assert len(bricks) > 0

    def test_bricks_direction_valid(self, sample_arrays):
        feats = compute_all(
            open_=sample_arrays["open"], high=sample_arrays["high"],
            low=sample_arrays["low"], close=sample_arrays["close"],
            volume=sample_arrays["volume"],
        )
        bricks = build_renko(sample_arrays["close"], feats.atr, 1.0)
        for b in bricks:
            assert b.direction in ("UP", "DOWN")

    def test_renko_context_length(self, sample_arrays):
        feats = compute_all(
            open_=sample_arrays["open"], high=sample_arrays["high"],
            low=sample_arrays["low"], close=sample_arrays["close"],
            volume=sample_arrays["volume"],
        )
        bricks = build_renko(sample_arrays["close"], feats.atr, 1.0)
        dirs, streaks = renko_context_per_bar(100, bricks)
        assert len(dirs)    == 100
        assert len(streaks) == 100

    def test_larger_brick_size_fewer_bricks(self, sample_arrays):
        feats = compute_all(
            open_=sample_arrays["open"], high=sample_arrays["high"],
            low=sample_arrays["low"], close=sample_arrays["close"],
            volume=sample_arrays["volume"],
        )
        bricks_small = build_renko(sample_arrays["close"], feats.atr, 0.5)
        bricks_large = build_renko(sample_arrays["close"], feats.atr, 3.0)
        assert len(bricks_small) > len(bricks_large)

    def test_renko_summary_keys(self, sample_arrays):
        feats = compute_all(
            open_=sample_arrays["open"], high=sample_arrays["high"],
            low=sample_arrays["low"], close=sample_arrays["close"],
            volume=sample_arrays["volume"],
        )
        bricks = build_renko(sample_arrays["close"], feats.atr, 1.0)
        s = renko_summary(bricks)
        assert "total" in s and "up" in s and "down" in s and "max_streak" in s


# ---------------------------------------------------------------------------
# Probability Scorer
# ---------------------------------------------------------------------------

class TestScorer:
    def _make_scores(self, n=50, seed=42):
        bars   = generate(n_bars=n, seed=seed)
        arrays = bars_to_arrays(bars)
        feats  = compute_all(
            open_=arrays["open"], high=arrays["high"],
            low=arrays["low"], close=arrays["close"],
            volume=arrays["volume"],
        )
        bricks = build_renko(arrays["close"], feats.atr, 1.0)
        dirs, streaks = renko_context_per_bar(n, bricks)
        return score_all(
            open_=arrays["open"], close=arrays["close"],
            trend_scores=feats.trend_score, momentum_scores=feats.momentum_score,
            rel_volume=feats.rel_volume, is_engulfing=feats.is_engulfing,
            is_hammer=feats.is_hammer, is_doji=feats.is_doji,
            is_shooting_star=feats.is_shooting_star,
            renko_dirs=dirs, renko_streaks=streaks,
        )

    def test_scores_correct_length(self):
        scores = self._make_scores(50)
        assert len(scores) == 50

    def test_probability_in_range(self):
        scores = self._make_scores(50)
        for s in scores:
            assert 0.0 <= s.probability <= 1.0

    def test_verdict_valid_values(self):
        scores = self._make_scores(50)
        valid = {"PROVEN", "PROMISING", "UNPROVEN", "INFLATED"}
        for s in scores:
            assert s.verdict in valid

    def test_direction_valid_values(self):
        scores = self._make_scores(50)
        valid = {"BULL", "BEAR", "NEUTRAL"}
        for s in scores:
            assert s.direction in valid

    def test_burn_rate_range(self):
        scores = self._make_scores(100)
        br = burn_rate(scores)
        assert 0.0 <= br <= 1.0

    def test_burn_rate_empty(self):
        assert burn_rate([]) == 0.0

    def test_components_present(self):
        scores = self._make_scores(20)
        for s in scores:
            assert "trend" in s.components
            assert "volume" in s.components
            assert "pattern" in s.components

    def test_weight_changes_probability(self):
        bars   = generate(n_bars=50, seed=42)
        arrays = bars_to_arrays(bars)
        feats  = compute_all(
            open_=arrays["open"], high=arrays["high"],
            low=arrays["low"], close=arrays["close"], volume=arrays["volume"],
        )
        bricks = build_renko(arrays["close"], feats.atr, 1.0)
        dirs, streaks = renko_context_per_bar(50, bricks)

        kwargs = dict(
            open_=arrays["open"], close=arrays["close"],
            trend_scores=feats.trend_score, momentum_scores=feats.momentum_score,
            rel_volume=feats.rel_volume, is_engulfing=feats.is_engulfing,
            is_hammer=feats.is_hammer, is_doji=feats.is_doji,
            is_shooting_star=feats.is_shooting_star,
            renko_dirs=dirs, renko_streaks=streaks,
        )

        p1 = ScorerParams(weight_trend=1.0, weight_volume=0.0, weight_pattern=0.0)
        p2 = ScorerParams(weight_trend=0.0, weight_volume=1.0, weight_pattern=0.0)
        scores1 = score_all(**kwargs, params=p1)
        scores2 = score_all(**kwargs, params=p2)
        probs1 = [s.probability for s in scores1]
        probs2 = [s.probability for s in scores2]
        assert probs1 != probs2  # weights actually change output
