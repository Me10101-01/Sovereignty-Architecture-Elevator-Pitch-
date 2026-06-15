"""
Trade metrics: the only numbers that actually matter.

Win Rate, Average Gain, Average Loss, Profit Factor,
Max Drawdown, Expected Value, Final Equity.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import NamedTuple


@dataclass
class Trade:
    index:    int
    strategy: str
    won:      bool
    pnl:      float      # dollar P&L on this trade
    pct:      float      # % return on capital risked


@dataclass
class Metrics:
    strategy:       str
    n_trades:       int
    n_wins:         int
    n_losses:       int
    win_rate:       float    # 0.0 – 1.0
    avg_gain:       float    # avg $ on winning trades
    avg_loss:       float    # avg $ on losing trades (positive number)
    profit_factor:  float    # sum(gains) / sum(losses)
    expected_value: float    # $ per trade
    max_drawdown:   float    # largest peak-to-trough drop ($)
    max_drawdown_pct: float  # same as % of peak equity
    final_equity:   float
    starting_equity: float
    total_return:   float    # (final - start) / start

    @property
    def loss_rate(self) -> float:
        return 1.0 - self.win_rate

    def verdict(self) -> str:
        if self.expected_value > 0 and self.profit_factor > 1.2:
            return "EDGE_DETECTED"
        if self.expected_value > 0:
            return "MARGINAL_EDGE"
        if self.expected_value > -10:
            return "BREAKEVEN"
        return "NEGATIVE_EV"

    def summary_line(self) -> str:
        pf = f"{self.profit_factor:.2f}" if self.profit_factor < 999 else "∞"
        return (
            f"{self.strategy:<26} "
            f"WR={self.win_rate*100:.1f}%  "
            f"EV=${self.expected_value:+.2f}  "
            f"PF={pf}  "
            f"MDD={self.max_drawdown_pct:.1f}%  "
            f"→ {self.verdict()}"
        )


def compute_metrics(
    strategy: str,
    trades:   list[Trade],
    starting_equity: float = 10_000.0,
) -> Metrics:
    n = len(trades)
    if n == 0:
        return Metrics(strategy, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, starting_equity, starting_equity, 0)

    wins   = [t for t in trades if t.won]
    losses = [t for t in trades if not t.won]

    win_rate = len(wins) / n
    avg_gain = sum(t.pnl for t in wins) / len(wins) if wins else 0.0
    avg_loss = abs(sum(t.pnl for t in losses) / len(losses)) if losses else 0.0

    total_gain = sum(t.pnl for t in wins)
    total_loss = abs(sum(t.pnl for t in losses))
    pf = total_gain / total_loss if total_loss > 0 else float("inf")

    ev = (win_rate * avg_gain) - ((1 - win_rate) * avg_loss)

    # equity curve + max drawdown
    equity = starting_equity
    peak   = starting_equity
    max_dd = 0.0
    for t in trades:
        equity += t.pnl
        if equity > peak:
            peak = equity
        dd = peak - equity
        if dd > max_dd:
            max_dd = dd

    max_dd_pct = (max_dd / peak * 100) if peak > 0 else 0.0
    total_return = (equity - starting_equity) / starting_equity

    return Metrics(
        strategy        = strategy,
        n_trades        = n,
        n_wins          = len(wins),
        n_losses        = len(losses),
        win_rate        = win_rate,
        avg_gain        = avg_gain,
        avg_loss        = avg_loss,
        profit_factor   = pf,
        expected_value  = ev,
        max_drawdown    = max_dd,
        max_drawdown_pct = max_dd_pct,
        final_equity    = equity,
        starting_equity = starting_equity,
        total_return    = total_return,
    )
