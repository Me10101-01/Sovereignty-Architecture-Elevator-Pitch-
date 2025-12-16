"""
FlameLang Core - Glyph-based Language for Neuro-Acoustic Signal Processing

This module implements the core FlameLang interpreter with support for:
- Hemi-sync algorithms (hemispheric synchronization via binaural audio)
- Time-series signal processing for ADHD, anxiety, and dementia applications
- Transformer-based pattern recognition
- AI-generated channel expansions
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class GlyphType(Enum):
    """Types of glyphs in FlameLang"""
    HEMI_SYNC = "HemiSync"
    WAVE_TRANSFORM = "WaveTransform"
    TIME_SERIES = "TimeSeries"
    SPATIAL_BUFFER = "SpatialBuffer"
    AI_EXPANSION = "AIExpansion"
    SWARM_PULSE = "SwarmPulse"


@dataclass
class Frequency:
    """Represents a frequency in Hz with optional modulation"""
    value: float  # Hz
    modulation: Optional[float] = None  # Hz
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError(f"Frequency must be positive, got {self.value}")


@dataclass
class GlyphParams:
    """Parameters for a glyph operation"""
    left_freq: Optional[Frequency] = None
    right_freq: Optional[Frequency] = None
    time_cycle_ms: Optional[int] = None
    buffer_size: Optional[int] = None
    channel_count: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Glyph:
    """Base class for FlameLang glyphs"""
    
    def __init__(self, glyph_type: GlyphType, params: GlyphParams):
        self.glyph_type = glyph_type
        self.params = params
        self.output = None
    
    def execute(self) -> Any:
        """Execute the glyph operation"""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def transform(self, input_data: np.ndarray) -> np.ndarray:
        """Transform input data according to glyph logic"""
        raise NotImplementedError("Subclasses must implement transform()")


class HemiSyncGlyph(Glyph):
    """
    HemiSync glyph for generating binaural beats
    
    Generates hemispheric synchronization audio by creating slightly
    different frequencies for left and right ears, inducing brainwave
    entrainment at the difference frequency.
    """
    
    def __init__(self, params: GlyphParams):
        super().__init__(GlyphType.HEMI_SYNC, params)
        
        if not params.left_freq or not params.right_freq:
            raise ValueError("HemiSync requires both left_freq and right_freq")
    
    def execute(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate binaural beat signals
        
        Returns:
            Tuple of (left_channel, right_channel) as numpy arrays
        """
        # Default duration: 1 second at 44.1kHz sample rate
        sample_rate = 44100
        duration = self.params.time_cycle_ms / 1000.0 if self.params.time_cycle_ms else 1.0
        
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        
        # Generate left and right channels
        left_signal = np.sin(2 * np.pi * self.params.left_freq.value * t)
        right_signal = np.sin(2 * np.pi * self.params.right_freq.value * t)
        
        self.output = (left_signal, right_signal)
        return self.output
    
    def get_beat_frequency(self) -> float:
        """Calculate the beat frequency (difference between left and right)"""
        return abs(self.params.left_freq.value - self.params.right_freq.value)
    
    def transform(self, input_data: np.ndarray) -> np.ndarray:
        """Apply hemi-sync transformation to existing audio data"""
        if len(input_data.shape) == 1:
            # Mono input - split into stereo with frequency modulation
            left_mod = np.sin(2 * np.pi * self.params.left_freq.value * 
                             np.arange(len(input_data)) / 44100)
            right_mod = np.sin(2 * np.pi * self.params.right_freq.value * 
                              np.arange(len(input_data)) / 44100)
            
            return np.column_stack([input_data * left_mod, input_data * right_mod])
        
        return input_data


class TimeSeriesGlyph(Glyph):
    """
    TimeSeries glyph for processing temporal signal data
    
    Implements time-series transformations including:
    - Frequency domain analysis
    - Pattern detection
    - Temporal windowing
    """
    
    def __init__(self, params: GlyphParams):
        super().__init__(GlyphType.TIME_SERIES, params)
    
    def execute(self) -> Dict[str, Any]:
        """Execute time-series analysis"""
        return {
            "cycle_ms": self.params.time_cycle_ms,
            "buffer_size": self.params.buffer_size,
            "status": "initialized"
        }
    
    def transform(self, input_data: np.ndarray) -> np.ndarray:
        """Apply time-series windowing and normalization"""
        # Apply Hann window for smooth transitions
        window = np.hanning(len(input_data))
        windowed = input_data * window
        
        # Normalize to [-1, 1] range
        max_val = np.max(np.abs(windowed))
        if max_val > 0:
            windowed = windowed / max_val
        
        return windowed


class SpatialBufferGlyph(Glyph):
    """
    SpatialBuffer glyph for 3D sound mapping
    
    Creates spatial audio buffers for ADHD/anxiety/dementia sound maps,
    mapping therapeutic sounds to spatial coordinates.
    """
    
    def __init__(self, params: GlyphParams):
        super().__init__(GlyphType.SPATIAL_BUFFER, params)
        self.buffer_size = params.buffer_size or 1024
        self.spatial_map = {}
    
    def execute(self) -> Dict[str, Any]:
        """Initialize spatial buffer"""
        return {
            "buffer_size": self.buffer_size,
            "channels": self.params.channel_count or 2,
            "spatial_dimensions": 3
        }
    
    def add_spatial_point(self, x: float, y: float, z: float, signal: np.ndarray):
        """Add a signal at specific spatial coordinates"""
        key = (round(x, 2), round(y, 2), round(z, 2))
        self.spatial_map[key] = signal
    
    def transform(self, input_data: np.ndarray) -> np.ndarray:
        """Apply spatial buffering and mixing"""
        # Simple spatial mix - can be extended with HRTF
        return input_data


