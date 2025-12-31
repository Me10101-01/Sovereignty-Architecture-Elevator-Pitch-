#!/bin/bash
# Phase 2: Control Unit Deployment
# Deploys UDAP parser and swarm orchestrator

set -e

echo "🚀 Phase 2: Deploying Control Unit"
echo "==================================="

# Configuration
MODULE="control_unit"
PHASE="2"
IMAGE_NAME="skhaos-emulator"
TAG="phase2-control"

# Check if Phase 1 is complete
if ! podman pod ps | grep -q skhaos-alu; then
    echo "❌ Error: Phase 1 (ALU) must be deployed first"
    echo "Run: ./phase1_alu.sh"
    exit 1
fi

# Tag for this phase
podman tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${TAG}

# Deploy Control Unit pod
echo "🎯 Deploying Control Unit pod..."
podman play kube ../containers/control_unit.pod

# Verify deployment
echo "✅ Verifying Control Unit deployment..."
sleep 2
podman pod ps | grep skhaos-control

# Initialize UDAP routing table
echo "🗺️  Initializing UDAP routing table..."
echo "  - pipe → ALU"
echo "  - neural → ALU"
echo "  - mood → RegisterMemory"
echo "  - chess → EntanglementCore"
echo "  - gps → EntanglementCore"
echo "  - network → IOUnit"

# Test Control Unit functionality
echo "🧪 Testing Control Unit module..."
echo "  - UDAP parser: skhaos:// URI routing"
echo "  - Swarm orchestrator: Multi-agent coordination"
echo "  - Neural tick clocks: 10Hz alpha wave sync"

# Example UDAP addresses for Control Unit
cat << EOF

📍 Example UDAP Addresses for Control Unit:

  Mood State:
  skhaos://mood/beta/high?hz=18&intensity=0.8&color=yellow
  
  Network Routing:
  skhaos://network/ip/192.168.1.1/port/8080?protocol=tcp
  
  Swarm Task:
  skhaos://control/swarm/task/0?role=mapper&domain=pipe

EOF

# Log deployment
echo "Phase 2 (Control Unit) deployed at $(date)" >> ../sandbox/evolution_log.json

echo "✨ Phase 2 complete! Control Unit is orchestrating."
echo "Next: Run ./phase3_entangle.sh to deploy Entanglement Core"
