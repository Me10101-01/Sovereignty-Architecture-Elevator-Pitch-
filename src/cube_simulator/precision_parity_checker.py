#!/usr/bin/env python3
"""
Precision Parity Checker
Extends reference parity to numeric precision domains.
Detects overflow/underflow in narrowing conversions.
"""

import math
from typing import Tuple


class PrecisionParityChecker:
    """
    Checks numeric precision parity for narrowing conversions.
    Detects overflow and underflow conditions using wave thresholds.
    """

    def __init__(self):
        self.numeric_ranges = {
            'Byte': (-128, 127),
            'Short': (-32768, 32767),
            'Integer': (-2147483648, 2147483647),
            'Float': (-3.4e38, 3.4e38),
            'Double': (-1.7e308, 1.7e308),
        }
    
    def check_narrowing(self, value: float, source_type: str, target_type: str) -> Tuple[str, float, str]:
        """
        Check if a narrowing conversion is safe.
        
        Returns:
            (status, wave_value, message)
        """
        if target_type not in self.numeric_ranges:
            return "ERROR", 0.0, f"Unknown type: {target_type}"
        
        min_val, max_val = self.numeric_ranges[target_type]
        
        # Calculate wave based on value proximity to bounds
        range_size = max_val - min_val
        normalized_value = (value - min_val) / range_size if range_size > 0 else 0
        wave = math.cos(2 * math.pi * normalized_value)
        
        # Check bounds
        if value < min_val:
            wave = -abs(wave)  # Negative for error
            return "PARITY_ERROR", wave, f"Underflow: {value} < {min_val} for {target_type}"
        elif value > max_val:
            wave = -abs(wave)  # Negative for error
            return "PARITY_ERROR", wave, f"Overflow: {value} > {max_val} for {target_type}"
        else:
            return "SAFE_NARROWING", wave, f"Safe: {value} within {target_type} range"


def main():
    """Demo: Check numeric precision parity."""
    checker = PrecisionParityChecker()
    
    print("\n=== PRECISION PARITY CHECKER DEMO ===\n")
    
    test_cases = [
        (100, 'Integer', 'Byte'),      # Safe
        (200, 'Integer', 'Byte'),      # Overflow
        (-200, 'Integer', 'Byte'),     # Underflow
        (1000, 'Integer', 'Short'),    # Safe
        (40000, 'Integer', 'Short'),   # Overflow
    ]
    
    for value, source, target in test_cases:
        status, wave, message = checker.check_narrowing(value, source, target)
        indicator = "❌" if "ERROR" in status else "✓"
        print(f"{indicator} {value:6d} ({source:7s} → {target:7s}) | Wave: {wave:6.3f}")
        print(f"  └─ {message}")


if __name__ == "__main__":
    main()
