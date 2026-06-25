#!/usr/bin/env bash
# verify.sh — Verify GPG clearsigned files
#
# Usage: ./gpg/verify.sh <file.gpg>
#   or:  ./gpg/verify.sh   (verifies all .gpg files in cwd)

set -euo pipefail

LOG_DIR="logs"
VERIFY_LOG="${LOG_DIR}/gpg_verify.log"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

sha256_file() {
    if command -v sha256sum &>/dev/null; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

verify_file() {
    local file="$1"
    [[ -f "$file" ]] || { echo "  NOT FOUND: $file"; return 1; }

    local hash
    hash=$(sha256_file "$file")

    if gpg --verify "$file" 2>/dev/null; then
        local verdict="PROVEN"
        echo "  ✓ PROVEN   $file  sha256=$hash"
    else
        local verdict="FAILED_COMPUTE"
        echo "  ✗ FAILED   $file  sha256=$hash"
    fi

    mkdir -p "$LOG_DIR"
    printf '{"ts":"%s","file":"%s","sha256":"%s","verdict":"%s"}\n' \
        "$(ts)" "$file" "$hash" "$verdict" >> "$VERIFY_LOG"
}

if [[ $# -ge 1 ]]; then
    for f in "$@"; do
        verify_file "$f"
    done
else
    PASS=0 FAIL=0
    for f in *.gpg; do
        [[ -f "$f" ]] || continue
        if verify_file "$f"; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
    done
    echo
    echo "  Verified: PASS=$PASS  FAIL=$FAIL"
    [[ $FAIL -eq 0 ]] || exit 1
fi
