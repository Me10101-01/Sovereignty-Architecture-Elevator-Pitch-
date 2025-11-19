#!/bin/bash
###############################################################################
# Council War Room Setup Script
# Purpose: Initialize the war room development environment
###############################################################################

set -e

echo "🧠 Initializing Council War Room..."
echo ""

# Install additional tools
echo "📦 Installing additional tools..."
npm install -g @devcontainers/cli
pip3 install -q pyyaml requests

# Install git-crypt for secrets management
if ! command -v git-crypt &> /dev/null; then
    echo "🔐 Installing git-crypt..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq git-crypt
fi

# Setup git configuration
echo "🔧 Configuring git..."
git config --global core.editor "code --wait"
git config --global pull.rebase false

# Create council vault directory if it doesn't exist
echo "📁 Setting up Council Vault structure..."
mkdir -p /workspaces/council-vault/{threat-models,playbooks,intel,archives}

# Initialize threat vault index if it doesn't exist
if [ ! -f /workspaces/council-vault/README.md ]; then
    cat > /workspaces/council-vault/README.md << 'EOF'
# Council Vault - Threat Intelligence Repository

## Structure

- `threat-models/` - Active threat assessments and models
- `playbooks/` - Response playbooks and procedures
- `intel/` - Gathered intelligence and reconnaissance data
- `archives/` - Historical records and completed assessments

## Tagging Convention

Use these tags for proper graph linking:
- `#threat-model-2025` - Current year threat models
- `#active-threat` - Ongoing threat assessment
- `#response-playbook` - Incident response procedures
- `#recon-data` - Reconnaissance findings
- `#legion-intel` - Legion-specific intelligence

## Access Control

This vault contains sensitive operational data.
- All changes are logged via git
- Auto-commit enabled via Obsidian Git plugin
- GPG encryption via git-crypt for sensitive files
EOF
fi

echo ""
echo "✅ Council War Room setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Run 'bash scripts/lockdown.sh' to secure the environment"
echo "   2. Initialize git-crypt: git crypt init"
echo "   3. Configure your GPG key for encryption"
echo "   4. Open /workspaces/council-vault in Obsidian"
echo ""
echo "🛡️  War room ready. Proceed with caution."
