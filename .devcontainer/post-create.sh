#!/bin/bash
# Post-creation script for Codespaces environment setup

set -e

echo "🚀 Setting up Sovereignty Architecture development environment..."

# Install additional dependencies
echo "📦 Installing additional packages..."
apt-get update -qq
apt-get install -y -qq \
  jq \
  curl \
  wget \
  git \
  make \
  build-essential \
  vim \
  htop

# Install Node.js packages
if [ -f "package.json" ]; then
  echo "📦 Installing Node.js dependencies..."
  npm install
fi

# Install Python packages
if [ -f "requirements.txt" ]; then
  echo "🐍 Installing Python dependencies..."
  pip install -r requirements.txt
fi

# Set up Git configuration
echo "🔧 Configuring Git..."
git config --global core.editor "vim"
git config --global pull.rebase false
git config --global init.defaultBranch main

# Create workspace directories
echo "📁 Creating workspace directories..."
mkdir -p /workspace/{logs,tmp,data}

# Set up environment variables template
if [ ! -f ".env" ]; then
  echo "🔐 Creating .env template from .env.example..."
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "⚠️  Please update .env with your actual credentials"
  fi
fi

# Display welcome message
echo ""
echo "✅ Sovereignty Architecture development environment ready!"
echo ""
echo "🧠 Origin Node Zero (DOM_010101) - Development Instance"
echo ""
echo "Available services:"
echo "  - Origin Node Zero: http://localhost:9000"
echo "  - LTAI Engine: http://localhost:8080"
echo "  - Arsenal Inventory: http://localhost:8081"
echo "  - IAM/Patent Research: http://localhost:8082"
echo "  - Sovryn MCP: http://localhost:8765"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo "  - Keycloak: http://localhost:8180 (admin/admin)"
echo "  - Vault: http://localhost:8200"
echo "  - Prometheus: http://localhost:9090"
echo ""
echo "Quick start commands:"
echo "  - Start all services: docker-compose -f docker-compose.sovereignty.yml up -d"
echo "  - View logs: docker-compose -f docker-compose.sovereignty.yml logs -f"
echo "  - Check status: docker-compose -f docker-compose.sovereignty.yml ps"
echo "  - Stop services: docker-compose -f docker-compose.sovereignty.yml down"
echo ""
echo "🎯 Ready to manifest sovereign infrastructure!"
echo ""
