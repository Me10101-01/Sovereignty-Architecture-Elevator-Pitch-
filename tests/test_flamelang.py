#!/usr/bin/env python3
"""
Tests for FlameLang Core Components

Tests the glyph-based neuro-acoustic signal processing system
including hemi-sync algorithms, spatial buffers, and AI expansions.
"""

import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from flamelang import (
    FlameLangInterpreter,
    HemiSyncGlyph,
    TimeSeriesGlyph,
    SpatialBufferGlyph,
    AIExpansionGlyph,
    GlyphParams,
    Frequency,
    GlyphType,
    calculate_five_day_cycle_ms,
    create_adhd_sound_map,
    create_dementia_relief_map,
)


class TestFrequency(unittest.TestCase):
    """Test Frequency class"""
    
    def test_valid_frequency(self):
        """Test creating a valid frequency"""
        freq = Frequency(432.0)
        self.assertEqual(freq.value, 432.0)
        self.assertIsNone(freq.modulation)
    
    def test_frequency_with_modulation(self):
        """Test frequency with modulation"""
        freq = Frequency(432.0, modulation=8.0)
        self.assertEqual(freq.value, 432.0)
        self.assertEqual(freq.modulation, 8.0)
    
    def test_invalid_frequency(self):
        """Test that negative frequencies raise error"""
        with self.assertRaises(ValueError):
            Frequency(-100.0)
        
        with self.assertRaises(ValueError):
            Frequency(0.0)


class TestGlyphParams(unittest.TestCase):
    """Test GlyphParams class"""
    
    def test_default_params(self):
        """Test default parameters"""
        params = GlyphParams()
        self.assertIsNone(params.left_freq)
        self.assertIsNone(params.right_freq)
        self.assertIsNone(params.time_cycle_ms)
        self.assertIsNotNone(params.metadata)
        self.assertEqual(params.metadata, {})
    
    def test_params_with_frequencies(self):
        """Test params with frequencies"""
        params = GlyphParams(
            left_freq=Frequency(432.0),
            right_freq=Frequency(440.0),
            time_cycle_ms=5000
        )
        self.assertEqual(params.left_freq.value, 432.0)
        self.assertEqual(params.right_freq.value, 440.0)
        self.assertEqual(params.time_cycle_ms, 5000)


class TestHemiSyncGlyph(unittest.TestCase):
    """Test HemiSync glyph for binaural beat generation"""
    
    def test_create_hemi_sync(self):
        """Test creating a HemiSync glyph"""
        params = GlyphParams(
            left_freq=Frequency(432.0),
            right_freq=Frequency(440.0),
            time_cycle_ms=1000
        )
        glyph = HemiSyncGlyph(params)
        self.assertEqual(glyph.glyph_type, GlyphType.HEMI_SYNC)
    
    def test_hemi_sync_requires_frequencies(self):
        """Test that HemiSync requires both frequencies"""
        params = GlyphParams(left_freq=Frequency(432.0))
        with self.assertRaises(ValueError):
            HemiSyncGlyph(params)
    
    def test_execute_hemi_sync(self):
        """Test executing HemiSync to generate binaural beats"""
        params = GlyphParams(
            left_freq=Frequency(432.0),
            right_freq=Frequency(440.0),
            time_cycle_ms=100  # Short for testing
        )
        glyph = HemiSyncGlyph(params)
        left, right = glyph.execute()
        
        # Check outputs are numpy arrays
        self.assertIsInstance(left, np.ndarray)
        self.assertIsInstance(right, np.ndarray)
        
        # Check they have same length
        self.assertEqual(len(left), len(right))
        
        # Check they contain valid audio data
        self.assertTrue(np.all(np.abs(left) <= 1.0))
        self.assertTrue(np.all(np.abs(right) <= 1.0))
    
    def test_get_beat_frequency(self):
        """Test beat frequency calculation"""
        params = GlyphParams(
            left_freq=Frequency(432.0),
            right_freq=Frequency(440.0)
        )
        glyph = HemiSyncGlyph(params)
        beat_freq = glyph.get_beat_frequency()
        self.assertEqual(beat_freq, 8.0)
    
    def test_transform(self):
        """Test transforming existing audio"""
        params = GlyphParams(
            left_freq=Frequency(432.0),
            right_freq=Frequency(440.0)
        )
        glyph = HemiSyncGlyph(params)
        
        # Create mono input
        mono_signal = np.sin(2 * np.pi * 100 * np.linspace(0, 1, 1000))
        stereo = glyph.transform(mono_signal)
        
        # Should output stereo
        self.assertEqual(stereo.shape[1], 2)


