"""
Reference Parity Checker Module
Inheritance hierarchies as entangled subtrees
Checks type compatibility and parity invariants
"""

import math
import json
from typing import Dict, Set, List, Tuple, Optional, Any
import networkx as nx


class ReferenceParityChecker:
    """Checks reference type parity using wave-based invariants"""
    
    def __init__(self, hierarchy_path: Optional[str] = None):
        self.hierarchy_path = hierarchy_path or "configs/oop_hierarchy.json"
        self.hierarchy_graph = nx.DiGraph()
        self.hierarchy_data: Dict[str, Any] = {}
        self.load_hierarchy()
    
    def load_hierarchy(self) -> None:
        """Load OOP hierarchy from JSON config"""
        try:
            with open(self.hierarchy_path, 'r') as f:
                data = json.load(f)
            
            self.hierarchy_data = data.get('hierarchy', {})
            
            # Build directed graph
            for type_name, type_info in self.hierarchy_data.items():
                self.hierarchy_graph.add_node(type_name, **type_info)
                
                # Add edges from parent to children
                parent = type_info.get('parent')
                if parent:
                    self.hierarchy_graph.add_edge(parent, type_name)
            
        except FileNotFoundError:
            print(f"Warning: {self.hierarchy_path} not found. Using empty hierarchy.")
    
    def get_subtree(self, type_name: str) -> Set[str]:
        """Get all descendants of a type (subtree)"""
        if type_name not in self.hierarchy_graph:
            return set()
        
        descendants = nx.descendants(self.hierarchy_graph, type_name)
        return descendants | {type_name}
    
    def get_ancestors(self, type_name: str) -> Set[str]:
        """Get all ancestors of a type"""
        if type_name not in self.hierarchy_graph:
            return set()
        
        return set(nx.ancestors(self.hierarchy_graph, type_name))
    
    def check_upcast(self, runtime_type: str, target_type: str) -> Tuple[bool, str, float]:
        """Check if upcast is safe (child -> parent)"""
        ancestors = self.get_ancestors(runtime_type)
        
        if target_type in ancestors:
            # Safe upcast
            wave = self._calculate_wave(runtime_type, target_type, direction="upcast")
            return True, "SAFE_UPCAST", wave
        
        return False, "INVALID_UPCAST", -1.0
    
    def check_downcast(self, runtime_type: str, target_type: str) -> Tuple[bool, str, float]:
        """Check if downcast is valid (parent -> child)"""
        subtree = self.get_subtree(target_type)
        
        if runtime_type not in subtree:
            # Parity error: runtime type not in target's subtree
            wave = self._calculate_wave(runtime_type, target_type, direction="downcast")
            return False, "PARITY_ERROR (ClassCastException)", wave
        
        # Valid downcast
        wave = self._calculate_wave(runtime_type, target_type, direction="downcast")
        return True, "SAFE_NARROWING", wave
    
    def reference_parity(self, runtime_type: str, target_type: str, tick: int = 0) -> Tuple[str, float]:
        """
        Main parity check for reference types
        Returns (status, wave) tuple
        """
        if runtime_type not in self.hierarchy_graph or target_type not in self.hierarchy_graph:
            return "TYPE_NOT_FOUND", 0.0
        
        # Check if downcast
        subtree = self.get_subtree(target_type)
        
        if runtime_type not in subtree:
            # Invalid cast
            wave = self._calculate_wave(runtime_type, target_type, direction="invalid")
            if wave < 0:
                return "PARITY_ERROR (ClassCastException)", wave
            return "INVARIANT_VIOLATION", wave
        
        # Valid narrowing
        wave = self._calculate_wave(runtime_type, target_type, direction="safe")
        return "SAFE_NARROWING", wave
    
    def _calculate_wave(self, runtime_type: str, target_type: str, direction: str) -> float:
        """Calculate wave function for type compatibility"""
        runtime_level = self.hierarchy_data.get(runtime_type, {}).get('level', 0)
        target_level = self.hierarchy_data.get(target_type, {}).get('level', 0)
        
        if direction == "upcast":
            # Upcast is always positive (safe)
            return abs(math.sin(math.pi * runtime_level / max(target_level, 1)))
        elif direction == "downcast" or direction == "safe":
            # Downcast depends on compatibility
            return math.sin(math.pi * runtime_level / max(target_level, 1))
        else:
            # Invalid cast is negative
            return -abs(math.cos(math.pi * runtime_level / max(target_level, 1)))
    
    def get_rank(self, type_name: str) -> int:
        """Get hierarchical rank (level) of a type"""
        return self.hierarchy_data.get(type_name, {}).get('level', 0)
    
    def visualize_hierarchy(self) -> None:
        """Print hierarchy tree"""
        print("\n=== REFERENCE TYPE HIERARCHY ===\n")
        
        def print_tree(node: str, prefix: str = "", is_last: bool = True):
            children = list(self.hierarchy_graph.successors(node))
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{node}")
            
            extension = "    " if is_last else "│   "
            for i, child in enumerate(children):
                print_tree(child, prefix + extension, i == len(children) - 1)
        
        # Find root nodes (nodes with no predecessors)
        roots = [n for n in self.hierarchy_graph.nodes() if self.hierarchy_graph.in_degree(n) == 0]
        
        for root in roots:
            print_tree(root)


def main():
    """Demo reference parity checker"""
    checker = ReferenceParityChecker()
    
    print("\n=== REFERENCE PARITY DEMO ===\n")
    
    # Test cases
    test_cases = [
        ("Cat", "Dog", "Should fail: incompatible siblings"),
        ("Dog", "Animal", "Should pass: upcast to parent"),
        ("Animal", "Dog", "Should fail: downcast without runtime check"),
        ("Car", "Vehicle", "Should pass: upcast to parent"),
        ("Cat", "Animal", "Should pass: upcast to parent"),
    ]
    
    for runtime, target, description in test_cases:
        status, wave = checker.reference_parity(runtime, target)
        print(f"{description}")
        print(f"  Cast: {runtime} -> {target}")
        print(f"  Status: {status}")
        print(f"  Wave: {wave:.3f}")
        print()
    
    checker.visualize_hierarchy()


if __name__ == "__main__":
    main()
