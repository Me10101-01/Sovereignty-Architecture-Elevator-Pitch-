"""
Data loader — CSV OHLCV or synthetic fallback.

Accepts:
  - CSV with columns: ts,open,high,low,close,volume
  - Yahoo Finance format (auto-detected)
  - Falls back to generator.generate() if no file provided
"""

import csv
import os
from pathlib import Path
from typing import Optional

from src.candle_generator.generator import CandleBar, generate


_YAHOO_COLS = {"Date", "Open", "High", "Low", "Close", "Volume"}
_SAGCO_COLS = {"ts", "open", "high", "low", "close", "volume"}


def _detect_format(header: list[str]) -> str:
    cols = set(c.strip() for c in header)
    if cols >= _YAHOO_COLS:
        return "yahoo"
    if cols >= _SAGCO_COLS:
        return "sagco"
    return "unknown"


def load_csv(path: str) -> list[CandleBar]:
    """Load OHLCV from CSV file."""
    bars = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fmt = _detect_format(list(reader.fieldnames or []))
        if fmt == "unknown":
            raise ValueError(
                f"Unrecognized CSV format. Expected columns: {_SAGCO_COLS} or {_YAHOO_COLS}"
            )
        for row in reader:
            if fmt == "yahoo":
                bars.append(CandleBar(
                    ts=row["Date"],
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row.get("Volume", 0)),
                ))
            else:
                bars.append(CandleBar(
                    ts=row["ts"],
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume", 0)),
                ))
    return bars


def load(
    csv_path: Optional[str] = None,
    n_bars:   int = 200,
    symbol:   str = "SIM",
    seed:     int = 42,
    drift:    float = 0.0002,
    volatility: float = 0.012,
) -> list[CandleBar]:
    """
    Load bars from CSV if path provided and file exists,
    otherwise generate synthetic data.
    """
    if csv_path and os.path.exists(csv_path):
        bars = load_csv(csv_path)
        if len(bars) > n_bars:
            bars = bars[-n_bars:]
        return bars

    return generate(
        n_bars=n_bars,
        symbol=symbol,
        seed=seed,
        drift=drift,
        volatility=volatility,
    )


def save_csv(bars: list[CandleBar], path: str) -> None:
    """Save bars to SAGCO-format CSV."""
    os.makedirs(Path(path).parent, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ts", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for b in bars:
            writer.writerow({
                "ts": b.ts, "open": b.open, "high": b.high,
                "low": b.low, "close": b.close, "volume": b.volume,
            })
