"""
Candlestick + Renko ML Simulator — Main Dashboard

Layout (matplotlib):
  ┌─────────────────────────────────────────────────┐
  │  TOP: Candlestick chart  |  Renko bricks         │
  │       + probability overlay                      │
  ├─────────────────────────────────────────────────┤
  │  MIDDLE: Probability histogram + ERU gauge       │
  ├─────────────────────────────────────────────────┤
  │  BOTTOM: Potentiometer sliders                   │
  └─────────────────────────────────────────────────┘

Controls: sliders for SMA period, ATR period, weights, brick size, etc.
Mode toggle: CANDLE | RENKO | HYBRID

Run: python -m src.visualizer.dashboard
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # fallback-safe; use 'Agg' for headless
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

from src.candle_generator.generator import generate, bars_to_arrays
from src.feature_engine.features import compute_all, FeatureParams
from src.renko_bridge.renko import build_renko, renko_context_per_bar, renko_summary
from src.ml_probability.scorer import score_all, ScorerParams, burn_rate, BarScore


# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
C_BG       = "#0d1117"
C_PANEL    = "#161b22"
C_GREEN    = "#00e676"
C_RED      = "#ff5252"
C_YELLOW   = "#ffd740"
C_BLUE     = "#40c4ff"
C_GRAY     = "#8b949e"
C_WHITE    = "#e6edf3"
C_PROVEN   = "#00e676"
C_PROMISING= "#ffd740"
C_UNPROVEN = "#ff9800"
C_INFLATED = "#ff5252"

VERDICT_COLORS = {
    "PROVEN":    C_PROVEN,
    "PROMISING": C_PROMISING,
    "UNPROVEN":  C_UNPROVEN,
    "INFLATED":  C_INFLATED,
}


def verdict_color(v: str) -> str:
    return VERDICT_COLORS.get(v, C_GRAY)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class SimState:
    def __init__(self):
        self.n_bars     = 200
        self.symbol     = "SIM"
        self.seed       = 42
        self.mode       = "HYBRID"   # CANDLE | RENKO | HYBRID

        self.feat_params   = FeatureParams(atr_period=14, sma_period=20, vol_lookback=20)
        self.score_params  = ScorerParams()
        self.atr_mult      = 1.0

        self.bars    = None
        self.arrays  = None
        self.feats   = None
        self.bricks  = None
        self.scores  = None

        self.regenerate()

    def regenerate(self):
        self.bars   = generate(n_bars=self.n_bars, symbol=self.symbol, seed=self.seed)
        self.arrays = bars_to_arrays(self.bars)
        self.recompute()

    def recompute(self):
        a = self.arrays
        self.feats = compute_all(
            open_=a["open"], high=a["high"], low=a["low"],
            close=a["close"], volume=a["volume"],
            params=self.feat_params,
        )
        self.bricks = build_renko(a["close"], self.feats.atr, self.atr_mult)
        renko_dirs, renko_streaks = renko_context_per_bar(self.n_bars, self.bricks)
        self.scores = score_all(
            open_=a["open"], close=a["close"],
            trend_scores=self.feats.trend_score,
            momentum_scores=self.feats.momentum_score,
            rel_volume=self.feats.rel_volume,
            is_engulfing=self.feats.is_engulfing,
            is_hammer=self.feats.is_hammer,
            is_doji=self.feats.is_doji,
            is_shooting_star=self.feats.is_shooting_star,
            renko_dirs=renko_dirs,
            renko_streaks=renko_streaks,
            params=self.score_params,
        )

    def br(self) -> float:
        return burn_rate(self.scores) if self.scores else 0.0


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_candles(ax, arrays: dict, scores: list[BarScore], lookback: int = 100):
    ax.clear()
    ax.set_facecolor(C_BG)
    ax.tick_params(colors=C_GRAY, labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor(C_PANEL)

    n = len(arrays["open"])
    start = max(0, n - lookback)
    idxs  = list(range(start, n))
    if not idxs:
        return

    opens  = arrays["open"][start:n]
    closes = arrays["close"][start:n]
    highs  = arrays["high"][start:n]
    lows   = arrays["low"][start:n]
    s_slice = scores[start:n] if scores else []

    bar_w = 0.4

    for j, (o, c, h, l) in enumerate(zip(opens, closes, highs, lows)):
        bull = c >= o
        color = C_GREEN if bull else C_RED
        if j < len(s_slice):
            v = s_slice[j].verdict
            alpha = 0.9 if v in ("PROVEN", "PROMISING") else 0.4
        else:
            alpha = 0.6

        # Body
        body_h = abs(c - o) if abs(c - o) > 0 else 0.01
        rect = mpatches.FancyBboxPatch(
            (j - bar_w/2, min(o, c)), bar_w, body_h,
            boxstyle="square,pad=0",
            linewidth=0, facecolor=color, alpha=alpha
        )
        ax.add_patch(rect)
        # Wick
        ax.plot([j, j], [l, min(o, c)], color=color, lw=0.8, alpha=alpha)
        ax.plot([j, j], [max(o, c), h], color=color, lw=0.8, alpha=alpha)

    # Probability overlay (bottom of candle chart)
    if s_slice:
        probs = [s.probability for s in s_slice]
        prob_min = min(lows)
        prob_range = max(highs) - prob_min
        scaled = [prob_min + p * prob_range * 0.15 for p in probs]
        ax.plot(range(len(scaled)), scaled, color=C_BLUE, lw=1.0, alpha=0.7, label="P-score")

    ax.set_xlim(-1, len(idxs))
    ax.set_title("Candlestick  +  P-score overlay", color=C_WHITE, fontsize=8, pad=2)
    ax.legend(loc="upper left", fontsize=6, facecolor=C_PANEL, labelcolor=C_BLUE)


def draw_renko(ax, bricks, lookback: int = 80):
    ax.clear()
    ax.set_facecolor(C_BG)
    ax.tick_params(colors=C_GRAY, labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor(C_PANEL)

    if not bricks:
        ax.text(0.5, 0.5, "No Renko bricks yet", color=C_GRAY,
                ha="center", va="center", transform=ax.transAxes)
        ax.set_title("Renko Bricks", color=C_WHITE, fontsize=8, pad=2)
        return

    disp = bricks[-lookback:] if len(bricks) > lookback else bricks
    bar_w = 0.8

    prev_close = None
    for j, b in enumerate(disp):
        color = C_GREEN if b.direction == "UP" else C_RED
        body_h = abs(b.close - b.open)
        rect = mpatches.FancyBboxPatch(
            (j - bar_w/2, min(b.open, b.close)), bar_w, max(body_h, 0.01),
            boxstyle="square,pad=0",
            linewidth=0.5, edgecolor=C_BG, facecolor=color, alpha=0.85
        )
        ax.add_patch(rect)
        prev_close = b.close

    ax.autoscale_view()
    ax.set_title(f"Renko Bricks  ({len(bricks)} total)", color=C_WHITE, fontsize=8, pad=2)

    summary = renko_summary(bricks)
    ax.text(0.02, 0.97,
            f"▲{summary['up']}  ▼{summary['down']}  streak={summary['max_streak']}",
            color=C_GRAY, fontsize=6, va="top", transform=ax.transAxes)


def draw_probability_panel(ax, scores: list[BarScore], lookback: int = 100):
    ax.clear()
    ax.set_facecolor(C_BG)
    ax.tick_params(colors=C_GRAY, labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor(C_PANEL)

    n = len(scores)
    start = max(0, n - lookback)
    s_slice = scores[start:n]
    if not s_slice:
        return

    xs    = list(range(len(s_slice)))
    probs = [s.probability for s in s_slice]
    verts = [s.verdict for s in s_slice]
    dirs  = [s.direction for s in s_slice]

    # Background bands
    ax.axhspan(0.75, 1.0,  alpha=0.08, color=C_PROVEN)
    ax.axhspan(0.50, 0.75, alpha=0.06, color=C_PROMISING)
    ax.axhspan(0.01, 0.50, alpha=0.04, color=C_UNPROVEN)
    ax.axhspan(0.0,  0.01, alpha=0.08, color=C_INFLATED)

    # Threshold lines
    ax.axhline(0.75, color=C_PROVEN,   lw=0.5, ls="--", alpha=0.4)
    ax.axhline(0.50, color=C_PROMISING,lw=0.5, ls="--", alpha=0.4)

    # Bars colored by verdict
    bar_colors = [verdict_color(v) for v in verts]
    ax.bar(xs, probs, color=bar_colors, alpha=0.7, width=0.9)
    ax.plot(xs, probs, color=C_WHITE, lw=0.5, alpha=0.3)

    ax.set_ylim(0, 1.05)
    ax.set_xlim(-1, len(xs))
    ax.set_ylabel("Probability", color=C_GRAY, fontsize=7)
    ax.set_title("ERU Probability  (per bar)", color=C_WHITE, fontsize=8, pad=2)

    br = burn_rate(s_slice)
    ax.text(0.98, 0.97, f"BurnRate {br:.1%}", color=C_WHITE,
            fontsize=8, fontweight="bold", ha="right", va="top",
            transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=C_PANEL, edgecolor=C_GRAY, alpha=0.8))


def draw_eru_gauge(ax, scores: list[BarScore]):
    ax.clear()
    ax.set_facecolor(C_BG)
    ax.set_aspect("equal")
    ax.axis("off")

    if not scores:
        return

    br = burn_rate(scores)
    counts = {v: 0 for v in ("PROVEN", "PROMISING", "UNPROVEN", "INFLATED")}
    for s in scores:
        counts[s.verdict] += 1

    # Donut chart
    sizes  = [counts[k] for k in ("PROVEN", "PROMISING", "UNPROVEN", "INFLATED")]
    colors = [C_PROVEN, C_PROMISING, C_UNPROVEN, C_INFLATED]
    wedges, _ = ax.pie(
        sizes, colors=colors, startangle=90,
        wedgeprops=dict(width=0.4, edgecolor=C_BG, linewidth=2),
        counterclock=False,
    )
    ax.text(0, 0, f"{br:.0%}\nBURN", color=C_WHITE, fontsize=11,
            fontweight="bold", ha="center", va="center")

    # Legend
    labels = list(counts.keys())
    for i, (label, color) in enumerate(zip(labels, colors)):
        ax.text(1.15, 0.6 - i * 0.35, f"{label}: {counts[label]}",
                color=color, fontsize=6.5, transform=ax.transAxes)
    ax.set_title("ERU Distribution", color=C_WHITE, fontsize=8, pad=2)


# ---------------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------------

def run_dashboard():
    state = SimState()

    fig = plt.figure(figsize=(16, 11), facecolor=C_BG)
    fig.suptitle("SAGCO Candlestick + Renko ML Simulator",
                 color=C_WHITE, fontsize=11, fontweight="bold", y=0.99)

    gs = GridSpec(
        4, 3,
        figure=fig,
        height_ratios=[3.5, 2, 1.2, 1.0],
        hspace=0.42, wspace=0.35,
        left=0.05, right=0.97, top=0.96, bottom=0.03,
    )

    ax_candle  = fig.add_subplot(gs[0, :2])
    ax_renko   = fig.add_subplot(gs[0, 2])
    ax_prob    = fig.add_subplot(gs[1, :2])
    ax_gauge   = fig.add_subplot(gs[1, 2])
    ax_sliders = fig.add_subplot(gs[2:, :])
    ax_sliders.axis("off")

    # --- Sliders (potentiometers) ---
    slider_ax_defs = [
        # (left, bottom, width, height, label, min, max, valinit, step)
        (0.07, 0.14, 0.18, 0.025, "SMA Period",    5,   100, 20,  1),
        (0.07, 0.10, 0.18, 0.025, "ATR Period",    5,   50,  14,  1),
        (0.07, 0.06, 0.18, 0.025, "Brick ATR×",    0.25, 4.0, 1.0, 0.25),

        (0.34, 0.14, 0.18, 0.025, "Trend Wt",      0.0, 1.0, 0.40, 0.05),
        (0.34, 0.10, 0.18, 0.025, "Volume Wt",     0.0, 1.0, 0.30, 0.05),
        (0.34, 0.06, 0.18, 0.025, "Pattern Wt",    0.0, 1.0, 0.30, 0.05),

        (0.61, 0.14, 0.18, 0.025, "PROVEN Thresh", 0.5, 0.99, 0.75, 0.01),
        (0.61, 0.10, 0.18, 0.025, "Vol Spike ×",   1.0, 4.0, 1.5,  0.1),
        (0.61, 0.06, 0.18, 0.025, "Lookback Bars", 20,  500, 100,  10),
    ]

    sliders = {}
    for l, b, w, h, label, mn, mx, vi, step in slider_ax_defs:
        ax_s = fig.add_axes([l, b, w, h], facecolor=C_PANEL)
        sl = Slider(ax_s, label, mn, mx, valinit=vi, valstep=step,
                    color=C_BLUE, initcolor=C_BLUE)
        sl.label.set_color(C_WHITE)
        sl.label.set_size(7)
        sl.valtext.set_color(C_YELLOW)
        sl.valtext.set_size(7)
        sliders[label] = sl

    # Mode radio
    ax_radio = fig.add_axes([0.84, 0.06, 0.09, 0.10], facecolor=C_PANEL)
    radio = RadioButtons(ax_radio, ("HYBRID", "CANDLE", "RENKO"),
                         activecolor=C_BLUE)
    for lbl in ax_radio.texts:
        lbl.set_color(C_WHITE)
        lbl.set_fontsize(7)
    ax_radio.set_title("Mode", color=C_WHITE, fontsize=7)

    # Regen button
    ax_btn = fig.add_axes([0.84, 0.17, 0.09, 0.03], facecolor=C_PANEL)
    btn_regen = Button(ax_btn, "New Data", color=C_PANEL, hovercolor=C_BLUE)
    btn_regen.label.set_color(C_WHITE)
    btn_regen.label.set_fontsize(7)

    def full_redraw():
        lookback = int(sliders["Lookback Bars"].val)
        draw_candles(ax_candle, state.arrays, state.scores, lookback)
        draw_renko(ax_renko, state.bricks, lookback)
        draw_probability_panel(ax_prob, state.scores, lookback)
        draw_eru_gauge(ax_gauge, state.scores)
        fig.canvas.draw_idle()

    def on_slider_change(val):
        state.feat_params.sma_period   = int(sliders["SMA Period"].val)
        state.feat_params.atr_period   = int(sliders["ATR Period"].val)
        state.atr_mult                 = sliders["Brick ATR×"].val
        state.score_params.weight_trend   = sliders["Trend Wt"].val
        state.score_params.weight_volume  = sliders["Volume Wt"].val
        state.score_params.weight_pattern = sliders["Pattern Wt"].val
        state.score_params.proven_threshold  = sliders["PROVEN Thresh"].val
        state.score_params.vol_spike_mult    = sliders["Vol Spike ×"].val
        state.recompute()
        full_redraw()

    def on_mode_change(label):
        state.mode = label
        full_redraw()

    def on_regen(event):
        state.seed += 1
        state.regenerate()
        full_redraw()

    for sl in sliders.values():
        sl.on_changed(on_slider_change)
    radio.on_clicked(on_mode_change)
    btn_regen.on_clicked(on_regen)

    full_redraw()
    plt.show()


if __name__ == "__main__":
    run_dashboard()