class TestTimeSeriesGlyph(unittest.TestCase):
    """Test TimeSeries glyph"""
    
    def test_create_time_series(self):
        """Test creating TimeSeries glyph"""
        params = GlyphParams(time_cycle_ms=5000, buffer_size=1024)
        glyph = TimeSeriesGlyph(params)
        self.assertEqual(glyph.glyph_type, GlyphType.TIME_SERIES)
    
    def test_execute_time_series(self):
        """Test executing TimeSeries"""
        params = GlyphParams(time_cycle_ms=5000, buffer_size=1024)
        glyph = TimeSeriesGlyph(params)
        result = glyph.execute()
        
        self.assertIn('cycle_ms', result)
        self.assertIn('buffer_size', result)
        self.assertEqual(result['cycle_ms'], 5000)
        self.assertEqual(result['buffer_size'], 1024)
    
    def test_transform_applies_windowing(self):
        """Test that transform applies windowing"""
        params = GlyphParams()
        glyph = TimeSeriesGlyph(params)
        
        signal = np.ones(1000)
        windowed = glyph.transform(signal)
        
        # Windowed signal should differ from original
        self.assertFalse(np.array_equal(signal, windowed))
        
        # Should be normalized
        self.assertTrue(np.max(np.abs(windowed)) <= 1.0)


class TestSpatialBufferGlyph(unittest.TestCase):
    """Test SpatialBuffer glyph"""
    
    def test_create_spatial_buffer(self):
        """Test creating SpatialBuffer"""
        params = GlyphParams(buffer_size=2048, channel_count=8)
        glyph = SpatialBufferGlyph(params)
        self.assertEqual(glyph.glyph_type, GlyphType.SPATIAL_BUFFER)
        self.assertEqual(glyph.buffer_size, 2048)
    
    def test_execute_spatial_buffer(self):
        """Test executing SpatialBuffer"""
        params = GlyphParams(buffer_size=1024, channel_count=4)
        glyph = SpatialBufferGlyph(params)
        result = glyph.execute()
        
        self.assertEqual(result['buffer_size'], 1024)
        self.assertEqual(result['channels'], 4)
        self.assertEqual(result['spatial_dimensions'], 3)
    
    def test_add_spatial_point(self):
        """Test adding spatial points"""
        params = GlyphParams()
        glyph = SpatialBufferGlyph(params)
        
        signal = np.random.randn(100)
        glyph.add_spatial_point(1.0, 2.0, 3.0, signal)
        
        # Check point was added
        self.assertEqual(len(glyph.spatial_map), 1)


