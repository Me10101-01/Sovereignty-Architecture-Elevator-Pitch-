#!/usr/bin/env python3
"""
PIPE TRADES CLI - Field Calibration System
==========================================
Decode Plus Codes / GPS coordinates
Calculate distances between points
Beam wrap material estimation
Rolling offset calculations (mirrors Pipe Trades Pro 4095)

Usage:
    python main.py decode "5MHH+P8G Lake Charles, Louisiana"
    python main.py beam --circ 44 --shoes 4 --boot 6 --rise 30
    python main.py offset --angle 45 --offset 5
    python main.py calibrate --satellite 305 --field 305 --unit ft
"""

import argparse
import math
import sys
from dataclasses import dataclass
from typing import Tuple

# ============================================================
# CONSTANTS
# ============================================================

SHOE_SIZE = 14  # inches - field measurement constant
CODE_ALPHABET = "23456789CFGHJMPQRVWX"
SEPARATOR = "+"
LATITUDE_MAX = 90
LONGITUDE_MAX = 180

REFERENCE_POINTS = {
    "lake charles": (30.2266, -93.2174),
    "sulphur": (30.2366, -93.3774),
    "louisiana": (30.9843, -91.9623),
}

# ============================================================
# GPS / PLUS CODE
# ============================================================

@dataclass
class CodeArea:
    south: float
    west: float
    north: float
    east: float
    
    @property
    def lat(self) -> float:
        return (self.south + self.north) / 2
    
    @property
    def lon(self) -> float:
        return (self.west + self.east) / 2


