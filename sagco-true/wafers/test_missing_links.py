"""
Wafer: missing_links_synthesis
Proves all 12 missing links are now implemented and functional.
STATUS: IRREFUTABLE if all pass.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sagco_true.language.bytecode.opcodes import Op, Instruction, Bytecode
from sagco_true.language.vm.vm import SAGCOVirtualMachine
from sagco_true.language.flameir.flame import (
    FlameIR, FlameGraph, FlameNode, FlameNodeKind, FlamePort, FlameEdge,
    save_flame,
)

PASS = []
FAIL = []

def check(name, result, expected=True):
    ok = result == expected
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}")
    if ok:
        PASS.append(name)
    else:
        FAIL.append(name)
    return ok


def vm_run(ops):
    bc = Bytecode(ops)
    vm = SAGCOVirtualMachine()
    vm.run(bc)
    return vm


# ── 1. Arithmetic (Binary System) ────────────────────────────────────────
def test_arithmetic():
    vm = vm_run([
        Instruction(Op.PUSH, 7),
        Instruction(Op.PUSH, 8),
        Instruction(Op.MUL),           # 7 * 8 = 56
        Instruction(Op.PUSH, 8),
        Instruction(Op.PUSH, 7),
        Instruction(Op.DIV),           # 8 / 7 ≈ 1.142...
        Instruction(Op.CAST, "int"),   # → 1
    ])
    top = vm.stack[-1]
    check("arithmetic: 7*8=56 on stack below", vm.stack[-2] == 56)
    check("arithmetic: cast(8/7, int) == 1", top == 1)


# ── 2. Bitwise (Binary System) ────────────────────────────────────────────
def test_bitwise():
    vm = vm_run([
        Instruction(Op.PUSH, 0b1010),
        Instruction(Op.PUSH, 0b1100),
        Instruction(Op.B_AND),         # 0b1000 = 8
        Instruction(Op.PUSH, 0b1010),
        Instruction(Op.PUSH, 0b1100),
        Instruction(Op.B_OR),          # 0b1110 = 14
        Instruction(Op.PUSH, 0b1010),
        Instruction(Op.PUSH, 0b1100),
        Instruction(Op.B_XOR),         # 0b0110 = 6
    ])
    check("bitwise AND: 0b1010 & 0b1100 == 8", vm.stack[-3] == 8)
    check("bitwise OR:  0b1010 | 0b1100 == 14", vm.stack[-2] == 14)
    check("bitwise XOR: 0b1010 ^ 0b1100 == 6", vm.stack[-1] == 6)


# ── 3. Alchemical Cast (Type System) ─────────────────────────────────────
def test_cast():
    vm = vm_run([
        Instruction(Op.PUSH, "440"),
        Instruction(Op.CAST, "float"),   # "440" → 440.0
        Instruction(Op.PUSH, 1),
        Instruction(Op.CAST, "str"),     # 1 → "1"
        Instruction(Op.PUSH, "yes"),
        Instruction(Op.CAST, "bool"),    # "yes" → truthy
    ])
    check("cast str→float: '440' → 440.0", vm.stack[-3] == 440.0)
    check("cast int→str: 1 → '1'", vm.stack[-2] == "1")
    check("cast 'yes'→bool is truthy", bool(vm.stack[-1]))


# ── 4. Unit System (Frequency / Chemistry / Geometry) ────────────────────
def test_units():
    vm = vm_run([
        Instruction(Op.PUSH, 440.0),
        Instruction(Op.UNIT, "hz"),
        Instruction(Op.CONVERT, "rpm"),
        Instruction(Op.MAGNITUDE),       # strip unit → 26400.0
    ])
    val = vm.stack[-1]
    check("unit: 440 hz → rpm magnitude == 26400.0", abs(val - 26400.0) < 0.01)

    vm2 = vm_run([
        Instruction(Op.PUSH, 90.0),
        Instruction(Op.UNIT, "deg"),
        Instruction(Op.CONVERT, "rad"),
        Instruction(Op.MAGNITUDE),
    ])
    import math
    val2 = vm2.stack[-1]
    check("unit: 90 deg → rad ≈ π/2", abs(val2 - math.pi/2) < 0.001)


# ── 5. Tick Sealing (Temporal Sovereignty) ───────────────────────────────
def test_ticks():
    vm = vm_run([
        Instruction(Op.PUSH, "organism"),
        Instruction(Op.STORE, "identity.name"),
        Instruction(Op.TICK, "genesis"),
        Instruction(Op.TICK, "step_1"),
        Instruction(Op.TICK_VERIFY, "genesis"),
    ])
    check("tick: chain has 2 ticks", len(vm._ticks) == 2)
    check("tick: genesis seal in memory", "tick.genesis.seal" in vm.memory)
    check("tick verify: genesis chain valid", vm.stack[-1] == True)


# ── 6. Proof Assertions (Invariant Layer) ────────────────────────────────
def test_proof():
    vm = vm_run([
        Instruction(Op.PUSH, "MyOrganism"),
        Instruction(Op.STORE, "identity.name"),
        Instruction(Op.PROOF, "organism_axiom"),
        Instruction(Op.LOAD, "identity.name"),
        Instruction(Op.PUSH, ""),
        Instruction(Op.NEQ),
        Instruction(Op.ASSERT, "identity.name must not be empty"),
        Instruction(Op.QED),
    ])
    check("proof: QED result is True", vm.stack[-1] == True)
    check("proof: memory records passed", vm.memory.get("proof.organism_axiom.passed") == True)
    check("proof: QED signal emitted", any(s.name == "QED" for s in vm.bus))

    # failing proof
    vm2 = vm_run([
        Instruction(Op.PROOF, "must_fail"),
        Instruction(Op.PUSH, False),
        Instruction(Op.ASSERT, "deliberately false"),
        Instruction(Op.QED),
    ])
    check("proof: failed proof emits PROOF_VIOLATION", any(s.name == "PROOF_VIOLATION" for s in vm2.bus))
    check("proof: failed QED returns False", vm2.stack[-1] == False)


# ── 7. Binding / Electronegativity ───────────────────────────────────────
def test_bonds():
    vm = vm_run([
        Instruction(Op.PUSH, "kernel"),
        Instruction(Op.PUSH, "boot_sequence"),
        Instruction(Op.BIND, "kernel:boot"),
        Instruction(Op.BONDS),
    ])
    bonds = vm.stack[-1]
    check("bond: kernel:boot bond exists", len(bonds) == 1)
    check("bond: bond name matches", bonds[0]["name"] == "kernel:boot")
    check("bond: a=kernel", bonds[0]["a"] == "kernel")


# ── 8. Pipeline (Rolling Offset) ─────────────────────────────────────────
def test_pipeline():
    # Explicit test: push value through chain using PIPE
    # PIPE routes to a labeled procedure
    vm = vm_run([
        Instruction(Op.LABEL, "__do__double"),
        Instruction(Op.PUSH, 2),
        Instruction(Op.MUL),
        Instruction(Op.RETURN),
        Instruction(Op.PUSH, 5),
        Instruction(Op.PIPE, "double"),  # 5 → double → 10
    ])
    check("pipe: 5 piped through double → 10", vm.stack[-1] == 10)


# ── 9. Frequency / Periodicity ───────────────────────────────────────────
def test_frequency():
    vm = vm_run([
        Instruction(Op.PUSH, 0.5),     # period = 0.5 seconds
        Instruction(Op.PERIOD, "beat"),
        Instruction(Op.PUSH, 0.5),
        Instruction(Op.FREQUENCY),     # 1/0.5 = 2.0 hz
    ])
    check("frequency: 1/0.5 == 2.0", vm.stack[-1] == 2.0)
    check("period stored: period.beat == 0.5", vm.memory.get("period.beat") == 0.5)


# ── 10. FlameLang IR (Missing Link 8: CONCERT→COMPILER bridge) ───────────
def test_flameir():
    graph = FlameGraph()
    graph.add_node(FlameNode(
        id="raw_freq",
        kind=FlameNodeKind.SOURCE,
        label="440hz audio input",
        intent="receive frequency measurement",
        outputs=[FlamePort("freq", "float", "hz")],
        provenance="stepper://audio",
    ))
    graph.add_node(FlameNode(
        id="cast_freq",
        kind=FlameNodeKind.TRANSFORM,
        label="Transmute hz to rpm",
        intent="convert frequency domain",
        inputs=[FlamePort("freq", "float", "hz")],
        outputs=[FlamePort("speed", "float", "rpm")],
        catalyst="unit_system_active",   # wafer must pass
    ))
    graph.add_node(FlameNode(
        id="output",
        kind=FlameNodeKind.SINK,
        label="RPM output",
        intent="emit converted value",
        inputs=[FlamePort("speed", "float", "rpm")],
    ))
    graph.connect("raw_freq", "freq", "cast_freq", "freq")
    graph.connect("cast_freq", "speed", "output", "speed")

    ir = FlameIR(
        title="Frequency Domain Transmutation",
        intent="convert audio hz to rotational rpm",
        source="test_missing_links",
        graph=graph,
        wafers=["unit_system_active"],
    )
    seal = ir.seal()
    issues = ir.validate()
    topo = ir.graph.topological_order()
    hints = ir.to_sagco_bytecode_hints()

    check("flameir: seal is sha256 hex (64 chars)", len(seal) == 64)
    check("flameir: no structural issues", issues == [])
    check("flameir: topological order has 3 nodes", len(topo) == 3)
    check("flameir: first node is SOURCE", topo[0].kind == FlameNodeKind.SOURCE)
    check("flameir: last node is SINK", topo[-1].kind == FlameNodeKind.SINK)
    check("flameir: bytecode hints generated", len(hints) > 5)


# ── 11. Truth report status IRREFUTABLE ──────────────────────────────────
def test_irrefutable_status():
    vm = vm_run([
        Instruction(Op.PUSH, "SAGCO"),
        Instruction(Op.STORE, "identity.name"),
        Instruction(Op.PUSH, "0.1.0"),
        Instruction(Op.STORE, "sagco.version"),
        Instruction(Op.PROOF, "irrefutability_proof"),
        Instruction(Op.LOAD, "identity.name"),
        Instruction(Op.PUSH, ""),
        Instruction(Op.NEQ),
        Instruction(Op.ASSERT, "identity.name not empty"),
        Instruction(Op.LOAD, "sagco.version"),
        Instruction(Op.PUSH, ""),
        Instruction(Op.NEQ),
        Instruction(Op.ASSERT, "sagco.version not empty"),
        Instruction(Op.QED),
        Instruction(Op.TICK, "irrefutable_moment"),
        Instruction(Op.PUSH, "SAGCO"),
        Instruction(Op.STORE, "wafer.core_axioms.expected"),
        Instruction(Op.PUSH, "SAGCO"),
        Instruction(Op.STORE, "wafer.core_axioms.actual"),
        Instruction(Op.MEASURE, "core_axioms"),
    ])
    report = vm.truth_report()
    check("irrefutable: status is IRREFUTABLE", report["status"] == "IRREFUTABLE")
    check("irrefutable: tick chain present", report["tick_chain_length"] >= 1)
    check("irrefutable: no proof violations", report["proof_violations"] == 0)


# ── 12. Cross-domain frequency mapping (Color of Sound) ──────────────────
def test_cross_domain():
    # 20hz → rpm
    vm = vm_run([
        Instruction(Op.PUSH, 20.0),
        Instruction(Op.UNIT, "hz"),
        Instruction(Op.CONVERT, "rpm"),
        Instruction(Op.MAGNITUDE),   # 20 * 60 = 1200
    ])
    check("cross-domain: 20hz → 1200rpm", abs(vm.stack[-1] - 1200.0) < 0.01)

    # degrees → radians
    import math
    vm2 = vm_run([
        Instruction(Op.PUSH, 180.0),
        Instruction(Op.UNIT, "deg"),
        Instruction(Op.CONVERT, "rad"),
        Instruction(Op.MAGNITUDE),
    ])
    check("cross-domain: 180deg → π rad", abs(vm2.stack[-1] - math.pi) < 0.001)


# ── Run all ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n  SAGCO Missing Links Synthesis — Particle Accelerator Run")
    print("  " + "─" * 58)
    test_arithmetic()
    test_bitwise()
    test_cast()
    test_units()
    test_ticks()
    test_proof()
    test_bonds()
    test_pipeline()
    test_frequency()
    test_flameir()
    test_irrefutable_status()
    test_cross_domain()
    print("  " + "─" * 58)
    total = len(PASS) + len(FAIL)
    print(f"  {len(PASS)}/{total} passed")
    if FAIL:
        print(f"  FAILED: {FAIL}")
        print("  STATUS: NEEDS_HEALING")
        sys.exit(1)
    else:
        print("  STATUS: IRREFUTABLE")
        sys.exit(0)
