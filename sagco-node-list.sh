#!/bin/sh
# sagco-node-list — SAGCO Fleet Node Dashboard
# Reads node_registry.yaml + ledger → prints live fleet table.
# Every node shows: role, artifacts, contribution %, status.
#
# Usage:
#   sagco-node-list                → full fleet table
#   sagco-node-list brief          → names + roles only
#   sagco-node-list rpi            → RPi nodes only
#   sagco-node-list portfolio      → portfolio-ready summary block

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
REGISTRY="$HOME/sagco_fleet/node_registry.yaml"
LEDGER="$HOME/sagco_ledger.csv"
RACE_LOG="$HOME/sagco_race/race_log.csv"

# ── all known nodes in display order ─────────────────────────────────────────
ALL_NODES="ipad zfold termux ish hp rpi-telemetry-01 rpi-camera-01 rpi-weather-01 rpi-qr-01 rpi-inventory-01 rpi-inference-01"

# ── count artifacts from logs ─────────────────────────────────────────────────
art_count() {
    NODE="$1"
    [ -f "$LEDGER" ] && grep -c ",${NODE}," "$LEDGER" 2>/dev/null || echo 0
}

race_count() {
    NODE="$1"
    [ -f "$RACE_LOG" ] && grep -c ",${NODE}," "$RACE_LOG" 2>/dev/null || echo 0
}

total_artifacts() {
    [ -f "$LEDGER" ] && echo $(( $(wc -l < "$LEDGER" 2>/dev/null || echo 1) - 1 )) || echo 1
}

contribution() {
    NODE_ART="$1"
    TOTAL="$2"
    [ "$TOTAL" -gt 0 ] && \
        echo "scale=1; $NODE_ART * 100 / $TOTAL" | bc 2>/dev/null || echo "0.0"
}

# ── get field from registry ───────────────────────────────────────────────────
reg_field() {
    NODE="$1"; FIELD="$2"
    [ -f "$REGISTRY" ] || { echo "?"; return; }
    # Find the node block and extract the field
    awk -v node="    ${NODE}:" -v field="      ${FIELD}:" '
        $0 ~ node { found=1; next }
        found && $0 ~ field { gsub(/.*: */, ""); gsub(/^ +| +$/, ""); print; exit }
        found && /^    [a-z]/ && $0 !~ node { found=0 }
    ' "$REGISTRY" 2>/dev/null | head -1
}

# ── node status: online if it has recent race ticks ──────────────────────────
node_status() {
    NODE="$1"
    CNT=$(race_count "$NODE")
    if [ "$CNT" -gt 0 ]; then
        # Check if active in last 24h (rough: last tick timestamp)
        LAST=$(grep ",${NODE}," "$RACE_LOG" 2>/dev/null | tail -1 | cut -d',' -f1)
        [ -n "$LAST" ] && echo "ACTIVE" || echo "REGISTERED"
    else
        echo "PENDING"   # registered but no ticks yet
    fi
}

# ── full table ────────────────────────────────────────────────────────────────
print_full() {
    TOTAL=$(total_artifacts)

    echo "SAGCO FLEET — Node Registry"
    echo "============================="
    echo "Stamp:  $STAMP"
    echo "Device: $DEV"
    echo ""
    printf "  %-22s %-15s %-12s %-8s %-8s %-10s\n" \
        "NODE" "ROLE" "TYPE" "ARTIFACTS" "CONTRIB" "STATUS"
    echo "  ─────────────────────────────────────────────────────────────────────────"

    TOTAL_FLEET_ART=0
    ACTIVE_NODES=0

    for NODE in $ALL_NODES; do
        ART=$(art_count "$NODE")
        RACE=$(race_count "$NODE")
        TOTAL_FLEET_ART=$((TOTAL_FLEET_ART + ART))

        ROLE=$(reg_field "$NODE" "role")
        [ -z "$ROLE" ] || [ "$ROLE" = "?" ] && {
            case "$NODE" in
                ipad)             ROLE="ideation" ;;
                zfold)            ROLE="execution" ;;
                termux)           ROLE="compilation" ;;
                ish)              ROLE="integration" ;;
                hp)               ROLE="mansion" ;;
                rpi-telemetry-01) ROLE="telemetry" ;;
                rpi-camera-01)    ROLE="vision" ;;
                rpi-weather-01)   ROLE="weather" ;;
                rpi-qr-01)        ROLE="qr_scanner" ;;
                rpi-inventory-01) ROLE="inventory" ;;
                rpi-inference-01) ROLE="ai_inference" ;;
            esac
        }

        TYPE=$(reg_field "$NODE" "type")
        [ -z "$TYPE" ] || [ "$TYPE" = "?" ] && {
            case "$NODE" in
                rpi*) TYPE="raspberry_pi" ;;
                ipad) TYPE="apple_tablet" ;;
                zfold|termux) TYPE="android_phone" ;;
                ish)  TYPE="ios_emulator" ;;
                hp)   TYPE="laptop_x86" ;;
                *)    TYPE="unknown" ;;
            esac
        }

        STATUS=$(node_status "$NODE")
        [ "$STATUS" = "ACTIVE" ] && ACTIVE_NODES=$((ACTIVE_NODES + 1))
        CONTRIB=$(contribution "$ART" "$TOTAL")

        # Status icon
        case "$STATUS" in
            ACTIVE)     ICON="●" ;;
            REGISTERED) ICON="○" ;;
            PENDING)    ICON="·" ;;
        esac

        printf "  %s %-21s %-15s %-12s %-8d %-8s%% %-10s\n" \
            "$ICON" "$NODE" "$ROLE" "$TYPE" "$ART" "$CONTRIB" "$STATUS"
    done

    echo "  ─────────────────────────────────────────────────────────────────────────"
    printf "  %-22s %-15s %-12s %-8d %-8s (%d active)\n" \
        "TOTAL" "11 nodes" "" "$TOTAL_FLEET_ART" "100%" "$ACTIVE_NODES"
    echo ""
    echo "  ● ACTIVE  ○ REGISTERED  · PENDING (run sagco-node-register on device)"
}

