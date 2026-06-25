#!/usr/bin/env python3
"""
audit_runner.py — SAGCO Audit CLI

Commands:
  log    <command> <result> [--verdict COMPUTED]  — append invocation entry
  trace  <claim_id> <expected> <actual> [domain]  — compute V=A/E and trace
  report                                           — build + print variance report
  burnrate                                         — print BurnRate summary
  tail   [n]                                       — last n invocation log entries
  antibodies                                       — list antibody registry

Usage:
  python audit_runner.py log "eru compute" "CPI=1.39" --verdict COMPUTED
  python audit_runner.py trace ERU-FIELD-ORIGIN-001 100 100 eru
  python audit_runner.py report
  python audit_runner.py burnrate
  python audit_runner.py tail 10
  python audit_runner.py antibodies
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(__file__))

import invocation_logger
import decision_tracer
import variance_reporter
from antibody_registry import load_registry, print_registry


def cmd_log(args: list[str]) -> None:
    command = args[0] if args else "unknown"
    result  = args[1] if len(args) > 1 else ""
    verdict = "COMPUTED"
    for i, a in enumerate(args):
        if a == "--verdict" and i + 1 < len(args):
            verdict = args[i + 1]

    t0    = time.time()
    entry = invocation_logger.log_invocation(
        command=command,
        args={},
        result=result,
        verdict=verdict,
        duration_ms=(time.time() - t0) * 1000,
    )
    print(f"  Logged  [{entry['verdict']:15s}]  {entry['command']}  sha256={entry['sha256'][:16]}...")


def cmd_trace(args: list[str]) -> None:
    if len(args) < 3:
        print("  Usage: trace <claim_id> <expected> <actual> [domain]")
        return
    claim_id = args[0]
    expected = float(args[1])
    actual   = float(args[2])
    domain   = args[3] if len(args) > 3 else "sagco"

    entry = decision_tracer.trace_decision(claim_id, expected, actual, domain)
    print(f"  [{entry['verdict']:10s}]  {claim_id}  V={entry['ratio']}  ({actual}/{expected})")
    print(f"  sha256={entry['sha256']}")


def cmd_report() -> None:
    report = variance_reporter.build_report()
    variance_reporter.print_report(report)


def cmd_burnrate() -> None:
    stats = decision_tracer.burn_rate()
    print(f"\n  SAGCO Audit — BurnRate")
    print(f"  {'─'*40}")
    print(f"  Total decisions : {stats['total']}")
    print(f"  Proven          : {stats['proven']}")
    print(f"  BurnRate        : {stats['burn_rate']:.1%}")
    print()
    print(f"  By verdict:")
    for v, c in sorted(stats["by_verdict"].items()):
        pct = c / stats["total"] * 100 if stats["total"] else 0
        print(f"    {v:12s}: {c:4d}  ({pct:.0f}%)")


def cmd_tail(args: list[str]) -> None:
    n = int(args[0]) if args else 10
    entries = invocation_logger.tail(n)
    if not entries:
        print("  (log empty — no invocations recorded yet)")
        return
    print(f"\n  Last {len(entries)} invocations:")
    print(f"  {'─'*70}")
    for e in entries:
        print(f"  [{e['verdict']:15s}] {e['ts'][:19]}  {e['command']}  →  {str(e['result'])[:50]}")


def cmd_antibodies() -> None:
    registry = load_registry()
    print_registry(registry)


COMMANDS = {
    "log":        cmd_log,
    "trace":      cmd_trace,
    "report":     lambda _: cmd_report(),
    "burnrate":   lambda _: cmd_burnrate(),
    "tail":       cmd_tail,
    "antibodies": lambda _: cmd_antibodies(),
}


def main() -> None:
    cmd  = sys.argv[1] if len(sys.argv) > 1 else "help"
    rest = sys.argv[2:]

    if cmd in COMMANDS:
        COMMANDS[cmd](rest)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
