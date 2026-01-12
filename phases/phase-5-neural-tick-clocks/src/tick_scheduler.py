"""
Phase 5: Neural Tick Scheduler
Trig-wave clocks: sin(ωt) * base_rate
"""

import math
import time

class NeuralTickScheduler:
    """Neural tick clock with trigonometric wave scheduling."""
    
    def __init__(self, base_rate=1.0, frequency=1.0):
        self.base_rate = base_rate
        self.frequency = frequency  # ω in sin(ωt)
        self.start_time = time.time()
    
    def get_current_rate(self):
        """Calculate current tick rate."""
        elapsed = time.time() - self.start_time
        wave = math.sin(2 * math.pi * self.frequency * elapsed)
        # Map [-1, 1] to [0.5, 1.5] for positive rates
        rate = self.base_rate * (1.0 + 0.5 * wave)
        return rate
    
    def tick(self):
        """Generate a tick event."""
        rate = self.get_current_rate()
        return {
            'rate': rate,
            'timestamp': time.time() - self.start_time
        }
    
    def schedule(self, duration=10):
        """Run scheduler for duration seconds."""
        print(f"Neural Tick Scheduler running for {duration}s...")
        end_time = time.time() + duration
        
        while time.time() < end_time:
            tick = self.tick()
            print(f"Tick @ {tick['timestamp']:.2f}s: rate={tick['rate']:.3f}")
            time.sleep(1)


if __name__ == '__main__':
    scheduler = NeuralTickScheduler(base_rate=1.0, frequency=0.1)
    scheduler.schedule(duration=10)
    print("Neural Tick Scheduler: Complete")
