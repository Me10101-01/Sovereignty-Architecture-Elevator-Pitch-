"""
Entanglement Core - Quantum-Inspired Swarm Synchronization
Implements quantum-like entanglement patterns for distributed synchronization

Uses quantum-inspired algorithms for swarm coordination and state coherence.
"""

import math
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class EntanglementState(Enum):
    """Quantum-inspired entanglement states"""
    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    COLLAPSED = "collapsed"
    DECOHERENT = "decoherent"


@dataclass
class QuantumNode:
    """Node in the quantum-inspired swarm"""
    id: int
    state: complex
    phase: float
    entangled_with: List[int]
    coherence: float = 1.0
    
    def __repr__(self):
        return f"Node({self.id}, |ψ|={abs(self.state):.3f}, φ={self.phase:.3f})"


class EntanglementCore:
    """
    Quantum-inspired swarm synchronization core
    Manages entanglement between distributed nodes
    """
    
    def __init__(self, num_nodes: int = 8):
        """
        Initialize entanglement core with swarm nodes
        
        Args:
            num_nodes: Number of nodes in the swarm
        """
        self.num_nodes = num_nodes
        self.nodes: Dict[int, QuantumNode] = {}
        self.entanglement_matrix: List[List[float]] = []
        
        self._initialize_nodes()
        self._initialize_entanglement_matrix()
        
    def _initialize_nodes(self) -> None:
        """Initialize all nodes in superposition state"""
        for i in range(self.num_nodes):
            # Initialize in superposition: (|0⟩ + |1⟩) / √2
            state = complex(1/math.sqrt(2), 1/math.sqrt(2))
            phase = random.uniform(0, 2 * math.pi)
            self.nodes[i] = QuantumNode(
                id=i,
                state=state,
                phase=phase,
                entangled_with=[]
            )
    
    def _initialize_entanglement_matrix(self) -> None:
        """Initialize entanglement strength matrix"""
        self.entanglement_matrix = [
            [0.0 for _ in range(self.num_nodes)]
            for _ in range(self.num_nodes)
        ]
    
    def entangle(self, node_a: int, node_b: int, strength: float = 1.0) -> bool:
        """
        Create entanglement between two nodes
        
        Args:
            node_a, node_b: Node IDs to entangle
            strength: Entanglement strength (0.0 to 1.0)
            
        Returns:
            True if entanglement successful
        """
        if node_a not in self.nodes or node_b not in self.nodes:
            return False
        
        if node_a == node_b:
            return False
        
        # Update entanglement matrix (symmetric)
        self.entanglement_matrix[node_a][node_b] = strength
        self.entanglement_matrix[node_b][node_a] = strength
        
        # Update node entanglement lists
        if node_b not in self.nodes[node_a].entangled_with:
            self.nodes[node_a].entangled_with.append(node_b)
        if node_a not in self.nodes[node_b].entangled_with:
            self.nodes[node_b].entangled_with.append(node_a)
        
        return True
    
    def measure(self, node_id: int) -> Tuple[int, float]:
        """
        Measure node state (causes collapse of superposition)
        
        Args:
            node_id: ID of node to measure
            
        Returns:
            Tuple of (collapsed_state, probability)
        """
        if node_id not in self.nodes:
            return 0, 0.0
        
        node = self.nodes[node_id]
        
        # Probability of measuring |1⟩
        prob_one = abs(node.state) ** 2
        
        # Collapse to |0⟩ or |1⟩
        collapsed_state = 1 if random.random() < prob_one else 0
        
        # Update node state to collapsed value
        node.state = complex(collapsed_state, 0)
        
        # Propagate collapse to entangled nodes
        self._propagate_collapse(node_id, collapsed_state)
        
        return collapsed_state, prob_one
    
    def _propagate_collapse(self, source_node: int, collapsed_value: int) -> None:
        """
        Propagate measurement collapse to entangled nodes
        
        Args:
            source_node: Node that was measured
            collapsed_value: Collapsed state value
        """
        for entangled_id in self.nodes[source_node].entangled_with:
            if entangled_id in self.nodes:
                strength = self.entanglement_matrix[source_node][entangled_id]
                
                # Influence entangled node based on strength
                entangled_node = self.nodes[entangled_id]
                influence = strength * collapsed_value
                
                # Partial collapse based on entanglement strength
                real_part = entangled_node.state.real * (1 - strength) + influence
                imag_part = entangled_node.state.imag * (1 - strength)
                entangled_node.state = complex(real_part, imag_part)
    
    def synchronize_phases(self) -> float:
        """
        Synchronize phases across all nodes
        
        Returns:
            Phase coherence metric (0.0 to 1.0)
        """
        if not self.nodes:
            return 0.0
        
        # Calculate average phase
        avg_phase = sum(node.phase for node in self.nodes.values()) / len(self.nodes)
        
        # Adjust all node phases toward average
        for node in self.nodes.values():
            phase_diff = avg_phase - node.phase
            node.phase += 0.1 * phase_diff  # Gradual adjustment
        
        # Calculate phase coherence
        phase_variance = sum((node.phase - avg_phase) ** 2 for node in self.nodes.values())
        phase_variance /= len(self.nodes)
        
        coherence = math.exp(-phase_variance)  # Coherence decreases with variance
        return coherence
    
    def decohere(self, node_id: int, rate: float = 0.1) -> None:
        """
        Apply decoherence to a node (environmental interaction)
        
        Args:
            node_id: ID of node to decohere
            rate: Decoherence rate (0.0 to 1.0)
        """
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        
        # Reduce coherence
        node.coherence *= (1 - rate)
        
        # Add random phase noise
        noise = random.uniform(-rate, rate)
        node.phase += noise
        
        # Reduce superposition (move toward classical state)
        node.state = complex(
            node.state.real * (1 - rate * 0.5),
            node.state.imag * (1 - rate * 0.5)
        )
    
    def get_swarm_coherence(self) -> float:
        """
        Calculate overall swarm coherence
        
        Returns:
            Average coherence across all nodes
        """
        if not self.nodes:
            return 0.0
        
        return sum(node.coherence for node in self.nodes.values()) / len(self.nodes)
    
    def get_entanglement_degree(self) -> float:
        """
        Calculate average entanglement degree
        
        Returns:
            Average number of entangled connections per node
        """
        if not self.nodes:
            return 0.0
        
        total_connections = sum(len(node.entangled_with) for node in self.nodes.values())
        return total_connections / len(self.nodes)
    
    def reset(self) -> None:
        """Reset all nodes to initial superposition state"""
        self._initialize_nodes()
        self._initialize_entanglement_matrix()


