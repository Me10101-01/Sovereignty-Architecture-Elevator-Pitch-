"""
Audio Sonification Module

GlyphSonix Resonance Core (GSRC) - FlameLang-inspired audio renderer
for Kemetic transliteration and Sumerian cuneiform sonification.
"""

from .gsrc_full import (
    DetermRng,
    sine,
    saw,
    triangle,
    adsr,
    tokenize_kemetic,
    classify_token,
    cents_to_mult,
    charity_gliss,
    node137_burst,
    fm_modulate,
    harmonic_layers,
    pan,
    simple_reverb,
    write_wav_stereo,
    render_line_to_stereo,
    SAMPLE_RATE,
    BIT_DEPTH,
    SEED,
    KEMETIC_MULTIGRAPHS,
    SUMERIAN_MAP,
    PHONEME_FM,
    LINE_CARRIERS,
)

__all__ = [
    'DetermRng',
    'sine',
    'saw',
    'triangle',
    'adsr',
    'tokenize_kemetic',
    'classify_token',
    'cents_to_mult',
    'charity_gliss',
    'node137_burst',
    'fm_modulate',
    'harmonic_layers',
    'pan',
    'simple_reverb',
    'write_wav_stereo',
    'render_line_to_stereo',
    'SAMPLE_RATE',
    'BIT_DEPTH',
    'SEED',
    'KEMETIC_MULTIGRAPHS',
    'SUMERIAN_MAP',
    'PHONEME_FM',
    'LINE_CARRIERS',
]
