#!/bin/bash
# Execute War Room Synthesizer
# Master Executive Autonomous Override Protocol

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "═══════════════════════════════════════════════════════════════"
echo "  Preparing War Room Synthesizer Execution"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if npm dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Execute the War Room Synthesizer
echo "🚀 Executing Master Executive Autonomous Override Protocol..."
echo ""
npm run war-room

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Post-Execution Actions"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if vault was generated
if [ -d "threat-model-2025-vault" ]; then
    echo "✅ Threat vault successfully generated"
    echo "   Location: ./threat-model-2025-vault/"
    echo ""
    echo "📖 To view in Obsidian:"
    echo "   1. Open Obsidian"
    echo "   2. Open folder as vault: $(pwd)/threat-model-2025-vault"
    echo "   3. View graph: Ctrl+G (Cmd+G on Mac)"
    echo ""
fi

# Check if ConfigMap was generated
if [ -f "threat-model-2025-configmap.yaml" ]; then
    echo "✅ Kubernetes ConfigMap generated"
    echo "   Location: ./threat-model-2025-configmap.yaml"
    echo ""
    echo "☸️ To deploy to Kubernetes:"
    echo "   kubectl apply -f threat-model-2025-configmap.yaml"
    echo ""
    echo "   Verify deployment:"
    echo "   kubectl get configmap threat-model-2025-vault -n security"
    echo ""
fi

echo "🛡️ War Room Synthesizer execution complete!"
echo "   The swarm is now hardened and vigilant."
echo ""