class AIExpansionGlyph(Glyph):
    """
    AIExpansion glyph for AI-generated channel variations
    
    Generates variations of input signals using AI-driven mutations,
    creating therapeutic sound expansions for personalized treatment.
    """
    
    def __init__(self, params: GlyphParams):
        super().__init__(GlyphType.AI_EXPANSION, params)
        self.expansion_factor = params.metadata.get("expansion_factor", 4)
    
    def execute(self) -> Dict[str, Any]:
        """Initialize AI expansion parameters"""
        return {
            "expansion_factor": self.expansion_factor,
            "mutation_rate": self.params.metadata.get("mutation_rate", 0.1),
            "status": "ready"
        }
    
    def transform(self, input_data: np.ndarray) -> List[np.ndarray]:
        """Generate multiple AI-expanded variations"""
        expansions = [input_data]  # Original
        
        for i in range(self.expansion_factor - 1):
            # Generate variation with slight frequency/phase shifts
            mutation = np.random.uniform(0.95, 1.05)
            phase_shift = np.random.uniform(0, 2 * np.pi)
            
            # Apply mutation
            expanded = input_data * mutation
            
            # Add phase variation
            if len(expanded) > 0:
                phase_mod = np.sin(np.linspace(0, phase_shift, len(expanded)))
                expanded = expanded * (1 + 0.1 * phase_mod)
            
            expansions.append(expanded)
        
        return expansions


class FlameLangInterpreter:
    """
    Main FlameLang interpreter
    
    Executes FlameLang programs composed of glyphs.
    """
    
    def __init__(self):
        self.glyphs: List[Glyph] = []
        self.execution_log: List[Dict[str, Any]] = []
    
    def add_glyph(self, glyph: Glyph):
        """Add a glyph to the execution pipeline"""
        self.glyphs.append(glyph)
    
    def execute(self) -> Dict[str, Any]:
        """Execute all glyphs in sequence"""
        results = {}
        
        for i, glyph in enumerate(self.glyphs):
            try:
                result = glyph.execute()
                results[f"glyph_{i}_{glyph.glyph_type.value}"] = result
                
                self.execution_log.append({
                    "glyph_type": glyph.glyph_type.value,
                    "index": i,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                self.execution_log.append({
                    "glyph_type": glyph.glyph_type.value,
                    "index": i,
                    "status": "error",
                    "error": str(e)
                })
                raise
        
        return results
    
    def get_log(self) -> List[Dict[str, Any]]:
        """Get execution log"""
        return self.execution_log


# Utility functions for common FlameLang operations

def calculate_five_day_cycle_ms() -> int:
    """
    Calculate milliseconds in 5 days (432 Hz cycle reference)
    
    5 days = 5 * 24 * 60 * 60 = 432,000 seconds
    432,000 seconds * 1000 = 432,000,000 milliseconds
    
    This aligns with the 432 Hz frequency used in sound healing.
    """
    return 5 * 24 * 60 * 60 * 1000


def create_adhd_sound_map(
    base_frequency: float = 432.0,
    beat_frequency: float = 8.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a basic ADHD therapeutic sound map using hemi-sync
    
    Args:
        base_frequency: Base carrier frequency (default 432 Hz)
        beat_frequency: Desired brainwave entrainment frequency (default 8 Hz alpha)
    
    Returns:
        Tuple of (left_channel, right_channel)
    """
    params = GlyphParams(
        left_freq=Frequency(base_frequency),
        right_freq=Frequency(base_frequency + beat_frequency),
        time_cycle_ms=5000  # 5 second sample
    )
    
    hemi_sync = HemiSyncGlyph(params)
    return hemi_sync.execute()


def create_dementia_relief_map(
    frequencies: List[float] = None
) -> Dict[str, np.ndarray]:
    """
    Create a dementia relief sound map with multiple therapeutic frequencies
    
    Args:
        frequencies: List of therapeutic frequencies (default to common healing frequencies)
    
    Returns:
        Dictionary mapping frequency names to audio signals
    """
    if frequencies is None:
        frequencies = [
            432.0,   # Natural tuning
            528.0,   # DNA repair frequency
            639.0,   # Relationship harmony
            741.0    # Problem solving
        ]
    
    sound_map = {}
    
    for freq in frequencies:
        params = GlyphParams(
            left_freq=Frequency(freq),
            right_freq=Frequency(freq + 4.0),  # 4 Hz theta wave
            time_cycle_ms=3000
        )
        
        hemi_sync = HemiSyncGlyph(params)
        left, right = hemi_sync.execute()
        sound_map[f"freq_{int(freq)}hz"] = np.column_stack([left, right])
    
    return sound_map
