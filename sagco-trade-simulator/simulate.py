#!/usr/bin/env python3
"""
SAGCO Trade Simulator

Usage:
  python simulate.py                        — run all 3 strategies, 100 trades each
  python simulate.py --strategy dividend    — one strategy only
  python simulate.py --n 500               — 500 trades
  python simulate.py --seed 99             — different random seed
  python simulate.py --capital 50000       — different starting capital
  python simulate.py --json                — JSON output
  python simulate.py --trades              — show individual trade log
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.simulator import run_all, run_strategy
from src.eru_report import full_report, ab_overfit_check


def main() -> None:
    p = argparse.ArgumentParser(description="SAGCO Trade Simulator")
    p.add_argument("--strategy", choices=["dividend", "trend", "reversion", "all"],
                   default="all")
    p.add_argument("--n",        type=int,   default=100,    help="Number of trades")
    p.add_argument("--seed",     type=int,   default=42,     help="Random seed")
    p.add_argument("--capital",  type=float, default=10_000, help="Starting capital ($)")
    p.add_argument("--risk",     type=float, default=0.01,   help="Risk per trade (fraction)")
    p.add_argument("--json",     action="store_true",        help="JSON output")
    p.add_argument("--trades",   action="store_true",        help="Show trade log")
    args = p.parse_args()

    if args.strategy == "all":
        results = run_all(
            n_trades=args.n, capital=args.capital,
            risk_per_trade=args.risk, seed=args.seed
        )
    else:
        results = [run_strategy(
            args.strategy, n_trades=args.n, capital=args.capital,
            risk_per_trade=args.risk, seed=args.seed
        )]

    if args.json:
        out = []
        for r in results:
            m = r.metrics
            out.append({
                "strategy":      m.strategy,
                "n_trades":      m.n_trades,
                "n_wins":        m.n_wins,
                "n_losses":      m.n_losses,
                "win_rate":      round(m.win_rate, 4),
                "avg_gain":      round(m.avg_gain, 2),
                "avg_loss":      round(m.avg_loss, 2),
                "profit_factor": round(m.profit_factor, 3),
                "expected_value": round(m.expected_value, 2),
                "max_drawdown":   round(m.max_drawdown, 2),
                "max_drawdown_pct": round(m.max_drawdown_pct, 2),
                "final_equity":  round(m.final_equity, 2),
                "total_return":  round(m.total_return, 4),
                "verdict":       m.verdict(),
                "ab_overfit":    ab_overfit_check(m),
            })
        print(json.dumps(out, indent=2))
        return

    if args.trades:
        for r in results:
            print(f"\n  {r.strategy} — trade log")
            for t in r.trades:
                icon = "✓" if t.won else "✗"
                print(f"    [{icon}] #{t.index:>3}  pnl={t.pnl:+8.2f}  pct={t.pct:+.3f}%")

    print(full_report(results))


if __name__ == "__main__":
    main()
