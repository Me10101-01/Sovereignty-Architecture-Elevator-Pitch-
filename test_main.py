#!/usr/bin/env python3
"""
Unit tests for the field calibration system.
"""

import unittest
import math
from main import (
    decode_plus_code,
    haversine_distance,
    pythagorean_distance,
    calibrate,
    BeamCalc,
    rolling_offset,
    cutback,
    recover_short_code,
    CODE_ALPHABET,
)


class TestPlusCodeDecoder(unittest.TestCase):
    """Test Plus Code decoding functionality"""
    
    def test_decode_full_code(self):
        """Test decoding a full Plus Code"""
        # Test a known code (New Orleans area)
        area = decode_plus_code("862G9XGF+GJ")
        self.assertIsNotNone(area)
        self.assertAlmostEqual(area.lat, 30.376312, places=5)
        self.assertAlmostEqual(area.lon, -89.025938, places=5)
    
    def test_decode_short_code_with_context(self):
        """Test decoding a short code with location context"""
        area = decode_plus_code("5MHH+P8G Lake Charles, Louisiana")
        self.assertIsNotNone(area)
        # Should be somewhere in Lake Charles area
        self.assertGreater(area.lat, 30.0)
        self.assertLess(area.lat, 30.5)
        self.assertGreater(area.lon, -94.0)
        self.assertLess(area.lon, -93.0)
    
    def test_code_area_properties(self):
        """Test CodeArea computed properties"""
        area = decode_plus_code("862G9XGF+GJ")
        lat, lon = area.center
        self.assertEqual(lat, area.lat)
        self.assertEqual(lon, area.lon)
        self.assertLess(area.south, area.north)
        self.assertLess(area.west, area.east)


class TestDistanceCalculations(unittest.TestCase):
    """Test distance calculation functions"""
    
    def test_haversine_distance_feet(self):
        """Test Haversine distance in feet"""
        # Lake Charles to Sulphur
        lat1, lon1 = 30.2266, -93.2174
        lat2, lon2 = 30.2366, -93.3774
        dist = haversine_distance(lat1, lon1, lat2, lon2, "ft")
        # Should be around 50,000-51,000 feet
        self.assertGreater(dist, 49000)
        self.assertLess(dist, 52000)
    
    def test_haversine_distance_miles(self):
        """Test Haversine distance in miles"""
        lat1, lon1 = 30.2266, -93.2174
        lat2, lon2 = 30.2366, -93.3774
        dist = haversine_distance(lat1, lon1, lat2, lon2, "mi")
        # Should be around 9-10 miles
        self.assertGreater(dist, 9)
        self.assertLess(dist, 10)
    
    def test_pythagorean_distance(self):
        """Test Pythagorean distance calculation"""
        # 3-4-5 triangle
        dist = pythagorean_distance(3, 4)
        self.assertAlmostEqual(dist, 5.0, places=5)
        
        # Test with provided example
        dist = pythagorean_distance(100, 50)
        self.assertAlmostEqual(dist, 111.8034, places=3)


class TestCalibration(unittest.TestCase):
    """Test calibration functionality"""
    
    def test_calibrate_exact_match(self):
        """Test calibration with exact match"""
        result = calibrate(305, 305)
        self.assertEqual(result["satellite"], 305)
        self.assertEqual(result["field"], 305)
        self.assertEqual(result["difference"], 0)
        self.assertEqual(result["pct_error"], 0)
        self.assertTrue(result["calibrated"])
        self.assertEqual(result["adjustment_factor"], 1.0)
    
    def test_calibrate_within_tolerance(self):
        """Test calibration within 2% tolerance"""
        result = calibrate(100, 101)
        self.assertEqual(result["difference"], 1)
        self.assertAlmostEqual(result["pct_error"], 1.0, places=5)
        self.assertTrue(result["calibrated"])
    
    def test_calibrate_outside_tolerance(self):
        """Test calibration outside 2% tolerance"""
        result = calibrate(100, 105)
        self.assertEqual(result["difference"], 5)
        self.assertAlmostEqual(result["pct_error"], 5.0, places=5)
        self.assertFalse(result["calibrated"])


class TestBeamCalculations(unittest.TestCase):
    """Test beam wrap calculations"""
    
    def test_beam_horizontal(self):
        """Test horizontal beam calculation"""
        beam = BeamCalc(
            circumference=44,
            shoe_count=4,
            boot_final=6,
            rise=0
        )
        self.assertEqual(beam.run, 62)  # 4*14 + 6
        self.assertEqual(beam.beam_length, 62)
        self.assertEqual(beam.beam_type, "Horizontal")
        self.assertEqual(beam.band_length, 52)  # 44 + 8
        self.assertEqual(beam.band_qty, 3)  # ceil(62/40) + 1
        self.assertEqual(beam.mesh_qty, 2)  # 3 - 1
    
    def test_beam_angled(self):
        """Test angled beam calculation"""
        beam = BeamCalc(
            circumference=44,
            shoe_count=4,
            boot_final=6,
            rise=30
        )
        self.assertEqual(beam.run, 62)
        self.assertAlmostEqual(beam.beam_length, 68.88, places=2)
        self.assertEqual(beam.beam_type, "Angled")
        self.assertEqual(beam.band_qty, 3)
        self.assertEqual(beam.mesh_length, 63)  # 44 + 19
    
    def test_beam_materials(self):
        """Test material calculations"""
        beam = BeamCalc(
            circumference=44,
            shoe_count=4,
            boot_final=6,
            rise=30
        )
        self.assertEqual(beam.total_band_stock, 156)  # 3 * 52
        self.assertEqual(beam.total_mesh_sqin, 5040)  # 2 * 63 * 40


class TestOffsetCalculations(unittest.TestCase):
    """Test offset calculations"""
    
    def test_rolling_offset_45_degrees(self):
        """Test rolling offset at 45 degrees"""
        result = rolling_offset(45, 5)
        self.assertAlmostEqual(result["travel"], 7.0711, places=3)
        self.assertAlmostEqual(result["advance"], 5.0, places=3)
        self.assertAlmostEqual(result["run"], 5.0, places=3)
    
    def test_cutback_45_degrees(self):
        """Test cutback at 45 degrees"""
        result = cutback(45, 10)
        self.assertAlmostEqual(result["cut"], 4.1421, places=3)
    
    def test_rolling_offset_30_degrees(self):
        """Test rolling offset at 30 degrees"""
        result = rolling_offset(30, 6)
        self.assertAlmostEqual(result["travel"], 12.0, places=1)
        self.assertAlmostEqual(result["advance"], 10.392, places=2)


class TestRecoverShortCode(unittest.TestCase):
    """Test short code recovery"""
    
    def test_recover_short_code(self):
        """Test recovering a full code from a short code"""
        # Lake Charles reference point
        ref_lat, ref_lon = 30.2266, -93.2174
        full_code = recover_short_code("5MHH+P8", ref_lat, ref_lon)
        self.assertIsNotNone(full_code)
        self.assertIn("+", full_code)
        # Should have 8 chars before +
        prefix, _ = full_code.split("+")
        self.assertEqual(len(prefix), 8)
    
    def test_full_code_unchanged(self):
        """Test that full codes are not modified"""
        full_code = "862G9XGF+GJ"
        result = recover_short_code(full_code, 30.0, -93.0)
        self.assertEqual(result, full_code)


if __name__ == "__main__":
    unittest.main()
