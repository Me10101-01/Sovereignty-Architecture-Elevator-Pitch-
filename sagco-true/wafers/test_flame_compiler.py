"""
Wafer: flame_compiler
Tests the FlameIR → Bytecode compiler.
Proves the domino chain closes: CONCERT → FLAMEIR → COMPILER → BYTECODE → SOVEREIGN
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sagco_true.language.flameir.flame import (
    FlameIR, FlameGraph, FlameNode, FlameNodeKind, FlamePort,
)
from sagco_true.language.bytecode.opcodes import Op, Bytecode
from sagco_true.language.vm.vm import SAGCOVirtualMachine
from sagco_true.language.compiler.flame_compiler import compile_ir, disassemble

PASS, FAIL = [], []

def check(name, result, expected=True):
    ok = result == expected
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    (PASS if ok else FAIL).append(name)


# ── Helper: build a minimal FlameIR ──────────────────────────────────────────

def _minimal_ir(title: str = "test-ir") -> FlameIR:
    g = FlameGraph()

    g.add_node(FlameNode(
        id="src",
        kind=FlameNodeKind.SOURCE,
        label="Test Source",
        intent="provide test values",
        outputs=[FlamePort("value", "int")],
        provenance="test@0",
        meta={"value": 42, "label": "test_value"},
    ))

    g.add_node(FlameNode(
        id="tick_node",
        kind=FlameNodeKind.TICK,
        label="Temporal Seal",
        meta={"seal": "abc123def456"},
    ))

    g.add_node(FlameNode(
        id="sink",
        kind=FlameNodeKind.SINK,
        label="Test Sink",
        inputs=[FlamePort("value", "int")],
        meta={"proof_passed": True},
    ))

    g.connect("src", "value", "sink", "value")
    g.connect("tick_node", "seal", "sink", "tick_seal")

    ir = FlameIR(
        title=title,
        intent="test compiler round-trip",
        source="test",
        graph=g,
    )
    ir.seal()
    return ir


# ── 1. Compiler produces bytecode ────────────────────────────────────────────

ir = _minimal_ir()
bc = compile_ir(ir)

check("Compiler: returns Bytecode object",         isinstance(bc, Bytecode))
check("Compiler: has instructions",                len(bc.instructions) > 0)
check("Compiler: ends with HALT",                  bc.instructions[-1].op == Op.HALT)
check("Compiler: has TICK instruction",
      any(i.op == Op.TICK for i in bc.instructions))
check("Compiler: has PROOF instruction",
      any(i.op == Op.PROOF for i in bc.instructions))
check("Compiler: has QED instruction",
      any(i.op == Op.QED for i in bc.instructions))
check("Compiler: has ASSERT instruction",
      any(i.op == Op.ASSERT for i in bc.instructions))
check("Compiler: has DEBUG instructions",
      any(i.op == Op.DEBUG for i in bc.instructions))

# ── 2. Disassembler ──────────────────────────────────────────────────────────

dis = disassemble(bc)
check("Disassemble: non-empty string",             len(dis) > 0)
check("Disassemble: has line numbers",             "0000" in dis)
check("Disassemble: has HALT",                     "HALT" in dis)

# ── 3. Compiled bytecode runs in the VM ──────────────────────────────────────

vm = SAGCOVirtualMachine()
vm.run(bc)

check("VM: ir.title stored",            vm.memory.get("ir.title") == ir.title)
check("VM: ir.intent stored",           vm.memory.get("ir.intent") == ir.intent)
check("VM: ir.source stored",           vm.memory.get("ir.source") == ir.source)
check("VM: src.value materialized",     vm.memory.get("src.value") == 42)
check("VM: tick_seal stored",           "tick_node.seal" in vm.memory)
check("VM: src provenance stored",      vm.memory.get("src.provenance") == "test@0")
check("VM: proof scope sealed",
      vm.memory.get("proof.sink.sink.passed") == True or
      any("sink" in k for k in vm.memory if "proof" in k))
check("VM: no bus CRITICAL signals",
      not any(s.name == "CRITICAL" for s in vm.bus))

# ── 4. Catalyst node compiles correctly ──────────────────────────────────────

g2 = FlameGraph()
g2.add_node(FlameNode(
    id="cat",
    kind=FlameNodeKind.CATALYST,
    label="Truth Gate",
    meta={"passed": True},
))
g2.add_node(FlameNode(
    id="sink2",
    kind=FlameNodeKind.SINK,
    label="Catalyzed Sink",
    meta={"proof_passed": True},
))
g2.connect("cat", "result", "sink2", "wafer_check")

ir2 = FlameIR(title="catalyst-test", intent="test catalyst", source="test")
ir2.graph = g2
ir2.seal()

bc2 = compile_ir(ir2)
vm2 = SAGCOVirtualMachine()
vm2.run(bc2)

check("Catalyst: PROOF/ASSERT/QED emitted",
      any(i.op == Op.PROOF   for i in bc2.instructions) and
      any(i.op == Op.ASSERT  for i in bc2.instructions) and
      any(i.op == Op.QED     for i in bc2.instructions))
check("Catalyst: VM ran without CRITICAL",
      not any(s.name == "CRITICAL" for s in vm2.bus))

# ── 5. Full CONCERT → compile round-trip ─────────────────────────────────────

from sagco_true.worlds.concert import Concert

concert = Concert()
result  = concert.run(title="compile-test", save=False)
bc_live = compile_ir(result.ir)

vm_live = SAGCOVirtualMachine()
vm_live.run(bc_live)

check("Concert→Compile: returns Bytecode",        isinstance(bc_live, Bytecode))
check("Concert→Compile: ir.title in vm memory",
      vm_live.memory.get("ir.title") == "compile-test")
check("Concert→Compile: primameria.date in vm",
      vm_live.memory.get("primameria_today.date") is not None or
      any("primameria" in k for k in vm_live.memory))
check("Concert→Compile: tick seal materialized",
      any("tick" in k and "seal" in k for k in vm_live.memory))
check("Concert→Compile: VM ends cleanly",
      not any(s.name == "CRITICAL" for s in vm_live.bus))

n_source = sum(1 for n in result.ir.graph.nodes if n.kind == FlameNodeKind.SOURCE)
check("Concert→Compile: ≥2 SOURCE nodes (ingest + primameria)", n_source >= 2)

# ── 6. Preamble values ───────────────────────────────────────────────────────

check("Preamble: ir.version stored",    isinstance(vm.memory.get("ir.version"), str))
check("Preamble: ir.generated_at > 0",
      isinstance(vm.memory.get("ir.generated_at"), float) and
      vm.memory.get("ir.generated_at") > 0)

# ── Summary ───────────────────────────────────────────────────────────────────

print(f"\n  Bytecode size: {len(bc.instructions)} instructions")
print(f"  Concert IR: {len(result.ir.graph.nodes)} nodes → "
      f"{len(bc_live.instructions)} instructions compiled")
print()

total = len(PASS) + len(FAIL)
print(f"  {len(PASS)}/{total} passed")
if FAIL:
    print(f"  FAILED: {FAIL}")
    print("  STATUS: NEEDS_HEALING")
    sys.exit(1)
else:
    print("  STATUS: DOMINO_CHAIN_CLOSED")
    sys.exit(0)
