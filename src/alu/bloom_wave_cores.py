#!/usr/bin/env python3
"""
Bloom Wave Cores Module
Multi-dimensional wave cores for Cognitive Cube faces (Bloom Taxonomy).
Implements trig-formula dimensions for cognitive operations.
"""

import math
import json
from typing import Dict, Callable


class BloomWaveCores:
    """
    Multi-dimensional wave cores mapping Bloom taxonomy to oscillatory functions.
    Each cognitive level (REMEMBER, UNDERSTAND, etc.) has a unique wave signature.
    """

    def __init__(self, config_path: str = 'configs/cube_mappings.json'):
        self.config_path = config_path
        self.bloom_faces = {}
        self.wave_formulas = {}
        self._init_wave_functions()
        
    def load_config(self) -> None:
        """Load Bloom face mappings from configuration."""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            self.bloom_faces = data.get('bloom_faces', {})
            self.wave_formulas = data.get('wave_formulas', {})
        except FileNotFoundError:
            print(f"Warning: {self.config_path} not found. Using default mappings.")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default Bloom face mappings."""
        self.bloom_faces = {
            'U': 'REMEMBER',
            'R': 'UNDERSTAND',
            'F': 'APPLY',
            'D': 'ANALYZE',
            'L': 'EVALUATE',
            'B': 'CREATE'
        }
    
    def _init_wave_functions(self) -> None:
        """Initialize wave function generators for each Bloom level."""
        self.wave_functions: Dict[str, Callable[[float], float]] = {
            'REMEMBER': self._wave_remember,
            'UNDERSTAND': self._wave_understand,
            'APPLY': self._wave_apply,
            'ANALYZE': self._wave_analyze,
            'EVALUATE': self._wave_evaluate,
            'CREATE': self._wave_create
        }
    
    def _wave_remember(self, x: float) -> float:
        """
        Base sine wave for REMEMBER (foundational retrieval).
        Simple oscillation representing basic recall.
        """
        return math.sin(math.pi * x / 6)
    
    def _wave_understand(self, x: float) -> float:
        """
        Cosine wave for UNDERSTAND (comprehension).
        Phase-shifted from REMEMBER, representing deeper processing.
        """
        return math.cos(math.pi * x / 6)
    
    def _wave_apply(self, x: float) -> float:
        """
        Composite wave for APPLY (practical application).
        Base sine with harmonic for complexity.
        """
        return math.sin(x) + 0.5 * math.sin(2 * x)
    
    def _wave_analyze(self, x: float) -> float:
        """
        Composite cosine for ANALYZE (breaking down).
        Multiple harmonics representing decomposition.
        """
        return math.cos(x) + 0.3 * math.cos(3 * x)
    
    def _wave_evaluate(self, x: float) -> float:
        """
        Exponential decay for EVALUATE (critical judgment).
        Represents convergence to a judgment.
        """
        return math.exp(-x / 10)
    
    def _wave_create(self, x: float) -> float:
        """
        Damped sine for CREATE (synthesis).
        Oscillation with decay representing creative emergence.
        """
        return math.sin(x) * math.exp(-x / 4)
    
    def compute_wave(self, face: str, depth: float = 1.0) -> float:
        """
        Compute wave amplitude for a given Bloom face at specified depth.
        
        Args:
            face: Cube face (U, R, F, D, L, B) or Bloom level name
            depth: Cognitive depth parameter (default: 1.0)
        
        Returns:
            Wave amplitude value
        """
        # Convert face notation to Bloom level if needed
        if face in self.bloom_faces:
            bloom_level = self.bloom_faces[face]
        else:
            bloom_level = face
        
        # Get wave function
        wave_func = self.wave_functions.get(bloom_level, self._wave_remember)
        
        return wave_func(depth)
    
    def compute_multidim_wave(self, faces: list, depth: float = 1.0) -> Dict[str, float]:
        """
        Compute multi-dimensional wave across multiple Bloom faces.
        Useful for complex cognitive operations spanning multiple dimensions.
        
        Args:
            faces: List of faces or Bloom levels
            depth: Cognitive depth parameter
        
        Returns:
            Dictionary mapping each face to its wave amplitude
        """
        results = {}
        for face in faces:
            results[face] = self.compute_wave(face, depth)
        return results
    
    def detect_parity_threshold(self, face: str, depth: float = 1.0, 
                                threshold: float = -0.5) -> bool:
        """
        Detect if wave amplitude crosses parity threshold.
        Negative values below threshold indicate "impossible cube" states.
        
        Args:
            face: Cube face or Bloom level
            depth: Cognitive depth parameter
            threshold: Parity error threshold (default: -0.5)
        
        Returns:
            True if parity error detected (wave < threshold)
        """
        wave = self.compute_wave(face, depth)
        return wave < threshold
    
    def get_dominant_face(self, depth: float = 1.0) -> str:
        """
        Determine dominant Bloom face at given depth.
        Returns the face with maximum wave amplitude.
        
        Args:
            depth: Cognitive depth parameter
        
        Returns:
            Dominant face notation (U, R, F, D, L, B)
        """
        max_amplitude = -float('inf')
        dominant = 'U'
        
        for face, bloom_level in self.bloom_faces.items():
            amplitude = abs(self.compute_wave(face, depth))
            if amplitude > max_amplitude:
                max_amplitude = amplitude
                dominant = face
        
        return dominant
    
    def visualize_wave_spectrum(self, depth_range: range = range(0, 10)) -> None:
        """Print ASCII visualization of wave spectrum across depth range."""
        print("\n=== BLOOM WAVE SPECTRUM ===\n")
        print(f"{'Depth':>6} | ", end='')
        for face in self.bloom_faces.keys():
            print(f"{face:>8}", end=' ')
        print()
        print("-" * 70)
        
        for depth in depth_range:
            print(f"{depth:>6} | ", end='')
            for face in self.bloom_faces.keys():
                wave = self.compute_wave(face, float(depth))
                print(f"{wave:>8.3f}", end=' ')
            print()


def main():
    """Demo: Compute and visualize Bloom wave cores."""
    cores = BloomWaveCores()
    cores.load_config()
    
    print("\n=== BLOOM WAVE CORES DEMO ===\n")
    
    # Test individual faces
    print("Individual Face Waves (depth=3):\n")
    for face, bloom_level in cores.bloom_faces.items():
        wave = cores.compute_wave(face, 3.0)
        print(f"  {face} ({bloom_level:10s}): {wave:7.4f}")
    
    # Test multi-dimensional wave
    print("\n\nMulti-Dimensional Wave (REMEMBER + CREATE, depth=5):\n")
    multi_wave = cores.compute_multidim_wave(['REMEMBER', 'CREATE'], 5.0)
    for face, amplitude in multi_wave.items():
        print(f"  {face:10s}: {amplitude:7.4f}")
    
    # Test parity threshold detection
    print("\n\nParity Threshold Detection (threshold=-0.5):\n")
    test_cases = [
        ('EVALUATE', 10.0),
        ('CREATE', 8.0),
        ('REMEMBER', 3.0),
    ]
    for face, depth in test_cases:
        has_error = cores.detect_parity_threshold(face, depth)
        wave = cores.compute_wave(face, depth)
        status = "❌ PARITY ERROR" if has_error else "✓ OK"
        print(f"  {face:10s} @ depth {depth:4.1f}: {wave:7.4f} - {status}")
    
    # Visualize spectrum
    print("\n")
    cores.visualize_wave_spectrum(range(0, 6))
    
    # Find dominant face at various depths
    print("\n\nDominant Face by Depth:\n")
    for depth in [1, 3, 5, 7, 9]:
        dominant = cores.get_dominant_face(float(depth))
        bloom_level = cores.bloom_faces[dominant]
        print(f"  Depth {depth}: {dominant} ({bloom_level})")


if __name__ == "__main__":
    main()
