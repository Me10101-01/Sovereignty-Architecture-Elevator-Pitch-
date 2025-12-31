#!/bin/bash
# Phase 13: Zipf Analyzer Module
# Build rankings for whale songs (humpback data sims)
# GPT generates 1/f distribution code
# Commit: "Entangle Zipf's law to quantum ranks"

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIO_PHYSICS_DIR="${REPO_ROOT}/skhaos-emulator/src/bio_physics"

echo "=== Phase 13: Zipf Analyzer Module ==="
echo "Building Zipf's law analyzer for whale communication patterns..."

# Create test data for whale songs
WHALE_SONGS_DIR="${REPO_ROOT}/skhaos-emulator/assets/whale_songs"
mkdir -p "${WHALE_SONGS_DIR}"

cat > "${WHALE_SONGS_DIR}/humpback_sample.txt" << 'EOF'
moan
moan
moan
moan
cry
cry
cry
grumble
grumble
wop
throb
EOF

echo "Created humpback whale song sample data"

# Generate Zipf analysis script
ANALYSIS_SCRIPT="${REPO_ROOT}/skhaos-emulator/analyze_zipf.py"
cat > "${ANALYSIS_SCRIPT}" << 'EOF'
#!/usr/bin/env python3
"""
Zipf's Law Analysis for Whale Communication Patterns
Analyzes frequency distribution and calculates Zipf rankings
"""

import sys
from collections import Counter
import math

def analyze_zipf(units):
    """Analyze units using Zipf's law: frequency ~ 1/rank"""
    freq_counter = Counter(units)
    
    # Sort by frequency (descending)
    sorted_units = sorted(freq_counter.items(), key=lambda x: x[1], reverse=True)
    
    print("\n=== Zipf Distribution Analysis ===")
    print(f"Total units: {len(units)}")
    print(f"Unique units: {len(freq_counter)}")
    
    # Calculate Zipf scores
    print("\nRank | Unit       | Frequency | Zipf Score (freq/rank)")
    print("-" * 55)
    
    for rank, (unit, freq) in enumerate(sorted_units, 1):
        zipf_score = freq / rank
        print(f"{rank:4d} | {unit:10s} | {freq:9d} | {zipf_score:10.3f}")
    
    # Calculate entropy
    total = len(units)
    entropy = 0.0
    for unit, count in freq_counter.items():
        p = count / total
        entropy -= p * math.log(p)
    
    print(f"\nShannon Entropy: {entropy:.4f}")
    
    # Goodness of fit (simplified R²)
    observed = [freq for _, freq in sorted_units]
    expected = [sorted_units[0][1] / (i + 1) for i in range(len(sorted_units))]
    
    mean_obs = sum(observed) / len(observed)
    ss_tot = sum((o - mean_obs) ** 2 for o in observed)
    ss_res = sum((o - e) ** 2 for o, e in zip(observed, expected))
    
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    print(f"Zipf Goodness of Fit (R²): {r_squared:.4f}")
    
    return sorted_units, entropy, r_squared

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_zipf.py <whale_song_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        units = [line.strip() for line in f if line.strip()]
    
    analyze_zipf(units)
EOF

chmod +x "${ANALYSIS_SCRIPT}"

echo "Running Zipf analysis on whale song data..."
python3 "${ANALYSIS_SCRIPT}" "${WHALE_SONGS_DIR}/humpback_sample.txt"

echo ""
echo "=== Phase 13 Complete ==="
echo "Zipf analyzer module built successfully"
echo "Swarms can now cultural-evolve units using Zipf rankings"
echo ""
echo "Next: Run phase14_dolphin.sh to add dolphin communication patterns"
