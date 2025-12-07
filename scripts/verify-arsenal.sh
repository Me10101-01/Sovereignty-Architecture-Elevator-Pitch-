#!/bin/bash
# Verification script for StrategicKhaos Arsenal Analysis documentation
# Version: 1.0
# Date: December 7, 2025

set -uo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for results
PASSED=0
FAILED=0
WARNINGS=0

echo "=================================================="
echo "StrategicKhaos Arsenal Analysis Verification"
echo "=================================================="
echo ""

# Function to print status
print_status() {
    local status=$1
    local message=$2
    
    case $status in
        "PASS")
            echo -e "${GREEN}✓ PASS${NC} - $message"
            ((PASSED++))
            ;;
        "FAIL")
            echo -e "${RED}✗ FAIL${NC} - $message"
            ((FAILED++))
            ;;
        "WARN")
            echo -e "${YELLOW}⚠ WARN${NC} - $message"
            ((WARNINGS++))
            ;;
        "INFO")
            echo -e "ℹ INFO - $message"
            ;;
    esac
}

# Function to check file exists
check_file_exists() {
    local file=$1
    if [[ -f "$file" ]]; then
        print_status "PASS" "File exists: $file"
        return 0
    else
        print_status "FAIL" "File missing: $file"
        return 1
    fi
}

# Function to verify SHA256 hash
verify_hash() {
    local file=$1
    if [[ -f "$file" ]]; then
        local hash=$(sha256sum "$file" | awk '{print $1}')
        print_status "INFO" "SHA256 ($file): $hash"
        
        # Store hash for future verification
        echo "$hash  $file" >> .hashes.txt
    fi
}

# Function to verify GPG signature
verify_gpg_signature() {
    local file=$1
    local sig_file="${file}.sig"
    
    if [[ -f "$sig_file" ]]; then
        if gpg --verify "$sig_file" "$file" 2>/dev/null; then
            print_status "PASS" "GPG signature valid: $file"
        else
            print_status "FAIL" "GPG signature invalid: $file"
        fi
    else
        print_status "WARN" "GPG signature not found (not yet signed): $file"
    fi
}

# Function to verify OpenTimestamp
verify_opentimestamp() {
    local file=$1
    local ots_file="${file}.ots"
    
    if [[ -f "$ots_file" ]]; then
        if command -v ots &> /dev/null; then
            if ots verify "$ots_file" 2>/dev/null; then
                print_status "PASS" "OpenTimestamp verified: $file"
            else
                print_status "WARN" "OpenTimestamp pending confirmation: $file"
            fi
        else
            print_status "WARN" "ots command not found (install with: pip install opentimestamps-client)"
        fi
    else
        print_status "WARN" "OpenTimestamp not found (not yet timestamped): $file"
    fi
}

# Main verification
echo "1. Document Existence Check"
echo "----------------------------"

DOCS=(
    "ARSENAL_ANALYSIS.md"
    "INVENTION_REGISTRY.md"
    "ZERO_VENDOR_LOCKIN.md"
    "COGNITIVE_ARCHITECTURE.md"
    "BLOOMS_TAXONOMY_FRAMEWORK.md"
    "TRUST_DECLARATION.md"
    "NON_AGGRESSION_CLAUSE.md"
    "public-identifier-registry.md"
    "README.md"
)

for doc in "${DOCS[@]}"; do
    check_file_exists "$doc"
done

echo ""
echo "2. Document Integrity (SHA256 Hashes)"
echo "--------------------------------------"

# Clear previous hashes
> .hashes.txt

for doc in "${DOCS[@]}"; do
    if [[ -f "$doc" ]]; then
        verify_hash "$doc"
    fi
done

echo ""
echo "3. GPG Signature Verification"
echo "------------------------------"

for doc in "${DOCS[@]}"; do
    if [[ -f "$doc" ]]; then
        verify_gpg_signature "$doc"
    fi
done

echo ""
echo "4. OpenTimestamp Verification"
echo "------------------------------"

for doc in "${DOCS[@]}"; do
    if [[ -f "$doc" ]]; then
        verify_opentimestamp "$doc"
    fi
done

echo ""
echo "5. Content Validation"
echo "---------------------"

# Check ARSENAL_ANALYSIS.md references other documents
if grep -q "INVENTION_REGISTRY.md" ARSENAL_ANALYSIS.md && \
   grep -q "ZERO_VENDOR_LOCKIN.md" ARSENAL_ANALYSIS.md && \
   grep -q "COGNITIVE_ARCHITECTURE.md" ARSENAL_ANALYSIS.md && \
   grep -q "BLOOMS_TAXONOMY_FRAMEWORK.md" ARSENAL_ANALYSIS.md; then
    print_status "PASS" "ARSENAL_ANALYSIS.md properly references all documents"
else
    print_status "FAIL" "ARSENAL_ANALYSIS.md missing document references"
fi

# Check INVENTION_REGISTRY.md has all 33 inventions
invention_count=$(grep -c "^### [0-9]\+\." INVENTION_REGISTRY.md || echo 0)
if [[ $invention_count -eq 33 ]]; then
    print_status "PASS" "INVENTION_REGISTRY.md contains all 33 inventions"
else
    print_status "WARN" "INVENTION_REGISTRY.md has $invention_count inventions (expected 33)"
fi

# Check ZERO_VENDOR_LOCKIN.md has all 12 principles
principle_count=$(grep -c "^### [0-9]\+\." ZERO_VENDOR_LOCKIN.md || echo 0)
if [[ $principle_count -ge 12 ]]; then
    print_status "PASS" "ZERO_VENDOR_LOCKIN.md contains at least 12 principles"
else
    print_status "WARN" "ZERO_VENDOR_LOCKIN.md has $principle_count principles (expected ≥12)"
fi

# Check README.md references new documents
if grep -q "ARSENAL_ANALYSIS.md" README.md; then
    print_status "PASS" "README.md references arsenal analysis documents"
else
    print_status "FAIL" "README.md does not reference arsenal analysis"
fi

echo ""
echo "6. Metadata Validation"
echo "----------------------"

# Check for version numbers
for doc in "${DOCS[@]}"; do
    if [[ -f "$doc" ]] && grep -q "Version.*1\.0" "$doc"; then
        print_status "PASS" "Version metadata found: $doc"
    elif [[ -f "$doc" ]]; then
        print_status "WARN" "Version metadata missing or different: $doc"
    fi
done

# Check for dates
for doc in "${DOCS[@]}"; do
    if [[ -f "$doc" ]] && grep -q "December.*2025" "$doc"; then
        print_status "PASS" "Date metadata found: $doc"
    elif [[ -f "$doc" ]]; then
        print_status "WARN" "Date metadata missing or different: $doc"
    fi
done

echo ""
echo "=================================================="
echo "Verification Summary"
echo "=================================================="
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    if [[ $WARNINGS -gt 0 ]]; then
        echo -e "${YELLOW}⚠ $WARNINGS warnings (non-critical)${NC}"
        echo ""
        echo "To resolve warnings:"
        echo "  - Sign documents: gpg --detach-sign --armor <file>"
        echo "  - Timestamp documents: ots stamp <file>"
    fi
    exit 0
else
    echo -e "${RED}✗ $FAILED critical checks failed!${NC}"
    exit 1
fi
