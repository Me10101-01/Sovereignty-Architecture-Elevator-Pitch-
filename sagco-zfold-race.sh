#!/data/data/com.termux/files/usr/bin/bash
# SAGCO ZFold Race Tick — run from anywhere, writes to the real ledger
# Usage: sagco-zfold-race.sh [event_name]
set -euo pipefail

STAMP="$(date -u +%Y%m%d_%H%M%S)"
DEVICE="$(cat ~/.sagco_device 2>/dev/null || echo zfold)"
EVENT="${1:-sagco_race_tick}"
RACE_LOG="${HOME}/sagco_race/race_log.csv"
RUST_SRC="${HOME}/downloads/sagco_rust_command_compiler"

mkdir -p "${HOME}/sagco_race"

# Seed headers if new file
if [[ ! -f "${RACE_LOG}" ]]; then
  echo "TICK_ID,DEVICE,EVENT,TIMESTAMP,STATUS" > "${RACE_LOG}"
fi

# Write tick
TICK_N=$(wc -l < "${RACE_LOG}")
echo "${TICK_N},${DEVICE},${EVENT},${STAMP},SAGCO_RACE_TICK" >> "${RACE_LOG}"
echo "TICK=${TICK_N} EVENT=${EVENT} STAMP=${STAMP}"

# Sync tick into the Rust workspace data dir so sagco-core resolve can read it
RUST_DATA="${RUST_SRC}/data"
mkdir -p "${RUST_DATA}"
cp "${RACE_LOG}" "${RUST_DATA}/ledger.csv"

# Also keep a proofs symlink
if [[ ! -L "${RUST_SRC}/proofs/race_log.csv" ]]; then
  mkdir -p "${RUST_SRC}/proofs"
  ln -sf "${RACE_LOG}" "${RUST_SRC}/proofs/race_log.csv" 2>/dev/null || true
fi

# Run resolve if the binary is built
CORE_BIN="${RUST_SRC}/target/debug/sagco-core"
if [[ -x "${CORE_BIN}" ]]; then
  echo "--- RUNNING sagco-core resolve ---"
  cd "${RUST_SRC}"
  "${CORE_BIN}" resolve 2>&1 || echo "STATUS=SAGCO_CORE_RESOLVE_FAIL (binary ran but errored)"
fi

echo "STATUS=SAGCO_RACE_TICK_COMPLETE"
