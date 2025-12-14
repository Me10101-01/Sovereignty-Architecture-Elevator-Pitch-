#!/usr/bin/env python3
"""
Test suite for the GlyphSonix Resonance Core (GSRC) audio renderer.
"""

import sys
import os
import tempfile
import wave

# Add src to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.audio_sonification import (
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
)


def test_determ_rng():
    """Test deterministic RNG."""
    print("Testing DetermRng...")
    rng1 = DetermRng(seed=42)
    rng2 = DetermRng(seed=42)
    
    # Same seed should produce same sequence
    vals1 = [rng1.uniform() for _ in range(100)]
    vals2 = [rng2.uniform() for _ in range(100)]
    
    assert vals1 == vals2, "Deterministic RNG failed"
    print("  ✓ DetermRng is deterministic")


def test_oscillators():
    """Test oscillator functions."""
    print("Testing oscillators...")
    
    # Test sine
    s = sine(440.0, 0.0)
    assert -1.0 <= s <= 1.0, "Sine out of range"
    
    # Test saw
    s = saw(440.0, 0.0)
    assert -1.0 <= s <= 1.0, "Saw out of range"
    
    # Test triangle
    s = triangle(440.0, 0.0)
    assert -1.0 <= s <= 1.0, "Triangle out of range"
    
    print("  ✓ All oscillators work correctly")


def test_adsr():
    """Test ADSR envelope."""
    print("Testing ADSR envelope...")
    
    # Test attack phase
    env = adsr(0.1, 5.0, 0.5, 0.7, 0.75, 1.0)
    assert 0.0 <= env <= 1.0, "ADSR envelope out of range"
    
    # Test sustain phase
    env = adsr(2.0, 5.0, 0.5, 0.7, 0.75, 1.0)
    assert abs(env - 0.75) < 0.01, "ADSR sustain incorrect"
    
    # Test release phase
    env = adsr(4.9, 5.0, 0.5, 0.7, 0.75, 1.0)
    assert 0.0 <= env < 0.75, "ADSR release incorrect"
    
    print("  ✓ ADSR envelope works correctly")


def test_tokenization():
    """Test Kemetic tokenization."""
    print("Testing tokenization...")
    
    # Test simple word
    tokens = tokenize_kemetic("Kemt")
    assert len(tokens) == 4, "Tokenization failed"
    
    # Test multigraphs
    tokens = tokenize_kemetic("ḥsb")
    assert tokens[0] == ('ḥ', 'voiced'), "Multigraph not detected"
    
    # Test classification
    assert classify_token('a') == 'vowel', "Classification failed"
    assert classify_token('b') == 'voiced', "Classification failed"
    assert classify_token('s') == 'sibilant', "Classification failed"
    assert classify_token('t') == 'stop', "Classification failed"
    assert classify_token('n') == 'nasal', "Classification failed"
    
    print("  ✓ Tokenization works correctly")


def test_cents_to_mult():
    """Test cents to frequency multiplier."""
    print("Testing cents_to_mult...")
    
    # 1200 cents = 1 octave = 2x frequency
    mult = cents_to_mult(1200.0)
    assert abs(mult - 2.0) < 0.001, "Cents conversion failed"
    
    # 0 cents = same frequency
    mult = cents_to_mult(0.0)
    assert abs(mult - 1.0) < 0.001, "Cents conversion failed"
    
    print("  ✓ Cents conversion works correctly")


def test_special_motifs():
    """Test special motifs."""
    print("Testing special motifs...")
    
    # Test charity gliss
    sig = charity_gliss(110.0, 0.5)
    assert isinstance(sig, float), "Charity gliss failed"
    
    # Test node137 burst
    sig = node137_burst(110.0, 0.5)
    assert isinstance(sig, float), "Node137 burst failed"
    
    print("  ✓ Special motifs work correctly")


def test_fm_modulate():
    """Test FM modulation."""
    print("Testing FM modulation...")
    
    sig = fm_modulate(110.0, 'vowel', 0.5)
    assert isinstance(sig, float), "FM modulation failed"
    assert abs(sig) <= 1.0, "FM modulation out of range"
    
    print("  ✓ FM modulation works correctly")


