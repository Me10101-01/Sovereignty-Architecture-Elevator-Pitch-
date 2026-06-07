"""
SAGCO True Language — Bytecode Virtual Machine
Executes compiled SAGCO bytecode. Owns its own stack, memory, signal bus,
process table, and world context. No external runtime dependencies.
"""

from __future__ import annotations
import hashlib
import os
import platform
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from ..bytecode.opcodes import Bytecode, Instruction, Op


# ── World detection (stdlib-only) ─────────────────────────────────────────

def detect_world() -> str:
    """Identify the execution environment with zero external deps."""
    # Termux
    if os.environ.get("TERMUX_VERSION") or os.path.exists("/data/data/com.termux"):
        return "termux"
    # Docker
    if os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"):
        return "docker"
    # Kubernetes
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "kubernetes"
    # WSL
    if "microsoft" in platform.uname().release.lower():
        return "wsl"
    # Windows
    if platform.system() == "Windows":
        return "windows"
    # Linux
    if platform.system() == "Linux":
        return "linux"
    # macOS
    if platform.system() == "Darwin":
        return "darwin"
    return "unknown"


# ── Process record ────────────────────────────────────────────────────────

@dataclass
class Process:
    pid: str
    label: str
    status: str = "running"    # running | done | error | halted
    started: float = field(default_factory=time.time)
    ended: float | None = None

    def finish(self, ok: bool = True) -> None:
        self.status = "done" if ok else "error"
        self.ended = time.time()


# ── Signal (emitted events) ───────────────────────────────────────────────

@dataclass
class Signal:
    name: str
    payload: dict = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


# ── Wafer result ──────────────────────────────────────────────────────────

@dataclass
class WaferResult:
    name: str
    expected: Any
    actual: Any
    passed: bool
    mode: str = "required"


# ── Virtual Machine ───────────────────────────────────────────────────────

