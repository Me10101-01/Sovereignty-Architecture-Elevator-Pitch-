"""
ALU Module - FlameLang Trig-Wave Cores
Layer 3: Wave - Trigonometric wave-based computation

Implements wave-based arithmetic operations inspired by quantum computing
and trigonometric transformations.
"""

import math
from typing import Union, List
import numpy as np


class WaveALU:
    """
    Arithmetic Logic Unit using trigonometric wave operations
    Layer 3: Wave computation core
    """
    
    def __init__(self, frequency: float = 1.0, amplitude: float = 1.0):
        """
        Initialize Wave ALU
        
        Args:
            frequency: Base frequency for wave operations
            amplitude: Base amplitude for wave operations
        """
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = 0.0
        
    def wave_add(self, a: float, b: float) -> float:
        """
        Add two values using wave superposition
        
        Args:
            a, b: Values to add
            
        Returns:
            Sum using wave interference
        """
        # Represent as wave amplitudes and superpose
        wave_a = self.amplitude * math.sin(2 * math.pi * self.frequency * a + self.phase)
        wave_b = self.amplitude * math.sin(2 * math.pi * self.frequency * b + self.phase)
        return wave_a + wave_b
    
    def wave_multiply(self, a: float, b: float) -> float:
        """
        Multiply using wave modulation
        
        Args:
            a, b: Values to multiply
            
        Returns:
            Product using amplitude modulation
        """
        # Amplitude modulation
        carrier = math.sin(2 * math.pi * self.frequency * a)
        modulator = math.sin(2 * math.pi * self.frequency * b)
        return self.amplitude * carrier * modulator
    
    def wave_transform(self, value: float, transform_type: str = 'sin') -> float:
        """
        Apply trigonometric transformation to value
        
        Args:
            value: Input value
            transform_type: Type of transformation ('sin', 'cos', 'tan')
            
        Returns:
            Transformed value
        """
        angle = 2 * math.pi * self.frequency * value + self.phase
        
        if transform_type == 'sin':
            return self.amplitude * math.sin(angle)
        elif transform_type == 'cos':
            return self.amplitude * math.cos(angle)
        elif transform_type == 'tan':
            return self.amplitude * math.tan(angle)
        else:
            raise ValueError(f"Unknown transform type: {transform_type}")
    
    def wave_vector_op(self, vector: List[float], operation: str = 'sin') -> List[float]:
        """
        Apply wave operation to entire vector
        
        Args:
            vector: Input vector
            operation: Operation type ('sin', 'cos', 'fft', 'ifft')
            
        Returns:
            Transformed vector
        """
        if operation in ['sin', 'cos', 'tan']:
            return [self.wave_transform(v, operation) for v in vector]
        elif operation == 'fft':
            # Fast Fourier Transform for frequency domain analysis
            return list(np.fft.fft(vector))
        elif operation == 'ifft':
            # Inverse FFT
            return list(np.fft.ifft(vector).real)
        else:
            raise ValueError(f"Unknown vector operation: {operation}")
    
    def interference_pattern(self, waves: List[tuple]) -> callable:
        """
        Generate interference pattern from multiple waves
        
        Args:
            waves: List of (frequency, amplitude, phase) tuples
            
        Returns:
            Function that computes interference at given point
        """
        def pattern(x: float) -> float:
            result = 0.0
            for freq, amp, phase in waves:
                result += amp * math.sin(2 * math.pi * freq * x + phase)
            return result
        return pattern
    
    def set_phase(self, phase: float) -> None:
        """Set the phase offset for wave operations"""
        self.phase = phase
    
    def reset(self) -> None:
        """Reset ALU state"""
        self.phase = 0.0


def main():
    """Demonstration of Wave ALU"""
    print("="*60)
    print("Wave ALU - FlameLang Trig-Wave Cores (Layer 3: Wave)")
    print("="*60)
    print()
    
    alu = WaveALU(frequency=1.0, amplitude=1.0)
    
    # Test wave addition
    print("Wave Addition:")
    result = alu.wave_add(0.5, 0.3)
    print(f"  wave_add(0.5, 0.3) = {result:.4f}")
    print()
    
    # Test wave multiplication
    print("Wave Multiplication:")
    result = alu.wave_multiply(0.5, 0.3)
    print(f"  wave_multiply(0.5, 0.3) = {result:.4f}")
    print()
    
    # Test transformations
    print("Wave Transformations:")
    value = 0.25
    for transform in ['sin', 'cos', 'tan']:
        result = alu.wave_transform(value, transform)
        print(f"  {transform}({value}) = {result:.4f}")
    print()
    
    # Test vector operations
    print("Vector Operations:")
    vector = [0.0, 0.25, 0.5, 0.75, 1.0]
    sin_result = alu.wave_vector_op(vector, 'sin')
    print(f"  sin(vector) = {[f'{x:.4f}' for x in sin_result]}")
    print()
    
    # Test interference pattern
    print("Interference Pattern:")
    waves = [(1.0, 1.0, 0.0), (2.0, 0.5, 0.0), (3.0, 0.25, 0.0)]
    pattern = alu.interference_pattern(waves)
    for x in [0.0, 0.1, 0.2, 0.3]:
        print(f"  pattern({x:.1f}) = {pattern(x):.4f}")
    
    print()
    print("="*60)


if __name__ == "__main__":
    main()
