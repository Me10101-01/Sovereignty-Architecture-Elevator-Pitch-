"""
SAGCO Virtual Machine
Executes SAGCO AST nodes. Maintains a process table (PID map),
register file (tool nodes), and a shared token bus.
"""

from __future__ import annotations
import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .parser import CommandNode, PipelineNode, ScriptNode, parse


# ── Register file — one slot per tool node ─────────────────────────────────

TOOL_NODES = [
    "powershell", "remote_desktop", "git", "claude", "codex",
    "obsidian", "termux", "docker", "kubernetes", "redis",
    "rpi", "midi", "scanner", "compiler", "memory",
]


@dataclass
class Register:
    name: str
    bound_tool: str | None = None
    state: dict = field(default_factory=dict)


# ── Process / PID table ────────────────────────────────────────────────────

@dataclass
class Process:
    pid: str
    verb: str
    target: str | None
    status: str = "queued"     # queued | running | done | error
    result: Any = None
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None

    def finish(self, result: Any, error: bool = False) -> None:
        self.result = result
        self.status = "error" if error else "done"
        self.ended_at = time.time()


# ── Token bus ──────────────────────────────────────────────────────────────

@dataclass
class SAGCOToken:
    token_id: str
    source: str           # originating command verb
    payload: Any
    tags: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "token_id": self.token_id,
            "source":   self.source,
            "payload":  self.payload,
            "tags":     self.tags,
            "created_at": self.created_at,
        }


def _make_token(source: str, payload: Any, tags: list[str] | None = None) -> SAGCOToken:
    tid = hashlib.sha256(
        f"{source}:{json.dumps(payload, default=str)}:{time.time()}".encode()
    ).hexdigest()[:16]
    return SAGCOToken(token_id=tid, source=source, payload=payload, tags=tags or [])


# ── Instruction handlers ────────────────────────────────────────────────────

