#!/bin/bash
# SovereignPRManager Installation Script
# Autonomous PR Review, Validation, and Merge Orchestration

set -e

echo "🚀 SovereignPRManager Installation"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo -e "${GREEN}✓ Python $python_version found${NC}"
else
    echo -e "${RED}✗ Python $required_version or higher required (found $python_version)${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating .env file...${NC}"
    cat > .env << 'EOF'
# SovereignPRManager Environment Configuration

# Required: GitHub Personal Access Token with 'repo' scope
GITHUB_TOKEN=

# Required: Repository to monitor (owner/repo format)
GITHUB_REPO=Me10101-01/Sovereignty-Architecture-Elevator-Pitch-

# Required for AI Reviews: At least one API key needed
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Optional: Discord webhook for notifications
DISCORD_WEBHOOK_URL=

# Optional: NATS server URL
NATS_URL=nats://localhost:4222

# Optional: Elasticsearch URL for audit logging
ELASTICSEARCH_URL=http://localhost:9200

# Optional: Path to Technical Declaration document
DECLARATION_PATH=

# Optional: Signing key for provenance (auto-generated if not set)
SIGNING_KEY=
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env file and add your API keys${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
python3 -c "from pr_monitor import PRMonitor; print('✓ PRMonitor')"
python3 -c "from legion_reviewer import LegionReviewer; print('✓ LegionReviewer')"
python3 -c "from conflict_detector import ConflictDetector; print('✓ ConflictDetector')"
python3 -c "from synthesis_engine import MergeDecisionEngine; print('✓ MergeDecisionEngine')"
python3 -c "from auto_merger import AutoMerger; print('✓ AutoMerger')"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ SovereignPRManager installed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Edit .env file with your API keys"
echo "2. Run a dry-run test: python process_existing_prs.py --dry-run --limit 1"
echo "3. Start continuous monitoring: python -m pr_monitor"

echo -e "\n${YELLOW}For Kubernetes deployment:${NC}"
echo "kubectl apply -f k8s/"

echo -e "\n🏛️ Zero-button operation awaits!"
