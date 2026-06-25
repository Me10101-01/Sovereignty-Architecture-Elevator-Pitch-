#!/usr/bin/env bash
# clearsign-athena.sh — GPG clearsign for SAGCO provenance
#
# Usage: ./gpg/clearsign-athena.sh <file>
#   or:  ./gpg/clearsign-athena.sh   (auto-signs all unsigned .md and .yaml in cwd)
#
# Closes: ML-AUDIT-002 (AB-GPG-UNSIGNED-001)
# Output: <file>.gpg  (armored clearsign block)
#
# Requirements: gpg2, SAGCO_GPG_KEY env var or interactive key selection

set -euo pipefail

# -- Config -------------------------------------------------------------------

SAGCO_KEY="${SAGCO_GPG_KEY:-}"           # set this env var to your key fingerprint
LOG_DIR="logs"
RECEIPT_LOG="${LOG_DIR}/gpg_receipts.log"

# -- Helpers ------------------------------------------------------------------

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

sha256_file() {
    if command -v sha256sum &>/dev/null; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

log_receipt() {
    local file="$1" sig="$2" hash="$3" verdict="$4"
    mkdir -p "$LOG_DIR"
    printf '{"ts":"%s","file":"%s","sig":"%s","sha256":"%s","verdict":"%s"}\n' \
        "$(ts)" "$file" "$sig" "$hash" "$verdict" >> "$RECEIPT_LOG"
}

select_key() {
    if [[ -n "$SAGCO_KEY" ]]; then
        echo "$SAGCO_KEY"
        return
    fi
    # List secret keys and pick the first one
    local key
    key=$(gpg --list-secret-keys --with-colons 2>/dev/null \
          | awk -F: '$1=="fpr"{print $10; exit}')
    if [[ -z "$key" ]]; then
        echo >&2 "  ERROR: No GPG secret keys found. Generate one first:"
        echo >&2 "    gpg --full-generate-key"
        exit 1
    fi
    echo "$key"
}

sign_file() {
    local file="$1"
    local key="$2"
    local out="${file}.gpg"

    if [[ ! -f "$file" ]]; then
        echo "  SKIP: $file not found"
        return 1
    fi

    echo "  Signing: $file → $out"
    gpg --batch --yes \
        --local-user "$key" \
        --armor \
        --clearsign \
        --output "$out" \
        "$file"

    local hash
    hash=$(sha256_file "$out")
    log_receipt "$file" "$out" "$hash" "COMPUTED"
    echo "    SHA-256: $hash  [PROVEN]"
}

# -- Main ---------------------------------------------------------------------

KEY=$(select_key)
echo "  GPG Key: $KEY"
echo

if [[ $# -ge 1 ]]; then
    # Sign specific file(s)
    for f in "$@"; do
        sign_file "$f" "$KEY"
    done
else
    # Auto-sign all unsigned .md and .yaml files in current directory
    SIGNED=0
    SKIPPED=0
    for f in *.md *.yaml *.toml 2>/dev/null; do
        [[ -f "$f" ]] || continue
        if [[ -f "${f}.gpg" ]]; then
            echo "  SKIP (already signed): $f"
            SKIPPED=$((SKIPPED+1))
            continue
        fi
        sign_file "$f" "$KEY" && SIGNED=$((SIGNED+1))
    done
    echo
    echo "  Done: signed=$SIGNED  skipped=$SKIPPED"
fi

echo
echo "  Receipts → $RECEIPT_LOG"
