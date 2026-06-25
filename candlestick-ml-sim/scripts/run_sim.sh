#!/usr/bin/env bash
# run_sim.sh — Launch the candlestick ML simulator
#
# Usage:
#   ./scripts/run_sim.sh              # interactive dashboard
#   ./scripts/run_sim.sh --headless   # run one pass, print report to stdout
#   ./scripts/run_sim.sh --test       # run test suite

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

MODE="${1:---dashboard}"

case "$MODE" in
    --test)
        python -m pytest tests/ -v
        ;;
    --headless)
        python - <<'EOF'
import sys
sys.path.insert(0, ".")
from src.candle_generator.generator import generate, bars_to_arrays
from src.feature_engine.features import compute_all
from src.renko_bridge.renko import build_renko, renko_context_per_bar, renko_summary
from src.ml_probability.scorer import score_all, burn_rate

bars   = generate(n_bars=200, seed=42)
arrays = bars_to_arrays(bars)
feats  = compute_all(open_=arrays["open"], high=arrays["high"],
                      low=arrays["low"],  close=arrays["close"],
                      volume=arrays["volume"])
bricks = build_renko(arrays["close"], feats.atr, 1.0)
dirs, streaks = renko_context_per_bar(200, bricks)
scores = score_all(
    open_=arrays["open"], close=arrays["close"],
    trend_scores=feats.trend_score, momentum_scores=feats.momentum_score,
    rel_volume=feats.rel_volume, is_engulfing=feats.is_engulfing,
    is_hammer=feats.is_hammer, is_doji=feats.is_doji,
    is_shooting_star=feats.is_shooting_star,
    renko_dirs=dirs, renko_streaks=streaks,
)

br = burn_rate(scores)
renko_s = renko_summary(bricks)
counts = {v:0 for v in ("PROVEN","PROMISING","UNPROVEN","INFLATED")}
for s in scores: counts[s.verdict] += 1

print(f"\n  SAGCO Candlestick ML Sim — Headless Report")
print(f"  Bars analyzed : 200")
print(f"  BurnRate      : {br:.1%}")
print(f"  Verdicts      : {counts}")
print(f"  Renko bricks  : {renko_s}")
antibodies = [a for s in scores for a in s.antibodies]
if antibodies:
    print(f"  Antibodies    : {list(set(antibodies))}")
EOF
        ;;
    --dashboard|*)
        python -m src.visualizer.dashboard
        ;;
esac
