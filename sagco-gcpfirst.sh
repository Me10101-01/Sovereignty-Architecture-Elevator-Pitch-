#!/bin/sh
# sagco-gcpfirst — First GCP Heartbeat Deployment Guide
# The cloud brain is waiting. This script closes the gap.
#
# Current state: GCP project exists, billing exists, logs explorer exists.
#                Workloads=0. Logs=0. The skull is built. Neurons waiting.
#
# What this does:
#   1. Check device identity and gcloud availability
#   2. Guide auth if needed
#   3. Send the first attributed heartbeat to logs/sagco-fleet
#   4. Verify it appears in Logs Explorer
#   5. Queue for offline flush if gcloud unavailable
#
# Usage:
#   sagco-gcpfirst              → full guided first-heartbeat flow
#   sagco-gcpfirst check        → diagnose what's missing
#   sagco-gcpfirst send         → send heartbeat now (requires gcloud auth)
#   sagco-gcpfirst verify       → check if any logs exist in GCP
#   sagco-gcpfirst guide        → step-by-step manual instructions

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
QUEUE="$HOME/sagco_race/cloud_ping_queue.csv"
GCP_PROJECT="SAGCO-OSComputConsciousness"
GCP_LOG="sagco-fleet"

# ── check: diagnose readiness ─────────────────────────────────────────────────
cmd_check() {
    echo "FIRST GCP HEARTBEAT — Readiness Check"
    echo "========================================"
    echo "Stamp:  $STAMP"
    echo "Device: $DEV"
    echo ""

    # Check 1: device identity
    if [ "$DEV" = "unknown" ]; then
        echo "  ❌ Device identity: unknown"
        echo "     Fix: echo zfold > ~/.sagco_device"
        echo "          echo hp    > ~/.sagco_device"
        echo "          echo ish   > ~/.sagco_device"
    else
        echo "  ✅ Device identity: $DEV"
    fi

    # Check 2: race log exists and has data
    if [ -f "$RACE_LOG" ] && [ "$(wc -l < "$RACE_LOG" 2>/dev/null || echo 0)" -gt 1 ]; then
        TICKS=$(( $(wc -l < "$RACE_LOG") - 1 ))
        echo "  ✅ Race log: $TICKS ticks"
    else
        echo "  ❌ Race log: empty or missing"
        echo "     Fix: sagco-race"
    fi

    # Check 3: unknown attribution
    UNK=$([ -f "$RACE_LOG" ] && grep -c ",unknown," "$RACE_LOG" 2>/dev/null || echo 0)
    if [ "$UNK" -eq 0 ]; then
        echo "  ✅ Attribution: clean (unknown=0)"
    else
        echo "  ⚠️  Attribution: $UNK unknown rows"
        echo "     Fix: sagco-boss-battle fix"
    fi

    # Check 4: gcloud
    if command -v gcloud >/dev/null 2>&1; then
        PROJ=$(gcloud config get-value project 2>/dev/null || echo "")
        if [ "$PROJ" = "$GCP_PROJECT" ]; then
            echo "  ✅ gcloud: installed, project=$GCP_PROJECT"
        else
            echo "  🟡 gcloud: installed but project not set"
            echo "     Fix: gcloud config set project $GCP_PROJECT"
        fi

        # Check auth
        AUTH=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
        if [ -n "$AUTH" ]; then
            echo "  ✅ gcloud auth: $AUTH"
        else
            echo "  ❌ gcloud auth: not authenticated"
            echo "     Fix: gcloud auth login"
        fi
    else
        echo "  ❌ gcloud: not installed on this node"
        echo "     Available options:"
        echo "       A) Run sagco-gcpfirst send on HP (where gcloud may be installed)"
        echo "       B) Run sagco-cloud-ping to queue, then flush on HP"
        echo "       C) Install gcloud: cloud.google.com/sdk/docs/install"
    fi

    # Check 5: cloud queue
    if [ -f "$QUEUE" ] && [ "$(wc -l < "$QUEUE" 2>/dev/null || echo 1)" -gt 1 ]; then
        Q_DEPTH=$(( $(wc -l < "$QUEUE") - 1 ))
        echo "  🟡 Cloud queue: $Q_DEPTH entries pending flush"
        echo "     Flush on HP: sagco-cloud-ping flush"
    else
        echo "  ⬜ Cloud queue: empty"
    fi

    echo ""
    echo "  Logs Explorer:"
    echo "  https://console.cloud.google.com/logs/query"
    echo "  Query: logName=\"projects/$GCP_PROJECT/logs/$GCP_LOG\""
}

