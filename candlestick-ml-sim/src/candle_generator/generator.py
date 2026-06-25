"""
Synthetic OHLCV candlestick generator.

Generates realistic-feeling price series using:
  - Geometric Brownian Motion (GBM) for the price path
  - Regime switching (trending / mean-reverting / volatile)
  - Volume correlated to ATR expansion
  - Optional dividend-style gap events

No randomness in output unless seed is provided.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class CandleBar:
    ts:     str
    open:   float
    high:   float
    low:    float
    close:  float
    volume: float


def generate(
    n_bars:     int   = 200,
    symbol:     str   = "SIM",
    start_price:float = 4500.0,
    drift:      float = 0.0002,   # per-bar drift (positive = bullish)
    volatility: float = 0.012,    # per-bar sigma
    seed:       Optional[int] = 42,
    regime_change_prob: float = 0.03,
    avg_volume: float = 10_000.0,
) -> list[CandleBar]:
    """
    Generate n_bars of synthetic OHLCV data.

    regime_change_prob: probability each bar triggers a regime flip
      Regimes: TREND_UP, TREND_DOWN, VOLATILE, SIDEWAYS
    """
    rng = np.random.default_rng(seed)

    REGIMES = {
        "TREND_UP":    (0.0004, 0.008),
        "TREND_DOWN":  (-0.0004, 0.008),
        "VOLATILE":    (0.0, 0.025),
        "SIDEWAYS":    (0.0, 0.005),
    }
    regime_list = list(REGIMES.keys())
    regime = "TREND_UP"

    price = start_price
    bars = []

    from datetime import datetime, timedelta, timezone
    base_ts = datetime(2025, 1, 1, 9, 30, 0, tzinfo=timezone.utc)

    for i in range(n_bars):
        # Regime switch
        if rng.random() < regime_change_prob:
            regime = rng.choice(regime_list)

        r_drift, r_vol = REGIMES[regime]
        effective_drift = drift + r_drift
        effective_vol   = volatility + r_vol

        # Bar returns (4 intra-bar samples → OHLC)
        returns = rng.normal(effective_drift, effective_vol, 4)
        prices  = price * np.cumprod(1 + returns)

        bar_open  = price
        bar_close = prices[-1]
        bar_high  = max(price, prices.max()) * (1 + abs(rng.normal(0, 0.002)))
        bar_low   = min(price, prices.min()) * (1 - abs(rng.normal(0, 0.002)))
        bar_high  = max(bar_high, bar_open, bar_close)
        bar_low   = min(bar_low,  bar_open, bar_close)

        # Volume: higher when ATR is expanding (volatile regime)
        true_range = bar_high - bar_low
        vol_mult   = 1.0 + (true_range / (price * effective_vol)) * 0.5
        bar_volume = avg_volume * vol_mult * abs(rng.normal(1.0, 0.3))

        ts_str = (base_ts + timedelta(minutes=5 * i)).isoformat()

        bars.append(CandleBar(
            ts=ts_str,
            open=round(bar_open, 2),
            high=round(bar_high, 2),
            low=round(bar_low, 2),
            close=round(bar_close, 2),
            volume=round(bar_volume, 0),
        ))
        price = bar_close

    return bars


def bars_to_arrays(bars: list[CandleBar]) -> dict:
    """Convert list of CandleBar → numpy arrays for vectorized feature computation."""
    return {
        "ts":     [b.ts for b in bars],
        "open":   np.array([b.open   for b in bars]),
        "high":   np.array([b.high   for b in bars]),
        "low":    np.array([b.low    for b in bars]),
        "close":  np.array([b.close  for b in bars]),
        "volume": np.array([b.volume for b in bars]),
    }
