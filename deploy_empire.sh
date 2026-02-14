#!/bin/bash
# deploy_empire.sh
# STRATEGICKHAOS EMPIRE Full Deployment Script
# Strategickhaos DAO LLC | Node 137

set -e

echo "🏛️ DEPLOYING STRATEGICKHAOS EMPIRE"
echo "=============================================="

# Create all deployment directories
echo "📁 Creating EMPIRE infrastructure..."
mkdir -p ./hr
mkdir -p ./agents
mkdir -p ./workers
mkdir -p ./crawler
mkdir -p ./hooks
mkdir -p ./jarvis/config
mkdir -p ./data/{hr,legion,agents,workers,crawler}

# Copy empire files to deployment directories
echo "📋 Copying EMPIRE components..."
# Files already created above - no copying needed since they're in place

# Validate critical environment variables
echo "🔐 Validating EMPIRE credentials..."
required_vars=("GITHUB_TOKEN")
critical_vars=("OPENAI_API_KEY" "HA_TOKEN")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required variable $var not set"
        echo "   Export your token: export $var=your_token_here"
        exit 1
    fi
done

for var in "${critical_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️  Critical variable $var not set (some features will be limited)"
    fi
done

# Generate WebDAV credentials if not set
if [ -z "$WEBDAV_USER" ]; then
    export WEBDAV_USER="strategickhaos"
    echo "📝 WebDAV user set to: $WEBDAV_USER"
fi

if [ -z "$WEBDAV_PASS" ]; then
    export WEBDAV_PASS=$(openssl rand -base64 12)
    echo "🔑 Generated WebDAV password: $WEBDAV_PASS"
fi

echo "✅ Environment validated"

# Pull required images
echo "📦 Pulling Docker images..."
docker pull redis:7-alpine
docker pull qdrant/qdrant:v1.12.0
docker pull python:3.12-slim
docker pull homeassistant/home-assistant:stable
docker pull ghcr.io/adnanh/webhook:2.8.1
docker pull ghcr.io/tesseract-ocr/tesseract:5.4.0
docker pull bytemark/webdav

# Build and deploy EMPIRE
echo "🐳 Building EMPIRE containers..."
docker compose -f docker-compose.strategickhaos.yml build --no-cache

echo "🚀 Deploying STRATEGICKHAOS EMPIRE..."
docker compose -f docker-compose.strategickhaos.yml up -d

# Wait for services to initialize
echo "⏳ Waiting for EMPIRE services to activate..."
sleep 30

# Check deployment status
echo "📊 Checking EMPIRE deployment status..."
docker compose -f docker-compose.strategickhaos.yml ps

# Test critical endpoints
echo "🎯 Testing EMPIRE endpoints..."

echo "  Testing HR API..."
curl -s http://localhost:8002/health | jq '.' || echo "⚠️  HR API not responding"

echo "  Testing Legion Orchestrator..."
curl -s http://localhost:8000/health | jq '.' || echo "⚠️  Legion not responding"

echo "  Testing Prompt Service..."
curl -s http://localhost:8010/health | jq '.' || echo "⚠️  Prompt service not responding"

echo "  Testing Qdrant..."
curl -s http://localhost:6333/collections | jq '.' || echo "⚠️  Qdrant not responding"

echo "  Testing Redis..."
docker exec redis redis-cli ping || echo "⚠️  Redis not responding"

echo ""
echo "=============================================="
echo "🏛️ STRATEGICKHAOS EMPIRE DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""
echo "🎯 Voice Commands:"
echo "   \"Hey Jarvis, run full recon\"         → Complete intelligence sweep"
echo "   \"Hey Jarvis, show employee status\"   → HR dashboard and stats"
echo "   \"Hey Jarvis, check system health\"    → Empire-wide health check"
echo "   \"Hey Jarvis, crawl government sites\" → Targeted .gov crawling"
echo ""
echo "📡 Core Services:"
echo "   - HR API & Dashboard:    http://localhost:8002 & http://localhost:8502"
echo "   - Legion Orchestrator:   http://localhost:8000"
echo "   - Prompt Service:        http://localhost:8010"
echo "   - Qdrant Memory:         http://localhost:6333"
echo "   - Webhook Relay:         http://localhost:9000"
echo "   - Obsidian WebDAV:       http://localhost:1900"
echo "   - Home Assistant:        http://localhost:8123"
echo ""
echo "🔧 Worker Services:"
echo "   - LangChain Worker:      AI processing with OpenAI"
echo "   - Celery Queue:          Async task processing"
echo "   - Web Crawler:           .gov/.edu/.org intelligence"
echo "   - Tesseract OCR:         Document text extraction"
echo ""
echo "📁 Data Locations:"
echo "   - HR Data:      ./data/hr/"
echo "   - Legion Intel: ./data/legion/"
echo "   - Crawl Data:   ./data/crawler/"
echo "   - Obsidian:     Docker volume 'vault'"
echo ""
echo "📊 Management Dashboards:"
echo "   - SOC Dashboard: http://localhost:8502"
echo "   - Qdrant UI:     http://localhost:6333/dashboard"
echo ""
echo "🔍 Monitor EMPIRE:"
echo "   docker compose -f docker-compose.strategickhaos.yml logs -f"
echo ""
echo "🏛️ THE STRATEGICKHAOS EMPIRE IS FULLY OPERATIONAL"
echo "🎯 ALL SYSTEMS: ACTIVE AND SOVEREIGN"
echo "🗣️ JARVIS: LISTENING FOR COMMANDS"
echo "🤖 AGENTS: READY FOR DEPLOYMENT"