# ── send: fire the first heartbeat ───────────────────────────────────────────
cmd_send() {
    echo "FIRST GCP HEARTBEAT — Sending"
    echo "================================"

    # Build payload
    TICKS=$([ -f "$RACE_LOG" ] && echo $(( $(wc -l < "$RACE_LOG" 2>/dev/null || echo 1) - 1 )) || echo 0)
    ARTS=$([ -f "$LEDGER" ] && echo $(( $(wc -l < "$LEDGER" 2>/dev/null || echo 1) - 1 )) || echo 0)
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    IPV4=$(ip -4 addr 2>/dev/null | awk '/inet /{print $2}' | head -1 || echo unknown)
    HOST=$(hostname 2>/dev/null || echo unknown)
    UNK=$([ -f "$RACE_LOG" ] && grep -c ",unknown," "$RACE_LOG" 2>/dev/null || echo 0)

    JSON="{\"device\":\"${DEV}\",\"event\":\"first_heartbeat\",\"timestamp\":\"${STAMP}\",\"race_ticks\":${TICKS},\"artifacts\":${ARTS},\"unknown\":${UNK},\"battery\":\"${BAT}\",\"ipv4\":\"${IPV4}\",\"hostname\":\"${HOST}\",\"gpg_key\":\"AE5519579584DEF5\",\"ssh_key\":\"SAGCO-OS PIPELINE\",\"status\":\"SAGCO_FLEET_HEARTBEAT\"}"

    echo "  Payload:"
    echo "  $JSON" | tr ',' '\n' | sed 's/^/    /'
    echo ""

    if command -v gcloud >/dev/null 2>&1; then
        # Set project if needed
        gcloud config set project "$GCP_PROJECT" >/dev/null 2>&1

        echo "  Sending to: projects/$GCP_PROJECT/logs/$GCP_LOG"
        gcloud logging write "$GCP_LOG" "$JSON" \
            --payload-type=json --severity=INFO --project="$GCP_PROJECT" \
            && {
                echo "  ✅ HEARTBEAT SENT"
                echo ""
                echo "  View in Logs Explorer:"
                echo "  https://console.cloud.google.com/logs/query"
                echo "  Filter: logName=\"projects/$GCP_PROJECT/logs/$GCP_LOG\""
                echo ""
                echo "  The cloud brain is no longer waiting."
                echo "  First neuron fired: $DEV → $STAMP"
            } || {
                echo "  ❌ Send failed — check auth: gcloud auth login"
                echo "  Queueing for HP flush..."
                [ -f "$QUEUE" ] || echo "timestamp,device,json_payload" > "$QUEUE"
                echo "${STAMP},${DEV},${JSON}" >> "$QUEUE"
                echo "  Queued. Flush on HP: sagco-cloud-ping flush"
            }
    else
        echo "  gcloud not available on $DEV"
        echo "  Queueing heartbeat for HP flush..."
        [ -f "$QUEUE" ] || echo "timestamp,device,json_payload" > "$QUEUE"
        echo "${STAMP},${DEV},${JSON}" >> "$QUEUE"
        echo "  ✅ Queued: $(basename "$QUEUE")"
        echo ""
        echo "  On HP SAGCO-OS, run:"
        echo "    sagco-cloud-ping flush"
        echo "  or:"
        echo "    sagco-gcpfirst send"
    fi

    # Write race tick
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_first_heartbeat,${PWD},${BAT},SAGCO_FIRST_HEARTBEAT" >> "$RACE_LOG"
    HASH=$(echo "${STAMP}sagco-gcpfirst${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-gcpfirst,${QUEUE},${HASH},SAGCO_FIRST_HEARTBEAT" >> "$LEDGER"
}

# ── verify: check if logs exist ───────────────────────────────────────────────
cmd_verify() {
    echo "GCP LOGS VERIFY"
    echo "================"

    if ! command -v gcloud >/dev/null 2>&1; then
        echo "  gcloud not available — check manually:"
        echo "  https://console.cloud.google.com/logs/query"
        echo "  Query: logName=\"projects/$GCP_PROJECT/logs/$GCP_LOG\""
        return
    fi

    echo "  Checking: projects/$GCP_PROJECT/logs/$GCP_LOG"
    COUNT=$(gcloud logging read "logName=\"projects/$GCP_PROJECT/logs/$GCP_LOG\"" \
        --limit=1 --project="$GCP_PROJECT" --format="value(timestamp)" 2>/dev/null | wc -l)

    if [ "$COUNT" -gt 0 ]; then
        echo "  ✅ Logs found — cloud brain is ALIVE"
        echo ""
        LAST=$(gcloud logging read "logName=\"projects/$GCP_PROJECT/logs/$GCP_LOG\"" \
            --limit=5 --project="$GCP_PROJECT" --format="table(timestamp,jsonPayload.device,jsonPayload.event)" \
            2>/dev/null)
        echo "$LAST"
    else
        echo "  ⬜ No logs yet — cloud brain is waiting"
        echo "  Run: sagco-gcpfirst send"
    fi
}

# ── guide: step-by-step manual instructions ───────────────────────────────────
cmd_guide() {
    cat << 'GUIDE'
FIRST GCP HEARTBEAT — Manual Guide
=====================================

The cloud brain has:  skull=built  neurons=waiting

Step 1: On HP SAGCO-OS (or any device with gcloud)
──────────────────────────────────────────────────

  a. Install gcloud if not present:
     https://cloud.google.com/sdk/docs/install

  b. Auth:
     gcloud auth login
     gcloud config set project SAGCO-OSComputConsciousness

  c. Send first heartbeat:
     sagco-gcpfirst send

     OR use sagco-cloud-ping:
     sagco-cloud-ping hp-sagco-os

Step 2: On Z Fold (no gcloud → queue)
──────────────────────────────────────────────────

  a. Run:
     sagco-cloud-ping zfold

  b. This writes to ~/sagco_race/cloud_ping_queue.csv

  c. On HP, flush the queue:
     sagco-cloud-ping flush

Step 3: On iSH / iPad (minimal)
──────────────────────────────────────────────────

  a. Run sagco-ish-heartbeat
  b. Git push from iSH to sync race_log
  c. HP sagco-daemon picks up the tick and ships it

Step 4: Verify in Logs Explorer
──────────────────────────────────────────────────

  URL: https://console.cloud.google.com/logs/query
  Project: SAGCO-OSComputConsciousness
  Query:
    logName="projects/SAGCO-OSComputConsciousness/logs/sagco-fleet"

  Expected first row:
    device: hp (or zfold)
    event: first_heartbeat (or fleet_heartbeat)
    timestamp: [today]
    status: SAGCO_FLEET_HEARTBEAT

Step 5: The moment it works
──────────────────────────────────────────────────

  Logs Found: 0
  ↓
  Logs Found: 1

  The cloud brain stops being a diagram.
  It becomes a living node in the fleet.

STATUS=SAGCO_FIRST_HEARTBEAT_GUIDE_COMPLETE
GUIDE
}

# ── full guided flow ──────────────────────────────────────────────────────────
cmd_full() {
    echo "SAGCO FIRST GCP HEARTBEAT"
    echo "=========================="
    echo "Google Cloud is waiting."
    echo "The skull is built. The neurons need a signal."
    echo ""
    cmd_check
    echo ""
    cmd_send
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-full}"

case "$CMD" in
    check)   cmd_check ;;
    send)    cmd_send ;;
    verify)  cmd_verify ;;
    guide)   cmd_guide ;;
    full|"") cmd_full ;;
    *)
        echo "Usage: sagco-gcpfirst [check|send|verify|guide]"
        echo ""
        echo "  check    diagnose what's needed for first heartbeat"
        echo "  send     fire first heartbeat to GCP now"
        echo "  verify   check if any logs exist in Logs Explorer"
        echo "  guide    step-by-step manual instructions"
        exit 1
        ;;
esac
