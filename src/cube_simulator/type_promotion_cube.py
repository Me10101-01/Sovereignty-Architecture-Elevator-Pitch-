#!/usr/bin/env python3
"""
Type Promotion Cube - Cognitive Cube Integration
Integrates thought-log overlay, reference parity checking, and Bloom wave cores.
Phase 11: Neural Tick Clocks and Multi-Dimensional Wave Reasoning.
"""

import sys
import os
import math
import networkx as nx

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.register_memory.thought_log_overlay import ThoughtLogOverlay
from src.entanglement_core.reference_parity_checker import ReferenceParityChecker
from src.alu.bloom_wave_cores import BloomWaveCores


class TypePromotionCube:
    """
    Unified Cognitive Cube integrating:
    - YAML thought-log as quantum register overlay
    - Reference parity checks for type hierarchies
    - Bloom wave cores for multi-dimensional cognitive operations
    """

    def __init__(self):
        self.thought_log = ThoughtLogOverlay()
        self.parity_checker = ReferenceParityChecker()
        self.wave_cores = BloomWaveCores()
        self.hierarchy = None
        
    def initialize(self) -> None:
        """Initialize all subsystems."""
        print("=== INITIALIZING TYPE PROMOTION CUBE ===\n")
        
        # Load configurations
        self.thought_log.load()
        self.parity_checker.load_hierarchies()
        self.wave_cores.load_config()
        
        # Build primary hierarchy graph
        if 'Animal Hierarchy' in self.parity_checker.graphs:
            self.hierarchy = self.parity_checker.graphs['Animal Hierarchy']
        
        print("✓ Thought-log overlay loaded")
        print("✓ Reference parity checker initialized")
        print("✓ Bloom wave cores configured\n")
    
    def load_thought_log(self, yaml_path: str = 'configs/thought_log.yaml') -> None:
        """
        Load and replay YAML thought-log.
        Maps sessions/thoughts to timestamped qubit states.
        """
        print("\n=== THOUGHT-LOG REPLAY (YAML v0.1) ===\n")
        self.thought_log.yaml_path = yaml_path
        self.thought_log.load()
        self.thought_log.replay_session("session-03AM")
    
    def reference_parity(self, runtime_type: str, target_type: str, 
                        hierarchy_name: str = "Animal Hierarchy",
                        tick: int = 0) -> tuple:
        """
        Check reference type parity using entangled subtree invariants.
        
        Returns:
            (status, wave_value, message)
        """
        status, wave, message = self.parity_checker.check_cast(
            runtime_type, target_type, hierarchy_name, tick
        )
        
        return status, wave, message
    
    def bloom_wave_core(self, face: str, depth: float = 1.0) -> float:
        """
        Compute multi-dimensional wave for Bloom taxonomy face.
        
        Args:
            face: Cube face (U/R/F/D/L/B) or Bloom level
            depth: Cognitive depth parameter
        
        Returns:
            Wave amplitude
        """
        return self.wave_cores.compute_wave(face, depth)
    
    def rank(self, type_name: str, hierarchy_name: str = "Animal Hierarchy") -> int:
        """Get rank (depth) of type in hierarchy."""
        return self.parity_checker.get_rank(type_name, hierarchy_name)
    
    def neural_tick_sequence(self, operations: list, tick_start: int = 0) -> None:
        """
        Execute a sequence of operations as neural tick steps.
        Each operation is a wave propagation with parity checking.
        """
        print("\n=== NEURAL TICK SEQUENCE ===\n")
        
        for i, operation in enumerate(operations):
            tick = tick_start + i
            op_type = operation.get('type')
            
            print(f"Tick {tick:3d}: {op_type}")
            
            if op_type == 'CAST_CHECK':
                runtime = operation.get('runtime_type')
                target = operation.get('target_type')
                hierarchy = operation.get('hierarchy', 'Animal Hierarchy')
                
                status, wave, message = self.reference_parity(runtime, target, hierarchy, tick)
                print(f"         └─> {message} | Wave: {wave:.3f}")
            
            elif op_type == 'BLOOM_COMPUTE':
                face = operation.get('face')
                depth = operation.get('depth', 1.0)
                
                wave = self.bloom_wave_core(face, depth)
                bloom_name = self.wave_cores.bloom_faces.get(face, face)
                print(f"         └─> {face} ({bloom_name}): {wave:.3f}")
            
            elif op_type == 'PARITY_THRESHOLD':
                face = operation.get('face')
                depth = operation.get('depth', 1.0)
                threshold = operation.get('threshold', -0.5)
                
                has_error = self.wave_cores.detect_parity_threshold(face, depth, threshold)
                status_str = "❌ PARITY ERROR" if has_error else "✓ OK"
                print(f"         └─> {status_str}")
    
    def integrated_demo(self) -> None:
        """
        Comprehensive demo integrating all Phase 11 components.
        """
        print("\n" + "="*70)
        print("  TYPE PROMOTION CUBE - PHASE 11 INTEGRATION")
        print("  Cognitive Cube Spec + Reference Parity Model")
        print("="*70 + "\n")
        
        # Demo 1: Thought-log replay
        self.load_thought_log()
        
        # Demo 2: Reference parity checks
        print("\n=== REFERENCE PARITY CHECKS ===\n")
        
        test_casts = [
            ('Cat', 'Dog', 'Animal Hierarchy'),
            ('Dog', 'Animal', 'Animal Hierarchy'),
            ('Mammal', 'Object', 'Animal Hierarchy'),
            ('Eagle', 'Animal', 'Animal Hierarchy'),
        ]
        
        for runtime, target, hierarchy in test_casts:
            status, wave, message = self.reference_parity(runtime, target, hierarchy)
            indicator = "❌" if "ERROR" in status else "✓"
            print(f"{indicator} {runtime:10s} → {target:10s} | Wave: {wave:6.3f}")
            print(f"  └─ {message}")
        
        # Demo 3: Bloom wave cores
        print("\n=== BLOOM WAVE CORES (Multi-Dimensional) ===\n")
        
        test_faces = [
            ('REMEMBER', 3),
            ('UNDERSTAND', 3),
            ('APPLY', 3),
            ('ANALYZE', 3),
            ('EVALUATE', 3),
            ('CREATE', 3),
        ]
        
        for face, depth in test_faces:
            wave = self.bloom_wave_core(face, depth)
            print(f"{face:10s} @ depth {depth}: {wave:7.4f}")
        
        # Demo 4: Neural tick sequence
        operations = [
            {'type': 'CAST_CHECK', 'runtime_type': 'Dog', 'target_type': 'Animal'},
            {'type': 'BLOOM_COMPUTE', 'face': 'ANALYZE', 'depth': 2.0},
            {'type': 'CAST_CHECK', 'runtime_type': 'Cat', 'target_type': 'Dog'},
            {'type': 'PARITY_THRESHOLD', 'face': 'CREATE', 'depth': 8.0, 'threshold': -0.5},
        ]
        
        self.neural_tick_sequence(operations, tick_start=0)
        
        # Demo 5: Build order phases
        print("\n=== BUILD ORDER PHASES (Sequencer Roadmap) ===\n")
        
        phases = [
            {'phase': 1, 'name': 'YAML_SUBSTRATE', 'ticks': [0, 1, 2]},
            {'phase': 2, 'name': 'PARITY_CATALOG', 'ticks': [3, 4, 5]},
            {'phase': 3, 'name': 'VIZ_ENGINE', 'ticks': [6, 7, 8]},
        ]
        
        for phase_info in phases:
            print(f"Phase {phase_info['phase']}: {phase_info['name']}")
            print(f"  Ticks: {phase_info['ticks']}")
        
        print("\n" + "="*70)
        print("  PHASE 11 INTEGRATION COMPLETE")
        print("="*70 + "\n")


def main():
    """Main entry point for Type Promotion Cube demo."""
    cube = TypePromotionCube()
    cube.initialize()
    cube.integrated_demo()


if __name__ == "__main__":
    main()
