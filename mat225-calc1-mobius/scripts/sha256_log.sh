#!/usr/bin/env bash
# sha256_log.sh — Evidence chain hasher
# Usage: ./sha256_log.sh "answer string"
# Appends SHA-256 + timestamp to evidence/submissions.log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/../evidence/submissions.log"

if [ $# -lt 1 ]; then
    echo "Usage: $0 \"answer string\""
    echo "Hashes the answer and logs to evidence/submissions.log"
    exit 1
fi

ANSWER="$*"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HASH=$(echo -n "$ANSWER" | sha256sum | cut -d' ' -f1)

ENTRY="$TS  SHA256=$HASH  answer=$(echo "$ANSWER" | head -c 120)"
echo "$ENTRY" | tee -a "$LOG_FILE"
echo "Logged to: $LOG_FILE"
