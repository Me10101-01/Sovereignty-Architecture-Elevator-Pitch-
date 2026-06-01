#!/usr/bin/env python3
"""sagco_command_daemon v0.2 — watch → eater → resolver → mapper → dna → archive → tick"""

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

VERSION = "0.2"
DAEMON_NAME = "sagco_command_daemon"
CONFIG_PATH = Path(__file__).parent / "sagco_daemon_config.yaml"

BANNER = f"""
╔═══════════════════════════════════════════════════════╗
║        SAGCO COMMAND DAEMON  v{VERSION}                      ║
║        daemon: {DAEMON_NAME}     ║
║        entity: Strategickhaos DAO LLC                 ║
╚═══════════════════════════════════════════════════════╝
"""

# ── Primitive map: keyword fragment → primitive opcode ──────────────────────
PRIM_MAP = {
    "plan":       "PLAN_EMIT",
    "canvas":     "RENDER_CANVAS",
    "obsidian":   "VAULT_WRITE",
    "dispatch":   "DISPATCH_CALL",
    "agent":      "AGENT_SPAWN",
    "efi":        "EFI_WRITE",
    "kernel":     "KERNEL_EXEC",
    "conversion": "TRANSFORM_OP",
    "ems":        "EMS_ROUTE",
    "phone":      "COMMS_INIT",
    "fleet":      "FLEET_DEPLOY",
    "master":     "ORCHESTRATE",
    "eater":      "INGEST",
    "archive":    "ARCHIVE_WRITE",
    "dna":        "DNA_ENCODE",
    "tick":       "TICK_EMIT",
    "recon":      "RECON_SCAN",
    "crawl":      "CRAWL_EXEC",
    "fossil":     "FOSSIL_RECORD",
    "compile":    "BYTECODE_EMIT",
    "resolver":   "RESOLVE_PRIM",
    "mapper":     "MAP_DISPATCH",
    "watch":      "WATCH_INODE",
    "patch":      "PATCH_APPLY",
    "status":     "STATUS_QUERY",
    "deploy":     "DEPLOY_EXEC",
    "verify":     "VERIFY_PROOF",
    "manifest":   "MANIFEST_READ",
    "evolution":  "EVOLVE_STEP",
    "baby":       "KERNEL_INIT",
    "custom":     "TRANSFORM_OP",
}


# ── Stage 1: Eater ────────────────────────────────────────────────────────────

def eater(watched_dirs: list, file_state: dict) -> tuple:
    """Ingest all files in watched dirs, return new artifacts and bytecode lines."""
    artifacts = []
    bytecode_lines = []

    for d in watched_dirs:
        path = Path(d.rstrip("/"))
        path.mkdir(parents=True, exist_ok=True)
        for f in sorted(path.rglob("*")):
            if not f.is_file():
                continue
            key = str(f)
            mtime = f.stat().st_mtime
            if file_state.get(key) == mtime:
                continue
            file_state[key] = mtime

            if f.suffix == ".sagco":
                try:
                    lines = f.read_text(errors="replace").splitlines()
                    bytecode_lines.extend(lines)
                    artifacts.append({"type": "bytecode", "path": key, "lines": len(lines)})
                except OSError:
                    pass

            elif f.suffix in (".sh", ".bash", "") and f.stat().st_size < 524288:
                try:
                    content = f.read_text(errors="replace")
                    found = re.findall(r'sagco[-_]\w+(?:\s+\w+)*', content)
                    found += re.findall(r'"sagco\s+\w+\s+\w+"', content)
                    cmds = list({c.strip().strip('"') for c in found})
                    if cmds:
                        artifacts.append({"type": "shell_artifact", "path": key, "commands": cmds})
                except OSError:
                    pass

            elif f.suffix in (".yaml", ".yml"):
                artifacts.append({"type": "config", "path": key})

            elif f.suffix == ".py":
                try:
                    content = f.read_text(errors="replace")
                    found = re.findall(r'sagco[-_]\w+', content)
                    if found:
                        artifacts.append({"type": "python_artifact", "path": key,
                                          "commands": list(set(found))})
                except OSError:
                    pass

    return artifacts, bytecode_lines


