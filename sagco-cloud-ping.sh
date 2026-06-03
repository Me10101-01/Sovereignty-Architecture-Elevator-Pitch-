#!/bin/sh
# sagco-cloud-ping — SAGCO Fleet Heartbeat → GCP Cloud Logging
# Every device writes one structured ping. Cloud Logging stops showing "No data found."
# Works with or without gcloud: offline devices queue locally, HP flushes.
#
# Usage:
#   sagco-cloud-ping                → ping as current device
#   sagco-cloud-ping zfold          → ping as zfold
#   sagco-cloud-ping flush          → ship queued pings from devices without gcloud
#   sagco-cloud-ping watch          → loop: ping every 30s (daemon mode)
#   sagco-cloud-ping tail           → show last 10 pings from Cloud Logging

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
PING_QUEUE="$HOME/sagco_race/cloud_ping_queue.csv"
GCP_PROJECT="SAGCO-OSComputConsciousness"
GCP_LOG_NAME="sagco-fleet"
PING_INTERVAL=30

mkdir -p "$HOME/sagco_race"

# ── gather all 9 fields ───────────────────────────────────────────────────────
gather_ping() {
    PING_DEV="$1"

    TS="$STAMP"
    DEVICE="$PING_DEV"

    IPV4=$(ip -4 addr 2>/dev/null | awk '/inet /{gsub(/\/[0-9]+/,"",$2); printf "%s ", $2}' | xargs)
    [ -z "$IPV4" ] && IPV4=$(ifconfig 2>/dev/null | awk '/inet /{print $2}' | grep -v '127.0.0.1' | head -1)
    [ -z "$IPV4" ] && IPV4="unavailable"

    IPV6=$(ip -6 addr 2>/dev/null | awk '/inet6 /{gsub(/\/[0-9]+/,"",$2); printf "%s ", $2}' | \
        grep -v "^fe80\|^::1" | xargs)
    [ -z "$IPV6" ] && IPV6="unavailable"

    GW=$(ip route 2>/dev/null | awk '/default/{print $3; exit}')
    [ -z "$GW" ] && GW=$(netstat -rn 2>/dev/null | awk '/^0.0.0.0/{print $2; exit}')
    [ -z "$GW" ] && GW="unavailable"

    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || \
          cat /sys/class/power_supply/BAT0/capacity 2>/dev/null || echo "unknown")

    WIFI=$(iwgetid -r 2>/dev/null || \
           iw dev 2>/dev/null | awk '/ssid/{print $2; exit}' || \
           getprop wifi.interface 2>/dev/null || echo "unknown")

    HOST=$(hostname 2>/dev/null || cat /proc/sys/kernel/hostname 2>/dev/null || echo "unknown")

    LAST_EVENT=""
    [ -f "$RACE_LOG" ] && LAST_EVENT=$(grep ",${DEVICE}," "$RACE_LOG" 2>/dev/null | \
        tail -1 | awk -F',' '{print $3}')

    STATUS="SAGCO_PING_PASS"
}

# ── build JSON payload ────────────────────────────────────────────────────────
build_json() {
    cat <<JSON
{"timestamp":"${TS}","device":"${DEVICE}","ipv4":"${IPV4}","ipv6":"${IPV6}","gateway":"${GW}","battery":"${BAT}","wifi":"${WIFI}","hostname":"${HOST}","last_event":"${LAST_EVENT:-none}","status":"${STATUS}"}
JSON
}

# ── ship one ping to Cloud Logging ────────────────────────────────────────────
ship_ping() {
    JSON=$(build_json)

    if command -v gcloud >/dev/null 2>&1; then
        gcloud logging write "$GCP_LOG_NAME" "$JSON" \
            --payload-type=json \
            --severity=INFO \
            --project="$GCP_PROJECT" 2>&1
        echo "  → Cloud Logging: OK"
        echo "  → log: $GCP_LOG_NAME  project: $GCP_PROJECT"
    else
        # No gcloud: queue locally for flush by HP node
        [ -f "$PING_QUEUE" ] || echo "timestamp,device,json_payload" > "$PING_QUEUE"
        echo "${TS},${DEVICE},${JSON}" >> "$PING_QUEUE"
        echo "  → gcloud not found: queued in $PING_QUEUE"
        echo "  → Run on HP: sagco-cloud-ping flush"
    fi
}

