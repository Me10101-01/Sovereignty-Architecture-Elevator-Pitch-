# SAGCO-TRADER ENGINE
## Headless Renko Simulator | SAGCO OS Native | Zero Dependencies

Part of the SAGCO OS citizen ecosystem.
Role: `sagco-trader` — simulation before execution. Evidence before live.

---

## Architecture

```
/sagco-trader-engine
  /core              → memory pools, scheduler, entry point
  /renko_dojo        → Ranko brick generator (tick → brick)
  /execution         → strategy simulator + order book
  /nt_bridge         → NinjaTrader replay file reader
  /risk              → hard risk limits (cannot be bypassed)
  /telemetry         → headless console stream
  /evidence          → immutable session log + verdict engine
  /tests             → unit + throughput tests
```

---

## Language: SAGCO (.sagco)

FlameLang syntax. Key conventions:
```sagco
struct Tick {
    price:     i64   // fixed-point * 100
    volume:    i64
    timestamp: i64   // nanoseconds
}

buf price_ticks: Tick[1048576]  // fixed stack array
ptr tick_head: *Tick            // raw pointer

fn build_brick(last_close: i64, tick_price: i64) -> Brick? { ... }
```

---

## Configuration

```sagco
const TICK_SIZE   = 25    // NQ minimum tick (0.25 points × 100)
const BRICK_TICKS = 8     // bricks form every 8 ticks
const BRICK_SIZE  = 200   // = TICK_SIZE × BRICK_TICKS

const LIVE_TRADING = false  // HARD LOCK — never true until evidence passes
```

---

## Speed Targets

| Phase | Target | Batch Size |
|-------|--------|------------|
| Phase 1 | 1,000,000 ticks/sec | 1,000 ticks |
| Phase 2 | 10,000,000 ticks/sec | 10,000 ticks |

---

## Evidence Gates (must pass before any live consideration)

- Minimum 100 simulated trades
- Win rate ≥ 52.00%
- Max drawdown ≤ 20% of net P&L
- Profit factor ≥ 1.50
- All risk limits remain intact throughout

---

## Build

```bash
ninja                          # Phase 1 binary
ninja bin/sagco-trader-phase2  # Phase 2 binary
ninja test_ranko               # Run unit tests
ninja test_phase1              # Throughput assertion
```

---

## Core Rule

> Raw ticks → Fixed Renko bricks → Simulated order book → Evidence log
> 
> SAGCO-TRADER masters simulation before execution.
> The trader is a citizen of SAGCO, not its own empire.

---

*Strategickhaos DAO LLC | SAGCO OS Ecosystem*
*LIVE_TRADING = false*