# ── Stage 2: Primitive Resolver ───────────────────────────────────────────────

def primitive_resolver(artifacts: list) -> dict:
    """Map each discovered command string to its primitive opcodes."""
    resolved = {}
    for artifact in artifacts:
        cmds = artifact.get("commands", [])
        for cmd in cmds:
            tokens = re.split(r'[-_\s]+', cmd.lower())
            prims = []
            for token in tokens:
                if token in PRIM_MAP:
                    prims.append(PRIM_MAP[token])
            if prims:
                resolved[cmd] = list(dict.fromkeys(prims))  # deduped, ordered
    return resolved


# ── Stage 3: Dispatch Mapper ──────────────────────────────────────────────────

def dispatch_mapper(artifacts: list, resolved: dict, cfg: dict) -> dict:
    """Build dispatch table: artifact name → {handler, type, primitives, status}."""
    table = {}

    for artifact in artifacts:
        name = Path(artifact["path"]).name
        cmds = artifact.get("commands", [])
        prims = []
        for cmd in cmds:
            prims.extend(resolved.get(cmd, []))
        prims = list(dict.fromkeys(prims)) or _infer_primitives(name)

        table[name] = {
            "handler": artifact["path"],
            "type":    artifact["type"],
            "primitives": prims,
            "status":  "active",
        }

    # Inject known fossil artifacts from config (mark as fossil if not already present)
    for known in cfg.get("known_artifacts", []):
        if known not in table:
            table[known] = {
                "handler":    f"artifacts/{known}",
                "type":       "shell_artifact",
                "primitives": _infer_primitives(known),
                "status":     "fossil",
            }

    # Inject known commands as virtual entries
    for cmd in cfg.get("known_commands", []):
        key = cmd.replace(" ", "_")
        if key not in table:
            prims = []
            for token in re.split(r'[-_\s]+', cmd.lower()):
                if token in PRIM_MAP:
                    prims.append(PRIM_MAP[token])
            table[key] = {
                "handler":    f"virtual/{key}",
                "type":       "virtual_command",
                "primitives": list(dict.fromkeys(prims)) or ["PASSTHROUGH"],
                "status":     "discovered",
            }

    return table


def _infer_primitives(name: str) -> list:
    tokens = re.split(r'[-_.\s]+', name.lower())
    prims = [PRIM_MAP[t] for t in tokens if t in PRIM_MAP]
    return list(dict.fromkeys(prims)) or ["PASSTHROUGH"]


# ── Stage 4: Command DNA ──────────────────────────────────────────────────────

def command_dna(artifacts: list, dispatch: dict, bytecode_count: int) -> dict:
    """Encode the full command ecosystem as SAGCO DNA."""
    type_counts: dict = defaultdict(int)
    for a in artifacts:
        type_counts[a["type"]] += 1

    # DNA strand header — mirrors the SAGCO-HYDRA codon format
    strand_codons = []
    for name, entry in sorted(dispatch.items()):
        codon = _name_to_codon(name)
        strand_codons.append(codon)

    strand = "ATG-" + "-".join(strand_codons[:12]) + "-TGG"
    sig = hashlib.sha256(str(sorted(dispatch.keys())).encode()).hexdigest()[:16]

    chromosomes = [
        {
            "gene":       name,
            "codon":      _name_to_codon(name),
            "primitives": entry["primitives"],
            "type":       entry["type"],
            "status":     entry.get("status", "active"),
        }
        for name, entry in sorted(dispatch.items())
    ]

    return {
        "version":  VERSION,
        "daemon":   DAEMON_NAME,
        "generated": datetime.now().isoformat(),
        "strand":   strand,
        "signature": sig,
        "stats": {
            "total_artifacts":  len(artifacts),
            "bytecode_lines":   bytecode_count,
            "dispatch_entries": len(dispatch),
            "artifact_types":   dict(type_counts),
            "chromosome_count": len(chromosomes),
        },
        "workflow":    ["eater", "primitive_resolver", "dispatch_mapper", "command_dna", "archive"],
        "chromosomes": chromosomes,
    }