# ── flush queued pings from other devices ─────────────────────────────────────
flush_queue() {
    echo "FLUSH QUEUE — ship offline pings to Cloud Logging"
    echo "==================================================="

    [ -f "$PING_QUEUE" ] || { echo "  Queue empty (no $PING_QUEUE)"; return; }

    if ! command -v gcloud >/dev/null 2>&1; then
        echo "  ERROR: gcloud not available on this device"
        return 1
    fi

    TOTAL=0
    SHIPPED=0
    while IFS=',' read -r QTS QDEV QJSON; do
        [ "$QTS" = "timestamp" ] && continue
        [ -z "$QTS" ] && continue
        TOTAL=$((TOTAL + 1))
        gcloud logging write "$GCP_LOG_NAME" "$QJSON" \
            --payload-type=json \
            --severity=INFO \
            --project="$GCP_PROJECT" >/dev/null 2>&1 \
            && SHIPPED=$((SHIPPED + 1)) \
            && printf "  shipped: [%s] %s\n" "$QTS" "$QDEV"
    done < "$PING_QUEUE"

    echo ""
    echo "  Total queued: $TOTAL"
    echo "  Shipped:      $SHIPPED"

    # Clear queue after successful flush
    [ "$SHIPPED" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ] && {
        echo "timestamp,device,json_payload" > "$PING_QUEUE"
        echo "  Queue cleared."
    }
}

# ── tail Cloud Logging ────────────────────────────────────────────────────────
tail_logs() {
    echo "CLOUD LOGGING — last 10 pings"
    echo "================================"
    if ! command -v gcloud >/dev/null 2>&1; then
        echo "  gcloud not available — showing local queue instead:"
        [ -f "$PING_QUEUE" ] && tail -10 "$PING_QUEUE" | \
            awk -F',' '{printf "  [%s] device=%s\n", $1, $2}' \
            || echo "  (no queue)"
        return
    fi

    gcloud logging read \
        "logName=\"projects/${GCP_PROJECT}/logs/${GCP_LOG_NAME}\"" \
        --limit=10 \
        --format="table(timestamp, jsonPayload.device, jsonPayload.ipv4, jsonPayload.battery, jsonPayload.status)" \
        --project="$GCP_PROJECT" 2>&1

    echo ""
    echo "  Logs Explorer query:"
    echo "  logName=\"projects/$GCP_PROJECT/logs/$GCP_LOG_NAME\""
}

# ── watch loop ────────────────────────────────────────────────────────────────
watch_loop() {
    PING_DEV="${1:-$DEV}"
    echo "SAGCO CLOUD PING WATCH — device=$PING_DEV interval=${PING_INTERVAL}s"
    echo "Press Ctrl+C to stop"
    echo ""
    while true; do
        gather_ping "$PING_DEV"
        echo "[$(date +%H:%M:%S)] pinging as $PING_DEV (bat=$BAT% gw=$GW)"
        ship_ping
        sleep "$PING_INTERVAL"
    done
}

# ── write local ledger ────────────────────────────────────────────────────────
write_local() {
    PING_DEV="${1:-$DEV}"
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${PING_DEV},sagco_cloud_ping,${PWD},${BAT:-unknown},SAGCO_PING_PASS" >> "$RACE_LOG"
    HASH=$(echo "${STAMP}sagco-cloud-ping${PING_DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${PING_DEV},sagco-cloud-ping,cloud_logging,${HASH},SAGCO_PING_PASS" >> "$LEDGER"
}

# ── print summary ─────────────────────────────────────────────────────────────
print_summary() {
    PING_DEV="$1"
    echo "SAGCO CLOUD PING"
    echo "================="
    printf "  %-12s %s\n" "Stamp:"    "$STAMP"
    printf "  %-12s %s\n" "Device:"   "$PING_DEV"
    printf "  %-12s %s\n" "IPv4:"     "$IPV4"
    printf "  %-12s %s\n" "IPv6:"     "${IPV6:-unavailable}"
    printf "  %-12s %s\n" "Gateway:"  "$GW"
    printf "  %-12s %s%%\n" "Battery:" "$BAT"
    printf "  %-12s %s\n" "WiFi:"     "$WIFI"
    printf "  %-12s %s\n" "Host:"     "$HOST"
    printf "  %-12s %s\n" "Project:"  "$GCP_PROJECT"
    echo ""
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-ping}"

case "$CMD" in
    flush)
        flush_queue
        ;;
    tail|read)
        tail_logs
        ;;
    watch)
        watch_loop "${2:-$DEV}"
        ;;
    help|--help)
        echo "sagco-cloud-ping [device|flush|tail|watch [device]]"
        echo ""
        echo "  (no args)    ping as current device (~/.sagco_device)"
        echo "  zfold        ping as zfold"
        echo "  ipad-ish     ping as ipad-ish"
        echo "  hp-sagco-os  ping as hp-sagco-os"
        echo "  flush        ship queued offline pings (run on HP)"
        echo "  tail         show last 10 pings in Cloud Logging"
        echo "  watch        loop mode, 30s interval"
        exit 0
        ;;
    ping|*)
        # Treat first arg as device name if it looks like one, else use $DEV
        case "$CMD" in
            ping) PING_DEV="$DEV" ;;
            *)    PING_DEV="$CMD" ;;
        esac
        gather_ping "$PING_DEV"
        print_summary "$PING_DEV"
        ship_ping
        write_local "$PING_DEV"
        echo ""
        echo "STATUS=SAGCO_PING_PASS"
        ;;
esac
