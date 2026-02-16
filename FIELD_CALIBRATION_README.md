# Field Calibration System

A comprehensive GPS and field measurement calibration tool with Plus Code decoding, distance calculations, and beam wrap material estimation.

## Features

### 1. Plus Code Decoder
Decode Google Plus Codes (Open Location Codes) to GPS coordinates:
```bash
python main.py decode "5MHH+P8G Lake Charles, Louisiana"
```

### 2. Distance Calculations
Calculate distances between two GPS points using the Haversine formula:
```bash
# Using coordinates
python main.py distance "30.2266,-93.2174" "30.2366,-93.3774" --unit mi

# Using Plus Codes
python main.py distance "5MHH+P8G" "5MHJ+R2G" --location "Lake Charles, LA" --unit ft
```

Supported units: `ft` (feet), `in` (inches), `m` (meters), `mi` (miles)

### 3. Calibration
Compare satellite/GPS measurements with field measurements:
```bash
python main.py calibrate --satellite 305 --field 305 --unit ft
```

The system indicates if measurements are calibrated (within 2% tolerance).

### 4. Beam Wrap Calculations
Calculate materials needed for beam wrapping projects:
```bash
python main.py beam --circ 44 --shoes 4 --boot 6 --rise 30
```

Calculates:
- Beam length (horizontal run + vertical rise)
- Band quantity and total stock needed
- Mesh panels and total square footage

### 5. Pipe Offset Calculations
Calculate rolling offsets for pipe fitting:
```bash
python main.py offset --angle 45 --offset 5
```

### 6. Cutback Calculations
Calculate cutback measurements:
```bash
python main.py cutback --angle 45 --offset 10
```

### 7. Pythagorean (Hypotenuse) Calculations
Calculate the true length from horizontal run and vertical rise:
```bash
python main.py hyp --run 100 --rise 50
```

## Installation

No external dependencies required! Uses only Python 3 standard library.

```bash
chmod +x main.py
python3 main.py --help
```

## Testing

Run the comprehensive test suite:
```bash
python3 -m unittest test_main -v
```

All 17 tests cover:
- Plus Code decoding (full and short codes)
- GPS distance calculations
- Calibration accuracy
- Beam wrap material calculations
- Offset and cutback calculations

## Technical Details

### Plus Code Decoding
- Supports full Plus Codes (8+ characters before +)
- Supports short codes with location context
- Resolution down to ~3m x 3m areas

### Distance Calculations
- Haversine formula for accurate Earth surface distances
- Multiple unit support (feet, inches, meters, miles)

### Beam Wrap Formulas
- Band length = circumference + 8"
- Band quantity = ceiling(beam_length / 40) + 1
- Mesh length = circumference + 19"
- Mesh panels = band quantity - 1

## Examples

### Complete Workflow Example
```bash
# 1. Decode field locations
python3 main.py decode "5MHH+P8G Lake Charles, Louisiana"

# 2. Measure distance between points
python3 main.py distance "30.179313,-93.321687" "30.226600,-93.217400" --unit ft

# 3. Calibrate measurement tools
python3 main.py calibrate --satellite 8500 --field 8520 --unit ft

# 4. Calculate beam wrap materials
python3 main.py beam --circ 44 --shoes 4 --boot 6 --rise 30
```

## License

Part of the Sovereignty Architecture project.
