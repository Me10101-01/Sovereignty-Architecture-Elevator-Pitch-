#!/usr/bin/env python3
"""
invocation_logger.py — Append-only SAGCO command invocation log

Every SAGCO CLI call logs here: timestamp, command, args, result, duration_ms.
Log is JSONL, one entry per line, never truncated.
"""

import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone


DEFAULT_LOG = Path(__file__).parent.parent / "registry" / "invocation_log.jsonl"


def _sha256(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def log_invocation(
    command: str,
    args: dict,
    result: str,
    verdict: str = "COMPUTED",
    duration_ms: float = 0.0,
    log_path: Path = DEFAULT_LOG,
) -> dict:
    """
    Append one invocation record to invocation_log.jsonl.

    verdict: COMPUTED | FAILED_COMPUTE | UNCOMPUTED
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts":          datetime.now(timezone.utc).isoformat(),
        "command":     command,
        "args":        args,
        "result":      result,
        "verdict":     verdict,
        "duration_ms": round(duration_ms, 2),
    }
    entry["sha256"] = _sha256({k: v for k, v in entry.items() if k != "sha256"})

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def tail(n: int = 20, log_path: Path = DEFAULT_LOG) -> list[dict]:
    """Return last n entries from the log."""
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in lines[-n:]:
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def count_by_verdict(log_path: Path = DEFAULT_LOG) -> dict[str, int]:
    """Return {verdict: count} summary across all entries."""
    counts: dict[str, int] = {}
    for entry in tail(n=999999, log_path=log_path):
        v = entry.get("verdict", "UNKNOWN")
        counts[v] = counts.get(v, 0) + 1
    return counts


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tail"

    if cmd == "tail":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        entries = tail(n)
        if not entries:
            print("  (log empty)")
        for e in entries:
            print(f"  [{e['verdict']:15s}] {e['ts'][:19]}  {e['command']}  →  {e['result'][:60]}")

    elif cmd == "summary":
        counts = count_by_verdict()
        total = sum(counts.values())
        print(f"  Total invocations: {total}")
        for v, c in sorted(counts.items()):
            print(f"    {v:20s}: {c}")
