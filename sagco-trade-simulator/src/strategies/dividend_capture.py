"""
Dividend Capture Strategy — Difficulty: 4/10

Buy before ex-dividend date, collect dividend, sell after.
The catch: stock often drops by approximately the dividend amount on ex-div day.
Dividend is not free money — it's priced into the drop.

Model parameters:
  dividend_yield:    0.005 – 0.02 (0.5–2% per trade)
  price_drop_factor: 0.5 – 1.2   (how much of dividend is baked into drop)
  holding_days:      2 – 5 days
  base_volatility:   1.5% daily   (additional noise around drop)
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
    risk_per_trade: float = 0.01,       # 1% of capital risked per trade
    seed:           int   = 42,
) -> list[Trade]:
    rng = random.Random(seed)
    trades: list[Trade] = []
    current_capital = capital

    for i in range(n_trades):
        risk_dollars = current_capital * risk_per_trade

        # Randomize trade parameters
        dividend_yield    = rng.uniform(0.005, 0.020)    # 0.5–2%
        price_drop_factor = rng.uniform(0.50, 1.20)      # how much stock drops vs dividend
        extra_noise_pct   = _box_muller(rng, 0.0, 0.015) # daily noise (1.5% std)

        net_pct = dividend_yield - (dividend_yield * price_drop_factor) + extra_noise_pct

        # Scale to dollar PnL based on risk (position sized to risk risk_dollars)
        # Position = risk_dollars / stop_loss_pct; we use 2% as implied stop
        position = risk_dollars / 0.02
        pnl = position * net_pct

        won = pnl > 0
        trade = Trade(
            index    = i,
            strategy = "dividend_capture",
            won      = won,
            pnl      = round(pnl, 2),
            pct      = round(net_pct * 100, 3),
        )
        trades.append(trade)
        current_capital += pnl

    return trades
