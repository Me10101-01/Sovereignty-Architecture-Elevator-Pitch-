"""
Renko Mean Reversion — Difficulty: 7/10

Buy after 3+ consecutive red bricks (oversold).
Sell after 3+ consecutive green bricks (overbought), or at target.

Works in range-bound markets. Destroyed by strong trends
(price keeps going against you — no mean to revert to).

Key risk: AB-OVERFIT-001 fires here most often.
Mean reversion strategies look beautiful in backtests
on historical range-bound periods. Real markets trend.

Model:
  regime:              ranging (45%) | trending (55%)
  reversion_strength:  how hard price snaps back
  trend_override:      when trending, reversion entries get caught on wrong side
"""

from __future__ import annotations
import math
import random
from ..metrics import Trade


def _box_muller(rng: random.Random, mean: float = 0.0, std: float = 1.0) -> float:
    u1 = max(rng.random(), 1e-10)
    u2 = rng.random()
    z  = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mean + std * z


def run(
    n_trades:       int   = 100,
    capital:        float = 10_000.0,
    risk_per_trade: float = 0.01,
    seed:           int   = 42,
) -> list[Trade]:
    rng = random.Random(seed)
    trades: list[Trade] = []
    current_capital = capital

    # Market is ranging only 45% of the time — this hurts mean reversion
    ranging_probability = 0.45

    for i in range(n_trades):
        risk_dollars = current_capital * risk_per_trade

        is_ranging = rng.random() < ranging_probability

        if is_ranging:
            # Good conditions: price snaps back after 3-brick extension
            reversion_bricks = rng.randint(2, 4)
            against_bricks   = rng.randint(1, 2)
            noise = _box_muller(rng, 0.002, 0.006)
        else:
            # Trending: we entered on a reversion that never came
            # Price continues against us — momentum trumps reversion
            reversion_bricks = rng.randint(0, 2)
            against_bricks   = rng.randint(2, 7)   # trend keeps going
            noise = _box_muller(rng, -0.005, 0.012)

        brick_size = 0.005
        gain_pct   = reversion_bricks * brick_size + noise
        loss_pct   = against_bricks   * brick_size

        # Stop is typically 1.5× brick run that triggered entry
        stop_pct = 3 * brick_size * 1.5
        won      = gain_pct > 0 and gain_pct > (loss_pct * 0.5)

        pnl = risk_dollars * (gain_pct / stop_pct) if won else -risk_dollars

        trade = Trade(
            index    = i,
            strategy = "renko_mean_reversion",
            won      = won,
            pnl      = round(pnl, 2),
            pct      = round((gain_pct if won else -loss_pct) * 100, 3),
        )
        trades.append(trade)
        current_capital += trade.pnl

    return trades