def main():
    """Demonstration of Entanglement Core"""
    print("="*60)
    print("Entanglement Core - Quantum-Inspired Swarm Sync")
    print("="*60)
    print()
    
    # Initialize core with 8 nodes
    core = EntanglementCore(num_nodes=8)
    
    print("Initial State:")
    for node_id, node in core.nodes.items():
        print(f"  {node}")
    print()
    
    # Create entanglements
    print("Creating Entanglements:")
    core.entangle(0, 1, strength=0.9)
    core.entangle(1, 2, strength=0.8)
    core.entangle(2, 3, strength=0.7)
    core.entangle(0, 4, strength=0.6)
    print(f"  Average entanglement degree: {core.get_entanglement_degree():.2f}")
    print()
    
    # Synchronize phases
    print("Phase Synchronization:")
    for i in range(3):
        coherence = core.synchronize_phases()
        print(f"  Cycle {i+1}: coherence = {coherence:.4f}")
    print()
    
    # Measure a node
    print("Measuring Node 0:")
    collapsed, prob = core.measure(0)
    print(f"  Collapsed to: |{collapsed}⟩ (probability: {prob:.4f})")
    print(f"  Node 0 after: {core.nodes[0]}")
    print(f"  Node 1 after (entangled): {core.nodes[1]}")
    print()
    
    # Apply decoherence
    print("Applying Decoherence to Node 2:")
    core.decohere(2, rate=0.3)
    print(f"  Node 2 after: {core.nodes[2]}")
    print(f"  Swarm coherence: {core.get_swarm_coherence():.4f}")
    print()
    
    print("="*60)


if __name__ == "__main__":
    main()
