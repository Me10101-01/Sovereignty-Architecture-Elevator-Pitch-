#!/bin/bash
# KhaosSearch Deployment Script
# Quick deployment of sovereign search engine
# Version: 1.0

set -e

echo "🔍 KhaosSearch Deployment Script"
echo "================================="
echo ""

# Check for required tools
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Check if .env exists
if [ ! -f searxng/.env ]; then
    echo "⚙️  Creating .env file from template..."
    cp searxng/.env.example searxng/.env
    
    # Generate random secret
    SECRET=$(openssl rand -hex 32)
    sed -i "s/changeme-generate-random-secret-here/$SECRET/g" searxng/.env
    
    echo "✅ Created searxng/.env with random secret"
    echo "⚠️  Please edit searxng/.env to configure your domain and email"
    echo ""
fi

# Ask user if they want to continue
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting KhaosSearch services..."
docker-compose -f docker-compose.khaossearch.yml up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose -f docker-compose.khaossearch.yml ps | grep -q "Up"; then
    echo "✅ KhaosSearch is running!"
    echo ""
    echo "📍 Access points:"
    echo "   - Search engine: http://localhost:8888"
    echo "   - Traefik dashboard: http://localhost:8080"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Configure your domain in searxng/.env"
    echo "   2. Update DNS records to point to this server"
    echo "   3. Restart services: docker-compose -f docker-compose.khaossearch.yml restart"
    echo ""
    echo "📖 Documentation: See KHAOSOS_ARCHITECTURE.md for details"
else
    echo "❌ Some services failed to start. Check logs:"
    echo "   docker-compose -f docker-compose.khaossearch.yml logs"
    exit 1
fi
