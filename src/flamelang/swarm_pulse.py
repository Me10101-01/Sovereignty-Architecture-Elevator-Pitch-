"""
SwarmPulse - Distributed Neuro-Acoustic Processing

Implements swarm-based signal processing for distributed therapeutic
sound generation across multiple nodes. Enables federated learning
and collaborative optimization of neuro-acoustic therapies.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SwarmNode:
    """Represents a node in the swarm network"""
    node_id: str
    capacity: float  # Processing capacity (0.0 to 1.0)
    location: Tuple[float, float, float]  # 3D coordinates
    active: bool = True
    current_load: float = 0.0
    processed_signals: int = 0
    
    def can_accept_task(self, task_load: float) -> bool:
        """Check if node can accept a task"""
        return self.active and (self.current_load + task_load) <= self.capacity


@dataclass
class SwarmTask:
    """Task for swarm processing"""
    task_id: str
    signal_data: np.ndarray
    task_type: str  # 'generation', 'analysis', 'optimization'
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    assigned_node: Optional[str] = None
    completed: bool = False
    result: Optional[Any] = None


class SwarmPulse:
    """
    Swarm-based pulse system for distributed neuro-acoustic processing
    
    Coordinates multiple processing nodes to generate and optimize
    therapeutic soundscapes in a distributed, resilient manner.
    """
    
    def __init__(self, cycle_ms: int = 432000000):
        """
        Initialize SwarmPulse
        
        Args:
            cycle_ms: Base cycle time in milliseconds (default 432M = 5 days)
        """
        self.cycle_ms = cycle_ms
        self.nodes: Dict[str, SwarmNode] = {}
        self.tasks: List[SwarmTask] = []
        self.completed_tasks: List[SwarmTask] = []
        self.pulse_count = 0
    
    def add_node(
        self,
        node_id: str,
        capacity: float = 1.0,
        location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    ):
        """Add a processing node to the swarm"""
        node = SwarmNode(
            node_id=node_id,
            capacity=capacity,
            location=location
        )
        self.nodes[node_id] = node
    
    def remove_node(self, node_id: str):
        """Remove a node from the swarm"""
        if node_id in self.nodes:
            del self.nodes[node_id]
    
    def submit_task(
        self,
        signal_data: np.ndarray,
        task_type: str = 'generation',
        priority: int = 1
    ) -> str:
        """
        Submit a task to the swarm
        
        Args:
            signal_data: Input signal data
            task_type: Type of processing task
            priority: Task priority (higher = more urgent)
            
        Returns:
            Task ID
        """
        task_id = f"task_{len(self.tasks)}_{datetime.now().timestamp()}"
        
        task = SwarmTask(
            task_id=task_id,
            signal_data=signal_data,
            task_type=task_type,
            priority=priority
        )
        
        self.tasks.append(task)
        return task_id
    
    def assign_tasks(self) -> int:
        """
        Assign pending tasks to available nodes
        
        Returns:
            Number of tasks assigned
        """
        # Sort tasks by priority
        pending_tasks = [t for t in self.tasks if not t.assigned_node]
        pending_tasks.sort(key=lambda t: t.priority, reverse=True)
        
        assigned_count = 0
        
        for task in pending_tasks:
            # Estimate task load
            task_load = self._estimate_task_load(task)
            
            # Find best node
            best_node = self._find_best_node(task_load, task.signal_data)
            
            if best_node:
                task.assigned_node = best_node.node_id
                best_node.current_load += task_load
                assigned_count += 1
        
        return assigned_count
    
    def _estimate_task_load(self, task: SwarmTask) -> float:
        """Estimate computational load of a task"""
        base_load = 0.1
        
        # Scale with signal size
        signal_factor = len(task.signal_data) / 44100.0  # Normalize to 1 second
        
        # Different task types have different costs
        type_multipliers = {
            'generation': 1.0,
            'analysis': 1.5,
            'optimization': 2.0,
        }
        
        multiplier = type_multipliers.get(task.task_type, 1.0)
        
        return base_load * signal_factor * multiplier
    
    def _find_best_node(
        self,
        task_load: float,
        signal_data: np.ndarray
    ) -> Optional[SwarmNode]:
        """
        Find the best node for a task
        
        Considers:
        - Available capacity
        - Current load
        - Spatial proximity (for distributed audio)
        """
        available_nodes = [
            node for node in self.nodes.values()
            if node.can_accept_task(task_load)
        ]
        
        if not available_nodes:
            return None
        
        # Score nodes
        scores = []
        for node in available_nodes:
            # Prefer nodes with lower current load
            load_score = 1.0 - (node.current_load / node.capacity)
            
            # Prefer nodes with higher capacity
            capacity_score = node.capacity
            
            # Combined score
            score = (load_score * 0.7) + (capacity_score * 0.3)
            scores.append((score, node))
        
        # Return best node - sort by score only
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[0][1]
    
    def pulse(self) -> Dict[str, Any]:
        """
        Execute one pulse cycle
        
        Processes assigned tasks and coordinates swarm activity
        
        Returns:
            Pulse statistics
        """
        self.pulse_count += 1
        
        # Assign pending tasks
        assigned = self.assign_tasks()
        
        # Process assigned tasks
        processed = self._process_tasks()
        
        # Update node states
        self._update_nodes()
        
        return {
            "pulse_number": self.pulse_count,
            "cycle_ms": self.cycle_ms,
            "nodes_active": sum(1 for n in self.nodes.values() if n.active),
            "nodes_total": len(self.nodes),
            "tasks_assigned": assigned,
            "tasks_processed": processed,
            "tasks_pending": len([t for t in self.tasks if not t.completed]),
            "average_node_load": self._calculate_average_load(),
        }
    
    def _process_tasks(self) -> int:
        """Process assigned tasks"""
        processed_count = 0
        
        for task in self.tasks:
            if task.assigned_node and not task.completed:
                # Simulate processing
                result = self._execute_task(task)
                
                if result:
                    task.completed = True
                    task.result = result
                    self.completed_tasks.append(task)
                    
                    # Release node capacity
                    if task.assigned_node in self.nodes:
                        node = self.nodes[task.assigned_node]
                        task_load = self._estimate_task_load(task)
                        node.current_load = max(0, node.current_load - task_load)
                        node.processed_signals += 1
                    
                    processed_count += 1
        
        # Remove completed tasks from active list
        self.tasks = [t for t in self.tasks if not t.completed]
        
        return processed_count
    
    def _execute_task(self, task: SwarmTask) -> Optional[Dict[str, Any]]:
        """Execute a task based on its type"""
        if task.task_type == 'generation':
            return self._generate_signal(task.signal_data)
        elif task.task_type == 'analysis':
            return self._analyze_signal(task.signal_data)
        elif task.task_type == 'optimization':
            return self._optimize_signal(task.signal_data)
        
        return None
    
    def _generate_signal(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Generate new signal based on input"""
        # Simple generation: create variation
        variation = input_data * np.random.uniform(0.9, 1.1)
        
        return {
            "output_signal": variation,
            "generation_method": "swarm_variation",
            "input_length": len(input_data),
            "output_length": len(variation),
        }
    
    def _analyze_signal(self, signal: np.ndarray) -> Dict[str, Any]:
        """Analyze signal properties"""
        return {
            "mean": float(np.mean(signal)),
            "std": float(np.std(signal)),
            "rms": float(np.sqrt(np.mean(signal ** 2))),
            "peak": float(np.max(np.abs(signal))),
            "length": len(signal),
        }
    
    def _optimize_signal(self, signal: np.ndarray) -> Dict[str, Any]:
        """Optimize signal for therapeutic effectiveness"""
        # Apply smoothing
        window_size = min(50, len(signal) // 10)
        if window_size > 0:
            window = np.ones(window_size) / window_size
            optimized = np.convolve(signal, window, mode='same')
        else:
            optimized = signal
        
        # Normalize
        max_val = np.max(np.abs(optimized))
        if max_val > 0:
            optimized = optimized / max_val
        
        return {
            "output_signal": optimized,
            "optimization_method": "smoothing_normalization",
            "improvement_score": self._calculate_improvement(signal, optimized),
        }
    
    def _calculate_improvement(self, original: np.ndarray, optimized: np.ndarray) -> float:
        """Calculate improvement score"""
        # Lower variance is better for therapeutic signals
        original_variance = np.var(np.diff(original)) if len(original) > 1 else 0
        optimized_variance = np.var(np.diff(optimized)) if len(optimized) > 1 else 0
        
        if original_variance == 0:
            return 0.0
        
        improvement = (original_variance - optimized_variance) / original_variance
        return float(np.clip(improvement, 0.0, 1.0))
    
    def _update_nodes(self):
        """Update node states"""
        # Could implement health checks, load balancing, etc.
        pass
    
    def _calculate_average_load(self) -> float:
        """Calculate average load across all nodes"""
        if not self.nodes:
            return 0.0
        
        total_load = sum(n.current_load for n in self.nodes.values())
        return total_load / len(self.nodes)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current swarm status"""
        return {
            "cycle_ms": self.cycle_ms,
            "pulse_count": self.pulse_count,
            "nodes": {
                node_id: {
                    "active": node.active,
                    "capacity": node.capacity,
                    "current_load": node.current_load,
                    "processed_signals": node.processed_signals,
                    "location": node.location,
                }
                for node_id, node in self.nodes.items()
            },
            "tasks_pending": len(self.tasks),
            "tasks_completed": len(self.completed_tasks),
            "average_load": self._calculate_average_load(),
        }
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get result of a completed task"""
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task.result
        
        return None
