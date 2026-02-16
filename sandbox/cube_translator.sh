#!/bin/bash
# Cube Translator Script
# Enhanced for YAML diffs and cognitive cube operations

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== CUBE TRANSLATOR ==="
echo "Cognitive Cube Operations with YAML Diff Support"
echo ""

# Function to translate cube operation
translate_operation() {
    local operation=$1
    
    case $operation in
        "diff")
            echo "Generating YAML diff..."
            python3 -c "
from src.register_memory.thought_log_overlay import ThoughtLogOverlay
overlay = ThoughtLogOverlay()
overlay.load()
overlay.export_diff('thought_log_diff.yaml')
"
            echo "Diff exported to thought_log_diff.yaml"
            ;;
        
        "replay")
            echo "Replaying thought-log session..."
            python3 -c "
from src.register_memory.thought_log_overlay import ThoughtLogOverlay
overlay = ThoughtLogOverlay()
overlay.load()
overlay.replay_session('session-03AM')
"
            ;;
        
        "parity")
            echo "Running parity checks..."
            python3 src/entanglement_core/reference_parity_checker.py
            ;;
        
        "waves")
            echo "Computing Bloom wave cores..."
            python3 src/alu/bloom_wave_cores.py
            ;;
        
        "full")
            echo "Running full cube integration..."
            python3 src/cube_simulator/type_promotion_cube.py
            ;;
        
        *)
            echo "Unknown operation: $operation"
            echo "Available operations: diff, replay, parity, waves, full"
            exit 1
            ;;
    esac
}

# Main execution
if [ $# -eq 0 ]; then
    echo "Usage: $0 <operation>"
    echo ""
    echo "Operations:"
    echo "  diff    - Export YAML diff for graph analysis"
    echo "  replay  - Replay thought-log session"
    echo "  parity  - Run reference parity checks"
    echo "  waves   - Compute Bloom wave cores"
    echo "  full    - Run full cube integration"
    exit 1
fi

translate_operation "$1"
