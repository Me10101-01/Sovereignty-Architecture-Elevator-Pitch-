"""
GTA Economy Simulator
Master simulator: Quantum states = income qubits
Orchestrates all Phase 6 components
"""

import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np

from .neural_tick_clock import NeuralTickClock
from .trig_wave_core import TrigWaveCore
from .entanglement_core import EntanglementCore
from .strategickhaos_swarm import StrategickhaosSwarm


class GTAEconomySim:
    """
    Master GTA Economy Simulator.
    Integrates all Phase 6 components for full economic simulation.
    """
    
    def __init__(self, yaml_path: str):
        """
        Initialize economy simulator.
        
        Args:
            yaml_path: Path to income_sources.yaml configuration
        """
        self.yaml_path = yaml_path
        
        # Load configuration
        with open(yaml_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.global_params = self.config['global_params']
        
        # Initialize all components
        self.tick_clock = NeuralTickClock(self.global_params)
        self.wave_core = TrigWaveCore(yaml_path)
        self.entanglement = EntanglementCore(yaml_path)
        
        # State tracking
        self.current_balances: Dict[str, float] = {}
        self.total_income = 0.0
        self.simulation_time = 0.0  # Minutes
        
        # Initialize balances
        self._initialize_balances()
        
    def _initialize_balances(self):
        """Initialize all income source balances to zero."""
        for source_name in self.wave_core.get_all_passive_sources():
            self.current_balances[source_name] = 0.0
    
    def activate_dependencies(self, dependencies: List[str]):
        """
        Activate specific dependencies.
        
        Args:
            dependencies: List of dependency names to activate
        """
        for dep in dependencies:
            self.entanglement.set_dependency_state(dep, True)
    
    def activate_all_dependencies(self):
        """Activate all dependencies for maximum production."""
        self.entanglement.activate_all_dependencies()
    
    def simulate_tick(self, dt: float = 1.0) -> Dict[str, float]:
        """
        Simulate one time tick.
        
        Args:
            dt: Time delta in minutes
            
        Returns:
            Dictionary of income generated this tick per source
        """
        tick_income = {}
        
        for source_name in self.wave_core.get_all_passive_sources():
            # Check if dependencies are satisfied
            deps_satisfied = self.entanglement.are_dependencies_satisfied(source_name)
            
            # Calculate production rate
            rate = self.wave_core.production_rate(
                source_name, self.simulation_time, deps_satisfied
            )
            
            # Apply entanglement boost
            boost = self.entanglement.get_entanglement_boost(source_name)
            rate *= boost
            
            # Calculate income for this tick
            income = rate * dt
            
            # Get cap
            source_config = self.wave_core.get_source_config(source_name)
            cap = source_config.get('cap', float('inf'))
            
            # Update balance (respecting cap)
            current = self.current_balances[source_name]
            if current + income > cap:
                income = cap - current
                self.current_balances[source_name] = cap
            else:
                self.current_balances[source_name] += income
            
            tick_income[source_name] = income
        
        self.simulation_time += dt
        return tick_income
    
    def collect_from_source(self, source_name: str) -> float:
        """
        Collect income from a specific source.
        
        Args:
            source_name: Name of the income source
            
        Returns:
            Amount collected
        """
        collected = self.current_balances.get(source_name, 0.0)
        self.current_balances[source_name] = 0.0
        self.total_income += collected
        return collected
    
    def collect_all(self) -> float:
        """
        Collect income from all sources.
        
        Returns:
            Total amount collected
        """
        total = 0.0
        for source_name in list(self.current_balances.keys()):
            total += self.collect_from_source(source_name)
        return total
    
    def run(self, duration_hours: float = 24, dt: float = 1.0) -> Dict[str, Any]:
        """
        Run simulation for a specified duration.
        
        Args:
            duration_hours: Duration in hours
            dt: Time step in minutes
            
        Returns:
            Simulation results
        """
        duration_min = duration_hours * 60
        steps = int(duration_min / dt)
        
        income_history = []
        
        for step in range(steps):
            tick_income = self.simulate_tick(dt)
            income_history.append(tick_income)
            
            # Auto-collect when sources hit cap
            for source_name, balance in self.current_balances.items():
                source_config = self.wave_core.get_source_config(source_name)
                cap = source_config.get('cap', float('inf'))
                
                if balance >= cap:
                    self.collect_from_source(source_name)
        
        # Final collection
        final_collection = self.collect_all()
        
        results = {
            'duration_hours': duration_hours,
            'total_income': self.total_income,
            'final_collection': final_collection,
            'simulation_time_min': self.simulation_time,
            'average_per_hour': self.total_income / duration_hours if duration_hours > 0 else 0,
            'income_by_source': self._calculate_source_totals(income_history),
            'entanglement_summary': self.entanglement.get_entanglement_summary()
        }
        
        return results
    
    def _calculate_source_totals(self, income_history: List[Dict[str, float]]) -> Dict[str, float]:
        """Calculate total income per source from history."""
        totals = {}
        for tick_income in income_history:
            for source_name, income in tick_income.items():
                totals[source_name] = totals.get(source_name, 0.0) + income
        return totals
    
    def optimize_with_swarm(self, duration_hours: float = 24) -> Dict[str, Any]:
        """
        Use particle swarm optimization to find best sell strategies.
        
        Args:
            duration_hours: Duration to simulate
            
        Returns:
            Optimization results
        """
        # Prepare simulation state for swarm
        source_names = self.wave_core.get_all_passive_sources()
        
        sim_state = {
            'source_names': source_names,
            'caps': {},
            'rates': {}
        }
        
        for source_name in source_names:
            source_config = self.wave_core.get_source_config(source_name)
            sim_state['caps'][source_name] = source_config.get('cap', 250000)
            sim_state['rates'][source_name] = self.wave_core.calculate_base_rate(source_name)
        
        # Initialize swarm
        swarm = StrategickhaosSwarm(
            n_particles=self.global_params.get('swarm_particle_count', 50),
            n_dimensions=len(source_names)
        )
        
        # Optimize
        best_thresholds = swarm.optimize_sell_timing(sim_state)
        
        return {
            'best_thresholds': best_thresholds,
            'swarm_stats': swarm.get_swarm_statistics(),
            'source_names': source_names
        }
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current simulation state.
        
        Returns:
            Current state dictionary
        """
        return {
            'simulation_time_min': self.simulation_time,
            'current_balances': self.current_balances.copy(),
            'total_income': self.total_income,
            'tick_rate': self.tick_clock.get_tick_rate(self.simulation_time),
            'entanglement_summary': self.entanglement.get_entanglement_summary()
        }
    
    def reset(self):
        """Reset simulation state."""
        self._initialize_balances()
        self.total_income = 0.0
        self.simulation_time = 0.0
