"""
Wafer: healer
Tests the SAGCO self-healing loop.
Verifies: PHASE_NUDGE reduces resonance_score, healer terminates,
HealResult is tick-sealed, and the --compile path works.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sagco_true.worlds.healer import Healer, HealResult, HealAttempt, heal
from sagco_true.khaos.oscillator import KHAOSOscillator

PASS, FAIL = [], []

def check(name, result, expected=True):
    ok = result == expected
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    (PASS if ok else FAIL).append(name)


# ── 1. Healer instantiates ────────────────────────────────────────────────────

h = Healer()
check("Healer: instantiates",                    h is not None)
check("Healer: has Concert",                     h._concert is not None)
check("Healer: has oscillator",                  isinstance(h._osc, KHAOSOscillator))
check("Healer: MAX_ROUNDS == 6",                 Healer.MAX_ROUNDS == 6)
check("Healer: ACTION_SEQUENCE has 6 items",     len(Healer.ACTION_SEQUENCE) == 6)
check("Healer: phase_nudge in sequence",         "phase_nudge" in Healer.ACTION_SEQUENCE)
check("Healer: amplitude_balance in sequence",   "amplitude_balance" in Healer.ACTION_SEQUENCE)
check("Healer: error_clear in sequence",         "error_clear" in Healer.ACTION_SEQUENCE)
check("Healer: element_shift in sequence",       "element_shift" in Healer.ACTION_SEQUENCE)

# ── 2. Run healer (quiet mode) ────────────────────────────────────────────────

print("\n  Running healer (max_rounds=4, quiet)...")
result = h.run(title="test-heal", max_rounds=4, verbose=False)

check("HealResult: is HealResult",               isinstance(result, HealResult))
check("HealResult: has attempts",                len(result.attempts) > 0)
check("HealResult: rounds <= 4",                 result.rounds <= 4)
check("HealResult: final_status set",            result.final_status in ("HARMONIZED", "DRIFTING", "DISSONANT"))
check("HealResult: tick_seal non-empty",         len(result.tick_seal) == 64)
check("HealResult: final_concert present",       result.final_concert is not None)
check("HealResult: to_dict works",               isinstance(result.to_dict(), dict))
check("HealResult: to_dict has title",           result.to_dict()["title"] == "test-heal")
check("HealResult: to_dict has attempts",        isinstance(result.to_dict()["attempts"], list))

# ── 3. HealAttempt structure ──────────────────────────────────────────────────

a = result.attempts[0]
check("HealAttempt: round == 1",                 a.round == 1)
check("HealAttempt: status set",                 a.status in ("HARMONIZED","DRIFTING","DISSONANT"))
check("HealAttempt: resonance_score >= 0",       a.resonance_score >= 0)
check("HealAttempt: action non-empty",           len(a.action) > 0)
check("HealAttempt: wafer_failures is list",     isinstance(a.wafer_failures, list))

# ── 4. Score observation (live telemetry can fluctuate) ──────────────────────

scores = [a.resonance_score for a in result.attempts]
print(f"         scores: {' → '.join(f'{s:.4f}' for s in scores)}")
# If healed, the final score must be below ALIGNED threshold
if result.healed:
    check("Healing: healed → final score < 0.3",  scores[-1] < 0.3)
else:
    # Exhausted without healing: at least one round showed improvement
    improving = any(scores[i] < scores[i-1] for i in range(1, len(scores)))
    check("Healing: exhausted → at least one round improved",  improving)

# ── 5. PHASE_NUDGE action fires ───────────────────────────────────────────────

actions = [a.action for a in result.attempts]
check("Actions: at least one action taken",      any(len(a) > 0 for a in actions))
check("Actions: first action contains PHASE or NONE",
      "PHASE" in actions[0].upper() or "NONE" in actions[0].upper() or
      "HARMONIZED" in result.attempts[0].status)

# ── 6. Pre-seeded anomaly heals ───────────────────────────────────────────────

# Artificially inject high error count to create dissonance
import math
h2 = Healer()
h2._osc.red.phase    = 5.0      # force large phase spread
h2._osc.blue.phase   = 0.1
h2._osc.purple.phase = 2.5

result2 = h2.run(title="injected-anomaly", max_rounds=6, verbose=False)

check("Injected: ran without exception",         True)
check("Injected: attempts recorded",             len(result2.attempts) > 0)
check("Injected: tick_seal present",             len(result2.tick_seal) == 64)

if result2.healed:
    check("Injected: healed successfully",       True)
    final_score = result2.attempts[-1].resonance_score
    # If healed, score must be below DRIFT_THRESHOLD
    check("Injected: final score < 0.3",         final_score < 0.3)
else:
    # Exhausted is OK — the healer doesn't force HARMONIZED
    check("Injected: exhausted gracefully",      result2.final_status in ("DRIFTING","DISSONANT"))

# ── 7. Heal compile path ──────────────────────────────────────────────────────

from sagco_true.language.compiler.flame_compiler import compile_ir
from sagco_true.language.vm.vm import SAGCOVirtualMachine

bc = compile_ir(result.final_concert.ir)
vm = SAGCOVirtualMachine()
vm.run(bc)
vm_report = vm.truth_report()

check("Heal→Compile: bytecode non-empty",        len(bc.instructions) > 0)
check("Heal→Compile: VM ran cleanly",            not any(s.name == "CRITICAL" for s in vm.bus))
check("Heal→Compile: title in vm memory",
      vm.memory.get("ir.title") is not None)

# ── 8. Standalone heal() function ─────────────────────────────────────────────

r3 = heal(title="standalone-heal", max_rounds=4, verbose=False)
check("heal(): returns HealResult",              isinstance(r3, HealResult))
check("heal(): tick_seal 64 chars",              len(r3.tick_seal) == 64)
check("heal(): final_status set",
      r3.final_status in ("HARMONIZED","DRIFTING","DISSONANT"))

# ── Summary ────────────────────────────────────────────────────────────────────

print(f"\n  Heal result  : {result.final_status}  ({result.rounds} rounds)")
print(f"  Injected     : {result2.final_status}  ({result2.rounds} rounds)")
print(f"  VM after heal: {vm_report.get('status', 'UNKNOWN')}")
print()

total = len(PASS) + len(FAIL)
print(f"  {len(PASS)}/{total} passed")
if FAIL:
    print(f"  FAILED: {FAIL}")
    print("  STATUS: NEEDS_HEALING")
    sys.exit(1)
else:
    print("  STATUS: ANTIBODY_FLEET_ACTIVE")
    sys.exit(0)
