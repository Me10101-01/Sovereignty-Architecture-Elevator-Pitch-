# Risk Disclaimer

Futures trading contains substantial risk and is not for every investor.

This codebase (`sagco-ninjascript-engine`) is an engineering tool. It does not constitute financial advice. Past performance is not indicative of future results.

## SAGCO risk controls

The following controls are enforced by `risk_engine.cs` before every order:

| Control | Default | Antibody if breached |
|---|---|---|
| Max daily loss | $500 | AB-DAILY-LOSS-LIMIT |
| Max position size | 1 lot | AB-POSITION-TOO-LARGE |
| Max single trade loss | $150 | AB-SINGLE-TRADE-LOSS |
| Min BurnRate to trade | 50% | AB-BURNRATE-TOO-LOW |

These are starting defaults. They must be reviewed before live trading.

## Before going live

1. Run all strategies in sim mode for minimum 30 sessions
2. BurnRate must be ≥ 70% on sim before switching to live
3. `ML-NINJA-002` must be COMPUTED (live account open, Articles of Organization uploaded)
4. `sagco ninja debug` smoke test must pass on live connection

## NinjaTrader clearing disclosures

View NinjaTrader Clearing, LLC FCM Disclosures at ninjatrader.com.

Strategickhaos DAO LLC (EIN 39-2900295) — trading for entity account only.
