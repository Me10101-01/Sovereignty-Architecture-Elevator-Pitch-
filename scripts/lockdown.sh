#!/bin/bash
###############################################################################
# Legion Node Lockdown Script
# Purpose: Harden legion nodes with proper file permissions and encryption
# Usage: ./scripts/lockdown.sh
###############################################################################

set -euo pipefail

echo "🔒 Legion lockdown engaged..."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running with appropriate permissions
if [[ $EUID -eq 0 ]]; then 
   echo -e "${RED}⚠️  Do not run this script as root. Run as the legion user.${NC}" 
   exit 1
fi

echo "📋 Step 1: Securing configuration files..."
# Find and secure all .conf files (read/write for user only)
if find . -name "*.conf" -type f 2>/dev/null | grep -q .; then
    find . -name "*.conf" -type f -exec chmod 600 {} \;
    echo -e "${GREEN}✓${NC} Configuration files secured (600)"
else
    echo -e "${YELLOW}ℹ${NC} No .conf files found"
fi

echo ""
echo "🔑 Step 2: Securing key files..."
# Find and secure all files with 'key' in the name (read-only for user)
if find . -name "*key*" -type f 2>/dev/null | grep -q .; then
    find . -name "*key*" -type f -exec chmod 400 {} \;
    echo -e "${GREEN}✓${NC} Key files secured (400)"
else
    echo -e "${YELLOW}ℹ${NC} No key files found"
fi

echo ""
echo "🔐 Step 3: Checking git-crypt availability..."
if command -v git-crypt &> /dev/null; then
    echo -e "${GREEN}✓${NC} git-crypt is installed"
    
    # Check if git-crypt is already initialized
    if git-crypt status &>/dev/null; then
        echo -e "${GREEN}✓${NC} git-crypt already initialized"
    else
        echo -e "${YELLOW}⚠${NC}  git-crypt not initialized. Initialize with:"
        echo "   git crypt init"
        echo "   git crypt add-gpg-user <your-gpg-key-id>"
    fi
else
    echo -e "${YELLOW}⚠${NC}  git-crypt not installed. Install with:"
    echo "   # Debian/Ubuntu"
    echo "   sudo apt-get install git-crypt"
    echo "   # macOS"
    echo "   brew install git-crypt"
    echo "   # Arch Linux"
    echo "   sudo pacman -S git-crypt"
fi

echo ""
echo "🛡️  Step 4: Securing environment files..."
# Secure .env files if they exist
if ls .env* 2>/dev/null | grep -q .; then
    chmod 600 .env* 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Environment files secured (600)"
else
    echo -e "${YELLOW}ℹ${NC} No .env files found"
fi

echo ""
echo "📝 Step 5: Checking .gitignore for sensitive patterns..."
# Ensure sensitive files are in .gitignore
SENSITIVE_PATTERNS=(
    "*.key"
    "*.pem"
    "*.p12"
    "*.pfx"
    ".env"
    ".env.*"
    "secrets/"
    "*.secret"
    "*_rsa"
    "*_dsa"
    "*_ecdsa"
    "*_ed25519"
)

GITIGNORE_FILE=".gitignore"
MISSING_PATTERNS=()

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if ! grep -q "^${pattern}$" "$GITIGNORE_FILE" 2>/dev/null; then
        MISSING_PATTERNS+=("$pattern")
    fi
done

if [ ${#MISSING_PATTERNS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All sensitive patterns in .gitignore"
else
    echo -e "${YELLOW}⚠${NC}  Missing patterns in .gitignore:"
    for pattern in "${MISSING_PATTERNS[@]}"; do
        echo "   - $pattern"
    done
    echo ""
    echo "   Add them with: echo '<pattern>' >> .gitignore"
fi

echo ""
echo "🔍 Step 6: Scanning for accidentally committed secrets..."
# Check for common secret patterns in tracked files
SECRET_FOUND=false

if git rev-parse --git-dir > /dev/null 2>&1; then
    # Check for private keys
    if git ls-files | xargs grep -l "BEGIN.*PRIVATE KEY" 2>/dev/null | head -5; then
        echo -e "${RED}⚠️  WARNING: Private keys found in tracked files!${NC}"
        SECRET_FOUND=true
    fi
    
    # Check for AWS keys
    if git ls-files | xargs grep -E "AKIA[0-9A-Z]{16}" 2>/dev/null | head -5; then
        echo -e "${RED}⚠️  WARNING: Possible AWS keys found in tracked files!${NC}"
        SECRET_FOUND=true
    fi
    
    if [ "$SECRET_FOUND" = false ]; then
        echo -e "${GREEN}✓${NC} No obvious secrets found in tracked files"
    else
        echo ""
        echo -e "${RED}ACTION REQUIRED: Remove secrets from git history${NC}"
        echo "   Use: git filter-branch or BFG Repo-Cleaner"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Legion lockdown complete${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🔒 Secrets encrypted. Only the worthy can read."
echo ""
echo "📚 Next steps:"
echo "   1. Review file permissions: ls -la"
echo "   2. Initialize git-crypt if needed"
echo "   3. Add GPG key: git crypt add-gpg-user <key-id>"
echo "   4. Commit .gitattributes if using git-crypt"
echo ""
echo "🛡️  Stay vigilant. Trust no one. Verify everything."
