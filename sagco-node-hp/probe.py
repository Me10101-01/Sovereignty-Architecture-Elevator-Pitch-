#!/usr/bin/env python3
"""
SAGCO Node Probe — HP Sovereign Node
Reach, check, and report on the HP compute node from any SAGCO node.

Usage:
  python probe.py --node hp [--quick] [--json]
  python probe.py --ip 192.168.1.X [--quick]
"""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Config ─────────────────────────────────────────────────────────────────

NODES_CONFIG = Path.home() / ".sagco" / "nodes.json"

KNOWN_PORTS = {
    "ssh":    22,
    "ollama": 11434,
    "docker": 2375,
    "http":   80,
    "https":  443,
    "wsl":    None,   # internal, not directly reachable
}

DEFAULT_TIMEOUT = 3   # seconds


# ── Data ────────────────────────────────────────────────────────────────────

@dataclass
class ServiceResult:
    name:     str
    port:     Optional[int]
    reachable: bool
    latency_ms: Optional[float] = None
    detail:   str = ""


@dataclass
class ProbeResult:
    node:      str
    ip:        str
    timestamp: float = field(default_factory=time.time)
    ping_ok:   bool  = False
    ping_ms:   Optional[float] = None
    services:  list[ServiceResult] = field(default_factory=list)
    ollama_models: list[str] = field(default_factory=list)
    errors:    list[str] = field(default_factory=list)

    @property
    def reachable(self) -> bool:
        return self.ping_ok or any(s.reachable for s in self.services)

    @property
    def status(self) -> str:
        if not self.reachable:
            return "UNREACHABLE"
        live = sum(1 for s in self.services if s.reachable)
        total = len(self.services)
        return f"ALIVE ({live}/{total} services up)"


# ── Probe functions ─────────────────────────────────────────────────────────

def tcp_probe(ip: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> tuple[bool, Optional[float]]:
    try:
        t0 = time.perf_counter()
        with socket.create_connection((ip, port), timeout=timeout):
            ms = (time.perf_counter() - t0) * 1000
            return True, round(ms, 1)
    except (OSError, TimeoutError):
        return False, None


def ping_probe(ip: str) -> tuple[bool, Optional[float]]:
    import platform
    flag = "-n" if platform.system() == "Windows" else "-c"
    try:
        t0 = time.perf_counter()
        r = subprocess.run(
            ["ping", flag, "1", "-W", "2", ip],
            capture_output=True, timeout=5
        )
        ms = (time.perf_counter() - t0) * 1000
        ok = r.returncode == 0
        return ok, round(ms, 1) if ok else None
    except Exception:
        return False, None


def ollama_probe(ip: str, port: int = 11434, timeout: float = DEFAULT_TIMEOUT) -> list[str]:
    try:
        url = f"http://{ip}:{port}/api/tags"
        req = urllib.request.Request(url, headers={"User-Agent": "sagco-probe/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []


# ── Main probe ──────────────────────────────────────────────────────────────

def probe_node(ip: str, node_name: str = "hp", quick: bool = False) -> ProbeResult:
    result = ProbeResult(node=node_name, ip=ip)

    # ICMP ping
    result.ping_ok, result.ping_ms = ping_probe(ip)

    ports_to_check = ["ssh", "ollama"] if quick else ["ssh", "ollama", "docker", "http", "https"]

    for svc_name in ports_to_check:
        port = KNOWN_PORTS.get(svc_name)
        if port is None:
            continue
        ok, ms = tcp_probe(ip, port)
        svc = ServiceResult(name=svc_name, port=port, reachable=ok, latency_ms=ms)
        if ok:
            svc.detail = f"{ms}ms"
            if svc_name == "ollama":
                models = ollama_probe(ip, port)
                result.ollama_models = models
                svc.detail += f" | models: {len(models)}"
        result.services.append(svc)

    return result


# ── Node config ─────────────────────────────────────────────────────────────

def load_node_config(node_name: str) -> Optional[str]:
    """Return IP for named node from ~/.sagco/nodes.json."""
    if not NODES_CONFIG.exists():
        return None
    try:
        data = json.loads(NODES_CONFIG.read_text())
        return data.get("nodes", {}).get(node_name, {}).get("ip")
    except Exception:
        return None


def save_node_config(node_name: str, ip: str) -> None:
    NODES_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if NODES_CONFIG.exists():
        try:
            data = json.loads(NODES_CONFIG.read_text())
        except Exception:
            pass
    data.setdefault("nodes", {})[node_name] = {"ip": ip}
    NODES_CONFIG.write_text(json.dumps(data, indent=2))
    print(f"  Saved {node_name} → {ip} in {NODES_CONFIG}")


# ── Report ───────────────────────────────────────────────────────────────────

def print_report(r: ProbeResult) -> None:
    print()
    print("  ╔═══════════════════════════════════════════════════╗")
    print(f"  ║  SAGCO Node Probe — {r.node.upper():<30} ║")
    print("  ╚═══════════════════════════════════════════════════╝")
    print(f"  Node:      {r.node}")
    print(f"  IP:        {r.ip}")
    print(f"  Status:    {r.status}")
    ping_str = f"{r.ping_ms}ms" if r.ping_ms else "—"
    print(f"  Ping:      {'✓' if r.ping_ok else '✗'}  {ping_str}")
    print()
    print("  Services:")
    for svc in r.services:
        icon = "✓" if svc.reachable else "✗"
        lat  = f"  {svc.detail}" if svc.detail else ""
        print(f"    [{icon}] {svc.name:<10} :{svc.port}{lat}")
    if r.ollama_models:
        print()
        print("  Ollama models:")
        for m in r.ollama_models:
            print(f"    • {m}")
    if r.errors:
        print()
        print("  Errors:")
        for e in r.errors:
            print(f"    ! {e}")
    print()
    print("  ─────────────────────────────────────────────────────")
    if r.reachable:
        print("  QED: HP node is reachable ✓")
    else:
        print("  HP node not reachable.")
        print(f"  Check: is the HP on the same network? IP correct ({r.ip})?")
        print(f"  Set IP: sagco node hp set-ip <your-hp-ip>")
    print()


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(description="SAGCO Node Probe — HP")
    p.add_argument("--node",    default="hp",   help="Node name (default: hp)")
    p.add_argument("--ip",      default=None,   help="Override IP address")
    p.add_argument("--quick",   action="store_true", help="Only probe SSH + Ollama")
    p.add_argument("--json",    action="store_true", help="Output JSON")
    p.add_argument("--set-ip",  default=None,   help="Save IP to config and exit")
    args = p.parse_args()

    if args.set_ip:
        save_node_config(args.node, args.set_ip)
        return

    ip = args.ip or load_node_config(args.node)
    if not ip:
        print(f"[sagco-probe] No IP set for node '{args.node}'.")
        print(f"  Run: sagco node hp set-ip <your-hp-ip>")
        print(f"  Or:  python probe.py --node hp --set-ip 192.168.1.X")
        sys.exit(1)

    result = probe_node(ip, node_name=args.node, quick=args.quick)

    if args.json:
        print(json.dumps({
            "node": result.node, "ip": result.ip,
            "reachable": result.reachable, "status": result.status,
            "ping_ok": result.ping_ok, "ping_ms": result.ping_ms,
            "services": [
                {"name": s.name, "port": s.port, "reachable": s.reachable,
                 "latency_ms": s.latency_ms, "detail": s.detail}
                for s in result.services
            ],
            "ollama_models": result.ollama_models,
        }, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
