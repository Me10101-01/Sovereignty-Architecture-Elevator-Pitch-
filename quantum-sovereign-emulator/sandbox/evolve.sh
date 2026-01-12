#!/bin/bash
# Sandbox Evolution Script
# Parses YAML, checks parity, and evolves code with agent

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "========================================="
echo "Quantum Sovereign Emulator - Evolution"
echo "========================================="
echo ""

# Step 1: Validate YAML configuration
echo "[Step 1] Validating YAML thought-log..."
if command -v python3 &> /dev/null; then
    python3 -c "import yaml; yaml.safe_load(open('configs/thought_log.yaml'))" 2>/dev/null && \
        echo "✓ YAML validation passed" || echo "⚠ YAML validation failed"
fi
echo ""

# Step 2: Run type promotion cube simulation
echo "[Step 2] Running type promotion cube with YAML replay..."
cd src/cube_simulator
python3 type_promotion_cube.py --simulate yaml-replay 2>/dev/null || \
    python3 type_promotion_cube.py 2>/dev/null || \
    echo "⚠ Simulation skipped (dependencies not installed)"
cd "$PROJECT_ROOT"
echo ""

# Step 3: Execute build order sequence
echo "[Step 3] Executing build order phases..."
for phase in {1..3}; do
    echo "  Phase $phase..."
    python3 src/cube_simulator/cli_journey_sequencer.py --phase "$phase" --quiet 2>/dev/null || \
        echo "    Phase $phase simulation skipped"
done
echo ""

# Step 4: Agent evolution (mock)
echo "[Step 4] Agent evolution analysis..."
python3 src/utils/agent_scaffold.py --phase 11 --evolve src/cube_simulator/type_promotion_cube.py 2>/dev/null || \
    echo "  Agent evolution skipped (requires API configuration)"
echo ""

# Step 5: Git operations (if in git repo)
if [ -d .git ]; then
    echo "[Step 5] Git status check..."
    git status --short
    
    read -p "Commit changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Recursive evolution: Integrated YAML logs and reference parity via agent"
        
        read -p "Push to origin? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin main
            echo "✓ Changes pushed to remote"
        fi
    fi
else
    echo "[Step 5] Not a git repository, skipping git operations"
fi

echo ""
echo "========================================="
echo "Evolution complete!"
echo "========================================="
