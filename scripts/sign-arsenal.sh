#!/bin/bash
# Script to sign and timestamp StrategicKhaos Arsenal Analysis documentation
# Version: 1.0
# Date: December 7, 2025

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "StrategicKhaos Arsenal Analysis Signing"
echo "=================================================="
echo ""

# Documents to sign
DOCS=(
    "ARSENAL_ANALYSIS.md"
    "INVENTION_REGISTRY.md"
    "ZERO_VENDOR_LOCKIN.md"
    "COGNITIVE_ARCHITECTURE.md"
    "BLOOMS_TAXONOMY_FRAMEWORK.md"
)

# Check if GPG is available
if ! command -v gpg &> /dev/null; then
    echo -e "${RED}✗ ERROR: gpg not found${NC}"
    echo "Install with: apt-get install gnupg (Debian/Ubuntu) or brew install gnupg (macOS)"
    exit 1
fi

# Check if ots is available for timestamping
OTS_AVAILABLE=false
if command -v ots &> /dev/null; then
    OTS_AVAILABLE=true
    echo -e "${GREEN}✓ OpenTimestamps client found${NC}"
else
    echo -e "${YELLOW}⚠ OpenTimestamps client not found (optional)${NC}"
    echo "Install with: pip install opentimestamps-client"
fi

echo ""
echo "GPG Signing"
echo "-----------"

# List available GPG keys
echo "Available GPG keys:"
gpg --list-secret-keys --keyid-format LONG

echo ""
read -p "Enter GPG key ID to use for signing (or press Enter to skip): " KEY_ID

if [[ -z "$KEY_ID" ]]; then
    echo -e "${YELLOW}⚠ Skipping GPG signing${NC}"
else
    for doc in "${DOCS[@]}"; do
        if [[ -f "$doc" ]]; then
            echo -n "Signing $doc... "
            if gpg --detach-sign --armor --local-user "$KEY_ID" "$doc" 2>/dev/null; then
                echo -e "${GREEN}✓ Done${NC}"
            else
                echo -e "${RED}✗ Failed${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ Skipping $doc (file not found)${NC}"
        fi
    done
fi

echo ""
echo "OpenTimestamp Stamping"
echo "----------------------"

if [[ "$OTS_AVAILABLE" = true ]]; then
    read -p "Timestamp documents with OpenTimestamps? (y/n): " TIMESTAMP
    
    if [[ "$TIMESTAMP" =~ ^[Yy]$ ]]; then
        for doc in "${DOCS[@]}"; do
            if [[ -f "$doc" ]]; then
                echo -n "Timestamping $doc... "
                if ots stamp "$doc" 2>/dev/null; then
                    echo -e "${GREEN}✓ Done${NC}"
                else
                    echo -e "${RED}✗ Failed${NC}"
                fi
            fi
        done
        
        echo ""
        echo -e "${YELLOW}Note: OpenTimestamps require Bitcoin confirmations.${NC}"
        echo "Verify after ~1 hour with: ots verify <file>.ots"
    else
        echo -e "${YELLOW}⚠ Skipping OpenTimestamps${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipping OpenTimestamps (client not available)${NC}"
fi

echo ""
echo "Hash Generation"
echo "---------------"

echo "Generating SHA256 hashes for all documents..."
> HASHES.txt

for doc in "${DOCS[@]}"; do
    if [[ -f "$doc" ]]; then
        hash=$(sha256sum "$doc" | awk '{print $1}')
        echo "$hash  $doc" >> HASHES.txt
        echo "  $doc: $hash"
    fi
done

echo ""
echo -e "${GREEN}✓ Hashes saved to HASHES.txt${NC}"

echo ""
echo "=================================================="
echo "Signing Complete"
echo "=================================================="
echo ""
echo "Files generated:"
if [[ -n "$KEY_ID" ]]; then
    echo "  - *.sig (GPG signatures)"
fi
if [[ "$OTS_AVAILABLE" = true ]] && [[ "${TIMESTAMP:-n}" =~ ^[Yy]$ ]]; then
    echo "  - *.ots (OpenTimestamp proofs)"
fi
echo "  - HASHES.txt (SHA256 checksums)"
echo ""
echo "Next steps:"
echo "  1. Run ./scripts/verify-arsenal.sh to validate signatures"
echo "  2. Commit signed files to repository"
echo "  3. Publish HASHES.txt for public verification"
echo ""
