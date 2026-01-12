#!/usr/bin/env python3
"""
Reference Parity Checker Module
Entanglement Invariant Checker for type hierarchies.
Validates casts and detects parity errors using wave invariants.
"""

import json
import math
import networkx as nx
from typing import Tuple, Set, Optional


class ReferenceParityChecker:
    """
    Checks reference type parity using entangled subtree invariants.
    Inheritance hierarchies as entangled subtrees with wave-based validation.
    """

    def __init__(self, hierarchy_path: str = 'configs/oop_hierarchy.json'):
        self.hierarchy_path = hierarchy_path
        self.hierarchies = {}
        self.graphs = {}
        self.cast_rules = {}
        
    def load_hierarchies(self) -> None:
        """Load type hierarchies from JSON configuration."""
        try:
            with open(self.hierarchy_path, 'r') as f:
                data = json.load(f)
            
            self.cast_rules = data.get('cast_rules', {})
            
            # Build NetworkX graphs for each hierarchy
            for hierarchy in data.get('hierarchies', []):
                name = hierarchy['name']
                self.hierarchies[name] = hierarchy
                self.graphs[name] = self._build_graph(hierarchy)
                
        except FileNotFoundError:
            print(f"Warning: {self.hierarchy_path} not found. Using empty hierarchies.")
    
    def _build_graph(self, hierarchy: dict) -> nx.DiGraph:
        """Build directed graph from hierarchy definition."""
        G = nx.DiGraph()
        
        nodes = hierarchy.get('nodes', {})
        for node_name, node_data in nodes.items():
            G.add_node(node_name, depth=node_data.get('depth', 0))
            
            # Add edges to children
            for child in node_data.get('children', []):
                G.add_edge(node_name, child)
        
        return G
    
    def check_cast(self, runtime_type: str, target_type: str, 
                   hierarchy_name: str = "Animal Hierarchy", 
                   tick: int = 0) -> Tuple[str, float, str]:
        """
        Check if a cast is safe using wave invariants.
        
        Returns:
            (status, wave_value, message)
            - status: "SAFE_UPCAST", "SAFE_NARROWING", "PARITY_ERROR"
            - wave_value: wave amplitude (negative indicates error)
            - message: description of the check result
        """
        if hierarchy_name not in self.graphs:
            return "ERROR", 0.0, f"Hierarchy '{hierarchy_name}' not found"
        
        G = self.graphs[hierarchy_name]
        
        # Check if both types exist in hierarchy
        if runtime_type not in G or target_type not in G:
            return "ERROR", 0.0, f"Type not found in hierarchy"
        
        # Get subtree of target type (descendants)
        try:
            subtree = set(nx.descendants(G, target_type)) | {target_type}
        except nx.NetworkXError:
            subtree = {target_type}
        
        # Calculate wave based on type ranks (depths)
        runtime_depth = G.nodes[runtime_type].get('depth', 0)
        target_depth = G.nodes[target_type].get('depth', 0)
        
        # Compute wave invariant
        if target_depth > 0:
            wave = math.sin(math.pi * runtime_depth / max(target_depth, 1))
        else:
            wave = 1.0
        
        # Check if runtime type is in target subtree
        if runtime_type not in subtree:
            # Check if this is an upcast (target is ancestor of runtime)
            try:
                ancestors = set(nx.ancestors(G, runtime_type)) | {runtime_type}
                if target_type in ancestors:
                    # Upcast - safe
                    return "SAFE_UPCAST", abs(wave), f"Safe upcast: {runtime_type} → {target_type}"
            except nx.NetworkXError:
                pass
            
            # Downcast without guarantee - parity error
            wave = -abs(wave)  # Negative indicates error
            return "PARITY_ERROR", wave, f"ClassCastException: {runtime_type} ∉ subtree({target_type})"
        
        # Runtime type is in target subtree - check if it's a narrowing
        if runtime_depth > target_depth:
            # Downcast but with runtime guarantee
            return "SAFE_NARROWING", wave, f"Safe narrowing with runtime check: {runtime_type} → {target_type}"
        else:
            # Upcast
            return "SAFE_UPCAST", wave, f"Safe upcast: {runtime_type} → {target_type}"
    
    def get_rank(self, type_name: str, hierarchy_name: str = "Animal Hierarchy") -> int:
        """Get rank (depth) of a type in hierarchy."""
        if hierarchy_name not in self.graphs:
            return 0
        
        G = self.graphs[hierarchy_name]
        if type_name not in G:
            return 0
        
        return G.nodes[type_name].get('depth', 0)
    
    def visualize_hierarchy(self, hierarchy_name: str = "Animal Hierarchy") -> None:
        """Print ASCII visualization of hierarchy."""
        if hierarchy_name not in self.graphs:
            print(f"Hierarchy '{hierarchy_name}' not found")
            return
        
        G = self.graphs[hierarchy_name]
        hierarchy = self.hierarchies[hierarchy_name]
        root = hierarchy.get('root')
        
        print(f"\n=== {hierarchy_name} ===\n")
        self._print_subtree(G, root, 0)
    
    def _print_subtree(self, G: nx.DiGraph, node: str, indent: int) -> None:
        """Recursively print subtree with indentation."""
        if node not in G:
            return
        
        print("  " * indent + f"├─ {node} (depth: {G.nodes[node].get('depth', 0)})")
        
        # Get children
        children = list(G.successors(node))
        for child in children:
            self._print_subtree(G, child, indent + 1)


def main():
    """Demo: Check various casts for parity errors."""
    checker = ReferenceParityChecker()
    checker.load_hierarchies()
    
    print("\n=== REFERENCE PARITY CHECKER DEMO ===\n")
    
    # Visualize hierarchy
    checker.visualize_hierarchy("Animal Hierarchy")
    
    print("\n=== CAST CHECKS ===\n")
    
    # Test various casts
    test_casts = [
        ("Dog", "Animal", "Animal Hierarchy"),
        ("Dog", "Object", "Animal Hierarchy"),
        ("Cat", "Dog", "Animal Hierarchy"),
        ("Animal", "Dog", "Animal Hierarchy"),
        ("Mammal", "Animal", "Animal Hierarchy"),
        ("Eagle", "Bird", "Animal Hierarchy"),
        ("Byte", "Integer", "Numeric Hierarchy"),
        ("Integer", "Byte", "Numeric Hierarchy"),
    ]
    
    for runtime, target, hierarchy in test_casts:
        status, wave, message = checker.check_cast(runtime, target, hierarchy)
        error_indicator = "❌" if "ERROR" in status else "✓"
        print(f"{error_indicator} {runtime:10s} → {target:10s} | {status:20s} | Wave: {wave:6.3f}")
        print(f"  └─ {message}")


if __name__ == "__main__":
    main()
