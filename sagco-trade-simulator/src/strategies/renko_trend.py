"""
Renko Trend Following — Difficulty: 6/10

Buy when brick color flips to green (trend confirmed).
Sell when brick flips to red.

Renko removes time — only price movement creates bricks.
Works well in trending markets. Fails in choppy/sideways conditions.

Model:
  brick_size:         0.5% of price
  trend_persistence:  probability next brick continues the trend
  choppy_probability: market is sideways (reduces win rate)
  regime:             trending (60%) | choppy (40%)
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

    # Market regime: 60% trending, 40% choppy
    trend_probability = 0.60

    for i in range(n_trades):
        risk_dollars = current_capital * risk_per_trade

        # Determine regime for this trade
        is_trending = rng.random() < trend_probability

        if is_trending:
            # Trending: trend continuation is likely (higher win rate)
            brick_run = rng.randint(2, 6)   # 2–6 bricks in our direction
            reversal  = rng.randint(1, 2)   # only 1–2 bricks against us on stop
            noise     = _box_muller(rng, 0.003, 0.008)   # positive drift
        else:
            # Choppy: mean reversion fights us
            brick_run = rng.randint(1, 3)
            reversal  = rng.randint(1, 4)
            noise     = _box_muller(rng, -0.002, 0.012)  # negative drift

        brick_size = 0.005   # 0.5% per brick
        gain_pct   = brick_run  * brick_size + noise
        loss_pct   = reversal   * brick_size * 0.8   # stop usually tighter

        # Risk-adjusted PnL
        position = risk_dollars / (loss_pct if loss_pct > 0 else 0.01)
        won      = gain_pct > loss_pct or (is_trending and rng.random() < 0.55)
        pnl      = position * gain_pct if won else -risk_dollars

        trade = Trade(
            index    = i,
            strategy = "renko_trend",
            won      = won,
            pnl      = round(pnl, 2),
            pct      = round((gain_pct if won else -loss_pct) * 100, 3),
        )
        trades.append(trade)
        current_capital += trade.pnl

    return trades
