#!/bin/bash
# Phase 14: Dolphin Communication Module
# Add whistles/clicks/dialects, entangle with whale patterns
# GPT reasons signatures
# Commit: "Incorporate dolphin patterns as ID probes"

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIO_PHYSICS_DIR="${REPO_ROOT}/skhaos-emulator/src/bio_physics"
DOLPHIN_COMM_DIR="${REPO_ROOT}/skhaos-emulator/assets/dolphin_comm"

echo "=== Phase 14: Dolphin Communication Module ==="
echo "Adding dolphin patterns (whistles, clicks, dialects)..."

# Create dolphin communication samples
mkdir -p "${DOLPHIN_COMM_DIR}"

cat > "${DOLPHIN_COMM_DIR}/signature_whistles.json" << 'EOF'
{
  "signatures": [
    {
      "dolphin_id": "alpha",
      "base_freq_hz": 10000,
      "contour": [10000, 12000, 15000, 12000, 10000],
      "duration_ms": 1200,
      "signature_type": "rising_falling"
    },
    {
      "dolphin_id": "beta",
      "base_freq_hz": 8000,
      "contour": [8000, 8500, 9000, 8500, 8000],
      "duration_ms": 1000,
      "signature_type": "modulated"
    },
    {
      "dolphin_id": "gamma",
      "base_freq_hz": 15000,
      "contour": [15000, 16000, 18000, 16000, 15000],
      "duration_ms": 1500,
      "signature_type": "high_frequency"
    }
  ]
}
EOF

cat > "${DOLPHIN_COMM_DIR}/echolocation_bursts.json" << 'EOF'
{
  "bursts": [
    {
      "purpose": "navigation",
      "center_freq_hz": 150000,
      "click_count": 20,
      "inter_click_interval_us": 50,
      "distance_range_m": 100
    },
    {
      "purpose": "prey_detection",
      "center_freq_hz": 180000,
      "click_count": 50,
      "inter_click_interval_us": 30,
      "distance_range_m": 50
    }
  ]
}
EOF

cat > "${DOLPHIN_COMM_DIR}/pod_dialects.json" << 'EOF'
{
  "pods": [
    {
      "pod_id": "pod_alpha",
      "matriline": "matriline_A",
      "location": "coastal_region_1",
      "chirp_patterns": ["chirp_A1", "chirp_A2", "chirp_A3"],
      "learned": true
    },
    {
      "pod_id": "pod_beta",
      "matriline": "matriline_B",
      "location": "offshore_region_2",
      "chirp_patterns": ["chirp_B1", "chirp_B2", "chirp_B3", "chirp_B4"],
      "learned": true
    }
  ]
}
EOF

echo "Created dolphin communication sample data"

# Generate dolphin analysis script
DOLPHIN_SCRIPT="${REPO_ROOT}/skhaos-emulator/analyze_dolphin.py"
cat > "${DOLPHIN_SCRIPT}" << 'EOF'
#!/usr/bin/env python3
"""
Dolphin Communication Pattern Analyzer
Analyzes signature whistles, echolocation bursts, and pod dialects
"""

import json
import sys

def analyze_signatures(signature_file):
    """Analyze dolphin signature whistles"""
    with open(signature_file, 'r') as f:
        data = json.load(f)
    
    print("\n=== Signature Whistle Analysis ===")
    print(f"Total signatures: {len(data['signatures'])}")
    
    print("\nDolphin ID | Base Freq (Hz) | Duration (ms) | Type")
    print("-" * 65)
    
    for sig in data['signatures']:
        print(f"{sig['dolphin_id']:10s} | {sig['base_freq_hz']:14d} | {sig['duration_ms']:13d} | {sig['signature_type']}")
    
    # Calculate frequency statistics
    freqs = [sig['base_freq_hz'] for sig in data['signatures']]
    avg_freq = sum(freqs) / len(freqs)
    print(f"\nAverage signature frequency: {avg_freq:.2f} Hz")
    print(f"Frequency range: {min(freqs)} - {max(freqs)} Hz")

def analyze_echolocation(burst_file):
    """Analyze echolocation burst patterns"""
    with open(burst_file, 'r') as f:
        data = json.load(f)
    
    print("\n=== Echolocation Burst Analysis ===")
    print(f"Total burst types: {len(data['bursts'])}")
    
    print("\nPurpose        | Center Freq (Hz) | Clicks | ICI (μs) | Range (m)")
    print("-" * 75)
    
    for burst in data['bursts']:
        print(f"{burst['purpose']:14s} | {burst['center_freq_hz']:16d} | {burst['click_count']:6d} | {burst['inter_click_interval_us']:8d} | {burst['distance_range_m']:8d}")

def analyze_dialects(dialect_file):
    """Analyze pod-specific dialects"""
    with open(dialect_file, 'r') as f:
        data = json.load(f)
    
    print("\n=== Pod Dialect Analysis ===")
    print(f"Total pods: {len(data['pods'])}")
    
    print("\nPod ID      | Matriline    | Patterns | Location")
    print("-" * 65)
    
    for pod in data['pods']:
        print(f"{pod['pod_id']:11s} | {pod['matriline']:12s} | {len(pod['chirp_patterns']):8d} | {pod['location']}")
    
    print("\nNote: Dialects are culturally transmitted (matrilineal)")

if __name__ == "__main__":
    dolphin_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    analyze_signatures(f"{dolphin_dir}/signature_whistles.json")
    analyze_echolocation(f"{dolphin_dir}/echolocation_bursts.json")
    analyze_dialects(f"{dolphin_dir}/pod_dialects.json")
    
    print("\n=== Quantum Probe Mapping ===")
    print("Signature whistles → Recon waves (ID persistence)")
    print("Echolocation bursts → Measurement collapse (120-200kHz)")
    print("Pod dialects → Entangled learning (matrilineal)")
EOF

chmod +x "${DOLPHIN_SCRIPT}"

echo ""
echo "Running dolphin communication analysis..."
python3 "${DOLPHIN_SCRIPT}" "${DOLPHIN_COMM_DIR}"

echo ""
echo "=== Phase 14 Complete ==="
echo "Dolphin communication module integrated successfully"
echo "Whistles mapped to quantum probes for BPEC compilation"
echo ""
echo "Next: Run phase15_physics.sh to integrate physics laws"
