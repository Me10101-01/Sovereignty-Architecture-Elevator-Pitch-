"""
Cognitive Cube Spec Module
Implements cognitive cube with Bloom taxonomy faces
Integrates with thought-log and reference parity systems
"""

import math
from typing import Dict, List, Tuple, Optional, Any


class CognitiveCubeSpec:
    """
    Cognitive Cube based on Bloom's Taxonomy
    6 faces representing cognitive levels
    """
    
    def __init__(self):
        self.faces = {
            'U': 'REMEMBER',   # Upper - Recall facts
            'R': 'UNDERSTAND',  # Right - Explain concepts
            'F': 'APPLY',       # Front - Use in new situations
            'D': 'ANALYZE',     # Down - Draw connections
            'L': 'EVALUATE',    # Left - Justify decisions
            'B': 'CREATE'       # Back - Produce original work
        }
        
        self.state = {
            'current_face': 'U',
            'rotation_history': [],
            'parity_errors': []
        }
    
    def rotate(self, direction: str) -> str:
        """
        Rotate cube to new face
        
        Args:
            direction: Target face code (U, R, F, D, L, B)
        
        Returns:
            New face name
        """
        if direction not in self.faces:
            print(f"Invalid direction: {direction}")
            return self.faces[self.state['current_face']]
        
        old_face = self.state['current_face']
        self.state['current_face'] = direction
        self.state['rotation_history'].append((old_face, direction))
        
        return self.faces[direction]
    
    def get_current_face(self) -> str:
        """Get current active face"""
        return self.faces[self.state['current_face']]
    
    def check_impossible_cube(self, transition: Tuple[str, str]) -> bool:
        """
        Check if transition represents an impossible cube
        Some cognitive transitions are illogical (e.g., CREATE without REMEMBER)
        
        Args:
            transition: (from_face, to_face) tuple
        
        Returns:
            True if transition is impossible
        """
        from_face, to_face = transition
        
        # Define impossible transitions
        impossible_transitions = {
            ('B', 'U'),  # Can't go from CREATE back to REMEMBER without synthesis
            ('L', 'U'),  # Can't go from EVALUATE back to REMEMBER without context
        }
        
        if (from_face, to_face) in impossible_transitions:
            self.state['parity_errors'].append({
                'transition': transition,
                'error': 'impossible_cube'
            })
            return True
        
        return False
    
    def calculate_transition_wave(self, from_face: str, to_face: str, tick: int = 0) -> float:
        """
        Calculate wave amplitude for cognitive transition
        Negative waves indicate problematic transitions
        """
        # Map faces to cognitive levels (0-5)
        level_map = {'U': 0, 'R': 1, 'F': 2, 'D': 3, 'L': 4, 'B': 5}
        
        from_level = level_map.get(from_face, 0)
        to_level = level_map.get(to_face, 0)
        
        # Calculate phase difference
        phase_diff = to_level - from_level
        
        # Forward progression (positive) vs backward (negative)
        if phase_diff > 0:
            # Forward is natural, use positive sine
            return math.sin(math.pi * phase_diff / 5)
        elif phase_diff < 0:
            # Backward requires reflection, use negative cosine
            return -abs(math.cos(math.pi * abs(phase_diff) / 5))
        else:
            # Same level, no transition
            return 0.0
    
    def get_rotation_sequence(self) -> List[Tuple[str, str]]:
        """Get history of rotations"""
        return self.state['rotation_history']
    
    def get_parity_errors(self) -> List[Dict[str, Any]]:
        """Get list of parity errors encountered"""
        return self.state['parity_errors']
    
    def reset(self) -> None:
        """Reset cube to initial state"""
        self.state = {
            'current_face': 'U',
            'rotation_history': [],
            'parity_errors': []
        }
    
    def visualize_state(self) -> None:
        """Print current cube state"""
        print("\n=== COGNITIVE CUBE STATE ===\n")
        print(f"Current Face: {self.state['current_face']} ({self.get_current_face()})")
        print(f"Rotations: {len(self.state['rotation_history'])}")
        print(f"Parity Errors: {len(self.state['parity_errors'])}")
        
        if self.state['rotation_history']:
            print("\nRecent Transitions:")
            for from_f, to_f in self.state['rotation_history'][-5:]:
                wave = self.calculate_transition_wave(from_f, to_f)
                print(f"  {from_f} → {to_f}: wave={wave:.3f}")


def main():
    """Demo cognitive cube"""
    cube = CognitiveCubeSpec()
    
    print("=== COGNITIVE CUBE DEMO ===\n")
    
    # Simulate cognitive journey
    journey = [
        ('R', 'Learn basics (REMEMBER)'),
        ('R', 'Understand concepts (UNDERSTAND)'),
        ('F', 'Apply knowledge (APPLY)'),
        ('D', 'Analyze patterns (ANALYZE)'),
        ('L', 'Evaluate solutions (EVALUATE)'),
        ('B', 'Create new work (CREATE)'),
        ('U', 'Reflect on fundamentals (REMEMBER)'),  # Potentially problematic
    ]
    
    for direction, description in journey:
        print(f"\n{description}")
        new_face = cube.rotate(direction)
        print(f"  Rotated to: {new_face}")
        
        # Check transition
        if len(cube.state['rotation_history']) >= 2:
            last_two = cube.state['rotation_history'][-2:]
            from_f, to_f = last_two[0][1], last_two[1][1]
            
            is_impossible = cube.check_impossible_cube((from_f, to_f))
            wave = cube.calculate_transition_wave(from_f, to_f)
            
            if is_impossible:
                print(f"  ⚠️  Impossible cube detected!")
            print(f"  Wave: {wave:.3f}")
    
    cube.visualize_state()
    
    # Show parity errors
    if cube.get_parity_errors():
        print("\n=== PARITY ERRORS ===\n")
        for error in cube.get_parity_errors():
            print(f"  Transition: {error['transition']}")
            print(f"  Error: {error['error']}")


if __name__ == "__main__":
    main()
