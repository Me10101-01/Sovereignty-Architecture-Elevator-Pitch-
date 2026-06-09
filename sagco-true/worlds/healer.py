"""
SAGCO Self-Healing Loop — Antibody Fleet

The organism detects dissonance and heals itself.

Position in organism lifecycle:
  CONCERT → [DISSONANT/DRIFTING] → HEALER → tune oscillator → CONCERT again → HARMONIZED

Healing protocol:
  Round 1: measure resonance_score and phase variance across RED/BLUE/PURPLE
  Round 2: apply targeted tuning based on which channel is farthest from mean
    - PHASE_NUDGE    → move channels toward mean phase (reduces resonance_score)
    - AMPLITUDE_BALANCE → equalize channel amplitudes if one is dominating
    - ERROR_CLEAR    → reset RED phase if err_count-driven anomaly
    - ELEMENT_SHIFT  → swap element to adjacent frequency on drifting channel
  Round N: re-run Concert, compare resonance_score to previous round
  If resonance_score is not decreasing → EXHAUSTED (organism needs external intervention)

The healer never forces HARMONIZED — it only nudges and observes.
Truth is measured, not declared.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from typing import Optional

from .concert import Concert, ConcertResult
from ..khaos.oscillator import KHAOSOscillator


# ── Healing records ───────────────────────────────────────────────────────────

@dataclass
class HealAttempt:
    round:           int
    status:          str        # HARMONIZED | DRIFTING | DISSONANT
    resonance_score: float
    phase_red:       float
    phase_blue:      float
    phase_purple:    float
    phase_variance:  float      # std_dev of phase differences = resonance_score
    action:          str        # action taken before next round
    delta_score:     float      # resonance_score change from previous round (negative = improving)
    wafer_failures:  list[str]  # wafer names that failed this round


@dataclass
class HealResult:
    title:         str
    attempts:      list[HealAttempt]
    final_status:  str          # terminal status
    healed:        bool         # True if final_status == HARMONIZED
    rounds:        int
    tick_seal:     str
    final_concert: ConcertResult

    def to_dict(self) -> dict:
        return {
            "title":        self.title,
            "healed":       self.healed,
            "final_status": self.final_status,
            "rounds":       self.rounds,
            "tick_seal":    self.tick_seal[:16] + "...",
            "attempts": [
                {
                    "round":           a.round,
                    "status":          a.status,
                    "resonance_score": round(a.resonance_score, 6),
                    "action":          a.action,
                    "delta_score":     round(a.delta_score, 6),
                    "wafer_failures":  a.wafer_failures,
                }
                for a in self.attempts
            ],
        }


# ── Diagnosis helpers ─────────────────────────────────────────────────────────

def _diagnose(result: ConcertResult) -> list[str]:
    """Return list of issues found in the Concert result."""
    issues = []
    c = result.coherence

    if c.status == "ANOMALY":
        issues.append("ANOMALY: resonance_score above 0.8 — severe phase incoherence")
    elif c.status == "DRIFTING":
        issues.append("DRIFTING: resonance_score above 0.3 — moderate phase variance")

    # Find which channel is farthest from mean phase
    phases = [c.phase_red, c.phase_blue, c.phase_purple]
    mean_phase = sum(phases) / 3
    deviations = [(abs(p - mean_phase), name)
                  for p, name in zip(phases, ["RED", "BLUE", "PURPLE"])]
    worst_dev, worst_channel = max(deviations)
    if worst_dev > 0.3:
        issues.append(f"PHASE_DRIFT: channel {worst_channel} is {worst_dev:.3f} rad from mean")

    # Check wafer failures (look in ir graph catalyst nodes)
    for node in result.ir.graph.nodes:
        if node.kind.value == "catalyst" and not node.meta.get("passed", True):
            issues.append(f"WAFER_FAIL: {node.id}")

    return issues


def _worst_channel(c) -> str:
    """Return name of channel with largest phase deviation from mean."""
    phases = [c.phase_red, c.phase_blue, c.phase_purple]
    mean_p = sum(phases) / 3
    devs = [(abs(p - mean_p), name) for p, name in zip(phases, ["RED", "BLUE", "PURPLE"])]
    return max(devs)[1]


# ── Tuning actions ────────────────────────────────────────────────────────────

def _phase_nudge(osc: KHAOSOscillator, c) -> str:
    """
    Move all channels toward their mean phase by a step.
    The nudge fraction shrinks each round (gradient descent on phase space).
    """
    phases = [c.phase_red, c.phase_blue, c.phase_purple]
    mean_p = sum(phases) / 3
    step = 0.15   # 15% of deviation corrected per round

    osc.red.phase    += (mean_p - c.phase_red)    * step
    osc.blue.phase   += (mean_p - c.phase_blue)   * step
    osc.purple.phase += (mean_p - c.phase_purple) * step

    # Keep phases in [0, 2π]
    tau = 2 * math.pi
    osc.red.phase    = osc.red.phase    % tau
    osc.blue.phase   = osc.blue.phase   % tau
    osc.purple.phase = osc.purple.phase % tau

    return f"PHASE_NUDGE → mean={mean_p:.3f}rad, stepped 15% toward alignment"


def _amplitude_balance(osc: KHAOSOscillator) -> str:
    """Equalize amplitudes — extreme amplitude difference causes frequency beats."""
    amps = [osc.red.amplitude, osc.blue.amplitude, osc.purple.amplitude]
    mean_amp = sum(amps) / 3
    osc.red.amplitude    = (osc.red.amplitude    + mean_amp) / 2
    osc.blue.amplitude   = (osc.blue.amplitude   + mean_amp) / 2
    osc.purple.amplitude = (osc.purple.amplitude + mean_amp) / 2
    return f"AMPLITUDE_BALANCE → equalized toward mean={mean_amp:.3f}"


def _error_clear(osc: KHAOSOscillator) -> str:
    """Clear error-encoded phase shift on RED — resets anomaly-trigger."""
    old = osc.red.phase
    osc.red.phase = 0.0
    return f"ERROR_CLEAR → RED.phase {old:.3f}→0.0 (error accumulation cleared)"


def _element_shift(osc: KHAOSOscillator, worst: str) -> str:
    """
    Shift the drifting channel to the next element in its brainwave band.
    This re-tunes the carrier frequency to a nearby KHAOS element.
    """
    from sagco_true.khaos.elements import BY_CHANNEL, BY_ID
    channel_map = {"RED": "RED", "BLUE": "BLUE", "PURPLE": "PURPLE"}
    band_elements = BY_CHANNEL.get(channel_map.get(worst, "RED"), [])
    if not band_elements:
        return f"ELEMENT_SHIFT → no elements for {worst} channel"

    if worst == "RED":
        ch = osc.red
    elif worst == "BLUE":
        ch = osc.blue
    else:
        ch = osc.purple

    # Find current element position in its band, advance by 1
    try:
        idx = next(i for i, e in enumerate(band_elements) if e.id == ch.element.id)
        next_el = band_elements[(idx + 1) % len(band_elements)]
    except StopIteration:
        next_el = band_elements[0]

    old_hz = ch.element.hz
    ch.element = next_el
    return (f"ELEMENT_SHIFT → {worst} channel: "
            f"{old_hz}Hz ({ch.element.name}) → {next_el.hz}Hz ({next_el.name})")


# ── Healer ────────────────────────────────────────────────────────────────────

class Healer:
    """
    Self-healing Concert loop.

    Runs Concert, detects dissonance, applies targeted oscillator tuning,
    repeats until HARMONIZED or MAX_ROUNDS exhausted.

    Each healing round is TICK-sealed — the organism's self-repair is observable
    and auditable, not a silent background process.
    """

    MAX_ROUNDS    = 6
    TARGET_SCORE  = 0.25   # aim for resonance_score < DRIFT_THRESHOLD

    # Healing action sequence (tried in order, cycling)
    ACTION_SEQUENCE = [
        "phase_nudge",
        "amplitude_balance",
        "phase_nudge",
        "error_clear",
        "element_shift",
        "phase_nudge",
    ]

    def __init__(self, organism_root=None) -> None:
        self._concert = Concert(organism_root=organism_root)
        self._osc     = self._concert._bridge.oscillator

    def run(
        self,
        title:        str = "heal",
        max_rounds:   int | None = None,
        verbose:      bool = True,
    ) -> HealResult:
        """
        Run the self-healing loop.
        Returns HealResult with full attempt history and final Concert state.
        """
        max_r    = max_rounds or self.MAX_ROUNDS
        attempts: list[HealAttempt] = []
        prev_score: float | None = None

        for round_n in range(1, max_r + 1):
            # Run a Concert measurement
            concert_title = f"{title}-r{round_n}"
            result = self._concert.run(title=concert_title, save=False)
            c      = result.coherence
            score  = c.resonance_score
            delta  = (score - prev_score) if prev_score is not None else 0.0

            # Wafer failures from IR catalyst nodes
            wafer_fails = [
                n.id for n in result.ir.graph.nodes
                if n.kind.value == "catalyst" and not n.meta.get("passed", True)
            ]

            if verbose:
                print(f"  Round {round_n}: {result.status:12s}  "
                      f"score={score:.4f}  Δ={delta:+.4f}  "
                      f"wafer_fails={len(wafer_fails)}")

            # If already HARMONIZED, we're done
            if result.status == "HARMONIZED":
                action = "NONE — already HARMONIZED"
                attempts.append(HealAttempt(
                    round=round_n, status=result.status,
                    resonance_score=score,
                    phase_red=c.phase_red, phase_blue=c.phase_blue,
                    phase_purple=c.phase_purple, phase_variance=score,
                    action=action, delta_score=delta,
                    wafer_failures=wafer_fails,
                ))
                return self._finalize(title, attempts, result, healed=True)

            # Determine and apply the healing action for this round
            action = self._apply_action(round_n, result, verbose)

            attempts.append(HealAttempt(
                round=round_n, status=result.status,
                resonance_score=score,
                phase_red=c.phase_red, phase_blue=c.phase_blue,
                phase_purple=c.phase_purple, phase_variance=score,
                action=action, delta_score=delta,
                wafer_failures=wafer_fails,
            ))

            # Stagnation guard: if score is not improving, escalate action
            if prev_score is not None and delta >= 0 and round_n >= 3:
                if verbose:
                    print(f"  ⚠  Stagnating (Δ={delta:+.4f}) — escalating to ELEMENT_SHIFT")
                action_extra = _element_shift(self._osc, _worst_channel(c))
                attempts[-1].action += f"; {action_extra}"
                if verbose:
                    print(f"     {action_extra}")

            prev_score = score

        # Exhausted without healing — return last Concert result
        last_result = self._concert.run(title=f"{title}-final", save=True)
        return self._finalize(title, attempts, last_result, healed=False)

    def _apply_action(self, round_n: int, result: ConcertResult, verbose: bool) -> str:
        c = result.coherence
        action_name = self.ACTION_SEQUENCE[(round_n - 1) % len(self.ACTION_SEQUENCE)]

        if action_name == "phase_nudge":
            action = _phase_nudge(self._osc, c)
        elif action_name == "amplitude_balance":
            action = _amplitude_balance(self._osc)
        elif action_name == "error_clear":
            action = _error_clear(self._osc)
        elif action_name == "element_shift":
            action = _element_shift(self._osc, _worst_channel(c))
        else:
            action = "NOP"

        if verbose:
            print(f"         → {action}")
        return action

    def _finalize(
        self,
        title: str,
        attempts: list[HealAttempt],
        final_result: ConcertResult,
        healed: bool,
    ) -> HealResult:
        # Seal the healing session with a TICK
        seal_content = json.dumps({
            "title":   title,
            "healed":  healed,
            "rounds":  len(attempts),
            "final":   final_result.coherence.to_dict(),
            "ts":      time.time(),
        }, sort_keys=True).encode()
        seal = hashlib.sha256(seal_content).hexdigest()

        # Also count as healed if the final concert landed HARMONIZED
        actually_healed = healed or (final_result.status == "HARMONIZED")

        return HealResult(
            title=title,
            attempts=attempts,
            final_status=final_result.status,
            healed=actually_healed,
            rounds=len(attempts),
            tick_seal=seal,
            final_concert=final_result,
        )


# ── Standalone entry ──────────────────────────────────────────────────────────

def heal(title: str = "self-heal", max_rounds: int = 6, verbose: bool = True) -> HealResult:
    """Run the self-healing loop from default organism root."""
    healer = Healer()
    return healer.run(title=title, max_rounds=max_rounds, verbose=verbose)
