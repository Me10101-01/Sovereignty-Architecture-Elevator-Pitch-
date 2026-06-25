"""
Renko bridge — converts OHLCV arrays into Renko bricks.

Classic ATR-based Renko:
  brick_size = ATR[last_valid] × atr_multiplier
  New UP brick: close >= last_brick_top + brick_size
  New DOWN brick: close <= last_brick_bottom - brick_size
  Reversal: 2× brick_size in opposite direction

Returns a RenkoBrick list aligned with (but shorter than) the input bars.
Also computes brick_dir and streak at each original bar index.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class RenkoBrick:
    bar_index: int      # index in original OHLCV array when brick was confirmed
    open:      float
    close:     float
    direction: str      # "UP" or "DOWN"
    brick_num: int      # sequential brick number


def build_renko(
    close:          np.ndarray,
    atr:            np.ndarray,
    atr_multiplier: float = 1.0,
) -> list[RenkoBrick]:
    """
    Build Renko bricks from close prices.

    Uses ATR at the first non-NaN bar to set brick_size.
    Fixed brick size throughout the series (recalculate by calling again).
    """
    n = len(close)
    bricks: list[RenkoBrick] = []

    # Find first valid ATR
    brick_size = None
    for i in range(n):
        if not np.isnan(atr[i]) and atr[i] > 0:
            brick_size = atr[i] * atr_multiplier
            break

    if brick_size is None or brick_size <= 0:
        return bricks

    # Initialize from first close
    start_idx = 0
    while start_idx < n and np.isnan(close[start_idx]):
        start_idx += 1
    if start_idx >= n:
        return bricks

    anchor = close[start_idx]
    # Snap anchor to brick_size grid
    anchor = round(anchor / brick_size) * brick_size
    current_top    = anchor + brick_size
    current_bottom = anchor

    brick_num = 0
    for i in range(start_idx, n):
        c = close[i]
        # UP bricks
        while c >= current_top + brick_size:
            bricks.append(RenkoBrick(
                bar_index=i,
                open=current_top,
                close=current_top + brick_size,
                direction="UP",
                brick_num=brick_num,
            ))
            current_bottom = current_top
            current_top    = current_top + brick_size
            brick_num += 1
        if c >= current_top:
            bricks.append(RenkoBrick(
                bar_index=i,
                open=current_bottom,
                close=current_top,
                direction="UP",
                brick_num=brick_num,
            ))
            current_bottom = current_top
            current_top    = current_top + brick_size
            brick_num += 1
            continue

        # DOWN bricks
        while c <= current_bottom - brick_size:
            bricks.append(RenkoBrick(
                bar_index=i,
                open=current_bottom,
                close=current_bottom - brick_size,
                direction="DOWN",
                brick_num=brick_num,
            ))
            current_top    = current_bottom
            current_bottom = current_bottom - brick_size
            brick_num += 1
        if c <= current_bottom:
            bricks.append(RenkoBrick(
                bar_index=i,
                open=current_top,
                close=current_bottom,
                direction="DOWN",
                brick_num=brick_num,
            ))
            current_top    = current_bottom
            current_bottom = current_bottom - brick_size
            brick_num += 1

    return bricks


def renko_context_per_bar(
    n_bars:  int,
    bricks:  list[RenkoBrick],
) -> tuple[list[Optional[str]], list[int]]:
    """
    For each original bar index, return:
      brick_dir  : direction of most recent brick ("UP"/"DOWN"/None)
      streak     : consecutive bricks in that direction
    """
    brick_dir  = [None] * n_bars
    streak_arr = [0]    * n_bars

    if not bricks:
        return brick_dir, streak_arr

    # Walk bricks in order, fill bar positions
    b_iter = iter(bricks)
    cur_brick = next(b_iter, None)
    streak = 0
    last_dir = None
    b_ptr = 0  # current brick pointer

    for i in range(n_bars):
        # Advance bricks that land on or before bar i
        while b_ptr < len(bricks) and bricks[b_ptr].bar_index <= i:
            d = bricks[b_ptr].direction
            if d == last_dir:
                streak += 1
            else:
                streak = 1
                last_dir = d
            b_ptr += 1

        brick_dir[i]  = last_dir
        streak_arr[i] = streak if last_dir else 0

    return brick_dir, streak_arr


def renko_summary(bricks: list[RenkoBrick]) -> dict:
    if not bricks:
        return {"total": 0, "up": 0, "down": 0, "max_streak": 0, "last_dir": None}
    up   = sum(1 for b in bricks if b.direction == "UP")
    down = sum(1 for b in bricks if b.direction == "DOWN")
    streak = 1
    max_s  = 1
    for j in range(1, len(bricks)):
        if bricks[j].direction == bricks[j-1].direction:
            streak += 1
            max_s = max(max_s, streak)
        else:
            streak = 1
    return {
        "total": len(bricks),
        "up":    up,
        "down":  down,
        "max_streak": max_s,
        "last_dir":   bricks[-1].direction,
    }