def test_harmonic_layers():
    """Test harmonic layers."""
    print("Testing harmonic layers...")
    
    sig = harmonic_layers(110.0, 0.5)
    assert isinstance(sig, float), "Harmonic layers failed"
    
    print("  ✓ Harmonic layers work correctly")


def test_pan():
    """Test stereo panning."""
    print("Testing stereo panning...")
    
    left, right = pan((0.7, 0.3), 1.0)
    assert abs(left - 0.7) < 0.001, "Panning failed"
    assert abs(right - 0.3) < 0.001, "Panning failed"
    
    print("  ✓ Stereo panning works correctly")


def test_simple_reverb():
    """Test reverb."""
    print("Testing reverb...")
    
    # Create a short impulse
    buffer = [0.0] * 1000
    buffer[100] = 1.0
    
    wet = simple_reverb(buffer, SAMPLE_RATE)
    assert len(wet) == len(buffer), "Reverb length mismatch"
    assert wet[100] != 0.0, "Reverb failed"
    
    print("  ✓ Reverb works correctly")


def test_wav_writer():
    """Test WAV file writer."""
    print("Testing WAV writer...")
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        filename = tmp.name
    
    try:
        # Create a short test signal
        duration = 0.1  # 100ms
        samples = int(duration * SAMPLE_RATE)
        left = [0.5] * samples
        right = [0.5] * samples
        
        # Write WAV file
        write_wav_stereo(filename, left, right, SAMPLE_RATE)
        
        # Verify file exists and has correct properties
        with wave.open(filename, 'rb') as wf:
            assert wf.getnchannels() == 2, "Wrong channel count"
            assert wf.getsampwidth() == 3, "Wrong sample width"
            assert wf.getframerate() == SAMPLE_RATE, "Wrong sample rate"
            assert wf.getnframes() == samples, "Wrong frame count"
        
        print("  ✓ WAV writer works correctly")
    finally:
        if os.path.exists(filename):
            os.unlink(filename)


def test_render_line():
    """Test line rendering."""
    print("Testing line rendering...")
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        filename = tmp.name
    
    try:
        # Render a short line
        text = "Ha.ty n Kemt"
        carrier = 110.0
        duration = 1.0  # 1 second
        
        left, right = render_line_to_stereo(text, carrier, duration)
        
        # Verify output
        expected_samples = int(duration * SAMPLE_RATE)
        assert len(left) == expected_samples, "Wrong sample count"
        assert len(right) == expected_samples, "Wrong sample count"
        
        # Write to file
        write_wav_stereo(filename, left, right, SAMPLE_RATE)
        
        # Verify file
        with wave.open(filename, 'rb') as wf:
            assert wf.getnframes() == expected_samples, "Wrong frame count"
        
        print("  ✓ Line rendering works correctly")
    finally:
        if os.path.exists(filename):
            os.unlink(filename)


def test_deterministic_render():
    """Test that rendering is deterministic."""
    print("Testing deterministic rendering...")
    
    text = "smn nṯrwy nfr"
    carrier = 110.0
    duration = 0.5
    
    # Reset RNG and render twice
    left1, right1 = render_line_to_stereo(text, carrier, duration)
    left2, right2 = render_line_to_stereo(text, carrier, duration)
    
    # Should produce identical output
    assert left1 == left2, "Rendering is not deterministic"
    assert right1 == right2, "Rendering is not deterministic"
    
    print("  ✓ Rendering is deterministic")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("GlyphSonix Resonance Core (GSRC) - Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        test_determ_rng,
        test_oscillators,
        test_adsr,
        test_tokenization,
        test_cents_to_mult,
        test_special_motifs,
        test_fm_modulate,
        test_harmonic_layers,
        test_pan,
        test_simple_reverb,
        test_wav_writer,
        test_render_line,
        test_deterministic_render,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__} failed: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"Tests passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"Tests failed: {failed}/{len(tests)}")
        sys.exit(1)
    else:
        print("All tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
