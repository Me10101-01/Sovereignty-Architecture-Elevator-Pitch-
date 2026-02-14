#!/bin/bash
# deploy_legion.sh
# LEGION OF MINDS Deployment Script
# Strategickhaos DAO LLC | Node 137

set -e

echo "🏛️ DEPLOYING LEGION OF MINDS"
echo "===================================================="

# Create deployment directories
echo "📁 Creating LEGION infrastructure..."
mkdir -p ./legion
mkdir -p ./jarvis/config
mkdir -p ./data/legion
mkdir -p ./data/reflexshell

# Copy LEGION files to deployment directories
echo "📋 Copying LEGION arsenal..."
cp legion_orchestrator.py ./legion/
cp curl_patterns.sh ./legion/
cp jarvis_config.yaml ./legion/

# Validate environment variables
echo "🔐 Validating LEGION credentials..."
required_vars=("GITHUB_TOKEN")
optional_vars=("JETBRAINS_TOKEN" "HARBOR_TOKEN" "OBSIDIAN_TOKEN" "HA_TOKEN")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required variable $var not set"
        echo "   Export your token: export $var=your_token_here"
        exit 1
    fi
done

for var in "${optional_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️  Optional variable $var not set (some patterns may fail)"
    fi
done

# Generate REFLEXSHELL token if not set
if [ -z "$REFLEXSHELL_TOKEN" ]; then
    echo "🔑 Generating REFLEXSHELL_TOKEN..."
    export REFLEXSHELL_TOKEN=$(openssl rand -hex 32)
    echo "   Generated token: $REFLEXSHELL_TOKEN"
    echo "   Save this token for future deployments!"
fi

echo "✅ Environment validated"

# Build and deploy LEGION containers
echo "🐳 Building LEGION containers..."
docker compose -f docker-compose.legion.yml build

echo "🚀 Deploying LEGION OF MINDS..."
docker compose -f docker-compose.legion.yml up -d

# Wait for services to initialize
echo "⏳ Waiting for LEGION systems to activate..."
sleep 15

# Check deployment status
echo "📊 Checking LEGION deployment status..."
docker compose -f docker-compose.legion.yml ps

# Test LEGION endpoints
echo "🎯 Testing LEGION orchestrator..."
curl -s http://localhost:8000/health | jq '.' || echo "⚠️  LEGION orchestrator not responding (may still be initializing)"

echo "🧠 Testing REFLEXSHELL BRAIN integration..."
curl -s http://localhost:8081/brain/status | jq '.' || echo "⚠️  REFLEXSHELL BRAIN not responding (may still be initializing)"

echo "🗄️ Testing Qdrant memory system..."
curl -s http://localhost:6333/collections | jq '.' || echo "⚠️  Qdrant not responding (may still be initializing)"

echo ""
echo "===================================================="
echo "🏛️ LEGION OF MINDS DEPLOYMENT COMPLETE"
echo "===================================================="
echo ""
echo "🎯 Voice Commands:"
echo "   \"Hey Jarvis, run legion recon\"     → Execute 30 recon patterns"
echo "   \"Hey Jarvis, legion status\"        → Check system status"
echo "   \"Hey Jarvis, show reports\"        → List intelligence reports"
echo "   \"Hey Jarvis, quit legion\"         → Safe shutdown"
echo ""
echo "📡 API Endpoints:"
echo "   - LEGION Orchestrator:  http://localhost:8000"
echo "   - REFLEXSHELL BRAIN:    http://localhost:8081"
echo "   - Qdrant Memory:        http://localhost:6333"
echo "   - Home Assistant:       http://localhost:8123"
echo ""
echo "📊 Management:"
echo "   - Trigger Recon:   POST http://localhost:8000/trigger"
echo "   - Check Status:    GET  http://localhost:8000/status"
echo "   - List Reports:    GET  http://localhost:8000/reports"
echo "   - Health Check:    GET  http://localhost:8000/health"
echo ""
echo "📁 Data Locations:"
echo "   - Recon Reports:   ./data/legion/"
echo "   - REFLEXSHELL:     ./data/reflexshell/"
echo "   - Qdrant Storage:  Docker volume"
echo ""
echo "🔍 Monitor LEGION:"
echo "   docker compose -f docker-compose.legion.yml logs -f"
echo ""
echo "🏛️ THE LEGION OF MINDS IS AWAKENED"
echo "🎯 THIRTY RECONNAISSANCE PATTERNS: ARMED"
echo "🗣️ JARVIS VOICE INTERFACE: LISTENING"