"""
Probability scorer — rule-based ERU model.

No trained model required. Computes a probability score per bar using:
  - Trend score (price vs SMA)
  - Momentum score (ATR expansion)
  - Volume score (relative volume above spike threshold)
  - Pattern score (engulfing, hammer, shooting star)
  - Renko context (streak alignment bonus)

Outputs: probability [0,1], verdict (PROVEN/PROMISING/UNPROVEN/INFLATED),
         direction (BULL/BEAR/NEUTRAL), antibodies_fired list.

Weights are controlled by potentiometer params.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScorerParams:
    weight_trend:   float = 0.40
    weight_volume:  float = 0.30
    weight_pattern: float = 0.30
    vol_spike_mult: float = 1.5
    # ERU thresholds
    proven_threshold:    float = 0.75
    promising_threshold: float = 0.50
    # Renko streak bonus
    renko_streak_bonus: float = 0.05   # per brick in streak, capped at 0.15
    renko_streak_cap:   int   = 3
    renko_streak_antibody: int = 5


@dataclass
class BarScore:
    probability: float
    verdict:     str
    direction:   str   # BULL / BEAR / NEUTRAL
    components:  dict  # sub-scores for debugging
    antibodies:  list[str] = field(default_factory=list)


def classify_eru(p: float, params: ScorerParams) -> str:
    if p >= params.proven_threshold:
        return "PROVEN"
    if p >= params.promising_threshold:
        return "PROMISING"
    if p >= 0.01:
        return "UNPROVEN"
    return "INFLATED"


def score_bar(
    i:              int,
    open_:          np.ndarray,
    close:          np.ndarray,
    trend_score:    np.ndarray,
    momentum_score: np.ndarray,
    rel_volume:     np.ndarray,
    is_engulfing:   np.ndarray,
    is_hammer:      np.ndarray,
    is_doji:        np.ndarray,
    is_shooting_star: np.ndarray,
    renko_dir:      Optional[str],
    renko_streak:   int,
    params:         ScorerParams,
) -> BarScore:
    # --- Trend component ---
    t = trend_score[i]
    if np.isnan(t):
        trend_component = 0.5
    else:
        trend_component = float(t)

    # --- Volume component ---
    rv = rel_volume[i] if not np.isnan(rel_volume[i]) else 1.0
    vol_component = min(rv / (params.vol_spike_mult * 2.0), 1.0)

    # --- Pattern component ---
    pattern_component = 0.5   # neutral baseline
    antibodies = []

    if is_engulfing[i]:
        pattern_component = 0.8
    elif is_hammer[i]:
        pattern_component = 0.7
    elif is_shooting_star[i]:
        pattern_component = 0.3
    elif is_doji[i]:
        pattern_component = 0.5   # indecision

    # --- Direction ---
    bull = close[i] > open_[i]
    bear = close[i] < open_[i]

    # Flip pattern score for bear bars
    if bear and pattern_component > 0.5:
        pattern_component = 1.0 - pattern_component

    # --- Base probability ---
    w_t = params.weight_trend
    w_v = params.weight_volume
    w_p = params.weight_pattern
    total_w = w_t + w_v + w_p
    if total_w <= 0:
        total_w = 1.0

    prob = (w_t * trend_component + w_v * vol_component + w_p * pattern_component) / total_w

    # --- Renko context bonus ---
    if renko_dir is not None and renko_streak >= 2:
        bonus = min(params.renko_streak_bonus * renko_streak, params.renko_streak_bonus * params.renko_streak_cap)
        if (renko_dir == "UP" and bull) or (renko_dir == "DOWN" and bear):
            prob = min(1.0, prob + bonus)
        else:
            prob = max(0.0, prob - bonus * 0.5)

        # Antibody: inflated streak
        if renko_streak >= params.renko_streak_antibody:
            antibodies.append(f"AB-RENKO-INFLATED-STREAK (streak={renko_streak})")

    # Antibody: volume spike on doji
    if is_doji[i] and rv >= params.vol_spike_mult:
        antibodies.append("AB-VOLUME-SPIKE-ON-DOJI")

    # Direction
    if bull:
        direction = "BULL"
    elif bear:
        direction = "BEAR"
    else:
        direction = "NEUTRAL"

    # For BEAR direction, flip probability to represent bearish confidence
    if direction == "BEAR":
        prob = 1.0 - trend_component * w_t / total_w + (1.0 - vol_component) * w_v / total_w + (1.0 - pattern_component) * w_p / total_w
        prob = float(np.clip(prob, 0.0, 1.0))

    prob = float(np.clip(prob, 0.0, 1.0))
    verdict = classify_eru(prob, params)

    return BarScore(
        probability=round(prob, 4),
        verdict=verdict,
        direction=direction,
        components={
            "trend":   round(trend_component, 3),
            "volume":  round(vol_component, 3),
            "pattern": round(pattern_component, 3),
        },
        antibodies=antibodies,
    )


def score_all(
    open_:          np.ndarray,
    close:          np.ndarray,
    trend_scores:   np.ndarray,
    momentum_scores:np.ndarray,
    rel_volume:     np.ndarray,
    is_engulfing:   np.ndarray,
    is_hammer:      np.ndarray,
    is_doji:        np.ndarray,
    is_shooting_star: np.ndarray,
    renko_dirs:     list,
    renko_streaks:  list,
    params:         Optional[ScorerParams] = None,
) -> list[BarScore]:
    if params is None:
        params = ScorerParams()
    n = len(close)
    scores = []
    for i in range(n):
        s = score_bar(
            i=i,
            open_=open_, close=close,
            trend_score=trend_scores,
            momentum_score=momentum_scores,
            rel_volume=rel_volume,
            is_engulfing=is_engulfing,
            is_hammer=is_hammer,
            is_doji=is_doji,
            is_shooting_star=is_shooting_star,
            renko_dir=renko_dirs[i] if renko_dirs else None,
            renko_streak=renko_streaks[i] if renko_streaks else 0,
            params=params,
        )
        scores.append(s)
    return scores


def burn_rate(scores: list[BarScore]) -> float:
    """(PROVEN + PROMISING) / total"""
    if not scores:
        return 0.0
    good = sum(1 for s in scores if s.verdict in ("PROVEN", "PROMISING"))
    return round(good / len(scores), 4)
