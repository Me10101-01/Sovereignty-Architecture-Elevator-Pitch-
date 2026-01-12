"""
Strategickhaos Swarm
Particle Swarm Optimization for sell thresholds
Recursive evolution in sandbox environment
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Callable
from dataclasses import dataclass
import random


@dataclass
class Particle:
    """Represents a particle in the swarm."""
    position: np.ndarray  # Sell thresholds for each source
    velocity: np.ndarray
    best_position: np.ndarray
    best_fitness: float
    fitness: float = 0.0


class StrategickhaosSwarm:
    """
    Particle Swarm Optimization for sell timing strategies.
    Evolves optimal thresholds for when to sell/collect income.
    """
    
    def __init__(self, n_particles: int = 50, n_dimensions: int = 6,
                 w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        """
        Initialize particle swarm optimizer.
        
        Args:
            n_particles: Number of particles in swarm
            n_dimensions: Number of dimensions (income sources)
            w: Inertia weight
            c1: Cognitive parameter
            c2: Social parameter
        """
        self.n_particles = n_particles
        self.n_dimensions = n_dimensions
        self.w = w  # Inertia
        self.c1 = c1  # Cognitive (personal best)
        self.c2 = c2  # Social (global best)
        
        self.particles: List[Particle] = []
        self.global_best_position = np.zeros(n_dimensions)
        self.global_best_fitness = float('-inf')
        
        self._initialize_swarm()
    
    def _initialize_swarm(self):
        """Initialize particles with random positions and velocities."""
        for _ in range(self.n_particles):
            # Position: sell threshold as percentage of cap (0.0 to 1.0)
            position = np.random.uniform(0.3, 0.95, self.n_dimensions)
            
            # Velocity: rate of change in threshold
            velocity = np.random.uniform(-0.1, 0.1, self.n_dimensions)
            
            particle = Particle(
                position=position,
                velocity=velocity,
                best_position=position.copy(),
                best_fitness=float('-inf')
            )
            
            self.particles.append(particle)
    
    def evaluate_fitness(self, particle: Particle, 
                        fitness_func: Callable[[np.ndarray], float]) -> float:
        """
        Evaluate fitness of a particle's position.
        
        Args:
            particle: Particle to evaluate
            fitness_func: Function that calculates fitness from position
            
        Returns:
            Fitness score
        """
        return fitness_func(particle.position)
    
    def update_particle(self, particle: Particle):
        """
        Update particle velocity and position.
        
        Args:
            particle: Particle to update
        """
        # Random factors
        r1 = np.random.random(self.n_dimensions)
        r2 = np.random.random(self.n_dimensions)
        
        # Velocity update
        cognitive = self.c1 * r1 * (particle.best_position - particle.position)
        social = self.c2 * r2 * (self.global_best_position - particle.position)
        
        particle.velocity = (self.w * particle.velocity + 
                           cognitive + social)
        
        # Position update
        particle.position = particle.position + particle.velocity
        
        # Clamp position to valid range [0.3, 0.95]
        particle.position = np.clip(particle.position, 0.3, 0.95)
    
    def optimize(self, fitness_func: Callable[[np.ndarray], float],
                max_iterations: int = 100) -> Tuple[np.ndarray, float]:
        """
        Run particle swarm optimization.
        
        Args:
            fitness_func: Function to evaluate fitness
            max_iterations: Maximum number of iterations
            
        Returns:
            Tuple of (best_position, best_fitness)
        """
        for iteration in range(max_iterations):
            for particle in self.particles:
                # Evaluate fitness
                particle.fitness = self.evaluate_fitness(particle, fitness_func)
                
                # Update personal best
                if particle.fitness > particle.best_fitness:
                    particle.best_fitness = particle.fitness
                    particle.best_position = particle.position.copy()
                
                # Update global best
                if particle.fitness > self.global_best_fitness:
                    self.global_best_fitness = particle.fitness
                    self.global_best_position = particle.position.copy()
            
            # Update all particles
            for particle in self.particles:
                self.update_particle(particle)
            
            # Optional: Print progress
            if (iteration + 1) % 10 == 0:
                print(f"Iteration {iteration + 1}/{max_iterations}: "
                      f"Best Fitness = {self.global_best_fitness:.2f}")
        
        return self.global_best_position, self.global_best_fitness
    
    def optimize_sell_timing(self, sim_state: Dict[str, Any]) -> Dict[str, float]:
        """
        Optimize sell timing thresholds for income sources.
        
        Args:
            sim_state: Current simulation state
            
        Returns:
            Dictionary mapping source names to optimal sell thresholds
        """
        source_names = sim_state.get('source_names', [])
        
        def fitness_function(thresholds: np.ndarray) -> float:
            """Calculate fitness based on total yield with these thresholds."""
            # Simulate 24h with these sell thresholds
            total_yield = 0.0
            
            for i, source_name in enumerate(source_names):
                threshold = thresholds[i]
                cap = sim_state.get('caps', {}).get(source_name, 250000)
                base_rate = sim_state.get('rates', {}).get(source_name, 1000)
                
                # Simulate income accumulation
                # Sell when threshold * cap is reached
                sell_point = threshold * cap
                time_to_sell = sell_point / base_rate if base_rate > 0 else float('inf')
                
                # Number of sells in 24h (1440 minutes)
                num_sells = min(1440 / time_to_sell if time_to_sell > 0 else 0, 100)
                total_yield += num_sells * sell_point
            
            return total_yield
        
        # Run optimization
        best_thresholds, best_fitness = self.optimize(fitness_function, max_iterations=100)
        
        # Convert to dictionary
        result = {}
        for i, source_name in enumerate(source_names):
            if i < len(best_thresholds):
                result[source_name] = float(best_thresholds[i])
        
        return result
    
    def get_swarm_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the current swarm state.
        
        Returns:
            Dictionary with swarm statistics
        """
        fitnesses = [p.fitness for p in self.particles]
        
        return {
            'n_particles': self.n_particles,
            'global_best_fitness': self.global_best_fitness,
            'global_best_position': self.global_best_position.tolist(),
            'mean_fitness': np.mean(fitnesses),
            'std_fitness': np.std(fitnesses),
            'min_fitness': np.min(fitnesses),
            'max_fitness': np.max(fitnesses)
        }
