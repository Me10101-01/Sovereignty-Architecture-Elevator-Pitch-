"""
Control Unit - Neural Tick Clocks & Lyapunov Chaos
Layer 5: DNA Timing - Chaotic timing based on Lyapunov exponents

Implements chaotic clock system for non-deterministic timing
and neural synchronization patterns.
"""

import math
import random
from typing import List, Tuple, Optional
from collections import deque


class LyapunovClock:
    """
    Neural tick clock using Lyapunov chaos theory
    Generates non-periodic timing signals for chaotic synchronization
    """
    
    def __init__(self, initial_state: float = 0.1, lyapunov_param: float = 3.9):
        """
        Initialize Lyapunov-based chaotic clock
        
        Args:
            initial_state: Initial state value (0 < x < 1)
            lyapunov_param: Lyapunov parameter (3.57 < r < 4 for chaos)
        """
        self.state = initial_state
        self.param = lyapunov_param
        self.tick_count = 0
        self.history = deque(maxlen=1000)
        
    def logistic_map(self, x: float) -> float:
        """
        Apply logistic map iteration: x_{n+1} = r * x_n * (1 - x_n)
        
        Args:
            x: Current state
            
        Returns:
            Next state
        """
        return self.param * x * (1 - x)
    
    def tick(self) -> float:
        """
        Generate next tick value using chaotic dynamics
        
        Returns:
            Chaotic tick value
        """
        self.state = self.logistic_map(self.state)
        self.history.append(self.state)
        self.tick_count += 1
        return self.state
    
    def tick_n(self, n: int) -> List[float]:
        """
        Generate n tick values
        
        Args:
            n: Number of ticks
            
        Returns:
            List of chaotic tick values
        """
        return [self.tick() for _ in range(n)]
    
    def estimate_lyapunov_exponent(self, iterations: int = 1000) -> float:
        """
        Estimate Lyapunov exponent for current parameter
        Positive exponent indicates chaos
        
        Args:
            iterations: Number of iterations for estimation
            
        Returns:
            Estimated Lyapunov exponent
        """
        x = self.state
        lyapunov_sum = 0.0
        
        for _ in range(iterations):
            x = self.logistic_map(x)
            # Derivative of logistic map
            derivative = abs(self.param * (1 - 2 * x))
            if derivative > 0:
                lyapunov_sum += math.log(derivative)
        
        return lyapunov_sum / iterations
    
    def reset(self, initial_state: Optional[float] = None) -> None:
        """Reset clock to initial state"""
        if initial_state is not None:
            self.state = initial_state
        self.tick_count = 0
        self.history.clear()


class NeuralControlUnit:
    """
    Control unit coordinating multiple neural tick clocks
    Implements DNA timing layer for processor synchronization
    """
    
    def __init__(self, num_clocks: int = 4):
        """
        Initialize neural control unit
        
        Args:
            num_clocks: Number of independent chaotic clocks
        """
        self.num_clocks = num_clocks
        self.clocks = []
        
        # Initialize clocks with different parameters for diversity
        for i in range(num_clocks):
            initial_state = 0.1 + (i * 0.1)
            param = 3.7 + (i * 0.05)  # Different chaos levels
            self.clocks.append(LyapunovClock(initial_state, param))
        
        self.sync_threshold = 0.5
        
    def tick_all(self) -> List[float]:
        """
        Tick all clocks simultaneously
        
        Returns:
            List of tick values from all clocks
        """
        return [clock.tick() for clock in self.clocks]
    
    def synchronize(self) -> Tuple[bool, float]:
        """
        Check if clocks are synchronized within threshold
        
        Returns:
            Tuple of (is_synchronized, sync_metric)
        """
        states = [clock.state for clock in self.clocks]
        mean_state = sum(states) / len(states)
        variance = sum((s - mean_state) ** 2 for s in states) / len(states)
        
        is_synced = variance < self.sync_threshold
        return is_synced, variance
    
    def phase_lock(self, target_phase: float = 0.5) -> None:
        """
        Attempt to phase-lock all clocks to target
        
        Args:
            target_phase: Target phase value for all clocks
        """
        for clock in self.clocks:
            # Nudge clock state toward target
            clock.state = (clock.state + target_phase) / 2
    
    def get_consensus_tick(self) -> float:
        """
        Get consensus tick value across all clocks
        
        Returns:
            Median tick value
        """
        ticks = self.tick_all()
        sorted_ticks = sorted(ticks)
        n = len(sorted_ticks)
        
        if n % 2 == 0:
            return (sorted_ticks[n//2 - 1] + sorted_ticks[n//2]) / 2
        else:
            return sorted_ticks[n//2]
    
    def chaos_metric(self) -> float:
        """
        Calculate overall chaos metric of the system
        
        Returns:
            Average Lyapunov exponent across all clocks
        """
        exponents = [clock.estimate_lyapunov_exponent(100) for clock in self.clocks]
        return sum(exponents) / len(exponents)
    
    def reset_all(self) -> None:
        """Reset all clocks"""
        for clock in self.clocks:
            clock.reset()


def main():
    """Demonstration of Neural Control Unit"""
    print("="*60)
    print("Control Unit - Neural Tick Clocks & Lyapunov Chaos")
    print("Layer 5: DNA Timing")
    print("="*60)
    print()
    
    # Test single Lyapunov clock
    print("Single Lyapunov Clock:")
    clock = LyapunovClock(initial_state=0.1, lyapunov_param=3.9)
    ticks = clock.tick_n(10)
    print(f"  First 10 ticks: {[f'{t:.4f}' for t in ticks]}")
    
    lyapunov = clock.estimate_lyapunov_exponent(1000)
    print(f"  Lyapunov exponent: {lyapunov:.4f}")
    print(f"  (Positive = Chaotic behavior)")
    print()
    
    # Test neural control unit
    print("Neural Control Unit (4 clocks):")
    control = NeuralControlUnit(num_clocks=4)
    
    print("  Tick all clocks:")
    for i in range(5):
        ticks = control.tick_all()
        is_synced, variance = control.synchronize()
        print(f"    Cycle {i+1}: {[f'{t:.4f}' for t in ticks]}")
        print(f"      Sync: {is_synced}, Variance: {variance:.6f}")
    print()
    
    print("  Consensus tick values:")
    for i in range(3):
        consensus = control.get_consensus_tick()
        print(f"    Consensus {i+1}: {consensus:.4f}")
    print()
    
    print("  System chaos metric:")
    chaos = control.chaos_metric()
    print(f"    Average Lyapunov exponent: {chaos:.4f}")
    print()
    
    print("="*60)


if __name__ == "__main__":
    main()
