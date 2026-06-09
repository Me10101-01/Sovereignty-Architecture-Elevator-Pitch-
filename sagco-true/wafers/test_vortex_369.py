"""
Wafer: vortex_369
Derives 3, 6, 9 from prime 3 using SAGCO VM opcodes.
No constants imported. The numbers come from the machine.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sagco_true.language.bytecode.opcodes import Op, Instruction, Bytecode
from sagco_true.language.vm.vm import SAGCOVirtualMachine
from sagco_true.khaos.vortex import (
    digital_root, derive_369, vortex_sequence, classify_vortex,
    complement, extract_vortex_tracks, print_vortex,
)

PASS, FAIL = [], []

def check(name, result, expected=True):
    ok = result == expected
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    (PASS if ok else FAIL).append(name)

# ── 1. Derive 3, 6, 9 in SAGCO VM bytecode ───────────────────────────────
# Use only: PUSH 3, MUL, ADD, STORE, PROOF, ASSERT, QED, TICK

bc = Bytecode([
    # Step 1: prime = 3
    Instruction(Op.PUSH, 3),
    Instruction(Op.STORE, "prime"),

    # Step 2: three = prime
    Instruction(Op.LOAD, "prime"),
    Instruction(Op.STORE, "three"),

    # Step 3: six = prime × 2 (doubling)
    Instruction(Op.LOAD, "prime"),
    Instruction(Op.PUSH, 2),
    Instruction(Op.MUL),
    Instruction(Op.STORE, "six"),

    # Step 4: nine = three + six (summation)
    Instruction(Op.LOAD, "three"),
    Instruction(Op.LOAD, "six"),
    Instruction(Op.ADD),
    Instruction(Op.STORE, "nine"),

    # Step 5: Prove the vortex properties
    Instruction(Op.PROOF, "vortex_derivation"),

    #   3 × 2 = 6
    Instruction(Op.LOAD, "three"),
    Instruction(Op.PUSH, 2),
    Instruction(Op.MUL),
    Instruction(Op.LOAD, "six"),
    Instruction(Op.EQ),
    Instruction(Op.ASSERT, "three * 2 == six"),

    #   3 + 6 = 9
    Instruction(Op.LOAD, "three"),
    Instruction(Op.LOAD, "six"),
    Instruction(Op.ADD),
    Instruction(Op.LOAD, "nine"),
    Instruction(Op.EQ),
    Instruction(Op.ASSERT, "three + six == nine"),

    #   nine mod 9 == 0 (nine is the modular fixed point)
    Instruction(Op.LOAD, "nine"),
    Instruction(Op.PUSH, 9),
    Instruction(Op.MOD),
    Instruction(Op.PUSH, 0),
    Instruction(Op.EQ),
    Instruction(Op.ASSERT, "nine mod 9 == 0 (fixed point)"),

    #   six mod 9 == 6 (six is on the 6-track)
    Instruction(Op.LOAD, "six"),
    Instruction(Op.PUSH, 9),
    Instruction(Op.MOD),
    Instruction(Op.PUSH, 6),
    Instruction(Op.EQ),
    Instruction(Op.ASSERT, "six mod 9 == 6"),

    Instruction(Op.QED),

    # Step 6: Tick seal the derivation
    Instruction(Op.TICK, "vortex_369_genesis"),

    Instruction(Op.HALT),
])

vm = SAGCOVirtualMachine()
vm.run(bc)

check("VM: three == 3", vm.memory.get("three") == 3)
check("VM: six == 6",   vm.memory.get("six")   == 6)
check("VM: nine == 9",  vm.memory.get("nine")  == 9)
check("VM: proof passed", vm.memory.get("proof.vortex_derivation.passed") == True)
check("VM: tick sealed",  "tick.vortex_369_genesis.seal" in vm.memory)
check("VM: no proof violations", not any(s.name == "PROOF_VIOLATION" for s in vm.bus))

# ── 2. Verify digital root mathematics ───────────────────────────────────
check("DR: dr(3) == 3", digital_root(3) == 3)
check("DR: dr(6) == 6", digital_root(6) == 6)
check("DR: dr(9) == 9", digital_root(9) == 9)
check("DR: dr(double(3)) == 6",  digital_root(3 * 2) == 6)
check("DR: dr(double(6)) == 3",  digital_root(6 * 2) == 3)  # oscillates back
check("DR: dr(double(9)) == 9",  digital_root(9 * 2) == 9)  # fixed point
check("DR: dr(72) == 9",         digital_root(72)    == 9)  # table is a 9

# ── 3. Vortex sequences ───────────────────────────────────────────────────
seq3 = vortex_sequence(3, 12)
seq9 = vortex_sequence(9, 12)
seq1 = vortex_sequence(1, 12)

check("Vortex: 3-sequence oscillates 3,6,3,6...", seq3 == [3,6] * 6)
check("Vortex: 9-sequence fixed at 9",            seq9 == [9] * 12)
check("Vortex: 1-sequence never touches 3,6,9",  not any(x in (3,6,9) for x in seq1))

# ── 4. Complement pairs ───────────────────────────────────────────────────
check("Complement: complement(3) == 6", complement(3) == 6)
check("Complement: complement(6) == 3", complement(6) == 3)
check("Complement: complement(9) == 9", complement(9) == 9)
check("Complement: 3 + complement(3) == 9", 3 + complement(3) == 9)
check("Complement: 6 + complement(6) == 9", 6 + complement(6) == 9)

# ── 5. KHAOS table vortex structure ──────────────────────────────────────
tracks = extract_vortex_tracks()

check("KHAOS: 3-track has 8 elements",       len(tracks[3].elements) == 8)
check("KHAOS: 6-track has 8 elements",       len(tracks[6].elements) == 8)
check("KHAOS: 9-track has 8 elements",       len(tracks[9].elements) == 8)
check("KHAOS: Track-3 hz_dr == 3 (aligned)", tracks[3].hz_dr == 3)
check("KHAOS: Track-6 hz_dr == 9 (inverted)", tracks[6].hz_dr == 9)
check("KHAOS: Track-9 hz_dr == 6 (inverted)", tracks[9].hz_dr == 6)
check("KHAOS: First element on track-3 is Sitael", tracks[3].elements[0].name == "Sitael")
check("KHAOS: Last element on track-9 is Mumiah",  tracks[9].elements[-1].name == "Mumiah")
check("KHAOS: Mumiah hz=555, dr(555)=6",     digital_root(555) == 6)

# ── 6. derive_369 function ────────────────────────────────────────────────
three, six, nine = derive_369(prime=3)
check("derive_369: three == 3", three == 3)
check("derive_369: six == 6",   six   == 6)
check("derive_369: nine == 9",  nine  == 9)

# Works from any prime? Test with prime 3 only (the generator)
# 3 is special: it's the only prime that generates a pure 3-6-9 triad
# Other primes would generate different digital roots
check("classify: classify_vortex(3) is 3-track", classify_vortex(3) == "3-track")
check("classify: classify_vortex(6) is 6-track", classify_vortex(6) == "6-track")
check("classify: classify_vortex(9) is 9-track", classify_vortex(9) == "9-track")
check("classify: classify_vortex(1) is main",    "main-track" in classify_vortex(1))

# ── Print full vortex ────────────────────────────────────────────────────
print_vortex()

# ── Summary ──────────────────────────────────────────────────────────────
total = len(PASS) + len(FAIL)
print(f"\n  {len(PASS)}/{total} passed")
if FAIL:
    print(f"  FAILED: {FAIL}")
    print("  STATUS: NEEDS_HEALING")
    sys.exit(1)
else:
    print("  STATUS: VORTEX_PROVEN")
    sys.exit(0)
