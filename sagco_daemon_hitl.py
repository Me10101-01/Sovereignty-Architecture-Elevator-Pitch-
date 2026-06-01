#!/usr/bin/env python3
"""sagco_daemon_hitl.py — v0.3 human-in-the-loop daemon

Pipeline fires only when you say so.
"""

import os
import re
import sys
import time
import yaml
import tarfile
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Import pipeline stages from core
sys.path.insert(0, str(Path(__file__).parent))
from sagco_daemon_core import (
    eater, primitive_resolver, dispatch_mapper,
    command_dna, write_command_index, write_bytecode_tick,
    archive_stage, write_tick,
    PRIM_MAP,
)

VERSION      = "0.3"
DAEMON_NAME  = "sagco_command_daemon"
MASTER_PATH  = Path(__file__).parent / "MASTER.COMMAND.yaml"
CONFIG_PATH  = Path(__file__).parent / "sagco_daemon_config.yaml"

# ── ANSI ─────────────────────────────────────────────────────────────────────
GRN = "\033[32m"; YLW = "\033[33m"; CYN = "\033[36m"; RED = "\033[31m"
BLD = "\033[1m";  DIM = "\033[2m";  RST = "\033[0m";  MGT = "\033[35m"

def c(text, *codes): return "".join(codes) + str(text) + RST

# ── Safety gate ───────────────────────────────────────────────────────────────
DESTRUCTIVE = (
    "sagco delete", "sagco reset", "sagco push --force",
    "sagco commit", "git reset --hard", "rm -rf",
    "git push", "sagco deploy prod", "sagco wipe",
)

def is_destructive(cmd: str) -> bool:
    return any(cmd.strip().startswith(d) for d in DESTRUCTIVE)


# ── Macro templates ───────────────────────────────────────────────────────────
# (trigger_fn, label, steps)
MACROS = [
    (
        lambda evs: any(e["kind"] == "bytecode"      for e in evs),
        "recon → compile → archive",
        ["sagco recon", "sagco compile", "sagco archive"],
    ),
    (
        lambda evs: any(e["kind"] == "contradiction"  for e in evs),
        "fix → verify → commit",
        ["sagco fix", "sagco verify", "sagco commit"],
    ),
    (
        lambda evs: any(e["kind"] == "recon_report"   for e in evs),
        "compile → dna → archive",
        ["sagco compile", "sagco dna", "sagco archive"],
    ),
    (
        lambda evs: any(e["kind"] == "new_artifact"   for e in evs),
        "index → dna → archive",
        ["sagco index", "sagco dna", "sagco archive"],
    ),
]

def best_macro(events: list) -> tuple | None:
    for trigger, label, steps in MACROS:
        if trigger(events):
            return label, steps
    return None


# ── TUI helpers ───────────────────────────────────────────────────────────────
def ask(prompt_str: str) -> str:
    sys.stdout.write(prompt_str)
    sys.stdout.flush()
    try:
        return input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "q"


def divider(label: str = ""):
    if label:
        pad = 54 - len(label) - 2
        print(c(f"─── {label} " + "─" * pad, DIM))
    else:
        print(c("─" * 58, DIM))


def show_event_list(events: list):
    divider("ARTIFACT DETAILS")
    for i, e in enumerate(events, 1):
        kind = c(f"[{e['kind']:14}]", CYN)
        name = c(e["name"], BLD)
        print(f"  {c(str(i), YLW)}.  {kind}  {name}")
        if e.get("lines") is not None:
            print(f"         {c(str(e['lines']) + ' lines', GRN)}  |  {c(e.get('path',''), DIM)}")
        elif "path" in e:
            print(f"         {c(e['path'], DIM)}")
        if desc := e.get("description"):
            print(f"         {c(desc, DIM)}")
    print()


def show_macro_prompt(label: str, steps: list) -> bool:
    """Display macro chain and return True if user approved."""
    print()
    divider("MACRO SUGGESTION")
    print(f"\n  {c('Macro:', BLD)}  {c(label, MGT)}\n")
    for i, step in enumerate(steps):
        arrow = "↓" if i < len(steps) - 1 else "✓"
        col   = RED if is_destructive(step) else GRN
        flag  = c("  ← requires approval", RED) if is_destructive(step) else ""
        print(f"  {c(step, col)}{flag}")
        if i < len(steps) - 1:
            print(f"  {c(arrow, DIM)}")
    print()
    ans = ask(f"  Allow? {c('[y/n]', YLW)} > ")
    return ans == "y"


