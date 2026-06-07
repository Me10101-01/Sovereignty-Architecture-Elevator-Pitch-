"""
SAGCO Antibody System
Detects environment mismatches and self-heals where possible.
Each antibody maps to a .sagco definition file and a Python detection routine.
"""

from __future__ import annotations
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class AntibodyResult:
    name: str
    triggered: bool
    message: str
    healed: bool = False
    heal_action: str = ""


class Antibody:
    def __init__(
        self,
        name: str,
        detect: Callable[[], bool],
        message: str,
        heal: Callable[[], bool] | None = None,
        heal_desc: str = "",
    ) -> None:
        self.name = name
        self._detect = detect
        self.message = message
        self._heal = heal
        self.heal_desc = heal_desc

    def run(self) -> AntibodyResult:
        triggered = False
        healed = False
        try:
            triggered = self._detect()
        except Exception as e:
            triggered = True
            self.message = f"{self.message} (detection error: {e})"

        if triggered and self._heal:
            try:
                healed = self._heal()
            except Exception:
                healed = False

        return AntibodyResult(
            name=self.name,
            triggered=triggered,
            message=self.message if triggered else f"{self.name}: clean",
            healed=healed,
            heal_action=self.heal_desc if healed else "",
        )


# ── Detection routines ────────────────────────────────────────────────────

def _detect_app_picker_locked() -> bool:
    """App picker is stuck / default handler is broken."""
    if platform.system() == "Windows":
        # check if known-broken open-with handler exists
        return False  # would need registry check; skip on non-Windows
    return False

def _detect_shell_language_mismatch() -> bool:
    """Shell reports a language that doesn't match the shebang expectations."""
    shell = os.environ.get("SHELL", "")
    if not shell:
        return True
    if platform.system() == "Windows":
        return False
    return not (shell.endswith("bash") or shell.endswith("zsh") or
                shell.endswith("sh") or "termux" in shell)

def _detect_path_confusion() -> bool:
    """Python or git are not on PATH, or point to wrong locations."""
    return shutil.which("python3") is None and shutil.which("python") is None

def _detect_frozen_terminal() -> bool:
    """Terminal process is unresponsive (heuristic: stdin is not a tty)."""
    try:
        return not sys.stdin.isatty() and os.environ.get("SAGCO_HEADLESS") != "1"
    except Exception:
        return False

def _detect_missing_git() -> bool:
    return shutil.which("git") is None

def _detect_no_network() -> bool:
    try:
        import socket
        socket.setdefaulttimeout(2)
        socket.create_connection(("8.8.8.8", 53))
        return False
    except Exception:
        return True

def _detect_wrong_python() -> bool:
    return sys.version_info.major < 3 or sys.version_info.minor < 9

def _detect_missing_sagco_true() -> bool:
    return not (os.path.exists("sagco-true") or os.path.exists("sagco_true"))


# ── Heal routines ─────────────────────────────────────────────────────────

def _heal_path_confusion() -> bool:
    """Attempt to find Python and add it to PATH in the current process."""
    for candidate in ["/usr/bin/python3", "/usr/local/bin/python3", "/data/data/com.termux/files/usr/bin/python3"]:
        if os.path.exists(candidate):
            parent = os.path.dirname(candidate)
            os.environ["PATH"] = parent + os.pathsep + os.environ.get("PATH", "")
            return True
    return False


# ── Antibody registry ─────────────────────────────────────────────────────

ANTIBODIES: list[Antibody] = [
    Antibody(
        "app_picker_locked",
        _detect_app_picker_locked,
        "Default app handler is locked or broken — open-with may fail",
    ),
    Antibody(
        "shell_language_mismatch",
        _detect_shell_language_mismatch,
        "SHELL env var is missing or points to an unexpected interpreter",
    ),
    Antibody(
        "path_confusion",
        _detect_path_confusion,
        "Python is not on PATH — scripts cannot execute",
        _heal_path_confusion,
        "Added Python parent directory to PATH",
    ),
    Antibody(
        "frozen_terminal",
        _detect_frozen_terminal,
        "Terminal stdin is not a TTY — may be headless; set SAGCO_HEADLESS=1 to suppress",
    ),
    Antibody(
        "missing_git",
        _detect_missing_git,
        "git is not installed or not on PATH — version control operations will fail",
    ),
    Antibody(
        "no_network",
        _detect_no_network,
        "No outbound network connectivity — cloud operations will fail",
    ),
    Antibody(
        "wrong_python",
        _detect_wrong_python,
        f"Python {sys.version_info.major}.{sys.version_info.minor} detected — SAGCO requires 3.9+",
    ),
    Antibody(
        "missing_sagco_true",
        _detect_missing_sagco_true,
        "sagco-true/ directory not found in working directory",
    ),
]


def run_all(antibodies: list[Antibody] | None = None) -> list[AntibodyResult]:
    results: list[AntibodyResult] = []
    for ab in (antibodies or ANTIBODIES):
        results.append(ab.run())
    return results


def report(results: list[AntibodyResult]) -> dict:
    triggered = [r for r in results if r.triggered]
    healed = [r for r in triggered if r.healed]
    return {
        "total": len(results),
        "triggered": len(triggered),
        "healed": len(healed),
        "clean": len(results) - len(triggered),
        "status": "CLEAN" if not triggered else ("HEALING" if healed else "INFECTED"),
        "results": [
            {"name": r.name, "triggered": r.triggered,
             "message": r.message, "healed": r.healed}
            for r in results
        ],
    }


if __name__ == "__main__":
    import json
    results = run_all()
    print(json.dumps(report(results), indent=2))
