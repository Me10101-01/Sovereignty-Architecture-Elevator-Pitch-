#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Red/Blue Battleground Cluster Connection Script
# StrategicKhaos DAO LLC - IDEA_101
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Configuration
GCP_PROJECT="jarvis-swarm-personal"
REGION="us-central1"
BLUE_CLUSTER="jarvis-swarm-personal-001"
RED_CLUSTER="red-team"

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🔵🔴 Red/Blue Battleground Cluster Connection"
echo "═══════════════════════════════════════════════════════════════════════════════"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

echo ""
echo "📍 Project: $GCP_PROJECT"
echo "📍 Region: $REGION"
echo ""

# Connect to Blue Team cluster
echo "🔵 Connecting to Blue Team (Defense Fortress): $BLUE_CLUSTER"
gcloud container clusters get-credentials "$BLUE_CLUSTER" \
    --region="$REGION" \
    --project="$GCP_PROJECT"

# Connect to Red Team cluster
echo "🔴 Connecting to Red Team (Chaos Engine): $RED_CLUSTER"
gcloud container clusters get-credentials "$RED_CLUSTER" \
    --region="$REGION" \
    --project="$GCP_PROJECT"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ Both clusters connected successfully!"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📝 Add these aliases to your ~/.bashrc or ~/.zshrc:"
echo ""
echo "alias blue='kubectl --context=gke_${GCP_PROJECT}_${REGION}_${BLUE_CLUSTER}'"
echo "alias red='kubectl --context=gke_${GCP_PROJECT}_${REGION}_${RED_CLUSTER}'"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🎯 Quick Commands:"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "  blue get nodes          # Check Blue Team nodes"
echo "  red get nodes           # Check Red Team nodes"
echo "  blue get pods -A        # List all Blue Team pods"
echo "  red get pods -A         # List all Red Team pods"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "⚔️  The battleground is ready. Choose your weapon, commander."
echo "═══════════════════════════════════════════════════════════════════════════════"