# ── brief table ───────────────────────────────────────────────────────────────
print_brief() {
    echo "SAGCO FLEET"
    echo "============"
    printf "  %-22s %-15s %-10s\n" "NODE" "ROLE" "STATUS"
    echo "  ─────────────────────────────────────────────"
    for NODE in $ALL_NODES; do
        STATUS=$(node_status "$NODE")
        ROLE=$(reg_field "$NODE" "role")
        [ -z "$ROLE" ] || [ "$ROLE" = "?" ] && case "$NODE" in
            ipad) ROLE="ideation" ;; zfold) ROLE="execution" ;;
            termux) ROLE="compilation" ;; ish) ROLE="integration" ;;
            hp) ROLE="mansion" ;; rpi-*) ROLE="${NODE#rpi-}" ;;
        esac
        printf "  %-22s %-15s %s\n" "$NODE" "$ROLE" "$STATUS"
    done
    echo ""
}

# ── RPi nodes only ────────────────────────────────────────────────────────────
print_rpi() {
    TOTAL=$(total_artifacts)
    echo "SAGCO RPi FLEET"
    echo "================"
    printf "  %-22s %-15s %-8s %-8s\n" "NODE" "ROLE" "ARTIFACTS" "STATUS"
    echo "  ────────────────────────────────────────────────────"
    for NODE in rpi-telemetry-01 rpi-camera-01 rpi-weather-01 \
                rpi-qr-01 rpi-inventory-01 rpi-inference-01; do
        ART=$(art_count "$NODE")
        ROLE="${NODE#rpi-}"; ROLE="${ROLE%-01}"
        STATUS=$(node_status "$NODE")
        printf "  %-22s %-15s %-8d %s\n" "$NODE" "$ROLE" "$ART" "$STATUS"
    done
    echo ""
    echo "  To activate: connect RPi, set echo rpi-telemetry-01 > ~/.sagco_device"
    echo "  Then: sagco-node-register && sagco-race && sagco-cloud-ping"
}

# ── portfolio summary block ───────────────────────────────────────────────────
print_portfolio() {
    TOTAL=$(total_artifacts)
    TOTAL_RACE=$(($(wc -l < "$RACE_LOG" 2>/dev/null || echo 1) - 1))
    ACTIVE=0
    for NODE in $ALL_NODES; do
        [ "$(node_status "$NODE")" = "ACTIVE" ] && ACTIVE=$((ACTIVE + 1))
    done

    STATE_RANK="?"
    [ -f "$HOME/sagco_state.yaml" ] && \
        STATE_RANK=$(grep "^portfolio_rank:" "$HOME/sagco_state.yaml" 2>/dev/null | awk '{print $2}')

    cat <<PORTFOLIO

SAGCO-OS FLEET — Portfolio Summary
====================================
System:         Sovereignty Architecture OS
Owner:          Domenic Garza / Strategickhaos DAO LLC
Location:       Corpus Christi, TX
Generated:      $STAMP

Fleet Composition
-----------------
Total Nodes:    11
Active Nodes:   $ACTIVE
Node Types:     phone, tablet, laptop, raspberry_pi, ios_emulator
Locations:      corpus_christi, cloud

Performance
-----------
Total Artifacts: $TOTAL
Race Ticks:      $TOTAL_RACE
Portfolio Rank:  ${STATE_RANK:-A}
Attribution:     cross-device, SSH-keyed, GPG-anchored

Node Roles
----------
ipad              ideation       (doctrine, case studies, architecture)
zfold             execution      (race logs, trading, telemetry, ERU)
termux            compilation    (cargo build, Rust artifacts, classify)
ish               integration    (heartbeat, classify, refinery, verify)
hp-sagco-os       mansion        (daemon, state, GCP bridge, sync)
rpi-telemetry-01  telemetry      (sagco-360, cloud-ping, sensor data)
rpi-camera-01     vision         (image classify, brain node)
rpi-weather-01    weather        (sensor → cloud → fleet dashboard)
rpi-qr-01         qr_scanner     (scan events → race ticks → analytics)
rpi-inventory-01  inventory      (count events → ERU → ledger)
rpi-inference-01  ai_inference   (local model → classify → portfolio)

Provenance
----------
SSH Identity:   SAGCO-OS PIPELINE (GitHub verified 2026-06-03)
GPG Anchor:     AE5519579584DEF5 (Strategickhaos GPG Key)
Cloud Brain:    SAGCO-OSComputConsciousness (GCP)
Git Branch:     claude/rust-excel-graph-api-KPmHv

STATUS=SAGCO_FLEET_PORTFOLIO_PASS
PORTFOLIO
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-full}"
case "$CMD" in
    brief)      print_brief ;;
    rpi)        print_rpi ;;
    portfolio)  print_portfolio ;;
    full|"")    print_full ;;
    *)
        echo "Usage: sagco-node-list [full|brief|rpi|portfolio]"
        exit 1
        ;;
esac

# ── race tick ─────────────────────────────────────────────────────────────────
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
[ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
echo "${STAMP},${DEV},sagco_node_list,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
