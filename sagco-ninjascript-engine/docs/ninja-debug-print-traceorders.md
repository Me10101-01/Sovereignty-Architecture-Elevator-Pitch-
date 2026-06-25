# NinjaScript Debug: Print() + TraceOrders

## The smoke test

Before any strategy goes live, run this check. Both must pass.

### TraceOrders = true

Every SAGCO strategy has this in `OnStateChange → State.SetDefaults`:

```csharp
TraceOrders = true;
```

This is non-negotiable. TraceOrders logs every order state transition to the NinjaTrader Output window. Without it, order behavior is a black box.

### SagcoPrintTrace.SmokeTest()

Call from `State.DataLoaded`:

```csharp
Sagco.Debug.SagcoTraceOrders.SmokeTest(Name);
```

Expected output in NT Output window:

```
[      COMPUTED] 2026-06-25T...  [SMOKE_TEST]  TraceOrders ACTIVE on strategy=SagcoStrategyCore
```

If you don't see this line, TraceOrders is not wired and the strategy must not run.

## Print() routing

Never call NinjaTrader's raw `Print()`. Always use:

```csharp
Sagco.Debug.SagcoPrintTrace.Print("COMPONENT", "message", "COMPUTED");
Sagco.Debug.SagcoPrintTrace.ERU("CLAIM-001", expected, actual, "trading");
Sagco.Debug.SagcoPrintTrace.Antibody("AB-ID", "trigger description");
```

All calls write to:
- NinjaTrader Output window
- `~/SAGCO/logs/ninjascript_print.log` (feeds sagco-audit on next Python run)

## Reading the output

```
[      COMPUTED] 2026-06-25T17:23:05Z  [ERU]  claim=BAR-100 expected=4500.25 actual=4512.50 V=1.002722 verdict=PROVEN domain=trading
[FAILED_COMPUTE] 2026-06-25T17:24:01Z  [ANTIBODY]  [AB-BURNRATE-DRIFT] FIRED — BurnRate=42% after 80 bars
```

Columns: `[verdict]  timestamp  [component]  message`

## sagco ninja debug command

```powershell
sagco ninja debug
```

Runs a sim account smoke test: loads `SagcoStrategyCore` on replay data, verifies `TraceOrders` fires, checks `ninjascript_print.log` for `SMOKE_TEST` entry, reports PROVEN/FAILED_COMPUTE.
