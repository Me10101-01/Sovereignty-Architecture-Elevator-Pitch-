# sagco-ninjascript-engine

**BRICK-019 — NinjaScript Debug + TraceOrders + Volume Engine**

SAGCO ERU running inside NinjaTrader 8. Every bar: `V = Close / SMA(baseline)`. TraceOrders always on. SHA-256 sealed receipts. Risk gate before every order.

## Commands

```
sagco ninja debug   — TraceOrders + Print smoke test
sagco ninja trace   — dump decision_trace from last N bars
sagco ninja volume  — bid/ask delta pulse
sagco ninja risk    — check positions against risk-limits.json
sagco ninja seal    — SHA-256 seal reports/SHA256SUMS.txt
```

## Deploy

```powershell
.\scripts\build.ps1
```

Then in NinjaTrader 8: `Tools → NinjaScript Editor → Compile All`

## Missing Links

| ID | Gap | Status |
|---|---|---|
| ML-NINJA-001 | sagco-audit bridge not wired | UNCOMPUTED |
| ML-NINJA-002 | Live account not open | UNCOMPUTED |
| ML-NINJA-003 | Real futures feed not in ERU | UNCOMPUTED |

## Risk

See `docs/risk-disclaimer.md`. Min BurnRate 50% to trade. $500 daily loss limit.
