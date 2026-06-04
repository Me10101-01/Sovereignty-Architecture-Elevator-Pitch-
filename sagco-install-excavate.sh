#!/data/data/com.termux/files/usr/bin/bash
# Deploy sagco-excavate into the live Rust workspace and compile it.
# Run from ~/Sovereignty-Architecture-Elevator-Pitch- after git pull.
set -euo pipefail

WORKSPACE="${HOME}/downloads/sagco_rust_command_compiler"
BIN_DIR="${WORKSPACE}/crates/sagco-core/src/bin"
SRC="$(dirname "$0")/rust/sagco-core/bin/sagco-excavate.rs"
STAMP="$(date -u +%Y%m%d_%H%M%S)"

echo "SAGCO INSTALL EXCAVATE"
echo "STAMP=${STAMP}"
echo "WORKSPACE=${WORKSPACE}"

if [[ ! -d "${WORKSPACE}" ]]; then
  echo "ERROR: workspace not found at ${WORKSPACE}"
  exit 1
fi

if [[ ! -d "${BIN_DIR}" ]]; then
  echo "ERROR: bin dir not found at ${BIN_DIR}"
  echo "Expected: ${WORKSPACE}/crates/sagco-core/src/bin/"
  exit 1
fi

# Copy source
cp "${SRC}" "${BIN_DIR}/sagco-excavate.rs"
echo "COPIED: ${BIN_DIR}/sagco-excavate.rs"

# Compile only the new binary (fast, no full rebuild)
cd "${WORKSPACE}"
echo "BUILDING..."
cargo build --bin sagco-excavate 2>&1 | tail -5

# Install to ~/bin
cp target/debug/sagco-excavate "${HOME}/bin/sagco-excavate"
chmod +x "${HOME}/bin/sagco-excavate"
echo "INSTALLED: ~/bin/sagco-excavate"

# Smoke test
echo ""
echo "=== SMOKE TEST ==="
"${HOME}/bin/sagco-excavate" "${HOME}/sagco_reports" 2>&1 | head -20

echo ""
echo "STATUS=SAGCO_EXCAVATE_INSTALLED"
echo ""
echo "Run: sagco-excavate \$HOME"
echo "Run: sagco-excavate ~/sagco_reports"
