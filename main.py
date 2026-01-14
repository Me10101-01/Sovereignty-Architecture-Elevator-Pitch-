#!/usr/bin/env python3
"""
FIELD CALIBRATION SYSTEM
========================
Decode Plus Codes / GPS coordinates
Calculate distances between points
Compare satellite vs field measurements
Calibrate measurement accuracy

Usage:
    python main.py decode "5MHH+P8G Lake Charles, Louisiana"
    python main.py distance "5MHH+P8G" "5MHJ+R2G" --location "Lake Charles, Louisiana"
    python main.py calibrate --satellite 305 --field 305 --unit ft
    python main.py beam --circ 44 --shoes 4 --boot 6 --rise 30
"""

import argparse
import math
import sys
from dataclasses import dataclass
from typing import Tuple, Optional

# ============================================================
# PLUS CODE DECODER
# ============================================================

# Plus Code alphabet (excludes confusable characters)
CODE_ALPHABET = "23456789CFGHJMPQRVWX"
ENCODING_BASE = len(CODE_ALPHABET)  # 20
LATITUDE_MAX = 90
LONGITUDE_MAX = 180
PAIR_CODE_LENGTH = 10
GRID_CODE_LENGTH = 11
SEPARATOR = "+"
SEPARATOR_POSITION = 8
PADDING_CHARACTER = "0"

# Resolution at each position (degrees)
PAIR_RESOLUTIONS = [20.0, 1.0, 0.05, 0.0025, 0.000125]
GRID_RESOLUTIONS = [0.000025, 0.000005]


@dataclass
class CodeArea:
    """Decoded Plus Code area"""
    south: float
    west: float
    north: float
    east: float
    
    @property
    def lat(self) -> float:
        """Center latitude"""
        return (self.south + self.north) / 2
    
    @property
    def lon(self) -> float:
        """Center longitude"""
        return (self.west + self.east) / 2
    
    @property
    def center(self) -> Tuple[float, float]:
        """Center point (lat, lon)"""
        return (self.lat, self.lon)


def recover_short_code(short_code: str, ref_lat: float, ref_lon: float) -> str:
    """
    Recover a full Plus Code from a short code using reference coordinates.
    Short codes like "5MHH+P8G" need a reference location to expand.
    """
    # Remove any location text after the code
    short_code = short_code.strip().split()[0].upper()
    
    # If it's already a full code (has 8+ chars before +), return it
    if SEPARATOR in short_code:
        prefix, suffix = short_code.split(SEPARATOR)
        if len(prefix) >= 8:
            return short_code
    
    # Calculate the prefix from reference coordinates
    # First 4 characters encode a 1° × 1° area
    lat_val = ref_lat + LATITUDE_MAX
    lon_val = ref_lon + LONGITUDE_MAX
    
    # Calculate first 4 characters (1° resolution)
    c1 = CODE_ALPHABET[int(lat_val / 20)]
    c2 = CODE_ALPHABET[int(lon_val / 20)]
    c3 = CODE_ALPHABET[int((lat_val % 20) / 1)]
    c4 = CODE_ALPHABET[int((lon_val % 20) / 1)]
    
    prefix = f"{c1}{c2}{c3}{c4}"
    
    # Combine with short code
    if SEPARATOR in short_code:
        return prefix + short_code
    else:
        return prefix + short_code[:4] + SEPARATOR + short_code[4:]


# Known reference points for Plus Code recovery
REFERENCE_POINTS = {
    "lake charles": (30.2266, -93.2174),
    "sulphur": (30.2366, -93.3774),
    "louisiana": (30.9843, -91.9623),
    "la": (30.9843, -91.9623),
}


