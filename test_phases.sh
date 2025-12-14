#!/bin/bash
# Integration test for Phases 1-7
# Tests each phase script execution

set -e

echo "==================================="
echo "Testing Sovereignty Architecture"
echo "Phases 1-7 Integration Test"
echo "==================================="
echo ""

# Change to repo root
cd "$(dirname "$0")"

# Install dependencies
echo "Installing dependencies..."
pip install -q pyyaml numpy sympy networkx

echo ""
echo "--- Phase 1: Bootstrap Tree ---"
cd phase1
python bootstrap.py
cd ..

echo ""
echo "--- Phase 2: Prior Art Guards ---"
cd phase2
python guards.py
cd ..

echo ""
echo "--- Phase 3: Quantum Components ---"
cd phase3
python quantum.py
cd ..

echo ""
echo "--- Phase 4: Register Memory ---"
cd phase4
python memory.py
cd ..

echo ""
echo "--- Phase 5: Full Integration (Swarm Activation) ---"
python phase5/integrate.py

echo ""
echo "--- Phase 6: Superposition Expansion ---"
python phase6/expand_claim8.py

echo ""
echo "--- Phase 7: Ripley Gates Deepening + Benchmarks ---"
python phase7/deepen_ripley_explore_sagco.py

echo ""
echo "==================================="
echo "All phases tested successfully!"
echo "==================================="
echo ""
echo "Generated Files:"
echo "  - feps/novel_table.yaml"
echo "  - benchmarks/ripley_sagco.yaml"
echo "  - docs/prior_art.pdf.yaml"
echo "  - src/swarm_bots/bots.yaml"
echo ""
echo "Next Steps:"
echo "  1. Run: podman-compose up --build"
echo "  2. Or: docker-compose up --build"
echo "  3. View logs: docker-compose logs -f integration"
echo ""