class SAGCOVirtualMachine:
    def __init__(self) -> None:
        self.stack: list[Any] = []
        self.memory: dict[str, Any] = {}
        self.bus: list[Signal] = []
        self.pid_table: dict[str, Process] = {}
        self.world: str = detect_world()
        self.wafer_results: list[WaferResult] = []
        self._procs: dict[str, list[Instruction]] = {}   # named procedures
        self._ip: int = 0

        # seed identity
        self.memory["world"] = self.world
        self.memory["sagco.version"] = "0.1.0"

    # ── stack helpers ──────────────────────────────────────────────────────

    def _push(self, val: Any) -> None:
        self.stack.append(val)

    def _pop(self) -> Any:
        return self.stack.pop() if self.stack else None

    def _peek_stack(self) -> Any:
        return self.stack[-1] if self.stack else None

    # ── execution ──────────────────────────────────────────────────────────

    def run(self, bytecode: Bytecode) -> dict:
        """Execute bytecode. Returns final memory state."""
        instructions = bytecode.instructions
        n = len(instructions)
        # index labels for jumps
        labels: dict[str, int] = {}
        for i, instr in enumerate(instructions):
            if instr.op == Op.LABEL:
                labels[str(instr.operand)] = i

        call_stack: list[int] = []
        ip = 0
        proc = self._new_proc("__main__")

        while ip < n:
            instr = instructions[ip]
            op = instr.op
            operand = instr.operand
            ip += 1

            if op == Op.NOP or op == Op.LABEL:
                continue

            elif op == Op.PUSH:
                self._push(operand)

            elif op == Op.POP:
                self._pop()

            elif op == Op.DUP:
                self._push(self._peek_stack())

            elif op == Op.SWAP:
                a, b = self._pop(), self._pop()
                self._push(a); self._push(b)

            elif op == Op.LOAD:
                self._push(self.memory.get(operand))

            elif op == Op.STORE:
                val = self._pop()
                self.memory[operand] = val

            elif op == Op.FORGET:
                self.memory.pop(operand, None)

            elif op == Op.EMIT:
                # collect payload items from stack until we hit a non-kv string
                payload: dict = {}
                # payload was pushed as "key=value" strings before EMIT
                while self.stack and isinstance(self._peek_stack(), str) and "=" in str(self._peek_stack()):
                    kv = self._pop()
                    k, _, v = str(kv).partition("=")
                    payload[k] = v
                self.bus.append(Signal(operand, payload))

            elif op == Op.MEASURE:
                self._run_measure(operand)

            elif op == Op.MATCH:
                actual = self._pop()
                expected = self._pop()
                result = (expected == actual) or (
                    isinstance(expected, bool) and isinstance(actual, bool) and expected == actual
                )
                self._push(result)

            elif op == Op.DETECT:
                self._push(self._detect(operand))

            elif op == Op.WORLD:
                self._push(self.world)

            elif op == Op.EQ:
                b, a = self._pop(), self._pop()
                self._push(a == b)

            elif op == Op.NEQ:
                b, a = self._pop(), self._pop()
                self._push(a != b)

            elif op == Op.JUMP:
                target = str(operand)
                if target in labels:
                    ip = labels[target] + 1
                elif isinstance(operand, int):
                    ip = operand

            elif op == Op.JUMP_IF:
                cond = self._pop()
                if cond:
                    target = str(operand)
                    if target in labels:
                        ip = labels[target] + 1

            elif op == Op.JUMP_NOT:
                cond = self._pop()
                if not cond:
                    target = str(operand)
                    if target in labels:
                        ip = labels[target] + 1

            elif op == Op.CALL:
                target_label = f"__do__{operand}"
                if target_label in labels:
                    call_stack.append(ip)
                    ip = labels[target_label] + 1
                # else: unknown call, skip silently (boot steps may not be defined yet)

            elif op == Op.RETURN:
                if call_stack:
                    ip = call_stack.pop()

            elif op == Op.SPAWN:
                child = self._new_proc(str(operand))
                self._push(child.pid)

            elif op == Op.HALT:
                proc.finish(ok=True)
                break

            elif op == Op.DEBUG:
                pass  # silent in production

            elif op == Op.READ:
                try:
                    content = open(str(operand)).read()
                    self._push(content)
                except Exception:
                    self._push(None)

            elif op == Op.WRITE:
                val = self._pop()
                try:
                    with open(str(operand), "w") as f:
                        f.write(str(val))
                    self._push(True)
                except Exception:
                    self._push(False)

        proc.finish(ok=True)
        return dict(self.memory)

    def _new_proc(self, label: str) -> Process:
        pid = hashlib.sha256(f"{label}:{time.time()}".encode()).hexdigest()[:8]
        proc = Process(pid=pid, label=label)
        self.pid_table[pid] = proc
        return proc

    def _detect(self, query: Any) -> Any:
        q = str(query).lower().strip()
        if q in ("world", "detect_world"):
            return self.world
        if q in ("python", "python_version"):
            import sys
            return f"{sys.version_info.major}.{sys.version_info.minor}"
        if q.startswith("env:"):
            return os.environ.get(q[4:], "")
        if q.startswith("file:"):
            return os.path.exists(q[5:])
        if q.startswith("path:"):
            return os.path.exists(q[5:])
        return None

    def _run_measure(self, wafer_name: str) -> None:
        if wafer_name == "all_wafers":
            # re-run all stored wafer definitions
            for key, val in self.memory.items():
                if key.startswith("wafer.") and key.endswith(".result"):
                    name = key[len("wafer."):-len(".result")]
                    exp = self.memory.get(f"wafer.{name}.expected")
                    act = self.memory.get(f"wafer.{name}.actual")
                    mode = self.memory.get(f"wafer.{name}.mode", "required")
                    passed = (exp == act)
                    self.wafer_results.append(WaferResult(name, exp, act, passed, mode))
        else:
            exp = self.memory.get(f"wafer.{wafer_name}.expected")
            act = self.memory.get(f"wafer.{wafer_name}.actual")
            mode = self.memory.get(f"wafer.{wafer_name}.mode", "required")
            passed = self.memory.get(f"wafer.{wafer_name}.result", exp == act)
            self.wafer_results.append(WaferResult(wafer_name, exp, act, bool(passed), mode))

    def truth_report(self) -> dict:
        total = len(self.wafer_results)
        passed = sum(1 for w in self.wafer_results if w.passed)
        failed = [w for w in self.wafer_results if not w.passed and w.mode == "required"]
        return {
            "total": total,
            "passed": passed,
            "failed_required": len(failed),
            "status": "TRUE_ENOUGH_TO_GROW" if not failed else "NEEDS_HEALING",
            "wafers": [
                {"name": w.name, "expected": w.expected,
                 "actual": w.actual, "passed": w.passed, "mode": w.mode}
                for w in self.wafer_results
            ],
        }

    def pid_dump(self) -> list[dict]:
        return [
            {"pid": p.pid, "label": p.label, "status": p.status,
             "elapsed": round((p.ended or time.time()) - p.started, 4)}
            for p in self.pid_table.values()
        ]


def run_file(path: str) -> SAGCOVirtualMachine:
    from ..bytecode.compiler import compile_source
    source = open(path).read()
    bc = compile_source(source, path)
    vm = SAGCOVirtualMachine()
    vm.run(bc)
    return vm


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("usage: python -m sagco_true.language.vm.vm <file.sagco>")
        sys.exit(1)
    vm = run_file(sys.argv[1])
    print(json.dumps(vm.truth_report(), indent=2))
    print(f"\nWorld:  {vm.world}")
    print(f"Memory: {len(vm.memory)} keys")
    print(f"Bus:    {len(vm.bus)} signals")
