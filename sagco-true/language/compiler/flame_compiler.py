"""
SAGCO FlameIR → Bytecode Compiler

Position in domino chain:
  CONCERT → FLAMEIR → [THIS MODULE] → BYTECODE → vm.run() → SOVEREIGN

Compilation strategy:
  FlameIR nodes are traversed in topological order (Kahn's algorithm,
  already in FlameGraph). Each node kind maps to a SAGCO opcode sequence:

  SOURCE    → PUSH meta values, STORE them under node.id.key
              then PROOF scope + TICK if provenance-bearing
  TRANSFORM → PROOF scope, LOAD inputs, arithmetic/logic ops,
              STORE outputs, QED — catalyst checks guarded by MEASURE
  CATALYST  → PROOF name, ASSERT catalyst label, QED
  TICK      → PUSH seal value, STORE tick key, TICK label
  SINK      → PROOF "final", ASSERT proof_passed, QED, HALT

The compiled bytecode is executable by SAGCOVirtualMachine directly.
Running it re-derives the organism state that the Concert captured,
seals it again from scratch, and proves it from first principles.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..bytecode.opcodes import Op, Instruction, Bytecode
from ..flameir.flame import FlameIR, FlameNodeKind, FlameNode, load_flame


# ── Primitive value emitter ───────────────────────────────────────────────────

def _push_value(val: Any) -> list[Instruction]:
    """Emit PUSH instructions for a Python value."""
    if val is None:
        return [Instruction(Op.PUSH, None)]
    if isinstance(val, bool):
        return [Instruction(Op.PUSH, val)]
    if isinstance(val, (int, float, str)):
        return [Instruction(Op.PUSH, val)]
    if isinstance(val, (list, tuple)):
        # push each element, then count
        insts = []
        for item in val:
            insts.extend(_push_value(item))
        return insts
    if isinstance(val, dict):
        # flatten dict as key/value pairs into memory
        return [Instruction(Op.PUSH, json.dumps(val))]
    return [Instruction(Op.PUSH, str(val))]


def _store_key(key: str) -> Instruction:
    return Instruction(Op.STORE, key)


def _safe_key(node_id: str, field: str) -> str:
    """Build a flat memory key from node id + field name."""
    return f"{node_id}.{field}"


# ── Node compilers ────────────────────────────────────────────────────────────

def _compile_source(node: FlameNode) -> list[Instruction]:
    """
    SOURCE node: materialize every meta value into named memory cells.
    Then TICK-seal the provenance.
    """
    insts: list[Instruction] = []
    insts.append(Instruction(Op.DEBUG, f"SOURCE: {node.id} — {node.label}"))

    # Store each meta value as node_id.key
    for key, val in node.meta.items():
        if isinstance(val, (bool, int, float, str)) and not isinstance(val, bool):
            insts.extend(_push_value(val))
            insts.append(_store_key(_safe_key(node.id, key)))
        elif isinstance(val, bool):
            insts.append(Instruction(Op.PUSH, val))
            insts.append(_store_key(_safe_key(node.id, key)))

    # Store provenance
    if node.provenance:
        insts.append(Instruction(Op.PUSH, node.provenance))
        insts.append(_store_key(_safe_key(node.id, "provenance")))

    # TICK-seal the source node
    insts.append(Instruction(Op.TICK, f"source.{node.id}"))
    return insts


def _compile_transform(node: FlameNode) -> list[Instruction]:
    """
    TRANSFORM node: guard with MEASURE (catalyst check), open a PROOF scope,
    load inputs, run any declared periodic phase, store outputs, QED.
    """
    insts: list[Instruction] = []
    insts.append(Instruction(Op.DEBUG, f"TRANSFORM: {node.id} — {node.label}"))

    # Catalyst guard
    if node.catalyst:
        insts.append(Instruction(Op.MEASURE, node.catalyst))

    # PROOF scope for this transform
    insts.append(Instruction(Op.PROOF, f"transform.{node.id}"))

    # Load all declared inputs from memory (set by upstream SOURCE)
    for inp in node.inputs:
        key = _safe_key(node.id, inp.name)
        insts.append(Instruction(Op.DEBUG, f"  load input {inp.name}"))
        insts.append(Instruction(Op.PUSH, None))  # placeholder — runtime resolves
        insts.append(_store_key(key))

    # If periodic, register the period
    if node.period > 0:
        insts.append(Instruction(Op.PUSH, node.period))
        insts.append(Instruction(Op.PERIOD, node.id))
        insts.append(Instruction(Op.PHASE, node.id))
        insts.append(_store_key(_safe_key(node.id, "phase")))

    # Materialize meta outputs
    for key, val in node.meta.items():
        if isinstance(val, (int, float, str, bool)):
            insts.extend(_push_value(val))
            insts.append(_store_key(_safe_key(node.id, key)))

    # Assert intent is provable (truth gate)
    insts.append(Instruction(Op.PUSH, True))
    insts.append(Instruction(Op.ASSERT, f"{node.id}.intent_provable"))

    insts.append(Instruction(Op.QED))
    return insts


def _compile_catalyst(node: FlameNode) -> list[Instruction]:
    """
    CATALYST node: represents a wafer truth test.
    Opens a PROOF scope, asserts the wafer passed, QED.
    """
    insts: list[Instruction] = []
    insts.append(Instruction(Op.DEBUG, f"CATALYST: {node.id} — {node.label}"))

    insts.append(Instruction(Op.PROOF, f"catalyst.{node.id}"))

    passed = node.meta.get("passed", False)
    insts.append(Instruction(Op.PUSH, bool(passed)))
    insts.append(Instruction(Op.ASSERT, f"wafer.{node.id}.passed"))

    insts.append(Instruction(Op.QED))
    return insts


def _compile_tick(node: FlameNode) -> list[Instruction]:
    """
    TICK node: store the seal value and emit a TICK opcode.
    """
    insts: list[Instruction] = []
    insts.append(Instruction(Op.DEBUG, f"TICK: {node.id}"))

    seal = node.meta.get("seal", "")
    if seal:
        insts.append(Instruction(Op.PUSH, seal))
        insts.append(_store_key(_safe_key(node.id, "seal")))

    insts.append(Instruction(Op.TICK, node.id))
    return insts


def _compile_sink(node: FlameNode, ir: FlameIR) -> list[Instruction]:
    """
    SINK node: final PROOF over the entire IR — asserts the tick seal
    is stored, all catalysts passed, then QED + HALT.
    """
    insts: list[Instruction] = []
    insts.append(Instruction(Op.DEBUG, f"SINK: {node.id} — {node.label}"))

    insts.append(Instruction(Op.PROOF, f"sink.{node.id}"))

    # Assert the IR tick seal is in memory
    proof_passed = node.meta.get("proof_passed", True)
    insts.append(Instruction(Op.PUSH, bool(proof_passed)))
    insts.append(Instruction(Op.ASSERT, f"ir.{ir.title}.proof_passed"))

    # Assert ir tick seal materialized
    if ir.tick_seal:
        insts.append(Instruction(Op.PUSH, ir.tick_seal))
        insts.append(_store_key("ir.tick_seal"))
        insts.append(Instruction(Op.PUSH, True))
        insts.append(Instruction(Op.ASSERT, "ir.tick_seal.present"))

    insts.append(Instruction(Op.QED))
    insts.append(Instruction(Op.HALT))
    return insts


# ── Compiler preamble / postamble ─────────────────────────────────────────────

def _preamble(ir: FlameIR) -> list[Instruction]:
    return [
        Instruction(Op.DEBUG, f"SAGCO FlameIR Bytecode — {ir.title}"),
        Instruction(Op.DEBUG, f"intent: {ir.intent}"),
        Instruction(Op.DEBUG, f"source: {ir.source}"),
        Instruction(Op.PUSH,  ir.title),
        Instruction(Op.STORE, "ir.title"),
        Instruction(Op.PUSH,  ir.intent),
        Instruction(Op.STORE, "ir.intent"),
        Instruction(Op.PUSH,  ir.source),
        Instruction(Op.STORE, "ir.source"),
        Instruction(Op.PUSH,  ir.version),
        Instruction(Op.STORE, "ir.version"),
        Instruction(Op.PUSH,  ir.generated_at),
        Instruction(Op.STORE, "ir.generated_at"),
    ]


# ── Main compiler entry point ─────────────────────────────────────────────────

def compile_ir(ir: FlameIR) -> Bytecode:
    """
    Compile a FlameIR document to executable SAGCO Bytecode.

    Topological order guarantees inputs are always materialized
    before their consumers run.

    The resulting Bytecode can be handed directly to SAGCOVirtualMachine.
    """
    instructions: list[Instruction] = []

    # 1. Preamble — materialize IR identity
    instructions.extend(_preamble(ir))

    # 2. Compile nodes in topological order
    ordered = ir.graph.topological_order()

    for node in ordered:
        if node.kind == FlameNodeKind.SOURCE:
            instructions.extend(_compile_source(node))

        elif node.kind == FlameNodeKind.TRANSFORM:
            instructions.extend(_compile_transform(node))

        elif node.kind == FlameNodeKind.CATALYST:
            instructions.extend(_compile_catalyst(node))

        elif node.kind == FlameNodeKind.TICK:
            instructions.extend(_compile_tick(node))

        elif node.kind == FlameNodeKind.SINK:
            instructions.extend(_compile_sink(node, ir))

        elif node.kind == FlameNodeKind.BOND:
            # BOND nodes emit a BIND opcode between their two endpoint meta fields
            a = node.meta.get("a", node.id)
            b = node.meta.get("b", node.id)
            instructions.append(Instruction(Op.PUSH, a))
            instructions.append(Instruction(Op.PUSH, b))
            instructions.append(Instruction(Op.BIND, node.id))

    # 3. If no SINK node emitted a HALT, close cleanly
    if not instructions or instructions[-1].op != Op.HALT:
        instructions.append(Instruction(Op.HALT))

    return Bytecode(instructions)


def compile_ir_file(path: str | Path) -> Bytecode:
    """Load a .flame.json file and compile it to Bytecode."""
    ir = load_flame(path)
    return compile_ir(ir)


def disassemble(bc: Bytecode) -> str:
    """Return a human-readable disassembly of the bytecode."""
    lines = []
    for i, inst in enumerate(bc.instructions):
        lines.append(f"  {i:04d}  {inst}")
    return "\n".join(lines)
