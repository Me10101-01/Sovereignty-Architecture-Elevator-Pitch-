"""
SAGCO Trade Simulator — Core Engine

Runs N fake trades per strategy, returns Metrics.
No real money. No real orders. A playground where ideas are tested
without consequences — that's exactly what this is.
"""

from __future__ import annotations
from dataclasses import dataclass
from .metrics import Trade, Metrics, compute_metrics
from .strategies import dividend_capture, renko_trend, renko_mean_reversion


@dataclass
class SimResult:
    strategy:  str
    trades:    list[Trade]
    metrics:   Metrics


def run_strategy(
    name:           str,
    n_trades:       int   = 100,
    capital:        float = 10_000.0,
    risk_per_trade: float = 0.01,
    seed:           int   = 42,
) -> SimResult:
    runners = {
        "dividend":  dividend_capture.run,
        "trend":     renko_trend.run,
        "reversion": renko_mean_reversion.run,
    }
    runner = runners.get(name)
    if runner is None:
        raise ValueError(f"Unknown strategy: {name!r}. Choose: {list(runners)}")

    trades  = runner(n_trades=n_trades, capital=capital,
                     risk_per_trade=risk_per_trade, seed=seed)
    metrics = compute_metrics(name, trades, starting_equity=capital)
    return SimResult(strategy=name, trades=trades, metrics=metrics)


def run_all(
    n_trades:       int   = 100,
    capital:        float = 10_000.0,
    risk_per_trade: float = 0.01,
    seed:           int   = 42,
) -> list[SimResult]:
    return [
        run_strategy("dividend",  n_trades, capital, risk_per_trade, seed),
        run_strategy("trend",     n_trades, capital, risk_per_trade, seed),
        run_strategy("reversion", n_trades, capital, risk_per_trade, seed),
    ]
