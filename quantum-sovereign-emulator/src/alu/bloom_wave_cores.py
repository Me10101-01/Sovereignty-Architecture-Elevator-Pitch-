"""
Bloom Wave Cores Module
Multi-dimensional wave functions for Bloom taxonomy faces
Cognitive operations mapped to trigonometric formulas
"""

import math
from typing import Dict, Callable, Any, Optional
import json


class BloomWaveCores:
    """Multi-dimensional wave cores for Bloom's taxonomy"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "configs/cube_mappings.json"
        self.face_mappings: Dict[str, str] = {}
        self.trig_mappings: Dict[str, str] = {}
        self.load_config()
        
        # Define wave functions for each Bloom level
        self.wave_functions: Dict[str, Callable[[float], float]] = {
            'REMEMBER': lambda x: math.sin(x),
            'UNDERSTAND': lambda x: math.cos(x),
            'APPLY': lambda x: math.sin(x) + 0.5 * math.sin(2 * x),
            'ANALYZE': lambda x: math.cos(x) + 0.3 * math.cos(3 * x),
            'EVALUATE': lambda x: math.exp(-x / 10),  # Dampened for judgment
            'CREATE': lambda x: math.sin(x) * math.exp(-x / 4)  # Damped oscillation
        }
    
    def load_config(self) -> None:
        """Load Bloom face mappings from config"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            self.face_mappings = data.get('bloom_faces', {})
            self.trig_mappings = data.get('face_to_trig', {})
        except FileNotFoundError:
            print(f"Warning: {self.config_path} not found. Using default mappings.")
            self.face_mappings = {
                "U": "REMEMBER",
                "R": "UNDERSTAND",
                "F": "APPLY",
                "D": "ANALYZE",
                "L": "EVALUATE",
                "B": "CREATE"
            }
    
    def bloom_wave_core(self, face: str, depth: int = 1) -> float:
        """
        Calculate multi-dimensional wave for a Bloom face
        
        Args:
            face: Bloom taxonomy level (REMEMBER, UNDERSTAND, etc.)
            depth: Cognitive depth (1-6 for Bloom levels)
        
        Returns:
            Wave amplitude representing cognitive state
        """
        if face not in self.wave_functions:
            print(f"Warning: Unknown face '{face}', using default sine wave")
            return math.sin(math.pi * depth / 6)
        
        # Map depth to phase (0 to π)
        phase = math.pi * depth / 6  # 6 Bloom levels
        
        return self.wave_functions[face](phase)
    
    def evaluate_cognitive_state(self, face: str, depth: int, threshold: float = 0.0) -> str:
        """
        Evaluate cognitive state based on wave amplitude
        
        Args:
            face: Bloom taxonomy level
            depth: Cognitive depth
            threshold: Minimum threshold for valid state
        
        Returns:
            State description (COHERENT, DAMPED, ERROR)
        """
        wave = self.bloom_wave_core(face, depth)
        
        if wave > threshold + 0.5:
            return "COHERENT"
        elif wave > threshold:
            return "STABLE"
        elif wave > threshold - 0.5:
            return "DAMPED"
        else:
            return "ERROR"
    
    def calculate_parity_threshold(self, face: str, depth: int) -> float:
        """
        Calculate parity threshold for detecting impossible cubes
        Negative values indicate parity errors
        """
        wave = self.bloom_wave_core(face, depth)
        
        # Apply damping for higher-order thinking (CREATE, EVALUATE)
        if face in ['CREATE', 'EVALUATE']:
            damping = math.exp(-depth / 8)
            return wave * damping
        
        return wave
    
    def get_face_from_code(self, face_code: str) -> str:
        """Convert face code (U, R, F, etc.) to Bloom level"""
        return self.face_mappings.get(face_code, "UNKNOWN")
    
    def visualize_waves(self, resolution: int = 20) -> None:
        """Visualize wave patterns for all Bloom levels"""
        print("\n=== BLOOM WAVE CORES VISUALIZATION ===\n")
        
        faces = ['REMEMBER', 'UNDERSTAND', 'APPLY', 'ANALYZE', 'EVALUATE', 'CREATE']
        
        for face in faces:
            print(f"{face}:")
            waves = [self.bloom_wave_core(face, d) for d in range(1, resolution + 1)]
            
            # Simple ASCII visualization
            for i, wave in enumerate(waves[:10], 1):  # Show first 10 points
                bar_length = int((wave + 1) * 20)  # Scale to 0-40
                bar = '█' * max(0, bar_length)
                print(f"  Depth {i:2d}: {wave:6.3f} {bar}")
            print()
    
    def multi_face_synthesis(self, faces: list, depths: list) -> float:
        """
        Synthesize multiple faces into combined wave
        Useful for complex cognitive operations
        """
        if len(faces) != len(depths):
            raise ValueError("Faces and depths must have same length")
        
        waves = [self.bloom_wave_core(face, depth) 
                for face, depth in zip(faces, depths)]
        
        # Combine with weighted average
        return sum(waves) / len(waves)


def main():
    """Demo Bloom wave cores"""
    cores = BloomWaveCores()
    
    print("\n=== BLOOM WAVE CORES DEMO ===\n")
    
    # Test individual faces
    test_faces = ['REMEMBER', 'UNDERSTAND', 'APPLY', 'ANALYZE', 'EVALUATE', 'CREATE']
    
    for face in test_faces:
        for depth in [1, 3, 5]:
            wave = cores.bloom_wave_core(face, depth)
            state = cores.evaluate_cognitive_state(face, depth)
            threshold = cores.calculate_parity_threshold(face, depth)
            
            print(f"{face:12s} (depth={depth}): wave={wave:6.3f}, state={state:10s}, threshold={threshold:6.3f}")
    
    print("\n=== MULTI-FACE SYNTHESIS ===\n")
    combined = cores.multi_face_synthesis(
        faces=['REMEMBER', 'APPLY', 'CREATE'],
        depths=[2, 3, 4]
    )
    print(f"Combined wave (REMEMBER+APPLY+CREATE): {combined:.3f}")
    
    # Visualize waves
    cores.visualize_waves()


if __name__ == "__main__":
    main()
