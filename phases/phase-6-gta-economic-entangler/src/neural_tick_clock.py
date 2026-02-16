"""
Neural Tick Clock - Phase 5 Integration
Trig-wave driven clock scheduler for economic simulation
Popularity decay: cos(2π * t / decay_period)
"""

import numpy as np
import math
from typing import Dict, Any


class NeuralTickClock:
    """
    Neural tick scheduler using trigonometric wave functions.
    Integrates with Phase 5 to provide time-varying rates.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize neural tick clock with global parameters.
        
        Args:
            config: Global parameters from YAML config
        """
        self.base_tick_rate = config.get('base_tick_rate', 1.0)
        self.in_game_day_irl_min = config.get('in_game_day_irl_min', 48)
        self.wave_amplitude_range = config.get('wave_amplitude_range', [0.5, 1.5])
        
    def get_tick_rate(self, t_irl: float) -> float:
        """
        Calculate current tick rate based on neural wave.
        
        Args:
            t_irl: In real life time in minutes
            
        Returns:
            Modulated tick rate
        """
        # Neural wave: sin wave with period matching game day
        wave = math.sin(2 * math.pi * t_irl / self.in_game_day_irl_min)
        
        # Map [-1, 1] to amplitude range
        min_amp, max_amp = self.wave_amplitude_range
        amplitude = min_amp + (max_amp - min_amp) * (wave + 1) / 2
        
        return self.base_tick_rate * amplitude
    
    def popularity_decay(self, t_irl: float, decay_period: float = 3600) -> float:
        """
        Calculate popularity decay using cosine wave.
        
        Args:
            t_irl: In real life time in minutes
            decay_period: Period for full decay cycle in minutes
            
        Returns:
            Popularity multiplier [0, 1]
        """
        decay = math.cos(2 * math.pi * t_irl / decay_period)
        # Map [-1, 1] to [0, 1]
        return (decay + 1) / 2
    
    def get_modulated_rate(self, base_rate: float, t_irl: float, 
                          apply_popularity: bool = False) -> float:
        """
        Get fully modulated production rate.
        
        Args:
            base_rate: Base production rate per time unit
            t_irl: In real life time in minutes
            apply_popularity: Whether to apply popularity decay
            
        Returns:
            Modulated production rate
        """
        tick_rate = self.get_tick_rate(t_irl)
        rate = base_rate * tick_rate
        
        if apply_popularity:
            popularity = self.popularity_decay(t_irl)
            rate *= popularity
            
        return rate
    
    def simulate_tick_sequence(self, duration_min: float, 
                              interval_min: float = 1.0) -> np.ndarray:
        """
        Simulate a sequence of tick rates over time.
        
        Args:
            duration_min: Total duration in minutes
            interval_min: Sampling interval in minutes
            
        Returns:
            Array of tick rates over time
        """
        time_points = np.arange(0, duration_min, interval_min)
        tick_rates = np.array([self.get_tick_rate(t) for t in time_points])
        return tick_rates
