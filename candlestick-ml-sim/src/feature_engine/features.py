"""
Feature engine — vectorized ATR, body/wick ratios, volume, patterns, trend.

All functions operate on numpy arrays and return arrays of same length.
First N values will be NaN where the lookback window isn't full yet.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FeatureParams:
    atr_period:    int   = 14
    sma_period:    int   = 20
    vol_lookback:  int   = 20
    vol_spike_mult:float = 1.5


@dataclass
class FeatureFrame:
    """All computed features for a bar series."""
    atr:           np.ndarray
    body_ratio:    np.ndarray
    upper_wick:    np.ndarray
    lower_wick:    np.ndarray
    rel_volume:    np.ndarray
    trend_score:   np.ndarray
    momentum_score:np.ndarray
    is_engulfing:  np.ndarray  # bool
    is_doji:       np.ndarray
    is_hammer:     np.ndarray
    is_shooting_star: np.ndarray


def compute_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
    n = len(high)
    tr = np.zeros(n)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))

    atr = np.full(n, np.nan)
    if n < period:
        return atr
    atr[period - 1] = np.mean(tr[:period])
    for i in range(period, n):
        atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
    return atr


def compute_sma(arr: np.ndarray, period: int) -> np.ndarray:
    sma = np.full(len(arr), np.nan)
    for i in range(period - 1, len(arr)):
        sma[i] = np.mean(arr[i - period + 1: i + 1])
    return sma


def body_ratio(open_: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    range_ = high - low
    body   = np.abs(close - open_)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(range_ > 0, body / range_, 0.0)
    return np.clip(ratio, 0.0, 1.0)


def upper_wick_ratio(open_: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    range_ = high - low
    top    = np.maximum(open_, close)
    upper  = high - top
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(range_ > 0, upper / range_, 0.0)
    return np.clip(ratio, 0.0, 1.0)


def lower_wick_ratio(open_: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    range_ = high - low
    bottom = np.minimum(open_, close)
    lower  = bottom - low
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(range_ > 0, lower / range_, 0.0)
    return np.clip(ratio, 0.0, 1.0)


def relative_volume(volume: np.ndarray, lookback: int = 20) -> np.ndarray:
    n = len(volume)
    rel = np.full(n, np.nan)
    for i in range(lookback - 1, n):
        mean = np.mean(volume[i - lookback + 1: i + 1])
        rel[i] = volume[i] / mean if mean > 0 else 1.0
    return rel


def trend_score(close: np.ndarray, atr: np.ndarray, sma_period: int = 20) -> np.ndarray:
    """
    Score 0–1: how strongly price is positioned ABOVE the SMA relative to ATR.
    0 = well below SMA, 0.5 = at SMA, 1 = well above.
    """
    sma = compute_sma(close, sma_period)
    with np.errstate(invalid="ignore"):
        dist = close - sma
        # Normalize by ATR: +1 ATR above = score ~0.83, -1 ATR below = ~0.17
        score = 0.5 + 0.5 * np.tanh(dist / np.where(np.isnan(atr) | (atr == 0), 1e-9, atr))
    score[np.isnan(sma)] = np.nan
    return score


def momentum_score(atr: np.ndarray, lookback: int = 5) -> np.ndarray:
    """
    Score 0–1: ATR expansion vs its recent average.
    >1 = expanding (momentum), <1 = contracting (consolidating).
    Normalized via tanh to [0,1].
    """
    n = len(atr)
    score = np.full(n, np.nan)
    for i in range(lookback, n):
        if np.isnan(atr[i]):
            continue
        window = atr[i - lookback: i]
        if np.all(np.isnan(window)):
            continue
        recent_mean = np.nanmean(window)
        if recent_mean > 0:
            ratio = atr[i] / recent_mean
            score[i] = float(np.clip(0.5 + 0.25 * (ratio - 1.0), 0.0, 1.0))
    return score


def detect_engulfing(open_: np.ndarray, close: np.ndarray) -> np.ndarray:
    """Bullish engulfing: current bar body engulfs prior bar body, closes higher."""
    n = len(open_)
    result = np.zeros(n, dtype=bool)
    for i in range(1, n):
        prev_bull = close[i-1] > open_[i-1]
        curr_bull = close[i]   > open_[i]
        if not prev_bull and curr_bull:
            if close[i] > open_[i-1] and open_[i] < close[i-1]:
                result[i] = True
    return result


def detect_doji(open_: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray,
                threshold: float = 0.1) -> np.ndarray:
    br = body_ratio(open_, high, low, close)
    return br < threshold


def detect_hammer(open_: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    """Lower wick > 2× body, small upper wick."""
    lw = lower_wick_ratio(open_, high, low, close)
    uw = upper_wick_ratio(open_, high, low, close)
    br = body_ratio(open_, high, low, close)
    return (lw >= 2 * br) & (uw <= 0.1) & (br > 0.05)


def detect_shooting_star(open_: np.ndarray, high: np.ndarray, low: np.ndarray,
                         close: np.ndarray) -> np.ndarray:
    """Upper wick > 2× body, small lower wick."""
    lw = lower_wick_ratio(open_, high, low, close)
    uw = upper_wick_ratio(open_, high, low, close)
    br = body_ratio(open_, high, low, close)
    return (uw >= 2 * br) & (lw <= 0.1) & (br > 0.05)


def compute_all(
    open_: np.ndarray,
    high:  np.ndarray,
    low:   np.ndarray,
    close: np.ndarray,
    volume:np.ndarray,
    params: Optional[FeatureParams] = None,
) -> FeatureFrame:
    if params is None:
        params = FeatureParams()

    atr = compute_atr(high, low, close, params.atr_period)

    return FeatureFrame(
        atr            = atr,
        body_ratio     = body_ratio(open_, high, low, close),
        upper_wick     = upper_wick_ratio(open_, high, low, close),
        lower_wick     = lower_wick_ratio(open_, high, low, close),
        rel_volume     = relative_volume(volume, params.vol_lookback),
        trend_score    = trend_score(close, atr, params.sma_period),
        momentum_score = momentum_score(atr),
        is_engulfing   = detect_engulfing(open_, close),
        is_doji        = detect_doji(open_, high, low, close),
        is_hammer      = detect_hammer(open_, high, low, close),
        is_shooting_star = detect_shooting_star(open_, high, low, close),
    )
