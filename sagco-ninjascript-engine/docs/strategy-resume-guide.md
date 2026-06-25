# Strategy Resume Guide

## The problem

When NinjaTrader restarts or a strategy re-enables, `OnStateChange → State.DataLoaded` fires fresh. ERU counters reset. BurnRate starts at 0. The organism forgets what it learned.

## The SAGCO solution

`SagcoResumeStateStrategy` persists ERU state to `~/SAGCO/state/resume_state.json`:

```json
{
  "EruProven": 47,
  "EruTotal": 63,
  "BurnRate": 0.746,
  "LastVerdict": "PROVEN",
  "LastSaveTime": "2026-06-25T17:00:00Z"
}
```

On `State.DataLoaded`, it loads this file and resumes from the prior BurnRate.

## NinjaTrader position resume

For order state persistence (re-entering a prior position), enable in strategy settings:

```
Strategy → Properties → "Restore prior position on enable" = true
```

This tells NinjaTrader to treat the strategy as if it never stopped. Combined with SAGCO state resume, the full organism state is continuous.

## Auto-save cadence

State saves every 50 bars and on `State.Terminated`. Change the interval:

```csharp
if (CurrentBar % 50 == 0) SaveState(verdict);
```

## State file location

```
~/SAGCO/state/resume_state.json
```

Back this up. It's the organism's memory between sessions.