def decode_plus_code(code: str) -> CodeArea:
    original = code.strip()
    ref_lat, ref_lon = None, None
    
    for loc_key, coords in REFERENCE_POINTS.items():
        if loc_key in original.lower():
            ref_lat, ref_lon = coords
            break
    
    code_part = original.upper().split()[0]
    
    if SEPARATOR in code_part:
        prefix, suffix = code_part.split(SEPARATOR)
        if len(prefix) < 8 and ref_lat is not None:
            lat_val = ref_lat + LATITUDE_MAX
            lon_val = ref_lon + LONGITUDE_MAX
            c1 = CODE_ALPHABET[int(lat_val / 20)]
            c2 = CODE_ALPHABET[int(lon_val / 20)]
            c3 = CODE_ALPHABET[int((lat_val % 20) / 1)]
            c4 = CODE_ALPHABET[int((lon_val % 20) / 1)]
            code_part = f"{c1}{c2}{c3}{c4}{code_part}"
    
    code = code_part.replace(SEPARATOR, "")
    
    PAIR_RESOLUTIONS = [20.0, 1.0, 0.05, 0.0025, 0.000125]
    south, west = 0.0, 0.0
    lat_res, lon_res = PAIR_RESOLUTIONS[0], PAIR_RESOLUTIONS[0]
    
    for i in range(0, min(len(code), 10), 2):
        if i + 1 >= len(code):
            break
        lat_res = PAIR_RESOLUTIONS[i // 2]
        lon_res = PAIR_RESOLUTIONS[i // 2]
        south += CODE_ALPHABET.index(code[i]) * lat_res
        west += CODE_ALPHABET.index(code[i + 1]) * lon_res
    
    south -= LATITUDE_MAX
    west -= LONGITUDE_MAX
    
    return CodeArea(south=south, west=west, north=south + lat_res, east=west + lon_res)


# ============================================================
# DISTANCE CALCULATIONS
# ============================================================

def haversine(lat1: float, lon1: float, lat2: float, lon2: float, unit: str = "ft") -> float:
    R_FT = 20902231
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist_ft = R_FT * c
    
    if unit == "m":
        return dist_ft * 0.3048
    return dist_ft


# ============================================================
# BEAM WRAP CALCULATIONS
# ============================================================

@dataclass
class BeamCalc:
    circumference: float  # inches
    num_shoes: int
    boot_height: float  # inches
    rise: float  # inches
    
    @property
    def shoe_span(self) -> float:
        return self.num_shoes * SHOE_SIZE
    
    @property
    def wrap_length(self) -> float:
        return self.shoe_span + (2 * self.boot_height)
    
    @property
    def material_area(self) -> float:
        return self.circumference * self.wrap_length
    
    @property
    def rise_factor(self) -> float:
        return math.sqrt(1 + (self.rise / self.shoe_span) ** 2)
    
    def report(self) -> str:
        lines = [
            "="*50,
            "BEAM WRAP MATERIAL ESTIMATION",
            "="*50,
            f"Circumference:     {self.circumference:.2f} in",
            f"Shoes:             {self.num_shoes}",
            f"Boot height:       {self.boot_height:.2f} in",
            f"Rise:              {self.rise:.2f} in",
            "",
            f"Shoe span:         {self.shoe_span:.2f} in",
            f"Wrap length:       {self.wrap_length:.2f} in",
            f"Material area:     {self.material_area:.2f} sq in",
            f"Rise factor:       {self.rise_factor:.4f}",
            "="*50
        ]
        return "\n".join(lines)


# ============================================================
# ROLLING OFFSET CALCULATIONS
# ============================================================

def rolling_offset(angle: float, offset: float) -> Tuple[float, float]:
    """
    Calculate rolling offset (mirrors Pipe Trades Pro 4095)
    Returns: (travel, advance)
    """
    angle_rad = math.radians(angle)
    travel = offset / math.sin(angle_rad)
    advance = offset / math.tan(angle_rad)
    return travel, advance


def cutback(diameter: float, angle: float) -> float:
    """Calculate cutback for pipe fitting"""
    return diameter * math.tan(math.radians(angle / 2))


# ============================================================
# CALIBRATION
# ============================================================

def calibrate(satellite: float, field: float, unit: str = "ft") -> dict:
    """Compare satellite vs field measurements"""
    delta = abs(satellite - field)
    error_pct = (delta / satellite * 100) if satellite != 0 else 0
    
    return {
        "satellite": satellite,
        "field": field,
        "delta": delta,
        "error_percent": error_pct,
        "unit": unit,
        "within_tolerance": error_pct < 5.0
    }


# ============================================================
# CLI COMMANDS
# ============================================================

def cmd_decode(args):
    """Decode Plus Code to GPS coordinates"""
    try:
        area = decode_plus_code(args.code)
        print(f"\n{'='*50}")
        print("PLUS CODE DECODED")
        print(f"{'='*50}")
        print(f"Input:       {args.code}")
        print(f"Latitude:    {area.lat:.6f}°")
        print(f"Longitude:   {area.lon:.6f}°")
        print(f"Bounds:")
        print(f"  South:     {area.south:.6f}°")
        print(f"  North:     {area.north:.6f}°")
        print(f"  West:      {area.west:.6f}°")
        print(f"  East:      {area.east:.6f}°")
        print(f"\nGoogle Maps: https://www.google.com/maps?q={area.lat},{area.lon}")
        print(f"{'='*50}\n")
    except Exception as e:
        print(f"Error decoding: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_beam(args):
    """Calculate beam wrap material requirements"""
    calc = BeamCalc(
        circumference=args.circ,
        num_shoes=args.shoes,
        boot_height=args.boot,
        rise=args.rise
    )
    print(f"\n{calc.report()}\n")
    return 0


def cmd_offset(args):
    """Calculate rolling offset"""
    travel, advance = rolling_offset(args.angle, args.offset)
    print(f"\n{'='*50}")
    print("ROLLING OFFSET CALCULATION")
    print(f"{'='*50}")
    print(f"Angle:       {args.angle}°")
    print(f"Offset:      {args.offset} in")
    print(f"\nTravel:      {travel:.4f} in")
    print(f"Advance:     {advance:.4f} in")
    print(f"{'='*50}\n")
    return 0


def cmd_calibrate(args):
    """Compare satellite vs field measurements"""
    result = calibrate(args.satellite, args.field, args.unit)
    
    status = "✓ PASS" if result["within_tolerance"] else "✗ FAIL"
    
    print(f"\n{'='*50}")
    print("CALIBRATION REPORT")
    print(f"{'='*50}")
    print(f"Satellite:   {result['satellite']:.2f} {result['unit']}")
    print(f"Field:       {result['field']:.2f} {result['unit']}")
    print(f"Delta:       {result['delta']:.2f} {result['unit']}")
    print(f"Error:       {result['error_percent']:.2f}%")
    print(f"Status:      {status}")
    print(f"{'='*50}\n")
    return 0 if result["within_tolerance"] else 1


# ============================================================
# MAIN CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="PIPE TRADES CLI - Field Calibration System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # decode command
    decode_parser = subparsers.add_parser("decode", help="Decode Plus Code / GPS")
    decode_parser.add_argument("code", help="Plus Code (e.g., '5MHH+P8G Lake Charles, Louisiana')")
    
    # beam command
    beam_parser = subparsers.add_parser("beam", help="Calculate beam wrap material")
    beam_parser.add_argument("--circ", type=float, required=True, help="Circumference (inches)")
    beam_parser.add_argument("--shoes", type=int, required=True, help="Number of shoes")
    beam_parser.add_argument("--boot", type=float, required=True, help="Boot height (inches)")
    beam_parser.add_argument("--rise", type=float, required=True, help="Rise (inches)")
    
    # offset command
    offset_parser = subparsers.add_parser("offset", help="Calculate rolling offset")
    offset_parser.add_argument("--angle", type=float, required=True, help="Angle (degrees)")
    offset_parser.add_argument("--offset", type=float, required=True, help="Offset (inches)")
    
    # calibrate command
    calibrate_parser = subparsers.add_parser("calibrate", help="Compare satellite vs field measurements")
    calibrate_parser.add_argument("--satellite", type=float, required=True, help="Satellite measurement")
    calibrate_parser.add_argument("--field", type=float, required=True, help="Field measurement")
    calibrate_parser.add_argument("--unit", default="ft", help="Unit (ft or m)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        "decode": cmd_decode,
        "beam": cmd_beam,
        "offset": cmd_offset,
        "calibrate": cmd_calibrate
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
