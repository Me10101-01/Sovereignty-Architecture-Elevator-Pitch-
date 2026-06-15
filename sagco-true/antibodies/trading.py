"""
Trading antibodies for SAGCO.

AB-OVERFIT-001          — high win rate, negative EV
AB-SCREENSHOT-CONFIG-001 — building machine configs from screenshots
"""

from __future__ import annotations
from .detector import Antibody, AntibodyResult


# ── AB-OVERFIT-001 ─────────────────────────────────────────────────────────────

def _detect_overfit() -> bool:
    return False   # passive — triggered from sim results


def _heal_overfit() -> bool:
    print()
    print("  AB-OVERFIT-001 — Remedy")
    print()
    print("  A strategy can be 60%+ accurate and STILL lose money.")
    print()
    print("  Formula:")
    print("    EV = (win_rate × avg_gain) - (loss_rate × avg_loss)")
    print()
    print("  Example of the trap:")
    print("    Win rate:  65%")
    print("    Avg gain:  $50")
    print("    Avg loss:  $120")
    print("    EV = (0.65 × 50) - (0.35 × 120) = 32.50 - 42.00 = -$9.50 per trade")
    print()
    print("  Fix: risk/reward ratio, not win rate.")
    print("  Target: avg_gain ≥ avg_loss (1:1 minimum)")
    print("          avg_gain ≥ 1.5 × avg_loss (1.5:1 target)")
    print()
    print("  Run: python simulate.py  — to test before risking real money")
    print()
    return True


OVERFIT_ANTIBODY = Antibody(
    name      = "AB-OVERFIT-001",
    detect    = _detect_overfit,
    message   = "High win rate + negative EV detected. Losses are eating the wins.",
    heal      = _heal_overfit,
    heal_desc = "Printed EV formula and risk/reward fix",
)


# ── AB-SCREENSHOT-CONFIG-001 ───────────────────────────────────────────────────

def _detect_screenshot_config() -> bool:
    return False   # passive — triggered when screenshot-sourced config is used


def _heal_screenshot_config() -> bool:
    print()
    print("  AB-SCREENSHOT-CONFIG-001 — Remedy")
    print()
    print("  Screenshot ≠ Ground truth")
    print()
    print("  Screenshot data can be:")
    print("    - Stale  (taken at a different time)")
    print("    - Misread (fonts small, glare, angle)")
    print("    - Changed (driver updated, IP changed via DHCP)")
    print()
    print("  Verify node hardware from actual commands:")
    print()
    print("  Windows:")
    print("    systeminfo")
    print("    Get-ComputerInfo | Select CsName, CsProcessors, OsArchitecture")
    print("    (Get-WmiObject Win32_VideoController).Name")
    print("    (Get-WmiObject Win32_PhysicalMemory).Capacity")
    print()
    print("  WSL2 / Linux:")
    print("    lscpu | grep 'Model name'")
    print("    free -h")
    print("    lspci | grep VGA")
    print("    ip addr show")
    print()
    print("  Ollama:")
    print("    ollama list")
    print("    ollama ps")
    print()
    print("  SAGCO:")
    print("    sagco node hp probe")
    print()
    return True


SCREENSHOT_CONFIG_ANTIBODY = Antibody(
    name      = "AB-SCREENSHOT-CONFIG-001",
    detect    = _detect_screenshot_config,
    message   = "Node config sourced from screenshot — may be stale. Verify with live commands.",
    heal      = _heal_screenshot_config,
    heal_desc = "Printed verification commands for hardware, network, and Ollama",
)


def fire_overfit_antibody() -> AntibodyResult:
    r = OVERFIT_ANTIBODY.run()
    r.triggered = True
    r.healed    = True
    _heal_overfit()
    return r


def fire_screenshot_config_antibody() -> AntibodyResult:
    r = SCREENSHOT_CONFIG_ANTIBODY.run()
    r.triggered = True
    r.healed    = True
    _heal_screenshot_config()
    return r
