#!/bin/bash
# Quick Start Guide for BPEC
# Runs all phases in sequence and demonstrates the system

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  BPEC Quick Start - Bio-Physics Entanglement Compiler         ║"
echo "║  INVENTION_074 - Patent-Pending Innovation                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${REPO_ROOT}"

echo "Repository: ${REPO_ROOT}"
echo ""

# Check dependencies
echo "=== Checking Dependencies ==="
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is required"; exit 1; }
command -v bash >/dev/null 2>&1 || { echo "Error: bash is required"; exit 1; }
echo "✓ Python 3: $(python3 --version)"
echo "✓ Bash: $(bash --version | head -1)"
echo ""

# Phase 13: Zipf Analyzer
echo "════════════════════════════════════════════════════════════════"
echo "PHASE 13: Zipf's Law Analysis"
echo "════════════════════════════════════════════════════════════════"
./phases/phase13_zipf.sh
echo ""
sleep 2

# Phase 14: Dolphin Communication
echo "════════════════════════════════════════════════════════════════"
echo "PHASE 14: Dolphin Communication Patterns"
echo "════════════════════════════════════════════════════════════════"
./phases/phase14_dolphin.sh
echo ""
sleep 2

# Phase 15: Physics DOM
echo "════════════════════════════════════════════════════════════════"
echo "PHASE 15: Physics Domain Ontology"
echo "════════════════════════════════════════════════════════════════"
./phases/phase15_physics.sh
echo ""
sleep 2

# Recursive Evolution
echo "════════════════════════════════════════════════════════════════"
echo "RECURSIVE EVOLUTION: Bio-Physics Hybrid Patterns"
echo "════════════════════════════════════════════════════════════════"
./phases/evolve_recursive.sh
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  BPEC System Operational - All Phases Complete                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Generated Outputs:"
echo "  • Zipf rankings: skhaos-emulator/assets/whale_songs/"
echo "  • Dolphin data: skhaos-emulator/assets/dolphin_comm/"
echo "  • Evolution log: skhaos-emulator/sandbox/evolution_log.json"
echo ""
echo "Documentation:"
echo "  • README.md - Complete system overview"
echo "  • CLI_COMMANDS.md - All 42 recon commands"
echo ""
echo "Next Steps:"
echo "  1. Review README.md for architecture details"
echo "  2. Explore CLI_COMMANDS.md for command reference"
echo "  3. Examine Rust modules in src/bio_physics/"
echo "  4. Run individual phase scripts for specific analyses"
echo ""
echo "UDAP URI Examples:"
echo "  • skhaos://bio/zipf/unit/1?law=entropy&hz=20"
echo "  • skhaos://bio/dolphin/whistle?signature=true&hz=10"
echo "  • skhaos://physics/rondo?law=conservation&hz=10"
echo ""
echo "✓ BPEC Quick Start Complete!"
