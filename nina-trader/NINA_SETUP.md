# Nina Trader Bot — SAGCO-OS Passive Income Engine

## What Nina Does

Three passive income strategies running on your own devices:

| Strategy | Logic | Risk |
|----------|-------|------|
| `dca` | Buy $10 of SPY/QQQ/VTI/AAPL/MSFT on every run | Very Low |
| `momentum` | Buy when RSI ≤ 35 (oversold), sell when RSI ≥ 65 | Low |
| `spy-mirror` | Mirror SPY yesterday's move → buy basket today if SPY was +0.5%+ | Low |

All strategies default to **paper trading** (Alpaca free account, no real money).

---

## Quick Setup (Termux/Android)

### 1. Get Alpaca Paper Trading API Keys (Free)
- Go to alpaca.markets → sign up free
- Dashboard → Paper Trading → API Keys → Generate
- Copy `API Key ID` and `Secret Key`

### 2. Set Environment Variables
```sh
export ALPACA_KEY="your_key_id_here"
export ALPACA_SECRET="your_secret_here"
export ALPACA_LIVE="false"        # paper trading — keep this false to start
export SAGCO_DEVICE="termux"
```

Add to `~/.bashrc` or `~/.zshrc` to persist.

### 3. Compile on Termux
```sh
cd ~/ninja-bot-forge/nina-trader
cargo build --release
cp target/release/nina-trader ~/bin/nina-trader
chmod +x ~/bin/nina-trader
```

### 4. Install SAGCO command
```sh
cp sagco-nina.sh ~/bin/sagco-nina
chmod +x ~/bin/sagco-nina
```

### 5. First Run (dry mode — no API calls)
```sh
sagco-nina status dry
sagco-nina dca dry
sagco-nina all dry
```

### 6. Paper trading (real API, fake money)
```sh
sagco-nina status paper
sagco-nina dca paper
```

---

## SAGCO-OS Integration

Every Nina trade is logged to SAGCO:
- `~/sagco_race/race_log.csv` — race ticks for each strategy run
- `~/sagco_ledger.csv` — ledger entries per run
- `~/sagco_nina/trade_log.csv` — full trade history (symbol, side, qty, price, P&L)

Run `sagco-state` after Nina runs to see Nina in your telemetry metrics.

---

## Automate with Cron (Termux)

```sh
# Daily DCA at 9:35am market open
35 9 * * 1-5 export ALPACA_KEY=xxx ALPACA_SECRET=xxx; ~/bin/nina-trader dca paper

# Momentum scan every morning
0 10 * * 1-5 export ALPACA_KEY=xxx ALPACA_SECRET=xxx; ~/bin/nina-trader momentum paper
```

---

## Go Live (Real Money — when ready)

Only flip `ALPACA_LIVE=true` after:
1. Paper trading for 30+ days
2. Consistent positive returns in paper mode
3. Starting capital: minimum $500 recommended for DCA
4. Never invest more than you can afford to lose

```sh
export ALPACA_LIVE="true"
sagco-nina all live
```

---

## SAGCO-OS Command Reference

```
sagco-nina status          # account balance
sagco-nina dca dry         # DCA dry run (no trades)
sagco-nina dca paper       # DCA on paper account
sagco-nina momentum dry    # RSI scan
sagco-nina spy-mirror dry  # SPY mirror
sagco-nina all dry         # all three strategies
sagco-nina portfolio       # current positions
sagco-nina history         # trade log
```