def decode_plus_code(code: str) -> CodeArea:
    """
    Decode a Plus Code to lat/lon coordinates.
    
    Args:
        code: Plus Code like "5MHH+P8G" or "5MHH+P8G Lake Charles, Louisiana"
    
    Returns:
        CodeArea with bounds and center coordinates
    """
    original = code.strip()
    
    # Check for location context in the string
    ref_lat, ref_lon = None, None
    for loc_key, coords in REFERENCE_POINTS.items():
        if loc_key in original.lower():
            ref_lat, ref_lon = coords
            break
    
    # Extract just the code part
    code_part = original.upper().split()[0]
    
    # Check if it's a short code (less than 8 chars before separator)
    if SEPARATOR in code_part:
        prefix, suffix = code_part.split(SEPARATOR)
        if len(prefix) < 8 and ref_lat is not None:
            # Recover full code using reference point
            code_part = recover_short_code(code_part, ref_lat, ref_lon)
    
    # Remove separator for processing
    code = code_part.replace(SEPARATOR, "")
    
    # Validate characters
    for char in code:
        if char not in CODE_ALPHABET and char != PADDING_CHARACTER:
            raise ValueError(f"Invalid character '{char}' in Plus Code. Valid characters are: {CODE_ALPHABET}")
    
    # Pad if necessary
    if len(code) < PAIR_CODE_LENGTH:
        code = code + PADDING_CHARACTER * (PAIR_CODE_LENGTH - len(code))
    
    # Initialize bounds
    south = 0.0
    west = 0.0
    lat_resolution = PAIR_RESOLUTIONS[0]
    lon_resolution = PAIR_RESOLUTIONS[0]
    
    # Decode pairs
    try:
        for i in range(0, min(len(code), PAIR_CODE_LENGTH), 2):
            lat_resolution = PAIR_RESOLUTIONS[i // 2]
            lon_resolution = PAIR_RESOLUTIONS[i // 2]
            
            lat_digit = CODE_ALPHABET.index(code[i])
            lon_digit = CODE_ALPHABET.index(code[i + 1])
            
            south += lat_digit * lat_resolution
            west += lon_digit * lon_resolution
        
        # Adjust for negative coordinates
        south -= LATITUDE_MAX
        west -= LONGITUDE_MAX
        
        # Calculate bounds
        north = south + lat_resolution
        east = west + lon_resolution
        
        # Decode grid refinement if present
        if len(code) > PAIR_CODE_LENGTH:
            for i in range(PAIR_CODE_LENGTH, len(code)):
                grid_idx = i - PAIR_CODE_LENGTH
                if grid_idx < len(GRID_RESOLUTIONS):
                    digit = CODE_ALPHABET.index(code[i])
                    row = digit // 4
                    col = digit % 4
                    
                    lat_resolution = GRID_RESOLUTIONS[grid_idx]
                    lon_resolution = GRID_RESOLUTIONS[grid_idx]
                    
                    south += row * lat_resolution
                    west += col * lon_resolution
                    north = south + lat_resolution
                    east = west + lon_resolution
    except ValueError as e:
        raise ValueError(f"Error decoding Plus Code: {e}")
    
    return CodeArea(south=south, west=west, north=north, east=east)


# ============================================================
# DISTANCE CALCULATIONS
# ============================================================

EARTH_RADIUS_FT = 20902231  # feet
EARTH_RADIUS_M = 6371000    # meters


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float, unit: str = "ft") -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        unit: Output unit - "ft", "m", "mi", "in"
    
    Returns:
        Distance in specified units
    """
    # Convert to radians
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_r) * math.cos(lat2_r) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in feet (base unit)
    distance_ft = EARTH_RADIUS_FT * c
    
    # Convert to requested unit
    conversions = {
        "ft": 1,
        "in": 12,
        "m": 0.3048,
        "mi": 1 / 5280,
        "yd": 1 / 3,
    }
    
    return distance_ft * conversions.get(unit, 1)


def pythagorean_distance(run: float, rise: float) -> float:
    """
    Calculate hypotenuse (true length) from run and rise.
    
    Args:
        run: Horizontal distance
        rise: Vertical distance
    
    Returns:
        Hypotenuse (travel/true length)
    """
    return math.sqrt(run ** 2 + rise ** 2)


# ============================================================
# CALIBRATION
# ============================================================

def calibrate(satellite: float, field: float) -> dict:
    """
    Compare satellite measurement to field measurement.
    
    Args:
        satellite: Distance from GPS/satellite
        field: Distance measured in field
    
    Returns:
        Calibration metrics
    """
    diff = field - satellite
    pct_error = (diff / satellite) * 100 if satellite != 0 else 0
    
    return {
        "satellite": satellite,
        "field": field,
        "difference": diff,
        "pct_error": pct_error,
        "calibrated": abs(pct_error) < 2,  # Within 2% = calibrated
        "adjustment_factor": field / satellite if satellite != 0 else 1,
    }


# ============================================================
# BEAM WRAP CALCULATIONS
# ============================================================

# Default shoe size constant
DEFAULT_SHOE_SIZE = 14.0

@dataclass
class BeamCalc:
    """Beam wrap calculation results"""
    # Inputs
    circumference: float
    shoe_count: int
    boot_final: float
    rise: float
    shoe_size: float = DEFAULT_SHOE_SIZE
    
    # Calculated
    @property
    def run(self) -> float:
        return (self.shoe_count * self.shoe_size) + self.boot_final
    
    @property
    def beam_length(self) -> float:
        if self.rise == 0:
            return self.run
        return math.sqrt(self.run ** 2 + self.rise ** 2)
    
    @property
    def beam_type(self) -> str:
        return "Angled" if self.rise > 0 else "Horizontal"
    
    @property
    def band_length(self) -> float:
        """Circumference + 7" bander grab + 1" clip fold"""
        return self.circumference + 8
    
    @property
    def band_qty(self) -> int:
        """Bands needed = ceiling(beam_length / 40) + 1"""
        return math.ceil(self.beam_length / 40) + 1
    
    @property
    def mesh_length(self) -> float:
        """Circumference + 12" corners + 3" overlap + 4" edge folds"""
        return self.circumference + 19
    
    @property
    def mesh_qty(self) -> int:
        """Mesh panels = bands - 1"""
        return max(self.band_qty - 1, 1)
    
    @property
    def total_band_stock(self) -> float:
        """Total linear inches of band material"""
        return self.band_qty * self.band_length
    
    @property
    def total_mesh_sqin(self) -> float:
        """Total square inches of mesh"""
        return self.mesh_qty * self.mesh_length * 40  # 40" Y-axis
    
    def report(self) -> str:
        """Generate calculation report"""
        lines = [
            "=" * 50,
            "BEAM WRAP CALCULATION",
            "=" * 50,
            f"Beam Type:        {self.beam_type}",
            f"Circumference:    {self.circumference}\"",
            f"Shoe Count:       {self.shoe_count} × {self.shoe_size}\" = {self.shoe_count * self.shoe_size}\"",
            f"Boot Final:       {self.boot_final}\"",
            f"Run (horizontal): {self.run}\"",
            f"Rise (vertical):  {self.rise}\"",
            "-" * 50,
            f"BEAM LENGTH:      {self.beam_length:.2f}\" ({self.beam_length/12:.2f} ft)",
            "-" * 50,
            f"Band Length:      {self.band_length}\" (circ + 8\")",
            f"Band Quantity:    {self.band_qty}",
            f"Total Band Stock: {self.total_band_stock}\" ({self.total_band_stock/12:.2f} ft)",
            "-" * 50,
            f"Mesh Length:      {self.mesh_length}\" (circ + 19\")",
            f"Mesh Panels:      {self.mesh_qty}",
            f"Mesh Width:       40\" (Y-axis)",
            f"Total Mesh:       {self.total_mesh_sqin:.0f} sq in ({self.total_mesh_sqin/144:.2f} sq ft)",
            "=" * 50,
        ]
        return "\n".join(lines)


# ============================================================
# OFFSET CALCULATIONS (Pipe Trades Pro style)
# ============================================================

def rolling_offset(angle: float, offset: float) -> dict:
    """
    Calculate rolling offset (matches Pipe Trades Pro).
    
    Args:
        angle: Angle in degrees
        offset: Offset distance
    
    Returns:
        Dict with travel, advance, run
    """
    angle_rad = math.radians(angle)
    sin_val = math.sin(angle_rad)
    tan_val = math.tan(angle_rad)
    
    # Check for edge cases
    if abs(sin_val) < 1e-10:  # Effectively zero
        travel = 0
        advance = 0
        run = 0
    else:
        travel = offset / sin_val
        advance = offset / tan_val if abs(tan_val) > 1e-10 else 0
        run = offset / tan_val if abs(tan_val) > 1e-10 else 0  # Simplified from offset * cos / sin
    
    return {
        "angle": angle,
        "offset": offset,
        "travel": travel,
        "advance": advance,
        "run": run,
    }


def cutback(angle: float, offset: float) -> dict:
    """
    Calculate cutback (matches Pipe Trades Pro).
    
    Args:
        angle: Angle in degrees
        offset: Offset distance
    
    Returns:
        Dict with cut length
    """
    angle_rad = math.radians(angle)
    
    # Cutback formula from Pipe Trades Pro
    cut = offset * math.tan(angle_rad / 2)
    
    return {
        "angle": angle,
        "offset": offset,
        "cut": cut,
    }


# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Field Calibration System - GPS + Beam Wrap Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py decode "5MHH+P8G Lake Charles, Louisiana"
  python main.py distance "5MHH+P8G" "5MHJ+R2G" --location "Lake Charles, LA"
  python main.py calibrate --satellite 305 --field 305 --unit ft
  python main.py beam --circ 44 --shoes 4 --boot 6 --rise 30
  python main.py offset --angle 45 --offset 5
  python main.py cutback --angle 45 --offset 10
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # DECODE command
    decode_parser = subparsers.add_parser("decode", help="Decode Plus Code to coordinates")
    decode_parser.add_argument("code", help="Plus Code (e.g., '5MHH+P8G Lake Charles, Louisiana')")
    
    # DISTANCE command
    dist_parser = subparsers.add_parser("distance", help="Calculate distance between two points")
    dist_parser.add_argument("point1", help="First Plus Code or 'lat,lon'")
    dist_parser.add_argument("point2", help="Second Plus Code or 'lat,lon'")
    dist_parser.add_argument("--unit", default="ft", choices=["ft", "in", "m", "mi"], help="Output unit")
    dist_parser.add_argument("--location", default="", help="Location context for short codes")
    
    # CALIBRATE command
    cal_parser = subparsers.add_parser("calibrate", help="Compare satellite vs field measurement")
    cal_parser.add_argument("--satellite", type=float, required=True, help="Satellite/GPS distance")
    cal_parser.add_argument("--field", type=float, required=True, help="Field measured distance")
    cal_parser.add_argument("--unit", default="ft", help="Measurement unit")
    
    # BEAM command
    beam_parser = subparsers.add_parser("beam", help="Calculate beam wrap materials")
    beam_parser.add_argument("--circ", type=float, required=True, help="Circumference (inches)")
    beam_parser.add_argument("--shoes", type=int, default=0, help="Shoe count for length")
    beam_parser.add_argument("--boot", type=float, default=0, help="Boot final measurement (inches)")
    beam_parser.add_argument("--rise", type=float, default=0, help="Rise for angled beams (inches)")
    beam_parser.add_argument("--length", type=float, default=0, help="Direct beam length input (inches)")
    
    # OFFSET command (rolling offset)
    offset_parser = subparsers.add_parser("offset", help="Calculate rolling offset")
    offset_parser.add_argument("--angle", type=float, required=True, help="Angle (degrees)")
    offset_parser.add_argument("--offset", type=float, required=True, help="Offset distance")
    
    # CUTBACK command
    cut_parser = subparsers.add_parser("cutback", help="Calculate cutback")
    cut_parser.add_argument("--angle", type=float, required=True, help="Angle (degrees)")
    cut_parser.add_argument("--offset", type=float, required=True, help="Offset distance")
    
    # HYPOTENUSE command
    hyp_parser = subparsers.add_parser("hyp", help="Calculate hypotenuse from run and rise")
    hyp_parser.add_argument("--run", type=float, required=True, help="Run (horizontal)")
    hyp_parser.add_argument("--rise", type=float, required=True, help="Rise (vertical)")
    
    args = parser.parse_args()
    
    if args.command == "decode":
        try:
            area = decode_plus_code(args.code)
            print(f"Plus Code: {args.code}")
            print(f"Latitude:  {area.lat:.6f}")
            print(f"Longitude: {area.lon:.6f}")
            print(f"Center:    ({area.lat:.6f}, {area.lon:.6f})")
            print(f"Bounds:    S:{area.south:.6f} W:{area.west:.6f} N:{area.north:.6f} E:{area.east:.6f}")
            print(f"\nGoogle Maps: https://maps.google.com/?q={area.lat},{area.lon}")
        except Exception as e:
            print(f"Error decoding: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "distance":
        try:
            # Parse points (Plus Code or lat,lon)
            def parse_point(p):
                # Check if it looks like lat,lon coordinates (contains comma and no + separator)
                if "," in p and SEPARATOR not in p:
                    try:
                        lat, lon = map(float, p.split(","))
                        return lat, lon
                    except ValueError:
                        pass
                # Otherwise treat as Plus Code
                area = decode_plus_code(p)
                return area.lat, area.lon
            
            lat1, lon1 = parse_point(args.point1)
            lat2, lon2 = parse_point(args.point2)
            
            dist = haversine_distance(lat1, lon1, lat2, lon2, args.unit)
            
            print(f"Point 1: ({lat1:.6f}, {lon1:.6f})")
            print(f"Point 2: ({lat2:.6f}, {lon2:.6f})")
            print(f"Distance: {dist:.2f} {args.unit}")
        except Exception as e:
            print(f"Error calculating distance: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "calibrate":
        result = calibrate(args.satellite, args.field)
        status = "✓ CALIBRATED" if result["calibrated"] else "✗ NEEDS ADJUSTMENT"
        print(f"Satellite: {result['satellite']:.2f} {args.unit}")
        print(f"Field:     {result['field']:.2f} {args.unit}")
        print(f"Difference: {result['difference']:+.2f} {args.unit}")
        print(f"Error:     {result['pct_error']:+.2f}%")
        print(f"Factor:    {result['adjustment_factor']:.4f}")
        print(f"Status:    {status}")
    
    elif args.command == "beam":
        # Allow direct length input or shoe calculation
        if args.length > 0:
            # Direct input mode - calculate shoes/boot equivalent
            beam = BeamCalc(
                circumference=args.circ,
                shoe_count=int(args.length // DEFAULT_SHOE_SIZE),
                boot_final=args.length % DEFAULT_SHOE_SIZE,
                rise=args.rise,
            )
        else:
            beam = BeamCalc(
                circumference=args.circ,
                shoe_count=args.shoes,
                boot_final=args.boot,
                rise=args.rise,
            )
        print(beam.report())
    
    elif args.command == "offset":
        result = rolling_offset(args.angle, args.offset)
        print(f"Rolling Offset Calculation")
        print(f"=" * 30)
        print(f"Angle:   {result['angle']}°")
        print(f"Offset:  {result['offset']}\"")
        print(f"-" * 30)
        print(f"Travel:  {result['travel']:.4f}\"")
        print(f"Advance: {result['advance']:.4f}\"")
        print(f"Run:     {result['run']:.4f}\"")
    
    elif args.command == "cutback":
        result = cutback(args.angle, args.offset)
        print(f"Cutback Calculation")
        print(f"=" * 30)
        print(f"Angle:  {result['angle']}°")
        print(f"Offset: {result['offset']}\"")
        print(f"-" * 30)
        print(f"Cut:    {result['cut']:.4f}\"")
    
    elif args.command == "hyp":
        travel = pythagorean_distance(args.run, args.rise)
        angle = math.degrees(math.atan2(args.rise, args.run))
        print(f"Pythagorean Calculation")
        print(f"=" * 30)
        print(f"Run:    {args.run}\"")
        print(f"Rise:   {args.rise}\"")
        print(f"-" * 30)
        print(f"Travel: {travel:.4f}\" ({travel/12:.4f} ft)")
        print(f"Angle:  {angle:.2f}°")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
