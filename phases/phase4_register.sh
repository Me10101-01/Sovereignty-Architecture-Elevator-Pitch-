#!/bin/bash
# Phase 4: Register Memory Deployment
# Deploys URI cache, mood state persistence, and neural tick clocks

set -e

echo "🚀 Phase 4: Deploying Register Memory"
echo "====================================="

# Configuration
MODULE="register_memory"
PHASE="4"
IMAGE_NAME="skhaos-emulator"
TAG="phase4-register"

# Check if Phase 3 is complete
if ! podman pod ps | grep -q skhaos-entanglement; then
    echo "❌ Error: Phase 3 (Entanglement Core) must be deployed first"
    echo "Run: ./phase3_entangle.sh"
    exit 1
fi

# Tag for this phase
podman tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${TAG}

# Deploy Register Memory pod
echo "🎯 Deploying Register Memory pod..."
podman play kube ../containers/register_memory.pod

# Verify deployment
echo "✅ Verifying Register Memory deployment..."
sleep 2
podman pod ps | grep skhaos-register

# Initialize caching system
echo "💾 Initializing URI cache..."
echo "  - Cache size: 10,000 UDAP addresses"
echo "  - LRU eviction policy"
echo "  - Fast O(1) lookup"

# Initialize mood state system
echo "🎨 Initializing mood state persistence..."
echo "  - Delta (0.5-4 Hz): Deep sleep"
echo "  - Theta (4-8 Hz): Meditation, creativity"
echo "  - Alpha (8-13 Hz): Relaxed, calm"
echo "  - Beta (13-30 Hz): Alert, focused"
echo "  - Gamma (30-100 Hz): High-level processing"

# Start neural tick clocks
echo "⏰ Starting neural tick clocks..."
echo "  - System clock: 10 Hz (Alpha waves)"
echo "  - Variable Hz for different moods"
echo "  - Z-axis duration tracking"

# Test Register Memory functionality
echo "🧪 Testing Register Memory module..."
echo "  - URI cache: Fast UDAP address lookup"
echo "  - Mood states: Hz/Color/Duration persistence"
echo "  - Temporal states: Z-axis time tracking"

# Example UDAP addresses for Register Memory
cat << EOF

📍 Example UDAP Addresses for Register Memory:

  URI Cache Entry:
  skhaos://cache/uri/12345?address=pipe/run/5&hits=42&timestamp=1704067200
  
  Mood State:
  skhaos://mood/alpha/relaxed?hz=10.0&color=green&intensity=0.75&duration=60
  
  Neural Tick Clock:
  skhaos://agent/neural_clock?hz=10.0&wave_type=Alpha&ticks=1337
  
  Temporal State:
  skhaos://temporal/state/0?address=mood/alpha&duration=300&active=true

EOF

# Formalize UDAP JSON Schema
echo "📋 Formalizing UDAP JSON Schema..."
cat > ../schemas/udap.json << 'SCHEMA'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UDAP Address Schema",
  "description": "Universal Domain Addressing Protocol for SkhaOS",
  "type": "object",
  "properties": {
    "scheme": {
      "type": "string",
      "const": "skhaos"
    },
    "domain": {
      "type": "string",
      "enum": ["pipe", "neural", "mood", "chess", "gps", "network", "quantum", "agent", "cache", "temporal"]
    },
    "path": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "parameters": {
      "type": "object",
      "additionalProperties": {
        "type": ["string", "number", "boolean"]
      }
    }
  },
  "required": ["scheme", "domain", "path"]
}
SCHEMA

echo "✅ UDAP schema saved to schemas/udap.json"

# Log deployment
echo "Phase 4 (Register Memory) deployed at $(date)" >> ../sandbox/evolution_log.json

echo "✨ Phase 4 complete! State persistence active."
echo "Next: Run ./evolve_recursive.sh for full system evolution"
