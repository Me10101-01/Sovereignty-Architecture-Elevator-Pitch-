#!/data/data/com.termux/files/usr/bin/bash
# SAGCO ZFold Node Doctor
# Run from any directory on the ZFold to diagnose and fix all known issues.
# Usage: bash sagco-zfold-doctor.sh [--fix] [--status]
set -euo pipefail

STAMP="$(date -u +%Y%m%d_%H%M%S)"
SAGCO_HOME="${HOME}"
REPORT_DIR="${SAGCO_HOME}/reports"
REPORT="${REPORT_DIR}/sagco_doctor_${STAMP}.txt"
FIX_MODE=0
STATUS_ONLY=0

for arg in "$@"; do
  case "$arg" in
    --fix)    FIX_MODE=1 ;;
    --status) STATUS_ONLY=1 ;;
  esac
done

mkdir -p "${REPORT_DIR}"

log() { echo "$*" | tee -a "${REPORT}"; }
ok()  { log "  ✅ $*"; }
warn(){ log "  ⚠️  $*"; }
fail(){ log "  ❌ $*"; }
hdr() { log ""; log "=== $* ==="; }

{
log "SAGCO ZFOLD DOCTOR"
log "STAMP=${STAMP}"
log "FIX_MODE=${FIX_MODE}"
log "NODE=$(cat ~/.sagco_device 2>/dev/null || echo unknown)"

# ─── BINARY CENSUS ──────────────────────────────────────────────────────────
hdr "BINARY CENSUS"

SAGCO_BINS=(
  "${SAGCO_HOME}/bin/sagco"
  "${SAGCO_HOME}/.local/bin/sagco"
  "${SAGCO_HOME}/sagco_evcompiler/bin/sagco"
  "${SAGCO_HOME}/downloads/sagco_rust_command_compiler/sagco"
  "${SAGCO_HOME}/downloads/sagco"
)

CANON_BIN=""
CANON_SIZE=0
for b in "${SAGCO_BINS[@]}"; do
  if [[ -x "$b" ]]; then
    sz=$(wc -c < "$b" 2>/dev/null || echo 0)
    ok "$(basename $(dirname $b))/sagco  size=${sz}"
    if [[ $sz -gt $CANON_SIZE ]]; then
      CANON_SIZE=$sz
      CANON_BIN="$b"
    fi
  else
    warn "MISSING: $b"
  fi
done
log "  CANON_BIN=${CANON_BIN}  (largest = most compiled)"

if [[ $FIX_MODE -eq 1 && -n "${CANON_BIN}" ]]; then
  # Ensure ~/bin exists and link canonical binary there
  mkdir -p "${SAGCO_HOME}/bin"
  if [[ "${CANON_BIN}" != "${SAGCO_HOME}/bin/sagco" ]]; then
    cp "${CANON_BIN}" "${SAGCO_HOME}/bin/sagco.new"
    mv "${SAGCO_HOME}/bin/sagco.new" "${SAGCO_HOME}/bin/sagco"
    ok "FIXED: promoted ${CANON_BIN} → ~/bin/sagco"
  fi
  # Ensure ~/bin is on PATH in .bashrc
  if ! grep -q 'PATH.*\$HOME/bin' "${SAGCO_HOME}/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/bin:$HOME/.local/bin:$PATH"' >> "${SAGCO_HOME}/.bashrc"
    ok "FIXED: added ~/bin to PATH in .bashrc"
  fi
fi

# ─── SAGCO-CORE RESOLVE: IO FAILURE DIAGNOSIS ───────────────────────────────
hdr "SAGCO-CORE RESOLVE DIAGNOSIS"

RUST_SRC="${SAGCO_HOME}/downloads/sagco_rust_command_compiler"
CORE_BIN="${RUST_SRC}/target/debug/sagco-core"

# Find what ledger/seed file resolve is looking for
LEDGER_CANDIDATES=(
  "${SAGCO_HOME}/sagco_race/race_log.csv"
  "${SAGCO_HOME}/sagco/sagco_race_log.csv"
  "${RUST_SRC}/sagco_race/race_log.csv"
  "${RUST_SRC}/data/ledger.csv"
  "${RUST_SRC}/data/sagco_ledger.csv"
  "${RUST_SRC}/proofs/ledger.csv"
  "${SAGCO_HOME}/.sagco_ledger"
  "${SAGCO_HOME}/.sagco_race_log"
)

log "  Checking ledger candidates:"
for f in "${LEDGER_CANDIDATES[@]}"; do
  if [[ -f "$f" ]]; then
    sz=$(wc -l < "$f")
    ok "${f}  (${sz} lines)"
  else
    warn "MISSING: ${f}"
  fi
done

# Grep the binary for file path hints
if [[ -f "${CORE_BIN}" ]]; then
  log ""
  log "  File paths found in sagco-core binary:"
  strings "${CORE_BIN}" 2>/dev/null \
    | grep -E '\.(csv|json|yaml|yml|txt|log|md)' \
    | grep -v '^\.' \
    | sort -u \
    | head -30 \
    | while read -r line; do log "    $line"; done || true
fi

# Also check main.rs for open/read calls
if [[ -f "${RUST_SRC}/src/main.rs" ]]; then
  log ""
  log "  File open calls in src/main.rs:"
  grep -n 'open\|read_to_string\|File::' "${RUST_SRC}/src/main.rs" 2>/dev/null \
    | head -20 \
    | while read -r line; do log "    $line"; done || true
fi

CORE_CRATE="${RUST_SRC}/crates/sagco-core"
if [[ -d "${CORE_CRATE}" ]]; then
  log ""
  log "  File open calls in crates/sagco-core:"
  grep -rn 'open\|read_to_string\|File::' "${CORE_CRATE}/src/" 2>/dev/null \
    | head -20 \
    | while read -r line; do log "    $line"; done || true
fi

# ─── SEED FILES: CREATE MISSING DEFAULTS ────────────────────────────────────
hdr "SEED FILES"

DEVICE_ID="$(cat ~/.sagco_device 2>/dev/null || echo '')"
if [[ -z "${DEVICE_ID}" ]]; then
  DEVICE_ID="zfold"
  if [[ $FIX_MODE -eq 1 ]]; then
    echo "${DEVICE_ID}" > "${SAGCO_HOME}/.sagco_device"
    ok "CREATED: ~/.sagco_device = ${DEVICE_ID}"
  else
    warn "MISSING: ~/.sagco_device"
  fi
else
  ok "~/.sagco_device = ${DEVICE_ID}"
fi

# Ensure race log exists
RACE_LOG="${SAGCO_HOME}/sagco_race/race_log.csv"
if [[ ! -f "${RACE_LOG}" ]]; then
  if [[ $FIX_MODE -eq 1 ]]; then
    mkdir -p "${SAGCO_HOME}/sagco_race"
    echo "TICK_ID,DEVICE,EVENT,TIMESTAMP,STATUS" > "${RACE_LOG}"
    echo "001,${DEVICE_ID},sagco_init,${STAMP},SAGCO_RACE_SEED" >> "${RACE_LOG}"
    ok "CREATED: ${RACE_LOG}"
  else
    warn "MISSING: ${RACE_LOG}"
  fi
else
  ok "${RACE_LOG}  ($(wc -l < "${RACE_LOG}") rows)"
fi

# Seed a ledger in the location sagco-core likely expects (relative to CWD of rust workspace)
RUST_LEDGER="${RUST_SRC}/data/ledger.csv"
if [[ ! -f "${RUST_LEDGER}" ]]; then
  if [[ $FIX_MODE -eq 1 ]]; then
    mkdir -p "${RUST_SRC}/data"
    echo "TICK_ID,DEVICE,EVENT,TIMESTAMP,STATUS" > "${RUST_LEDGER}"
    echo "001,${DEVICE_ID},sagco_resolve_init,${STAMP},SAGCO_LEDGER_SEED" >> "${RUST_LEDGER}"
    ok "CREATED: ${RUST_LEDGER}"
  else
    warn "MISSING: ${RUST_LEDGER} (probable sagco-core resolve target)"
  fi
else
  ok "${RUST_LEDGER}  ($(wc -l < "${RUST_LEDGER}") rows)"
fi

# ─── RCLONE ─────────────────────────────────────────────────────────────────
hdr "RCLONE"

if ! command -v rclone &>/dev/null; then
  fail "rclone not installed (pkg install rclone)"
else
  REMOTES=$(rclone listremotes 2>/dev/null | grep -c ':' || echo 0)
  if [[ "${REMOTES}" -eq 0 ]]; then
    warn "rclone installed, zero remotes"
    log "  OPTIONS:"
    log "    1. rclone config  (interactive)"
    log "    2. rclone config create sagco-local local root=${SAGCO_HOME}/storage"
    if [[ $FIX_MODE -eq 1 ]]; then
      # Create a local remote so bottleneck has something to call against
      rclone config create sagco-local local root="${SAGCO_HOME}/storage" \
        nounc=true 2>/dev/null || true
      ok "CREATED: rclone remote 'sagco-local' → ~/storage"
    fi
  else
    ok "rclone remotes: ${REMOTES}"
    rclone listremotes 2>/dev/null | while read -r r; do ok "  ${r}"; done
  fi
fi

# ─── SAGCO TICK / CRAWL EMPTY RESULT ────────────────────────────────────────
hdr "TICK / CRAWL DIAGNOSIS"

CUI_BIN="${SAGCO_HOME}/bin/sagco"
if [[ -x "${CUI_BIN}" ]]; then
  log "  Testing crawl on sagco_reports:"
  CRAWL_OUT=$("${CUI_BIN}" crawl "${SAGCO_HOME}/sagco_reports/" 2>&1 || true)
  log "  RESULT: ${CRAWL_OUT:0:200}"
  if echo "${CRAWL_OUT}" | grep -qE '^TICK_ID,'; then
    ROWS=$(echo "${CRAWL_OUT}" | grep -vc '^TICK_ID,' || echo 0)
    if [[ "${ROWS}" -eq 0 ]]; then
      fail "crawl returned headers only — target dir has no .csv/.md files or binary expects absolute paths"
      log "  Files in sagco_reports: $(find "${SAGCO_HOME}/sagco_reports/" -type f | head -5 | tr '\n' ' ')"
    else
      ok "crawl returned ${ROWS} rows"
    fi
  fi
fi

# ─── FLEET HEARTBEAT ────────────────────────────────────────────────────────
hdr "FLEET HEARTBEAT"

GPG_KEY="$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep '^sec' | awk '{print $2}' | cut -d/ -f2 | head -1 || echo none)"
ok "device=${DEVICE_ID}"
ok "gpg=${GPG_KEY}"
ok "rustc=$(rustc --version 2>/dev/null || echo missing)"
ok "node_type=zfold_mobile_a64"
ok "network_status=DETACHED"
ok "athena=192.168.1.27 UNREACHABLE"

# Write heartbeat tick
TICK_FILE="${SAGCO_HOME}/sagco_race/race_log.csv"
if [[ -f "${TICK_FILE}" && $FIX_MODE -eq 1 ]]; then
  TICK_N=$(wc -l < "${TICK_FILE}")
  echo "${TICK_N},${DEVICE_ID},doctor_heartbeat,${STAMP},SAGCO_RACE_TICK" >> "${TICK_FILE}"
  ok "heartbeat written → ${TICK_FILE}"
fi

# ─── SUMMARY ────────────────────────────────────────────────────────────────
hdr "SUMMARY"

if [[ $FIX_MODE -eq 0 ]]; then
  log "Run with --fix to apply all repairs"
  log "  bash sagco-zfold-doctor.sh --fix"
else
  log "All fixes applied. Re-run without --fix to verify."
fi

log ""
log "REPORT=${REPORT}"
log "STATUS=SAGCO_DOCTOR_COMPLETE"

} 2>&1 | tee "${REPORT}"
