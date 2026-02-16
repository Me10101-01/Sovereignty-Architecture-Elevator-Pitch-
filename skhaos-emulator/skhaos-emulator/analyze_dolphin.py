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