def _name_to_codon(name: str) -> str:
    """Convert artifact name to a short uppercase codon token."""
    parts = re.split(r'[-_.\s]+', name.upper())
    initials = "".join(p[:3] for p in parts if p and p not in ("SH", "PY", "YAML", "YML"))
    return (initials[:6] or "CMD") + str(len(name) % 100)


# ── Output Writers ────────────────────────────────────────────────────────────

def write_command_index(dispatch: dict, bytecode_lines: list, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_bc = len(bytecode_lines)

    rows = []
    for name, entry in sorted(dispatch.items()):
        status = entry.get("status", "active").upper()
        chain  = " → ".join(entry["primitives"])
        rows.append((status, name, entry["handler"], chain, entry["type"]))

    lines = [
        "╔══════════════════════════════════════════════════════════════════════╗",
        f"║   SAGCO TOP COMMAND INDEX — v{VERSION}                                    ║",
        f"║   Generated: {ts}                              ║",
        "╚══════════════════════════════════════════════════════════════════════╝",
        "",
        f"  Commands indexed : {len(dispatch)}",
        f"  Bytecode lines   : {total_bc:,}",
        "",
        "─── DISPATCH TABLE ─────────────────────────────────────────────────────",
        "",
    ]
    for status, name, handler, chain, atype in rows:
        lines += [
            f"  [{status:10}]  {name}",
            f"               handler    : {handler}",
            f"               primitives : {chain}",
            f"               type       : {atype}",
            "",
        ]

    if bytecode_lines:
        lines += [
            "─── BYTECODE SAMPLE (first 30 lines) ──────────────────────────────────",
            "",
        ]
        for bl in bytecode_lines[:30]:
            lines.append(f"  {bl}")
        if total_bc > 30:
            lines.append(f"  ... [{total_bc - 30:,} more lines]")
        lines.append("")

    lines.append("─── END OF INDEX ───────────────────────────────────────────────────────")
    Path(path).write_text("\n".join(lines) + "\n")


def write_bytecode_tick(bytecode_lines: list, output_dir: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"sagco_command_ticks_{ts}.sagco"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        f"; SAGCO COMMAND TICKS — daemon v{VERSION}",
        f"; daemon: {DAEMON_NAME}",
        f"; generated: {datetime.now().isoformat()}",
        f"; lines: {len(bytecode_lines)}",
        "; strand: ATG ... TGG",
        "",
    ]
    path.write_text("\n".join(header + bytecode_lines) + "\n")
    return str(path)


def archive_stage(source_dirs: list, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    skip = {output_path}
    with tarfile.open(output_path, "w:gz") as tar:
        for d in source_dirs:
            p = Path(d.rstrip("/"))
            if not p.exists():
                continue
            for f in sorted(p.rglob("*")):
                if f.is_file() and str(f) not in skip:
                    tar.add(str(f), arcname=str(f))
    return output_path


def write_tick(ticks_dir: str, payload: dict) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(ticks_dir) / f"tick_{ts}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    tick = {
        "daemon":    DAEMON_NAME,
        "version":   VERSION,
        "timestamp": datetime.now().isoformat(),
        "result":    payload,
    }
    path.write_text(yaml.dump(tick, default_flow_style=False, sort_keys=False))
    return str(path)


# ── Pipeline orchestrator ─────────────────────────────────────────────────────

def run_pipeline(cfg: dict, file_state: dict, force: bool = False) -> dict | None:
    watched  = [d.rstrip("/") for d in cfg.get("watch", ["reports", "compiled", "ticks", "archives"])]
    outputs  = cfg.get("outputs", {})

    idx_path  = outputs.get("command_index", {}).get("path", "reports/SAGCO_TOP_COMMAND_INDEX.txt")
    bc_dir    = str(Path(outputs.get("bytecode",  {}).get("path", "compiled/sagco_command_ticks.sagco")).parent)
    dna_path  = outputs.get("dna",           {}).get("path", "reports/SAGCO_COMMAND_DNA.yaml")
    arc_path  = outputs.get("archive",       {}).get("path", "archives/sagco_command_fossil_record.tar.gz")

    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{ts}] ⚡ pipeline triggered")

    # Stage 1
    print("  → eater              scanning artifacts...", end=" ", flush=True)
    artifacts, bytecode_lines = eater(watched, file_state)
    print(f"{len(artifacts)} artifacts  |  {len(bytecode_lines):,} bytecode lines")

    if not artifacts and not bytecode_lines and not force:
        print("  ✓ nothing new\n")
        return None

    # Stage 2
    print("  → primitive_resolver resolving commands...", end=" ", flush=True)
    resolved = primitive_resolver(artifacts)
    print(f"{len(resolved)} commands resolved")

    # Stage 3
    print("  → dispatch_mapper    building table...", end=" ", flush=True)
    dispatch = dispatch_mapper(artifacts, resolved, cfg)
    print(f"{len(dispatch)} entries")

    # Stage 4
    print("  → command_dna        encoding DNA...", end=" ", flush=True)
    dna = command_dna(artifacts, dispatch, len(bytecode_lines))
    Path(dna_path).parent.mkdir(parents=True, exist_ok=True)
    with open(dna_path, "w") as fh:
        yaml.dump(dna, fh, default_flow_style=False, sort_keys=False)
    write_command_index(dispatch, bytecode_lines, idx_path)
    bc_tick = write_bytecode_tick(bytecode_lines, bc_dir)
    print(f"strand={dna['strand'][:40]}...")

    # Stage 5
    print("  → archive            writing fossil record...", end=" ", flush=True)
    archive_stage(watched, arc_path)
    arc_size = Path(arc_path).stat().st_size
    print(f"{arc_size:,} bytes → {arc_path}")

    result = {
        "stages":         ["eater", "primitive_resolver", "dispatch_mapper", "command_dna", "archive"],
        "artifacts":      len(artifacts),
        "bytecode_lines": len(bytecode_lines),
        "dispatch_entries": len(dispatch),
        "dna_signature":  dna["signature"],
        "outputs": {
            "index":    idx_path,
            "dna":      dna_path,
            "bytecode": bc_tick,
            "archive":  arc_path,
        },
    }

    tick = write_tick("ticks", result)
    print(f"  ✓ tick → {tick}")
    return result


