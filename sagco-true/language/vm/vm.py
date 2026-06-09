"""
SAGCO True Language — Bytecode Virtual Machine
Executes compiled SAGCO bytecode. Owns its own stack, memory, signal bus,
process table, and world context. No external runtime dependencies.
"""

from __future__ import annotations
import hashlib
import json
import math
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

@dataclass
class TickRecord:
    label: str
    seal: str        # SHA-256 of (label + state_hash + parent_seal)
    state_hash: str  # SHA-256 of memory snapshot at tick time
    ts: float
    parent: str      # seal of previous tick in chain (empty = genesis)


@dataclass
class BondRecord:
    name: str
    a: str
    b: str
    strength: str = "required"  # required | optional (covalent | ionic)


@dataclass
class ProofScope:
    name: str
    assertions: list[dict] = field(default_factory=list)
    passed: bool = True


# ── Unit system — frequency/chemistry/geometry need this ──────────────────

UNIT_CONVERSIONS: dict[str, dict[str, float]] = {
    # frequency
    "hz":  {"rpm": 60.0,  "rad_s": 2 * math.pi,  "khz": 0.001,  "mhz": 1e-6},
    "rpm": {"hz": 1/60,   "rad_s": 2*math.pi/60},
    "khz": {"hz": 1000,   "mhz": 0.001},
    "mhz": {"hz": 1e6,    "khz": 1000},
    "rad_s": {"hz": 1/(2*math.pi), "rpm": 60/(2*math.pi)},
    # angles
    "deg": {"rad": math.pi/180, "grad": 10/9},
    "rad": {"deg": 180/math.pi, "grad": 200/math.pi},
    # distance
    "m":   {"ft": 3.28084, "in": 39.3701, "mm": 1000, "cm": 100, "km": 0.001},
    "ft":  {"m": 0.3048,   "in": 12,      "mm": 304.8},
    "in":  {"m": 0.0254,   "ft": 1/12,    "mm": 25.4, "cm": 2.54},
    "mm":  {"m": 0.001,    "in": 1/25.4,  "cm": 0.1},
    "cm":  {"m": 0.01,     "in": 1/2.54,  "mm": 10},
    # color/light
    "nm":  {"um": 0.001,   "ang": 10},   # nanometer wavelength
    "ang": {"nm": 0.1},                   # Angstrom
}


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
        self._ticks: list[TickRecord] = []
        self._bonds: dict[str, BondRecord] = {}
        self._proof_stack: list[ProofScope] = []
        self._periods: dict[str, float] = {}  # label -> period in seconds

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

            # ── Arithmetic ────────────────────────────────────────────────
            elif op == Op.ADD:
                b, a = self._pop(), self._pop()
                try:
                    self._push(a + b)
                except TypeError:
                    self._push(str(a) + str(b))

            elif op == Op.SUB:
                b, a = self._pop(), self._pop()
                try:
                    self._push(a - b)
                except TypeError:
                    self._push(None)

            elif op == Op.MUL:
                b, a = self._pop(), self._pop()
                try:
                    self._push(a * b)
                except TypeError:
                    self._push(None)

            elif op == Op.DIV:
                b, a = self._pop(), self._pop()
                self._push(a / b if b else None)

            elif op == Op.MOD:
                b, a = self._pop(), self._pop()
                self._push(a % b if b else None)

            elif op == Op.NEG:
                self._push(-self._pop())

            elif op == Op.ABS:
                self._push(abs(self._pop()))

            # ── Bitwise ───────────────────────────────────────────────────
            elif op == Op.B_AND:
                b, a = int(self._pop()), int(self._pop())
                self._push(a & b)

            elif op == Op.B_OR:
                b, a = int(self._pop()), int(self._pop())
                self._push(a | b)

            elif op == Op.B_XOR:
                b, a = int(self._pop()), int(self._pop())
                self._push(a ^ b)

            elif op == Op.B_NOT:
                self._push(~int(self._pop()))

            elif op == Op.B_SHL:
                n = int(operand) if operand is not None else int(self._pop())
                self._push(int(self._pop()) << n)

            elif op == Op.B_SHR:
                n = int(operand) if operand is not None else int(self._pop())
                self._push(int(self._pop()) >> n)

            # ── Alchemical cast ───────────────────────────────────────────
            elif op == Op.CAST:
                val = self._pop()
                target = str(operand).lower() if operand else "str"
                try:
                    if target in ("int", "integer"):
                        self._push(int(float(str(val))))
                    elif target in ("float", "number", "real"):
                        self._push(float(str(val)))
                    elif target in ("str", "string", "text"):
                        self._push(str(val))
                    elif target in ("bool", "boolean"):
                        self._push(bool(val))
                    else:
                        self._push(val)
                except (ValueError, TypeError):
                    self._push(None)

            elif op == Op.TYPE_OF:
                val = self._peek_stack()
                name = type(val).__name__
                self._push(name)

            # ── Units (frequency / chemistry / geometry) ──────────────────
            elif op == Op.UNIT:
                val = self._pop()
                symbol = str(operand).lower() if operand else "?"
                self._push({"__sagco_unit__": symbol, "value": val})

            elif op == Op.CONVERT:
                target = str(operand).lower() if operand else ""
                top = self._pop()
                if isinstance(top, dict) and "__sagco_unit__" in top:
                    src = top["__sagco_unit__"]
                    val = top["value"]
                    factor = UNIT_CONVERSIONS.get(src, {}).get(target)
                    if factor is not None:
                        self._push({"__sagco_unit__": target, "value": val * factor})
                    else:
                        self._push({"__sagco_unit__": target, "value": val, "conversion": "unknown"})
                else:
                    self._push({"__sagco_unit__": target, "value": top})

            elif op == Op.MAGNITUDE:
                top = self._pop()
                if isinstance(top, dict) and "__sagco_unit__" in top:
                    self._push(top["value"])
                else:
                    self._push(top)

            # ── Binding (electronegativity model) ─────────────────────────
            elif op == Op.BIND:
                b = str(self._pop())
                a = str(self._pop())
                name = str(operand) if operand else f"{a}:{b}"
                strength = "required"
                self._bonds[name] = BondRecord(name, a, b, strength)
                self.memory[f"bond.{name}"] = {"a": a, "b": b, "strength": strength}

            elif op == Op.RELEASE:
                name = str(operand) if operand else ""
                self._bonds.pop(name, None)
                self.memory.pop(f"bond.{name}", None)

            elif op == Op.BONDS:
                self._push([{"name": b.name, "a": b.a, "b": b.b, "strength": b.strength}
                             for b in self._bonds.values()])

            # ── Tick / temporal sovereignty ───────────────────────────────
            elif op == Op.TICK:
                label = str(operand) if operand else f"tick_{len(self._ticks)}"
                state_snapshot = json.dumps(
                    {k: str(v) for k, v in self.memory.items()}, sort_keys=True
                ).encode()
                state_hash = hashlib.sha256(state_snapshot).hexdigest()
                parent_seal = self._ticks[-1].seal if self._ticks else ""
                raw = f"{label}:{state_hash}:{parent_seal}:{time.time()}".encode()
                seal = hashlib.sha256(raw).hexdigest()
                rec = TickRecord(label, seal, state_hash, time.time(), parent_seal)
                self._ticks.append(rec)
                self.memory[f"tick.{label}.seal"] = seal
                self.memory[f"tick.{label}.ts"] = rec.ts
                self._push(seal)

            elif op == Op.TICK_GET:
                label = str(operand) if operand else ""
                tick = next((t for t in reversed(self._ticks) if t.label == label), None)
                self._push({"label": tick.label, "seal": tick.seal, "ts": tick.ts} if tick else None)

            elif op == Op.TICK_VERIFY:
                label = str(operand) if operand else ""
                ticks_for = [t for t in self._ticks if t.label == label]
                ok = True
                for i, t in enumerate(ticks_for):
                    expected_parent = ticks_for[i-1].seal if i > 0 else ""
                    if t.parent != expected_parent:
                        ok = False
                        break
                self._push(ok)

            # ── Proof / invariant assertions ──────────────────────────────
            elif op == Op.PROOF:
                name = str(operand) if operand else f"proof_{len(self._proof_stack)}"
                self._proof_stack.append(ProofScope(name))

            elif op == Op.ASSERT:
                msg = str(operand) if operand else "assertion"
                val = self._pop()
                passed = bool(val)
                entry = {"msg": msg, "passed": passed}
                if self._proof_stack:
                    self._proof_stack[-1].assertions.append(entry)
                    if not passed:
                        self._proof_stack[-1].passed = False
                if not passed:
                    self.bus.append(Signal("PROOF_VIOLATION", {"msg": msg, "status": "CRITICAL"}))

            elif op == Op.QED:
                if self._proof_stack:
                    scope = self._proof_stack.pop()
                    passed = scope.passed
                    self.memory[f"proof.{scope.name}.passed"] = passed
                    self.memory[f"proof.{scope.name}.assertions"] = len(scope.assertions)
                    self.bus.append(Signal("QED", {"proof": scope.name, "passed": passed}))
                    self._push(passed)

            # ── Pipeline / transform chain ────────────────────────────────
            elif op == Op.PIPE:
                proc_name = str(operand) if operand else ""
                val = self._pop()
                target_label = f"__do__{proc_name}"
                if target_label in labels:
                    self._push(val)
                    call_stack.append(ip)
                    ip = labels[target_label] + 1
                else:
                    self._push(val)   # pass through unchanged

            elif op == Op.COMPOSE:
                n = int(operand) if operand else 2
                procs = [str(self._pop()) for _ in range(n)]
                procs.reverse()
                self._push({"__sagco_composed__": procs})

            elif op == Op.FOLD:
                proc_name = str(operand) if operand else ""
                lst = self._pop()
                if not isinstance(lst, list) or not lst:
                    self._push(None)
                else:
                    acc = lst[0]
                    target_label = f"__do__{proc_name}"
                    for item in lst[1:]:
                        if target_label in labels:
                            self._push(acc)
                            self._push(item)
                            call_stack.append(ip)
                            ip = labels[target_label] + 1
                        acc = self._pop() if self.stack else acc
                    self._push(acc)

            # ── Frequency / periodicity ───────────────────────────────────
            elif op == Op.PERIOD:
                label = str(operand) if operand else "default"
                val = self._pop()
                try:
                    self._periods[label] = float(val)
                    self.memory[f"period.{label}"] = float(val)
                except (TypeError, ValueError):
                    pass

            elif op == Op.FREQUENCY:
                val = self._pop()
                try:
                    p = float(val)
                    self._push(1.0 / p if p != 0 else None)
                except (TypeError, ValueError):
                    self._push(None)

            elif op == Op.PHASE:
                label = str(operand) if operand else "default"
                period = self._periods.get(label, 1.0)
                start_key = f"period.{label}.start"
                started = self.memory.get(start_key, time.time())
                self.memory.setdefault(start_key, started)
                elapsed = time.time() - started
                phase = (elapsed % period) / period if period else 0.0
                self._push(round(phase, 6))

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
        proof_violations = [
            s for s in self.bus if s.name == "PROOF_VIOLATION"
        ]
        irrefutable = not failed and not proof_violations
        return {
            "total": total,
            "passed": passed,
            "failed_required": len(failed),
            "proof_violations": len(proof_violations),
            "tick_chain_length": len(self._ticks),
            "active_bonds": len(self._bonds),
            "status": "IRREFUTABLE" if irrefutable and total > 0
                      else ("TRUE_ENOUGH_TO_GROW" if not failed else "NEEDS_HEALING"),
            "wafers": [
                {"name": w.name, "expected": w.expected,
                 "actual": w.actual, "passed": w.passed, "mode": w.mode}
                for w in self.wafer_results
            ],
            "ticks": [
                {"label": t.label, "seal": t.seal[:16] + "...", "ts": t.ts}
                for t in self._ticks
            ],
            "bonds": [
                {"name": b.name, "a": b.a, "b": b.b, "strength": b.strength}
                for b in self._bonds.values()
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
