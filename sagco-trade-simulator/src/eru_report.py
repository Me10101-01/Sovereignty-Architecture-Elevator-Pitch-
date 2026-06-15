"""
ERU Report wrapper for trade simulation results.

Converts simulation Metrics into ERU assessments.
AB-OVERFIT-001 fires here when a strategy looks good but EV is negative.
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'sagco-true'))

from .metrics import Metrics

try:
    from sagco_true.eru.eru import ERU, VERDICT_PROVEN, VERDICT_PROMISING, VERDICT_UNPROVEN, VERDICT_INFLATED
    _ERU_AVAILABLE = True
except ImportError:
    _ERU_AVAILABLE = False


def metrics_to_eru(m: Metrics) -> "ERU | None":
    if not _ERU_AVAILABLE:
        return None

    claim = f"{m.strategy} is a profitable strategy"

    expected = [
        "positive expected value (EV > 0)",
        "profit factor > 1.2",
        "win rate consistent with risk/reward",
        "max drawdown < 20%",
        "consistent results across market conditions",
    ]

    actual = []
    if m.expected_value > 0:
        actual.append("positive expected value (EV > 0)")
    if m.profit_factor > 1.2:
        actual.append("profit factor > 1.2")
    if m.win_rate > 0.4 and m.avg_gain > m.avg_loss * 0.8:
        actual.append("win rate consistent with risk/reward")
    if m.max_drawdown_pct < 20:
        actual.append("max drawdown < 20%")

    notes = (
        f"WR={m.win_rate*100:.1f}% | "
        f"EV=${m.expected_value:+.2f} | "
        f"PF={m.profit_factor:.2f} | "
        f"MDD={m.max_drawdown_pct:.1f}% | "
        f"Return={m.total_return*100:+.1f}%"
    )

    return ERU(claim=claim, expected=expected, actual=actual, notes=notes)


def ab_overfit_check(m: Metrics) -> str | None:
    """
    AB-OVERFIT-001: fires when win rate looks high but EV is negative.
    A strategy can be 60% accurate and still lose money if risk is bad.
    """
    if m.win_rate > 0.55 and m.expected_value < 0:
        return (
            f"AB-OVERFIT-001 TRIGGERED on {m.strategy}: "
            f"win_rate={m.win_rate*100:.1f}% looks good "
            f"but EV=${m.expected_value:.2f} is negative. "
            f"avg_gain=${m.avg_gain:.2f} vs avg_loss=${m.avg_loss:.2f} — "
            f"losses eat the wins. Fix risk/reward, not win rate."
        )
    if m.profit_factor < 0.8 and m.total_return < -0.10:
        return (
            f"AB-OVERFIT-001 TRIGGERED on {m.strategy}: "
            f"PF={m.profit_factor:.2f}, return={m.total_return*100:.1f}%. "
            f"Strategy is destroying capital."
        )
    return None


def full_report(results: list) -> str:
    lines = []
    lines.append("")
    lines.append("  ╔══════════════════════════════════════════════════════════╗")
    lines.append("  ║         SAGCO Trade Simulator — ERU Report               ║")
    lines.append("  ╚══════════════════════════════════════════════════════════╝")
    lines.append("")
    lines.append(f"  Trades per strategy: {results[0].metrics.n_trades}")
    lines.append(f"  Starting capital:    ${results[0].metrics.starting_equity:,.0f}")
    lines.append(f"  Risk per trade:      1% of equity")
    lines.append("")
    lines.append("  ── Strategy Scorecard ─────────────────────────────────────")
    lines.append("")

    strategy_labels = {
        "dividend":  "Dividend Capture (4/10)",
        "trend":     "Renko Trend Follow (6/10)",
        "reversion": "Renko Mean Reversion (7/10)",
    }

    for r in results:
        m = r.metrics
        label = strategy_labels.get(m.strategy, m.strategy)
        lines.append(f"  {label}")
        lines.append(f"    Trades:         {m.n_trades}  ({m.n_wins}W / {m.n_losses}L)")
        lines.append(f"    Win Rate:       {m.win_rate*100:.1f}%")
        lines.append(f"    Avg Gain:       ${m.avg_gain:.2f}")
        lines.append(f"    Avg Loss:       ${m.avg_loss:.2f}")
        lines.append(f"    Profit Factor:  {m.profit_factor:.2f}")
        lines.append(f"    Expected Value: ${m.expected_value:+.2f} per trade")
        lines.append(f"    Max Drawdown:   ${m.max_drawdown:.2f}  ({m.max_drawdown_pct:.1f}%)")
        lines.append(f"    Final Equity:   ${m.final_equity:,.2f}  ({m.total_return*100:+.1f}%)")
        lines.append(f"    Verdict:        {m.verdict()}")

        ab = ab_overfit_check(m)
        if ab:
            lines.append(f"    🔴 {ab}")

        lines.append("")

    lines.append("  ── ERU Assessment ─────────────────────────────────────────")
    lines.append("")
    for r in results:
        eru = metrics_to_eru(r.metrics)
        if eru:
            lines.append(eru.report())

    lines.append("")
    lines.append("  ── Antibodies ─────────────────────────────────────────────")
    lines.append("")
    lines.append("  AB-OVERFIT-001:")
    lines.append("    trigger: high win rate + negative EV")
    lines.append("    cause:   losses eat the wins when avg_loss >> avg_gain")
    lines.append("    remedy:  fix risk/reward ratio, not win rate")
    lines.append("")
    lines.append("  AB-SCREENSHOT-CONFIG-001:")
    lines.append("    trigger: building node configs from screenshots")
    lines.append("    remedy:  verify with systeminfo | dxdiag | Get-ComputerInfo | ollama list")
    lines.append("")
    lines.append("  ── Key Insight ────────────────────────────────────────────")
    lines.append("")
    lines.append("  A strategy can be 60% accurate and still lose money.")
    lines.append("  Expected Value = (win_rate × avg_gain) - (loss_rate × avg_loss)")
    lines.append("  Risk management > win rate. Always.")
    lines.append("")
    lines.append("  This is a simulator. No real money. No real orders.")
    lines.append("  A playground where ideas are tested without consequences.")
    lines.append("  ────────────────────────────────────────────────────────────")
    return "\n".join(lines)
