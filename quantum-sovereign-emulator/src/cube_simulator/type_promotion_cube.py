"""
Type Promotion Cube - Enhanced with Thought-Log Integration
Integrates YAML thought-logs, reference parity, and Bloom wave cores
Main demonstration module for Phase 11
"""

import math
import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import networkx as nx
    import yaml
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)

from register_memory.thought_log_overlay import ThoughtLogOverlay
from entanglement_core.reference_parity_checker import ReferenceParityChecker
from alu.bloom_wave_cores import BloomWaveCores
from cube_simulator.cognitive_cube_spec import CognitiveCubeSpec


class TypePromotionCube:
    """
    Enhanced Type Promotion Cube with Phase 11 features:
    - YAML thought-log integration
    - Reference parity checking
    - Bloom wave cores
    - Cognitive cube simulation
    """
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(__file__).parent.parent.parent / config_dir
        
        # Initialize components
        self.thought_log = ThoughtLogOverlay(
            str(self.config_dir / "thought_log.yaml")
        )
        self.parity_checker = ReferenceParityChecker(
            str(self.config_dir / "oop_hierarchy.json")
        )
        self.wave_cores = BloomWaveCores(
            str(self.config_dir / "cube_mappings.json")
        )
        self.cognitive_cube = CognitiveCubeSpec()
        
        # Build hierarchy graph for type promotions
        self.hierarchy = nx.DiGraph()
        self._build_type_hierarchy()
    
    def _build_type_hierarchy(self):
        """Build type promotion hierarchy graph"""
        # Primitive type hierarchy
        promotions = {
            'byte': ['short', 'int', 'long', 'float', 'double'],
            'short': ['int', 'long', 'float', 'double'],
            'char': ['int', 'long', 'float', 'double'],
            'int': ['long', 'float', 'double'],
            'long': ['float', 'double'],
            'float': ['double']
        }
        
        for source, targets in promotions.items():
            self.hierarchy.add_node(source)
            for target in targets:
                self.hierarchy.add_edge(source, target)
    
    def load_thought_log(self, yaml_path: str = None):
        """Load and replay YAML thought-log"""
        if yaml_path:
            self.thought_log.config_path = yaml_path
        
        self.thought_log.load_yaml()
        self.thought_log.replay_session()
    
    def reference_parity(self, runtime_type: str, target_type: str, tick: int = 0):
        """
        Check reference type parity with wave calculation
        
        Args:
            runtime_type: Actual type at runtime
            target_type: Target type for cast
            tick: Neural tick for wave phase
        
        Returns:
            Tuple of (status, wave_value)
        """
        return self.parity_checker.reference_parity(runtime_type, target_type, tick)
    
    def bloom_wave_core(self, face: str, depth: int = 1):
        """
        Calculate multi-dimensional wave for Bloom face
        
        Args:
            face: Bloom taxonomy level (REMEMBER, UNDERSTAND, etc.)
            depth: Cognitive depth (1-6)
        
        Returns:
            Wave amplitude
        """
        return self.wave_cores.bloom_wave_core(face, depth)
    
    def rank(self, type_name: str) -> int:
        """Get hierarchical rank of a type"""
        return self.parity_checker.get_rank(type_name)
    
    def simulate_cognitive_journey(self):
        """Simulate a cognitive journey through Bloom levels"""
        print("\n=== COGNITIVE JOURNEY SIMULATION ===\n")
        
        journey = [
            ('U', 'REMEMBER', 'Recall basic type concepts'),
            ('R', 'UNDERSTAND', 'Understand type hierarchy'),
            ('F', 'APPLY', 'Apply type promotion rules'),
            ('D', 'ANALYZE', 'Analyze parity violations'),
            ('L', 'EVALUATE', 'Evaluate cast safety'),
            ('B', 'CREATE', 'Create type-safe abstractions'),
        ]
        
        for face_code, face_name, description in journey:
            self.cognitive_cube.rotate(face_code)
            wave = self.bloom_wave_core(face_name, depth=3)
            state = self.wave_cores.evaluate_cognitive_state(face_name, depth=3)
            
            print(f"{face_name:12s}: {description}")
            print(f"  Wave: {wave:6.3f}, State: {state}")
            print()
    
    def main_demo(self):
        """Run comprehensive Phase 11 demonstration"""
        print("=" * 70)
        print("PHASE 11: Cognitive Cube Integration with Thought-Log Registers")
        print("=" * 70)
        
        # 1. Thought-Log Replay
        print("\n" + "=" * 70)
        self.load_thought_log()
        
        # 2. Reference Parity Demo
        print("\n" + "=" * 70)
        print("\n=== REFERENCE PARITY DEMO ===\n")
        
        test_cases = [
            ('Cat', 'Dog', 'Incompatible siblings'),
            ('Dog', 'Animal', 'Safe upcast'),
            ('Animal', 'Dog', 'Unsafe downcast'),
            ('Car', 'Vehicle', 'Safe upcast'),
        ]
        
        for runtime, target, description in test_cases:
            status, wave = self.reference_parity(runtime, target)
            
            print(f"{description}:")
            print(f"  Cast: {runtime} -> {target}")
            print(f"  Status: {status}")
            print(f"  Wave: {wave:.3f}")
            
            if "ERROR" in status:
                print(f"  ⚠️  ClassCastException would occur at runtime!")
            
            print()
        
        # 3. Bloom Wave Cores Demo
        print("=" * 70)
        print("\n=== BLOOM WAVE CORES ===\n")
        
        for face in ['REMEMBER', 'UNDERSTAND', 'APPLY', 'ANALYZE', 'EVALUATE', 'CREATE']:
            wave = self.bloom_wave_core(face, depth=3)
            threshold = self.wave_cores.calculate_parity_threshold(face, depth=3)
            state = self.wave_cores.evaluate_cognitive_state(face, depth=3)
            
            print(f"{face:12s}: wave={wave:6.3f}, threshold={threshold:6.3f}, state={state}")
        
        # 4. Cognitive Journey
        print("\n" + "=" * 70)
        self.simulate_cognitive_journey()
        
        # 5. Hierarchy Visualization
        print("=" * 70)
        self.parity_checker.visualize_hierarchy()
        
        print("\n" + "=" * 70)
        print("Phase 11 demonstration complete!")
        print("=" * 70)


def main():
    """Entry point for type promotion cube demo"""
    # Handle command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--simulate':
        if sys.argv[2] == 'yaml-replay':
            print("Running YAML replay simulation...")
    
    # Run main demo
    cube = TypePromotionCube()
    cube.main_demo()


if __name__ == "__main__":
    main()
