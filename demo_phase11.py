#!/usr/bin/env python3
"""
Phase 11 Complete Demonstration
Showcases all integrated components of the Cognitive Cube Spec
"""

import sys
sys.path.insert(0, 'src')

from control_unit.dispatcher import Dispatcher
from entanglement_core import ReferenceParityChecker
from register_memory import ThoughtLogOverlay
from alu import BloomWaveCores
from cube_simulator import TypePromotionCube
from cube_simulator.precision_parity_checker import PrecisionParityChecker


def print_header(title):
    """Print section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def main():
    """Run complete Phase 11 demonstration."""
    
    print_header("PHASE 11: COGNITIVE CUBE SPEC DEMONSTRATION")
    
    print("Quantum Sovereign Emulator")
    print("Integrating Thought-Log Registers, Reference Parity Model,")
    print("and Bloom Taxonomy Wave Cores\n")
    
    # Demo 1: Thought-Log Replay
    print_header("1. THOUGHT-LOG OVERLAY - Quantum Register States")
    
    overlay = ThoughtLogOverlay('configs/thought_log.yaml')
    overlay.load()
    
    print("YAML Thought Stream → Quantum Register Overlay")
    print(f"Loaded {len(overlay.thought_stream)} thought states")
    print(f"Session ID: session-03AM")
    print(f"Parity Events Catalog: {len(overlay.parity_events)} types\n")
    
    # Show first thought
    thought = overlay.thought_stream[0]
    print(f"Example Thought State T{thought['id']}:")
    print(f"  Operation: {thought['operation']}")
    print(f"  Face: {thought['active_face']} ({overlay.bloom_faces.get(thought['active_face'])})")
    print(f"  Timestamp: {thought['timestamp']}")
    
    # Demo 2: Reference Parity Checks
    print_header("2. REFERENCE PARITY CHECKER - Entanglement Invariants")
    
    checker = ReferenceParityChecker('configs/oop_hierarchy.json')
    checker.load_hierarchies()
    
    print("Type Hierarchies as Entangled Subtrees\n")
    
    test_cases = [
        ("Safe Upcast", "Dog", "Animal", "Animal Hierarchy"),
        ("Parity Error", "Cat", "Dog", "Animal Hierarchy"),
        ("Safe Narrowing", "Byte", "Integer", "Numeric Hierarchy"),
        ("Overflow Risk", "Integer", "Byte", "Numeric Hierarchy"),
    ]
    
    for label, runtime, target, hierarchy in test_cases:
        status, wave, msg = checker.check_cast(runtime, target, hierarchy)
        icon = "✅" if "SAFE" in status else "❌"
        print(f"{icon} {label:15s} | {runtime:8s} → {target:8s}")
        print(f"   Status: {status:20s} | Wave: {wave:6.3f}")
        print(f"   {msg}\n")
    
    # Demo 3: Bloom Wave Cores
    print_header("3. BLOOM WAVE CORES - Multi-Dimensional Cognition")
    
    cores = BloomWaveCores('configs/cube_mappings.json')
    cores.load_config()
    
    print("Bloom Taxonomy → Trig-Formula Wave Functions\n")
    print(f"{'Face':<6} {'Bloom Level':<12} {'Wave (d=3)':<12} {'Formula':<30}")
    print("-" * 70)
    
    for face, bloom in cores.bloom_faces.items():
        wave = cores.compute_wave(face, 3.0)
        formula = cores.wave_formulas.get(bloom, "N/A")
        print(f"{face:<6} {bloom:<12} {wave:>11.4f}  {formula:<30}")
    
    # Demo 4: Precision Parity
    print_header("4. PRECISION PARITY CHECKER - Numeric Overflow Detection")
    
    precision = PrecisionParityChecker()
    
    print("Narrowing Conversions with Bounds Checking\n")
    
    numeric_tests = [
        (100, "Integer", "Byte", "Within bounds"),
        (200, "Integer", "Byte", "Overflow"),
        (-200, "Integer", "Byte", "Underflow"),
    ]
    
    for value, source, target, desc in numeric_tests:
        status, wave, msg = precision.check_narrowing(value, source, target)
        icon = "✅" if "SAFE" in status else "❌"
        print(f"{icon} {desc:15s} | {value:6d} ({source} → {target})")
        print(f"   Wave: {wave:6.3f} | {msg}\n")
    
    # Demo 5: Full Integration
    print_header("5. TYPE PROMOTION CUBE - Unified Integration")
    
    cube = TypePromotionCube()
    cube.initialize()
    
    print("Neural Tick Sequence Example:\n")
    
    operations = [
        {'type': 'CAST_CHECK', 'runtime_type': 'Dog', 'target_type': 'Animal'},
        {'type': 'BLOOM_COMPUTE', 'face': 'ANALYZE', 'depth': 2.0},
        {'type': 'PARITY_THRESHOLD', 'face': 'CREATE', 'depth': 8.0, 'threshold': -0.5},
    ]
    
    for i, op in enumerate(operations):
        tick = i
        print(f"Tick {tick}: {op['type']}")
        
        if op['type'] == 'CAST_CHECK':
            status, wave, msg = cube.reference_parity(
                op['runtime_type'], op['target_type']
            )
            print(f"  └─> {msg} | Wave: {wave:.3f}\n")
        elif op['type'] == 'BLOOM_COMPUTE':
            wave = cube.bloom_wave_core(op['face'], op['depth'])
            print(f"  └─> {op['face']}: {wave:.3f}\n")
        elif op['type'] == 'PARITY_THRESHOLD':
            has_error = cores.detect_parity_threshold(
                op['face'], op['depth'], op['threshold']
            )
            status_str = "❌ PARITY ERROR" if has_error else "✅ OK"
            print(f"  └─> {status_str}\n")
    
    # Demo 6: Build Order Phases
    print_header("6. BUILD ORDER SEQUENCER - Neural Tick Phases")
    
    print("Phase 1 (Ticks 0-2): YAML_SUBSTRATE")
    print("  • Memory initialization with thought-log parsing")
    print("  • Quantum register overlay configuration\n")
    
    print("Phase 2 (Ticks 3-5): PARITY_CATALOG")
    print("  • Type hierarchy graph construction")
    print("  • Reference and precision parity checks")
    print("  • Entanglement invariant validation\n")
    
    print("Phase 3 (Ticks 6-8): VIZ_ENGINE")
    print("  • Graph renderer initialization")
    print("  • Hasse diagram and Cayley graph generators")
    print("  • Diffable graph export for CI/CD\n")
    
    # Summary
    print_header("PHASE 11 COMPLETE")
    
    print("✅ Thought-Log Overlay: YAML → Quantum States")
    print("✅ Reference Parity: Type Hierarchies → Entangled Subtrees")
    print("✅ Bloom Wave Cores: Taxonomy → Multi-Dim Waves")
    print("✅ Precision Parity: Numeric → Overflow Detection")
    print("✅ Integration Hub: Unified Type Promotion Cube")
    print("✅ Build Sequencer: Neural Tick Phases")
    print("\nSystem Status: OPERATIONAL")
    print("Ready for Phase 12: Visualization Engine Enhancement\n")


if __name__ == "__main__":
    main()
