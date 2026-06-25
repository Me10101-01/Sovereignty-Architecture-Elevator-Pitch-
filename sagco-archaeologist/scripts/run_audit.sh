#!/usr/bin/env bash
# sagco-archaeologist: run full 6-agent pipeline on an artifact
#
# Usage:
#   ./scripts/run_audit.sh <artifact_path> [repo_root] [logs_dir] [out_dir]
#
# Example:
#   ./scripts/run_audit.sh sagco-audit/src/invocation_logger.py . logs reports

set -euo pipefail

ARTIFACT="${1:-sagco-audit/src/invocation_logger.py}"
REPO_ROOT="${2:-.}"
LOGS_DIR="${3:-logs}"
OUT_DIR="${4:-reports}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ARCH_ROOT="$( dirname "$SCRIPT_DIR" )"

python3 - <<EOF
import sys
sys.path.insert(0, "$ARCH_ROOT")
from runner.archaeologist import audit

result = audit(
    artifact_path="$ARTIFACT",
    repo_root="$REPO_ROOT",
    logs_dir="$LOGS_DIR",
    out_dir="$OUT_DIR",
    verbose=True,
)
print()
print(f"  AGGREGATE VERDICT : {result['aggregate_verdict']}")
print(f"  MANIFEST          : {result['manifest_path']}")
print(f"  SHA-256           : {result['manifest_sha256']}")
EOF
