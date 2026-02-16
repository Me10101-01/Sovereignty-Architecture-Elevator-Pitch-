"""
FlameLang - Glyph-based Language for Neuro-Acoustic AI Systems

A specialized programming language for processing time-series signals,
generating therapeutic soundscapes, and applying AI-driven expansions
for mental health applications (ADHD, anxiety, dementia).
"""

from .core import (
    FlameLangInterpreter,
    Glyph,
    GlyphType,
    GlyphParams,
    Frequency,
    HemiSyncGlyph,
    TimeSeriesGlyph,
    SpatialBufferGlyph,
    AIExpansionGlyph,
    calculate_five_day_cycle_ms,
    create_adhd_sound_map,
    create_dementia_relief_map,
)

__version__ = "0.1.0"

__all__ = [
    "FlameLangInterpreter",
    "Glyph",
    "GlyphType",
    "GlyphParams",
    "Frequency",
    "HemiSyncGlyph",
    "TimeSeriesGlyph",
    "SpatialBufferGlyph",
    "AIExpansionGlyph",
    "calculate_five_day_cycle_ms",
    "create_adhd_sound_map",
    "create_dementia_relief_map",
]