def execute_macro(steps: list):
    """Run each step, gating on destructive ones."""
    print()
    for step in steps:
        if is_destructive(step):
            ans = ask(f"\n  {c('⚠  destructive action:', RED)} {c(step, BLD)}\n"
                      f"  Confirm? {c('[y/n]', YLW)} > ")
            if ans != "y":
                print(f"  {c('↳ deferred', YLW)}")
                continue
        print(f"  {c('→', DIM)} {step}", end=" ", flush=True)
        # Hook: replace time.sleep with real subprocess.run(step.split()) once
        # you wire the phone agent to your actual sagco binaries.
        time.sleep(0.4)
        print(c("✓", GRN))
    print(f"\n  {c('Macro complete.', GRN)}")


# ── Main HITL prompt ──────────────────────────────────────────────────────────
def hitl_prompt(events: list) -> str:
    """
    Minimal HITL prompt — watch, notify, ask. Nothing else.
    Returns: "allow" | "macro" | "defer" | "quit"
    """
    macro = best_macro(events)

    # One artifact per line, clean
    print(f"\n{c('SAGCO>', BLD + GRN)}\n")
    if len(events) == 1:
        print(f"  New artifact discovered\n")
        print(f"  {c(events[0]['path'], YLW)}\n")
    else:
        print(f"  New artifacts discovered: {c(str(len(events)), BLD)}\n")
        for e in events:
            print(f"  {c(e['path'], YLW)}")
        print()

    print(f"  {c('[a]', GRN)} allow")
    print(f"  {c('[s]', CYN)} show")
    if macro:
        print(f"  {c('[m]', MGT)} macro")
    print(f"  {c('[q]', DIM)} quit")
    print()

    while True:
        key = ask(f"{c('> ', GRN)}")

        if key == "a":
            return "allow"

        elif key == "s":
            show_event_list(events)
            print(f"  {c('[a]', GRN)} allow  "
                  + (f"{c('[m]', MGT)} macro  " if macro else "")
                  + f"{c('[q]', DIM)} quit")

        elif key == "m":
            if macro:
                approved = show_macro_prompt(macro[0], macro[1])
                if approved:
                    execute_macro(macro[1])
                    return "macro"
                else:
                    print(f"  {c('deferred.', YLW)}")
                    return "defer"
            else:
                print(f"  {c('no macro for this artifact set.', DIM)}")

        elif key in ("d", ""):
            print(f"  {c('deferred.', YLW)}")
            return "defer"

        elif key == "q":
            print(f"\n  {c('stopped.', DIM)}\n")
            sys.exit(0)

        else:
            print(f"  {c('?', RED)} a / s / m / q")


# ── Event builder (diff file_state → event list) ──────────────────────────────
def build_events(artifacts: list, bytecode_lines: list) -> list:
    """Turn raw eater output into structured events for the HITL prompt."""
    events = []
    for a in artifacts:
        name = Path(a["path"]).name
        kind = a["type"]

        # Classify kind into user-visible event categories
        if kind == "bytecode":
            display_kind = "bytecode"
            desc = f"{a.get('lines', 0):,} lines of bytecode"
        elif kind == "shell_artifact":
            display_kind = "new_artifact"
            cmds = a.get("commands", [])
            desc = f"commands: {', '.join(cmds[:3])}" + (" ..." if len(cmds) > 3 else "")
        elif kind == "config":
            display_kind = "new_artifact"
            desc = "configuration artifact"
        elif kind == "python_artifact":
            display_kind = "new_artifact"
            desc = "python module"
        else:
            display_kind = "new_artifact"
            desc = kind

        # Contradiction detection: look for known error patterns in bytecode
        if bytecode_lines:
            text = "\n".join(bytecode_lines[:100]).lower()
            if any(kw in text for kw in ("error", "missing", "not found", "expected", "actual")):
                events.append({
                    "kind":        "contradiction",
                    "name":        "Contradiction detected in bytecode",
                    "description": "expected vs actual mismatch — review before proceeding",
                    "path":        "compiled/",
                })

        events.append({
            "kind":        display_kind,
            "name":        name,
            "description": desc,
            "path":        a["path"],
            "lines":       a.get("lines"),
        })

    # Deduplicate contradiction events
    seen = set()
    deduped = []
    for e in events:
        key = (e["kind"], e["name"])
        if key not in seen:
            seen.add(key)
            deduped.append(e)
    return deduped


