"""
Trigonometric Wave Core
Production waves with amplitude modulated by dependencies
Quantum-inspired: Wave amplitude = entangled deps state
"""

import math
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path


class TrigWaveCore:
    """
    Trigonometric wave-based production rate calculator.
    Integrates with neural tick clock and entanglement core.
    """
    
    def __init__(self, yaml_config_path: str):
        """
        Initialize trig wave core with YAML configuration.
        
        Args:
            yaml_config_path: Path to income_sources.yaml
        """
        with open(yaml_config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.income_sources = self.config['income_sources']
        self.global_params = self.config['global_params']
        
        # Import here to avoid circular dependency
        from .neural_tick_clock import NeuralTickClock
        self.scheduler = NeuralTickClock(self.global_params)
        
    def get_source_config(self, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve configuration for a specific income source.
        
        Args:
            source_name: Name of the income source
            
        Returns:
            Source configuration dict or None if not found
        """
        for category in ['truly_passive', 'semi_passive', 'active_high_yield']:
            if category in self.income_sources:
                for source in self.income_sources[category]:
                    if source['name'] == source_name:
                        return source
        return None
    
    def calculate_base_rate(self, source_name: str) -> float:
        """
        Calculate base production rate per minute.
        
        Args:
            source_name: Name of the income source
            
        Returns:
            Base rate per minute
        """
        source = self.get_source_config(source_name)
        if not source:
            return 0.0
        
        # For truly passive sources
        if 'max_rate_per_48min' in source:
            return source['max_rate_per_48min'] / 48.0
        elif 'rate_per_48min' in source:
            return source['rate_per_48min'] / 48.0
        elif 'base_rate_per_48min' in source:
            return source['base_rate_per_48min'] / 48.0
        elif 'production_per_irl_min' in source:
            return source['production_per_irl_min']
        
        return 0.0
    
    def production_rate(self, source_name: str, t_irl: float, 
                       deps_satisfied: bool = True) -> float:
        """
        Calculate production rate with trig wave modulation.
        
        Args:
            source_name: Name of the income source
            t_irl: In real life time in minutes
            deps_satisfied: Whether dependencies are satisfied
            
        Returns:
            Current production rate per minute
        """
        source = self.get_source_config(source_name)
        if not source:
            return 0.0
        
        base_rate = self.calculate_base_rate(source_name)
        
        # Apply trigonometric wave modulation
        wave_period = self.global_params['in_game_day_irl_min']
        wave = math.sin(2 * math.pi * t_irl / wave_period)
        
        # Use absolute value to keep production positive
        wave_factor = abs(wave)
        
        # Dependency factor (entanglement)
        deps_factor = 1.0 if deps_satisfied else 0.5
        
        # Apply popularity decay for nightclub
        apply_popularity = (source_name == 'nightclub_safe')
        
        # Get neural tick modulated rate
        rate = self.scheduler.get_modulated_rate(
            base_rate, t_irl, apply_popularity=apply_popularity
        )
        
        # Apply wave and dependency factors
        final_rate = rate * wave_factor * deps_factor
        
        return final_rate
    
    def accumulated_income(self, source_name: str, duration_min: float,
                          deps_satisfied: bool = True) -> float:
        """
        Calculate total accumulated income over a duration.
        
        Args:
            source_name: Name of the income source
            duration_min: Duration in minutes
            deps_satisfied: Whether dependencies are satisfied
            
        Returns:
            Total accumulated income
        """
        source = self.get_source_config(source_name)
        if not source:
            return 0.0
        
        cap = source.get('cap', float('inf'))
        
        # Integrate over time using numerical integration
        total = 0.0
        dt = 1.0  # 1 minute intervals
        
        for t in range(0, int(duration_min), int(dt)):
            rate = self.production_rate(source_name, t, deps_satisfied)
            income = rate * dt
            
            # Apply cap
            if total + income > cap:
                total = cap
                break
            
            total += income
        
        return total
    
    def get_all_passive_sources(self) -> List[str]:
        """
        Get list of all truly passive income source names.
        
        Returns:
            List of source names
        """
        if 'truly_passive' not in self.income_sources:
            return []
        return [s['name'] for s in self.income_sources['truly_passive']]
    
    def get_source_dependencies(self, source_name: str) -> List[str]:
        """
        Get dependencies for a source.
        
        Args:
            source_name: Name of the income source
            
        Returns:
            List of dependency names
        """
        source = self.get_source_config(source_name)
        if not source:
            return []
        return source.get('dependencies', [])