# ── Watcher ───────────────────────────────────────────────────────────────────

def _snapshot(watched: list) -> dict:
    snap = {}
    for d in watched:
        p = Path(d.rstrip("/"))
        if not p.exists():
            continue
        for f in p.rglob("*"):
            if f.is_file():
                snap[str(f)] = f.stat().st_mtime
    return snap


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
    print(BANNER)

    cfg = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as fh:
            cfg = yaml.safe_load(fh) or {}

    watched       = [d.rstrip("/") for d in cfg.get("watch", ["reports", "compiled", "ticks", "archives"])]
    poll_interval = int(cfg.get("poll_interval", 5))

    for d in watched + ["ticks"]:
        Path(d).mkdir(parents=True, exist_ok=True)

    print(f"  watching : {', '.join(watched)}")
    print(f"  interval : {poll_interval}s")
    print(f"  pipeline : eater → primitive_resolver → dispatch_mapper → command_dna → archive")
    print(f"\nPress Ctrl+C to stop.\n")

    file_state: dict = {}

    # First run — process whatever is already here
    run_pipeline(cfg, file_state, force=True)
    print(f"[daemon] watching for changes...")

    try:
        while True:
            time.sleep(poll_interval)
            if _has_changes(watched, file_state):
                run_pipeline(cfg, file_state)
                print(f"[daemon] watching for changes...")
    except KeyboardInterrupt:
        print("\n[daemon] stopped. goodbye.")
        sys.exit(0)


if __name__ == "__main__":
    main()