# ── Pipeline runner (called after user approves) ───────────────────────────────
def run_pipeline_approved(cfg: dict, artifacts: list, bytecode_lines: list) -> dict:
    outputs  = cfg.get("outputs", {})
    watched  = [d.rstrip("/") for d in cfg.get("watch", ["reports", "compiled", "ticks", "archives"])]

    idx_path = outputs.get("command_index", {}).get("path", "reports/SAGCO_TOP_COMMAND_INDEX.txt")
    bc_dir   = str(Path(outputs.get("bytecode", {}).get("path", "compiled/sagco_command_ticks.sagco")).parent)
    dna_path = outputs.get("dna", {}).get("path", "reports/SAGCO_COMMAND_DNA.yaml")
    arc_path = outputs.get("archive", {}).get("path", "archives/sagco_command_fossil_record.tar.gz")

    fake_state = {}
    resolved = primitive_resolver(artifacts)
    dispatch = dispatch_mapper(artifacts, resolved, cfg)
    dna      = command_dna(artifacts, dispatch, len(bytecode_lines))

    Path(dna_path).parent.mkdir(parents=True, exist_ok=True)
    import yaml as _yaml
    with open(dna_path, "w") as fh:
        _yaml.dump(dna, fh, default_flow_style=False, sort_keys=False)

    write_command_index(dispatch, bytecode_lines, idx_path)
    bc_tick  = write_bytecode_tick(bytecode_lines, bc_dir)
    archive_stage(watched, arc_path)

    result = {
        "stages": ["eater", "primitive_resolver", "dispatch_mapper", "command_dna", "archive"],
        "artifacts": len(artifacts),
        "bytecode_lines": len(bytecode_lines),
        "dispatch_entries": len(dispatch),
        "dna_signature": dna["signature"],
        "approved_by": "human",
        "outputs": {
            "index":    idx_path,
            "dna":      dna_path,
            "bytecode": bc_tick,
            "archive":  arc_path,
        },
    }

    tick = write_tick("ticks", result)

    print(f"\n  {c('Pipeline outputs:', BLD)}")
    print(f"  {c('command index', DIM)} → {idx_path}")
    print(f"  {c('command dna',   DIM)} → {dna_path}  {c('(sig: ' + dna['signature'] + ')', DIM)}")
    print(f"  {c('bytecode tick', DIM)} → {bc_tick}")
    arc_kb = Path(arc_path).stat().st_size // 1024
    print(f"  {c('fossil record', DIM)} → {arc_path}  {c(f'({arc_kb} KB)', DIM)}")
    print(f"  {c('tick', DIM)}          → {tick}")
    return result


# ── Watcher helpers ───────────────────────────────────────────────────────────
def _has_changes(watched: list, file_state: dict) -> bool:
    for d in watched:
        p = Path(d.rstrip("/"))
        if not p.exists():
            continue
        for f in p.rglob("*"):
            if f.is_file() and file_state.get(str(f)) != f.stat().st_mtime:
                return True
    return False


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    # Load MASTER.COMMAND.yaml first, fall back to sagco_daemon_config.yaml
    master = {}
    if MASTER_PATH.exists():
        with open(MASTER_PATH) as fh:
            master = import_yaml(fh)
    cfg = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as fh:
            cfg = import_yaml(fh)

    # MASTER.COMMAND.yaml is the source of truth for watch dirs
    watched = [d.rstrip("/") for d in (
        master.get("watch") or cfg.get("watch") or ["reports", "compiled", "ticks"]
    )]
    poll_interval = int(cfg.get("poll_interval", 5))
    approval_required = master.get("approval_required", ["deploy", "delete", "push"])

    for d in watched + ["ticks"]:
        Path(d).mkdir(parents=True, exist_ok=True)

    # ── Boot screen ────────────────────────────────────────────────────────────
    print(f"\n{c('[SAGCO DAEMON]', BLD + GRN)}\n")
    print("Watching:")
    for d in watched:
        print(f"  {d}/")
    print()
    print(f"Approval required for: {', '.join(approval_required)}")
    print()
    print(f"{c('Status: ONLINE', BLD + GRN)}")
    print()
    print(c("─" * 40, DIM))
    print(f"{c('Ctrl+C to stop.', DIM)}")
    print(c("─" * 40, DIM))
    print()

    file_state: dict = {}

    # Initial scan
    artifacts, bytecode_lines = eater(watched, file_state)
    if artifacts or bytecode_lines:
        events = build_events(artifacts, bytecode_lines)
        decision = hitl_prompt(events)
        if decision == "allow":
            print()
            run_pipeline_approved(cfg, artifacts, bytecode_lines)

    try:
        while True:
            time.sleep(poll_interval)
            if _has_changes(watched, file_state):
                artifacts, bytecode_lines = eater(watched, file_state)
                events = build_events(artifacts, bytecode_lines)
                if not events:
                    continue
                decision = hitl_prompt(events)
                if decision == "allow":
                    print()
                    run_pipeline_approved(cfg, artifacts, bytecode_lines)
    except KeyboardInterrupt:
        print(f"\n{c('stopped.', DIM)}\n")
        sys.exit(0)


def import_yaml(fh):
    import yaml
    return yaml.safe_load(fh) or {}


if __name__ == "__main__":
    main()
