# SAGCO-OS — Evidence-Driven Engineering Runtime

```
case_study: SAGCO-OS-001
classification: portable engineering evidence system
devices: iPad, Z Fold, iSH, Termux
status: OPERATIONAL
```

---

## Architecture

```
SAGCO-OS
│
├── Runtime Layer
│   ├── sagco-race        — device event ticker
│   ├── sagco-ledger      — unified evidence ledger
│   ├── sagco-master      — pipeline orchestrator
│   └── sagco-mansion     — 10-floor unified build
│
├── Evidence Layer
│   ├── sagco-attribution — who did what, on which device
│   ├── sagco-eru         — Expected vs Actual work units (global)
│   ├── sagco-eru-device  — ERU breakdown per device ← NEW
│   ├── sagco-variance    — adaptation% vs creation%
│   └── sagco-identity    — universal device identity ← NEW
│
├── Intelligence Layer
│   ├── sagco-portfolio   — candlestick S/A/B/C portfolio rank
│   ├── sagco-state       — YAML system snapshot
│   └── sagco-cell        — IF-THEN-WHEN pattern matcher
│
├── Client Layer
│   ├── sagco-qr-audit    — QR/barcode security verification
│   ├── sagco-wafer       — engineering report refinery
│   └── sagco-nina        — Nina Trader Bot Refinery
│       ├── dry-run       — backtest + reports/
│       ├── dca           — Dollar Cost Average strategy
│       ├── momentum      — RSI buy/sell strategy
│       └── spy-mirror    — S&P 500 mirror strategy
│
└── Deployment Layer
    ├── sagco-pack-os     — tar.gz artifact packager
    ├── GitHub            — versioned evidence chain
    ├── Dropbox           — client file delivery
    └── Google Cloud      — SAGCO-OSComputConsciousness
```

---

## The Core Pattern

Every command in SAGCO-OS follows one invariant:

```
command
  ↓
artifact
  ↓
ledger entry
  ↓
report
  ↓
state snapshot
```

This makes every engineering action traceable to a device, timestamp, and output.

---

## Device Identity

Run once per device to eliminate `unknown` attribution permanently:

```sh
# Install sagco-identity to ~/bin
chmod +x sagco-identity.sh
cp sagco-identity.sh ~/bin/sagco-identity

# Detect and register
sagco-identity

# Make permanent
sagco-identity install

# Verify
sagco-identity show
```

Each device gets a persistent identity file at `~/.sagco_device`.

---

## Per-Device ERU

After running `sagco-identity` on each device, `sagco-eru-device` shows:

```
  ipad       total=4    creates=3    fixes=1    create_pct=75%  adapt_pct=25%  score=A
  zfold      total=1    creates=1    fixes=0    create_pct=100% adapt_pct=0%   score=C
  termux     total=5    creates=3    fixes=2    create_pct=60%  adapt_pct=40%  score=A
  ish        total=2    creates=1    fixes=1    create_pct=50%  adapt_pct=50%  score=B

  ── GLOBAL ──────────────────────────────────────────────────────
  ALL        total=12   creates=8    fixes=4    create_pct=67%  adapt_pct=33%
```

Phase interpretation:
- `create_pct > 60%` → construction phase (making new bricks)
- `adapt_pct > 60%` → integration phase (making bricks hold together)

---

## Client Case Study: Bell'Aroma Cafe

Cleanest client-facing deliverable:

**Input:** QR code URL  
**Output:**
```
Risk Level: NONE
Verified: TRUE
Fingerprint: sha256:abc123...
```

**Artifacts:**
- `Bell_Aroma_Uptown_audit_STAMP.md`
- `Bell_Aroma_Southside_audit_STAMP.md`

No explanation of SAGCO required. Business owner reads the report directly.

---

## Nina Trader Bot Refinery

**Status:** research/demo only  
**Purpose:** headless Rust backtesting + paper-trading simulator

**Risk gate:** live trading blocked until:
- 30+ days paper trading logs
- Max drawdown < 10%
- Sharpe ratio > 1.0
- Win rate > 50%

**Dry-run command:**
```sh
sagco-nina dry-run all
```

**Outputs:**
```
~/sagco_nina/reports/backtest.md
~/sagco_nina/reports/risk.md
~/sagco_nina/reports/ledger.csv
~/sagco_nina/reports/strategy_score.yaml
STATUS=SAGCO_NINA_DRYRUN_PASS
```

---

## The Polyglot Propagation Chain

The real bottleneck SAGCO-OS measures:

```
Human Idea
    ↓ iPad ideation
Claude / ChatGPT
    ↓ architecture synthesis
iSH / Termux
    ↓ compilation + execution
GitHub
    ↓ versioned provenance
SAGCO Ledger
    ↓ evidence + attribution
Reports
    ↓ client deliverable
```

Propagation time through this chain = the true engineering velocity metric.

---

```
STATUS=SAGCO_ARCHITECTURE_v1.0
commands: 28
devices: 4 (ipad, zfold, ish, termux)
attribution: 100%
portfolio_rank: S
```