class VM:
    def __init__(self, workspace: str | Path = ".") -> None:
        self.workspace = Path(workspace)
        self.registers: dict[str, Register] = {
            n: Register(name=n) for n in TOOL_NODES
        }
        self.pid_table: dict[str, Process] = {}
        self.bus: list[SAGCOToken] = []
        self._handlers: dict[str, Callable[[CommandNode, Process], Any]] = {
            "crawl":    self._exec_crawl,
            "ingest":   self._exec_ingest,
            "emit":     self._exec_emit,
            "link":     self._exec_link,
            "spawn":    self._exec_spawn,
            "halt":     self._exec_halt,
            "deploy":   self._exec_deploy,
            "status":   self._exec_status,
            "dna":      self._exec_dna,
            "pipeline": self._exec_pipeline_cmd,
            "vm":       self._exec_vm_meta,
            "run":      self._exec_run,
            "audit":    self._exec_audit,
            "sync":     self._exec_sync,
            "boot":     self._exec_boot,
            "convert":  self._exec_convert,
        }

    # ── PID management ──────────────────────────────────────────────────────

    def _spawn_pid(self, verb: str, target: str | None) -> Process:
        pid = str(uuid.uuid4())[:8]
        proc = Process(pid=pid, verb=verb, target=target, status="running")
        self.pid_table[pid] = proc
        return proc

    def _emit_token(self, source: str, payload: Any, tags: list[str] | None = None) -> SAGCOToken:
        tok = _make_token(source, payload, tags)
        self.bus.append(tok)
        return tok

    # ── Script / pipeline execution ─────────────────────────────────────────

    def execute(self, source: str) -> list[Process]:
        script = parse(source)
        procs: list[Process] = []
        for pipeline in script.pipelines:
            procs.extend(self._run_pipeline(pipeline))
        return procs

    def _run_pipeline(self, pipeline: PipelineNode) -> list[Process]:
        procs: list[Process] = []
        prev_token: SAGCOToken | None = None
        for cmd in pipeline.stages:
            proc = self._run_command(cmd, prev_token)
            procs.append(proc)
            if proc.result and isinstance(proc.result, SAGCOToken):
                prev_token = proc.result
        return procs

    def _run_command(self, cmd: CommandNode,
                     incoming: SAGCOToken | None = None) -> Process:
        proc = self._spawn_pid(cmd.verb, cmd.target)
        handler = self._handlers.get(cmd.verb)
        if handler is None:
            proc.finish(f"unknown verb: {cmd.verb}", error=True)
            return proc
        try:
            result = handler(cmd, proc)
            proc.finish(result)
        except Exception as exc:
            proc.finish(str(exc), error=True)
        return proc

    # ── Instruction set ─────────────────────────────────────────────────────

    def _exec_crawl(self, cmd: CommandNode, proc: Process) -> SAGCOToken:
        root = self.workspace / (cmd.target or ".")
        depth = int(cmd.flag("depth", 3))
        emit_format = cmd.flag("emit", "tokens")
        nodes: list[dict] = []

        def _walk(path: Path, current_depth: int) -> None:
            if current_depth > depth:
                return
            for entry in sorted(path.iterdir()):
                if entry.name.startswith("."):
                    continue
                node = {
                    "path": str(entry.relative_to(self.workspace)),
                    "type": "dir" if entry.is_dir() else "file",
                    "depth": current_depth,
                }
                nodes.append(node)
                if entry.is_dir():
                    _walk(entry, current_depth + 1)

        if root.exists():
            _walk(root, 1)

        payload = {"root": str(root), "depth": depth, "nodes": nodes, "format": emit_format}
        tok = self._emit_token("crawl", payload, tags=["filesystem", "topology"])
        return tok

    def _exec_ingest(self, cmd: CommandNode, proc: Process) -> SAGCOToken:
        target = cmd.target or "README.md"
        path = self.workspace / target
        convert = cmd.flag("convert", "raw")

        content = path.read_text(errors="replace") if path.exists() else f"[not found: {path}]"

        payload = {
            "file": target,
            "size": len(content),
            "format": convert,
            "content": content[:4096],   # first 4 KB on the bus
        }
        tok = self._emit_token("ingest", payload, tags=["document", convert])
        return tok

    def _exec_emit(self, cmd: CommandNode, proc: Process) -> SAGCOToken:
        payload = {"target": cmd.target, "flags": {f.key: f.value for f in cmd.flags}}
        tok = self._emit_token("emit", payload, tags=["signal"])
        return tok

    def _exec_link(self, cmd: CommandNode, proc: Process) -> dict:
        parts = (cmd.target or "").split(",")
        node_a = parts[0].strip() if parts else "?"
        node_b = parts[1].strip() if len(parts) > 1 else "?"
        edge = {"from": node_a, "to": node_b, "weight": cmd.flag("weight", 1)}
        self._emit_token("link", edge, tags=["graph", "edge"])
        return edge

    def _exec_spawn(self, cmd: CommandNode, proc: Process) -> dict:
        agent = cmd.target or "anonymous"
        config = {f.key: f.value for f in cmd.flags}
        child_pid = str(uuid.uuid4())[:8]
        child = Process(pid=child_pid, verb="agent", target=agent, status="running")
        self.pid_table[child_pid] = child
        self._emit_token("spawn", {"agent": agent, "pid": child_pid, "config": config},
                         tags=["agent", "spawn"])
        return {"agent": agent, "child_pid": child_pid}

    def _exec_halt(self, cmd: CommandNode, proc: Process) -> dict:
        pid = cmd.target or cmd.flag("pid", "")
        if pid and pid in self.pid_table:
            self.pid_table[pid].status = "halted"
            return {"halted": pid}
        return {"halted": None, "error": f"pid {pid!r} not found"}

    def _exec_deploy(self, cmd: CommandNode, proc: Process) -> dict:
        target = cmd.flag("target", "local")
        host = cmd.flag("host", "localhost")
        branch = cmd.flag("branch", "main")
        payload = {"target": target, "host": host, "branch": branch}
        self._emit_token("deploy", payload, tags=["deploy", target])
        return payload

    def _exec_status(self, cmd: CommandNode, proc: Process) -> dict:
        return {
            "pids": len(self.pid_table),
            "bus_tokens": len(self.bus),
            "registers": {k: v.bound_tool for k, v in self.registers.items()},
        }

    def _exec_dna(self, cmd: CommandNode, proc: Process) -> SAGCOToken:
        from .dna_cell import ingest_to_dna
        target = cmd.target or "README.md"
        path = self.workspace / target
        content = path.read_text(errors="replace") if path.exists() else ""
        cell = ingest_to_dna(name=target, content=content, source_path=str(path))
        tok = self._emit_token("dna", cell, tags=["dna", "cell"])
        return tok

    def _exec_pipeline_cmd(self, cmd: CommandNode, proc: Process) -> dict:
        from .crawler import StepperCrawler
        root = self.workspace / (cmd.target or ".")
        crawler = StepperCrawler(root, vm=self)
        return crawler.run()

    def _exec_vm_meta(self, cmd: CommandNode, proc: Process) -> dict:
        sub = cmd.target or "status"
        if sub == "status":
            return self._exec_status(cmd, proc)
        elif sub == "pids":
            return {pid: p.status for pid, p in self.pid_table.items()}
        elif sub == "bus":
            return [t.to_dict() for t in self.bus[-10:]]
        return {"sub": sub, "error": "unknown vm sub-command"}

    def _exec_run(self, cmd: CommandNode, proc: Process) -> dict:
        sub = cmd.target or ""
        return {"run": sub, "status": "dispatched"}

    def _exec_audit(self, cmd: CommandNode, proc: Process) -> dict:
        target = self.workspace / (cmd.target or ".")
        findings: list[dict] = []
        if target.is_dir():
            for p in sorted(target.rglob("*")):
                if not p.name.startswith(".") and p.is_file():
                    findings.append({"file": str(p.relative_to(self.workspace)),
                                     "size": p.stat().st_size})
        self._emit_token("audit", {"findings": findings}, tags=["audit"])
        return {"files_found": len(findings)}

    def _exec_sync(self, cmd: CommandNode, proc: Process) -> dict:
        source = cmd.target
        dest = cmd.flag("dest", "remote")
        return {"sync": source, "dest": dest, "status": "queued"}

    def _exec_boot(self, cmd: CommandNode, proc: Process) -> dict:
        profile = cmd.target or "default"
        for name in TOOL_NODES:
            self.registers[name].bound_tool = name
        self._emit_token("boot", {"profile": profile, "registers": TOOL_NODES}, tags=["boot"])
        return {"booted": profile, "registers": len(self.registers)}

    def _exec_convert(self, cmd: CommandNode, proc: Process) -> SAGCOToken:
        target = cmd.target or "README.md"
        fmt = cmd.flag("format", "dna")
        return self._exec_dna(
            type("_", (), {"target": target, "flags": [], "flag": lambda k, d=None: None})(),
            proc
        )

    # ── Introspection helpers ───────────────────────────────────────────────

    def pid_table_dump(self) -> list[dict]:
        return [
            {
                "pid": p.pid, "verb": p.verb, "target": p.target,
                "status": p.status, "elapsed": round(
                    (p.ended_at or time.time()) - p.started_at, 4
                ),
            }
            for p in self.pid_table.values()
        ]

    def bus_dump(self) -> list[dict]:
        return [t.to_dict() for t in self.bus]


if __name__ == "__main__":
    import sys
    src = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
          "sagco boot default | sagco crawl ./sagco --depth=2 | sagco dna README.md"
    vm = VM()
    procs = vm.execute(src)
    print(json.dumps(vm.pid_table_dump(), indent=2))
    print(f"\nBus tokens: {len(vm.bus)}")
