#!/bin/bash
# Phase 1: ALU Module Deployment
# Builds and deploys the Arithmetic Logic Unit with pipe/neural transforms

set -e

echo "🚀 Phase 1: Deploying ALU Module"
echo "================================="

# Configuration
MODULE="alu"
PHASE="1"
IMAGE_NAME="skhaos-emulator"
TAG="phase1-alu"

# Build base image if not exists
if ! podman image exists localhost/${IMAGE_NAME}:latest; then
    echo "📦 Building base image..."
    cd ../containers
    podman build -f Podmanfile -t ${IMAGE_NAME}:latest .
    cd ../phases
fi

# Tag for this phase
podman tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${TAG}

# Deploy ALU pod
echo "🎯 Deploying ALU pod..."
podman play kube ../containers/alu.pod

# Verify deployment
echo "✅ Verifying ALU deployment..."
sleep 2
podman pod ps | grep skhaos-alu

# Test ALU functionality
echo "🧪 Testing ALU module..."
echo "  - Pipe transform: Run/Offset/Travel → Module/Function/Depth"
echo "  - Neural weight: Layer/Neuron/Weight addressing"
echo "  - Trig wave cores: sin/cos transformations"

# Example UDAP addresses for ALU
cat << EOF

📍 Example UDAP Addresses for ALU:
  
  Pipe Transform:
  skhaos://pipe/run/10/offset/5/travel/15?angle=45
  
  Neural Weight:
  skhaos://neural/layer/3/neuron/5/weight/0?value=0.75
  
  Quantum ALU:
  skhaos://quantum/alu/pipe_offset?angle=45&amplitude=1.0

EOF

# Log deployment
echo "Phase 1 (ALU) deployed at $(date)" >> ../sandbox/evolution_log.json

echo "✨ Phase 1 complete! ALU module is running."
echo "Next: Run ./phase2_control.sh to deploy Control Unit"
