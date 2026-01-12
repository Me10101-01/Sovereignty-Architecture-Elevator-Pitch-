"""
Sandbox Evolver
Recursive genetic algorithm for strategy evolution
Self-modifying strategies via mutation and selection
"""

import random
import json
from typing import Dict, List, Any, Tuple
import numpy as np
from pathlib import Path

from gta_economy_sim import GTAEconomySim


class Strategy:
    """Represents an evolved strategy."""
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize strategy with parameters.
        
        Args:
            params: Strategy parameters
        """
        self.params = params
        self.fitness = 0.0
    
    def mutate(self, mutation_rate: float = 0.01) -> 'Strategy':
        """
        Create a mutated copy of this strategy.
        
        Args:
            mutation_rate: Probability of mutation per parameter
            
        Returns:
            New mutated strategy
        """
        new_params = self.params.copy()
        
        for key, value in new_params.items():
            if random.random() < mutation_rate:
                if isinstance(value, (int, float)):
                    # Mutate numeric values by ±20%
                    delta = value * random.uniform(-0.2, 0.2)
                    new_params[key] = type(value)(value + delta)
                elif isinstance(value, bool):
                    # Flip boolean
                    new_params[key] = not value
        
        return Strategy(new_params)
    
    def crossover(self, other: 'Strategy') -> 'Strategy':
        """
        Create offspring via crossover with another strategy.
        
        Args:
            other: Another strategy to crossover with
            
        Returns:
            New offspring strategy
        """
        new_params = {}
        
        for key in self.params:
            # Randomly choose from either parent
            if random.random() < 0.5:
                new_params[key] = self.params[key]
            else:
                new_params[key] = other.params.get(key, self.params[key])
        
        return Strategy(new_params)


class SandboxEvolver:
    """
    Recursive genetic algorithm evolution sandbox.
    Evolves optimal strategies for GTA economy simulation.
    """
    
    def __init__(self, yaml_path: str, population_size: int = 20):
        """
        Initialize sandbox evolver.
        
        Args:
            yaml_path: Path to income_sources.yaml
            population_size: Number of strategies in population
        """
        self.yaml_path = yaml_path
        self.population_size = population_size
        self.population: List[Strategy] = []
        self.generation = 0
        self.best_strategy: Strategy = None
        self.fitness_history: List[float] = []
        
        self._initialize_population()
    
    def _initialize_population(self):
        """Initialize random population of strategies."""
        for _ in range(self.population_size):
            params = {
                'activate_all_deps': random.choice([True, False]),
                'collection_interval_min': random.randint(30, 180),
                'use_swarm_optimization': random.choice([True, False]),
                'priority_sources': random.sample(
                    ['nightclub_safe', 'agency_safe', 'arcade_safe', 
                     'salvage_yard_safe', 'garment_factory_safe', 'hands_on_car_wash'],
                    k=random.randint(1, 4)
                )
            }
            self.population.append(Strategy(params))
    
    def evaluate_strategy(self, strategy: Strategy, 
                         duration_hours: float = 24) -> float:
        """
        Evaluate a strategy's fitness.
        
        Args:
            strategy: Strategy to evaluate
            duration_hours: Simulation duration
            
        Returns:
            Fitness score (total income)
        """
        sim = GTAEconomySim(self.yaml_path)
        
        # Apply strategy
        if strategy.params.get('activate_all_deps', False):
            sim.activate_all_dependencies()
        
        # Run simulation
        results = sim.run(duration_hours=duration_hours)
        
        # Fitness = total income
        strategy.fitness = results['total_income']
        
        return strategy.fitness
    
    def select_parents(self, n_parents: int = 5) -> List[Strategy]:
        """
        Select top strategies for breeding.
        
        Args:
            n_parents: Number of parents to select
            
        Returns:
            List of parent strategies
        """
        sorted_pop = sorted(self.population, key=lambda s: s.fitness, reverse=True)
        return sorted_pop[:n_parents]
    
    def evolve_generation(self, mutation_rate: float = 0.01) -> Dict[str, Any]:
        """
        Evolve one generation.
        
        Args:
            mutation_rate: Mutation probability
            
        Returns:
            Generation statistics
        """
        # Evaluate all strategies
        for strategy in self.population:
            self.evaluate_strategy(strategy)
        
        # Track best
        best = max(self.population, key=lambda s: s.fitness)
        if self.best_strategy is None or best.fitness > self.best_strategy.fitness:
            self.best_strategy = best
        
        self.fitness_history.append(best.fitness)
        
        # Selection
        parents = self.select_parents(n_parents=5)
        
        # Generate new population
        new_population = parents.copy()  # Keep elite
        
        while len(new_population) < self.population_size:
            # Crossover
            parent1, parent2 = random.sample(parents, 2)
            offspring = parent1.crossover(parent2)
            
            # Mutation
            if random.random() < 0.8:  # 80% chance of mutation
                offspring = offspring.mutate(mutation_rate)
            
            new_population.append(offspring)
        
        self.population = new_population
        self.generation += 1
        
        # Statistics
        fitnesses = [s.fitness for s in self.population]
        
        return {
            'generation': self.generation,
            'best_fitness': best.fitness,
            'mean_fitness': np.mean(fitnesses),
            'std_fitness': np.std(fitnesses),
            'best_params': best.params
        }
    
    def run(self, iterations: int = 100, 
           mutation_rate: float = 0.01) -> Dict[str, Any]:
        """
        Run evolution for multiple iterations.
        
        Args:
            iterations: Number of generations
            mutation_rate: Mutation probability
            
        Returns:
            Final evolution results
        """
        print(f"Starting evolution for {iterations} generations...")
        
        for i in range(iterations):
            stats = self.evolve_generation(mutation_rate)
            
            if (i + 1) % 10 == 0:
                print(f"Generation {stats['generation']}: "
                      f"Best=${stats['best_fitness']:,.0f}, "
                      f"Mean=${stats['mean_fitness']:,.0f}")
        
        results = {
            'total_generations': self.generation,
            'best_strategy': {
                'params': self.best_strategy.params,
                'fitness': self.best_strategy.fitness
            },
            'fitness_history': self.fitness_history,
            'final_mean_fitness': np.mean([s.fitness for s in self.population])
        }
        
        print(f"\nEvolution complete!")
        print(f"Best strategy fitness: ${results['best_strategy']['fitness']:,.0f}")
        print(f"Best params: {results['best_strategy']['params']}")
        
        return results
    
    def save_results(self, output_path: str):
        """
        Save evolution results to file.
        
        Args:
            output_path: Path to save results
        """
        if self.best_strategy is None:
            print("No results to save - run evolution first")
            return
        
        results = {
            'generation': self.generation,
            'best_strategy': {
                'params': self.best_strategy.params,
                'fitness': self.best_strategy.fitness
            },
            'fitness_history': self.fitness_history
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {output_path}")


def main():
    """Main entry point for sandbox evolver."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GTA Economy Strategy Evolver')
    parser.add_argument('--iterations', type=int, default=100,
                       help='Number of evolution iterations')
    parser.add_argument('--mutate-rate', type=float, default=0.01,
                       help='Mutation rate')
    parser.add_argument('--config', type=str, 
                       default='config/income_sources.yaml',
                       help='Path to config YAML')
    parser.add_argument('--output', type=str,
                       default='evolution_results.json',
                       help='Output file path')
    
    args = parser.parse_args()
    
    # Run evolution
    evolver = SandboxEvolver(args.config)
    results = evolver.run(iterations=args.iterations, 
                         mutation_rate=args.mutate_rate)
    
    # Save results
    evolver.save_results(args.output)


if __name__ == '__main__':
    main()
