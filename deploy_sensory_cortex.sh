#!/bin/bash
# deploy_sensory_cortex.sh
# REFLEXSHELL BRAIN v1 Sensory Cortex Deployment
# Strategickhaos DAO LLC | Node 137

set -e

echo "🧠 DEPLOYING SENSORY CORTEX v1"
echo "=================================================="

# Create deployment directories
echo "📁 Creating deployment structure..."
mkdir -p ./comms
mkdir -p ./data/comms
mkdir -p ./data/reflexshell

# Copy configuration files to comms directory
echo "📋 Copying configuration files..."
cp comms_orchestrator_v1.yaml ./comms/
cp comms_orchestrator.py ./comms/

# Validate environment variables
echo "🔐 Validating environment..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN not set"
    echo "   Export your GitHub token: export GITHUB_TOKEN=ghp_your_token_here"
    exit 1
fi

if [ -z "$REFLEXSHELL_TOKEN" ]; then
    echo "🔑 Generating REFLEXSHELL_TOKEN..."
    export REFLEXSHELL_TOKEN=$(openssl rand -hex 32)
    echo "   Generated token: $REFLEXSHELL_TOKEN"
    echo "   Save this token for future deployments!"
fi

echo "✅ Environment validated"

# Build and deploy containers
echo "🐳 Building Docker containers..."
docker compose -f docker-compose.comms.yml build

echo "🚀 Deploying SENSORY CORTEX..."
docker compose -f docker-compose.comms.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check deployment status
echo "📊 Checking deployment status..."
docker compose -f docker-compose.comms.yml ps

# Test REFLEXSHELL BRAIN endpoint
echo "🧠 Testing REFLEXSHELL BRAIN connectivity..."
curl -s http://localhost:8080/brain/status || echo "⚠️  REFLEXSHELL BRAIN not responding (may still be starting)"

echo ""
echo "=================================================="
echo "🎯 SENSORY CORTEX v1 DEPLOYMENT COMPLETE"
echo "=================================================="
echo ""
echo "📡 Services:"
echo "   - Comms Orchestrator: ACTIVE (GitHub events → unified stream)"
echo "   - REFLEXSHELL BRAIN:  http://localhost:8080"
echo ""
echo "📊 Endpoints:"
echo "   - Brain Status:  GET  http://localhost:8080/brain/status"
echo "   - Query Events:  GET  http://localhost:8080/events/query"
echo "   - Event Webhook: POST http://localhost:8080/events"
echo ""
echo "📁 Data Locations:"
echo "   - Unified Events: ./data/comms/events.jsonl"
echo "   - Brain Events:   ./data/reflexshell/brain_events.jsonl"
echo ""
echo "🔍 Monitor logs:"
echo "   docker compose -f docker-compose.comms.yml logs -f"
echo ""
echo "🧠 THE NERVE BUNDLE IS ALIVE"
echo "🚀 NEURAL PATHWAYS: FIRING"