class TestAIExpansionGlyph(unittest.TestCase):
    """Test AIExpansion glyph"""
    
    def test_create_ai_expansion(self):
        """Test creating AIExpansion"""
        params = GlyphParams(metadata={"expansion_factor": 4})
        glyph = AIExpansionGlyph(params)
        self.assertEqual(glyph.glyph_type, GlyphType.AI_EXPANSION)
        self.assertEqual(glyph.expansion_factor, 4)
    
    def test_execute_ai_expansion(self):
        """Test executing AIExpansion"""
        params = GlyphParams(metadata={"expansion_factor": 3, "mutation_rate": 0.1})
        glyph = AIExpansionGlyph(params)
        result = glyph.execute()
        
        self.assertEqual(result['expansion_factor'], 3)
        self.assertEqual(result['mutation_rate'], 0.1)
    
    def test_transform_generates_expansions(self):
        """Test that transform generates multiple variations"""
        params = GlyphParams(metadata={"expansion_factor": 4})
        glyph = AIExpansionGlyph(params)
        
        signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 1000))
        expansions = glyph.transform(signal)
        
        # Should generate expansion_factor variations
        self.assertEqual(len(expansions), 4)
        
        # First should be original
        np.testing.assert_array_equal(expansions[0], signal)
        
        # Others should be different
        for i in range(1, 4):
            self.assertFalse(np.array_equal(expansions[i], signal))


class TestFlameLangInterpreter(unittest.TestCase):
    """Test FlameLang interpreter"""
    
    def test_create_interpreter(self):
        """Test creating interpreter"""
        interpreter = FlameLangInterpreter()
        self.assertEqual(len(interpreter.glyphs), 0)
        self.assertEqual(len(interpreter.execution_log), 0)
    
    def test_add_glyph(self):
        """Test adding glyphs"""
        interpreter = FlameLangInterpreter()
        
        params = GlyphParams(
            left_freq=Frequency(432.0),
            right_freq=Frequency(440.0)
        )
        glyph = HemiSyncGlyph(params)
        
        interpreter.add_glyph(glyph)
        self.assertEqual(len(interpreter.glyphs), 1)
    
    def test_execute_pipeline(self):
        """Test executing glyph pipeline"""
        interpreter = FlameLangInterpreter()
        
        # Add multiple glyphs
        hemi_params = GlyphParams(
            left_freq=Frequency(432.0),
            right_freq=Frequency(440.0),
            time_cycle_ms=100
        )
        interpreter.add_glyph(HemiSyncGlyph(hemi_params))
        
        time_params = GlyphParams(time_cycle_ms=1000, buffer_size=512)
        interpreter.add_glyph(TimeSeriesGlyph(time_params))
        
        # Execute
        results = interpreter.execute()
        
        # Should have results for both glyphs
        self.assertEqual(len(results), 2)
        
        # Check log
        log = interpreter.get_log()
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0]['status'], 'success')
        self.assertEqual(log[1]['status'], 'success')


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_calculate_five_day_cycle(self):
        """Test five-day cycle calculation"""
        cycle_ms = calculate_five_day_cycle_ms()
        
        # 5 days = 5 * 24 * 60 * 60 * 1000 ms
        expected = 5 * 24 * 60 * 60 * 1000
        self.assertEqual(cycle_ms, expected)
        self.assertEqual(cycle_ms, 432000000)
    
    def test_create_adhd_sound_map(self):
        """Test ADHD sound map creation"""
        left, right = create_adhd_sound_map()
        
        # Should return stereo signals
        self.assertIsInstance(left, np.ndarray)
        self.assertIsInstance(right, np.ndarray)
        self.assertEqual(len(left), len(right))
        
        # Should have reasonable length (5 seconds at 44.1kHz)
        self.assertGreater(len(left), 200000)
    
    def test_create_dementia_relief_map(self):
        """Test dementia relief map creation"""
        sound_map = create_dementia_relief_map()
        
        # Should return dictionary
        self.assertIsInstance(sound_map, dict)
        
        # Should have multiple frequencies
        self.assertGreater(len(sound_map), 0)
        
        # Check each entry is stereo
        for freq_name, audio in sound_map.items():
            self.assertEqual(audio.shape[1], 2)  # Stereo
    
    def test_create_dementia_relief_custom_frequencies(self):
        """Test dementia relief with custom frequencies"""
        custom_freqs = [440.0, 528.0]
        sound_map = create_dementia_relief_map(frequencies=custom_freqs)
        
        self.assertEqual(len(sound_map), len(custom_freqs))


if __name__ == '__main__':
    unittest.main()
