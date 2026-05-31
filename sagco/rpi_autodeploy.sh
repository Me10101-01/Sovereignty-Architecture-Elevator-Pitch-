#!/usr/bin/env bash
# SAGCO Raspberry Pi Autodeploy Agent
# Runs on the Pi. Polls the remote for new commits on the SAGCO branch,
# pulls, re-crawls the workspace, and restarts any running SAGCO VM process.
#
# Usage (on Pi):
#   chmod +x rpi_autodeploy.sh
#   ./rpi_autodeploy.sh [--branch <branch>] [--interval <seconds>] [--once]
#
# Install as a systemd service: see sagco-rpi.service below.

set -euo pipefail

# ── defaults ──────────────────────────────────────────────────────────────
BRANCH="${SAGCO_BRANCH:-main}"
REPO_DIR="${SAGCO_REPO_DIR:-$HOME/sagco-workspace}"
REPO_URL="${SAGCO_REPO_URL:-}"
POLL_INTERVAL="${SAGCO_POLL_INTERVAL:-60}"
PYTHON="${SAGCO_PYTHON:-python3}"
LOG_FILE="${SAGCO_LOG:-$REPO_DIR/sagco-deploy.log}"
RUN_ONCE=false
SAGCO_CMD="sagco"

# ── arg parse ─────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case $1 in
    --branch)    BRANCH="$2";        shift 2 ;;
    --interval)  POLL_INTERVAL="$2"; shift 2 ;;
    --once)      RUN_ONCE=true;      shift   ;;
    --repo)      REPO_URL="$2";      shift 2 ;;
    --dir)       REPO_DIR="$2";      shift 2 ;;
    *) echo "unknown arg: $1" >&2;   shift   ;;
  esac
done

# ── log helper ────────────────────────────────────────────────────────────
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"; }

# ── environment fingerprint ───────────────────────────────────────────────
detect_rpi() {
  if [[ -f /proc/cpuinfo ]] && grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "rpi"
  elif [[ "$(uname -m)" == "aarch64" || "$(uname -m)" == "armv7l" ]]; then
    echo "arm"
  else
    echo "generic"
  fi
}

PLATFORM=$(detect_rpi)
log "Platform detected: $PLATFORM"

# ── initial clone / pull ──────────────────────────────────────────────────
bootstrap_repo() {
  if [[ -d "$REPO_DIR/.git" ]]; then
    log "Repo exists at $REPO_DIR — fetching"
    git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet
  elif [[ -n "$REPO_URL" ]]; then
    log "Cloning $REPO_URL → $REPO_DIR"
    git clone --depth=1 --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
  else
    log "ERROR: SAGCO_REPO_URL not set and no repo at $REPO_DIR"
    exit 1
  fi
}

# ── get current and remote SHA ────────────────────────────────────────────
local_sha()  { git -C "$REPO_DIR" rev-parse HEAD 2>/dev/null || echo ""; }
remote_sha() { git -C "$REPO_DIR" rev-parse "origin/$BRANCH" 2>/dev/null || echo ""; }

# ── pull & deploy ─────────────────────────────────────────────────────────
deploy() {
  local prev="$1"
  log "New commit detected — deploying"

  git -C "$REPO_DIR" reset --hard "origin/$BRANCH" --quiet
  git -C "$REPO_DIR" clean -fd --quiet

  local new_sha
  new_sha=$(local_sha)
  log "Updated: $prev → $new_sha"

  # install/update Python deps if requirements file exists
  local req="$REPO_DIR/requirements.sovereignty.txt"
  if [[ -f "$req" ]]; then
    log "Installing Python deps from $req"
    "$PYTHON" -m pip install -q -r "$req" || true
  fi

  # run SAGCO pipeline crawl over workspace
  log "Running SAGCO stepper crawl"
  "$PYTHON" -m sagco.crawler "$REPO_DIR" 3 2>&1 | tee -a "$LOG_FILE" || true

  # emit deploy token via SAGCO VM
  log "Emitting deploy token"
  "$PYTHON" - <<EOF 2>&1 | tee -a "$LOG_FILE" || true
import sys, json
sys.path.insert(0, "$REPO_DIR")
from sagco import VM
vm = VM("$REPO_DIR")
procs = vm.execute("sagco deploy --target=rpi --branch=$BRANCH --sha=$new_sha")
for p in procs:
    print(json.dumps({"pid": p.pid, "status": p.status}))
EOF

  # restart any running sagco-vm systemd service
  if systemctl is-active --quiet sagco-vm 2>/dev/null; then
    log "Restarting sagco-vm service"
    sudo systemctl restart sagco-vm
  fi

  log "Deploy complete: $new_sha"
}

# ── main loop ─────────────────────────────────────────────────────────────
mkdir -p "$REPO_DIR" "$(dirname "$LOG_FILE")"
bootstrap_repo

log "SAGCO autodeploy agent started (branch=$BRANCH, interval=${POLL_INTERVAL}s)"

while true; do
  git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet 2>/dev/null || {
    log "WARN: fetch failed — network issue? retrying next cycle"
  }

  LOCAL=$(local_sha)
  REMOTE=$(remote_sha)

  if [[ -n "$REMOTE" && "$LOCAL" != "$REMOTE" ]]; then
    deploy "$LOCAL"
  fi

  "$RUN_ONCE" && { log "Run-once mode: exiting"; exit 0; }

  sleep "$POLL_INTERVAL"
done


# ────────────────────────────────────────────────────────────────────────────
# EMBEDDED SYSTEMD UNIT (copy to /etc/systemd/system/sagco-rpi.service)
# ────────────────────────────────────────────────────────────────────────────
# [Unit]
# Description=SAGCO Raspberry Pi Autodeploy Agent
# After=network-online.target
# Wants=network-online.target
#
# [Service]
# Type=simple
# User=pi
# WorkingDirectory=/home/pi
# EnvironmentFile=-/home/pi/.sagco.env
# ExecStart=/home/pi/sagco-workspace/sagco/rpi_autodeploy.sh
# Restart=on-failure
# RestartSec=30
# StandardOutput=journal
# StandardError=journal
#
# [Install]
# WantedBy=multi-user.target
