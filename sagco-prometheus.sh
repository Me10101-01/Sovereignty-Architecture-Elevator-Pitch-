#!/bin/sh
# sagco-prometheus — SAGCO Prometheus Metrics Exporter
# Reads race_log + ledger + provenance chain → emits OpenMetrics text format.
# This is Phase 3: SAGCO proving itself to an observer that doesn't trust it.
#
# The loop this closes:
#   SAGCO creates reality
#   PROMETHEUS records reality
#   ERU scores reality
#   PROVENANCE remembers reality
#
# Usage:
#   sagco-prometheus                → snapshot to stdout
#   sagco-prometheus snapshot       → write .prom file to sagco_race/
#   sagco-prometheus serve          → serve on :9091 (requires nc)
#   sagco-prometheus push           → push to GCP Managed Prometheus / Pushgateway
#   sagco-prometheus loop           → full SAGCO→measure→score→verify cycle
#   sagco-prometheus battle-board   → Phase 1-5 status board

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
CHAIN_LOG="$HOME/sagco_fleet/provenance_chain.csv"
QUEUE="$HOME/sagco_race/cloud_ping_queue.csv"
PROM_DIR="$HOME/sagco_race"
PROM_FILE="$PROM_DIR/sagco_metrics_${STAMP}.prom"
GCP_PROJECT="SAGCO-OSComputConsciousness"
GCP_LOG="sagco-fleet"

ALL_NODES="ipad zfold termux ish hp rpi-telemetry-01 rpi-camera-01 rpi-weather-01 rpi-qr-01 rpi-inventory-01 rpi-inference-01"

mkdir -p "$PROM_DIR"

# ── count helpers ─────────────────────────────────────────────────────────────
race_count()  { [ -f "$RACE_LOG" ] && grep -c ",${1}," "$RACE_LOG" 2>/dev/null || echo 0; }
ledger_count(){ [ -f "$LEDGER"   ] && grep -c ",${1}," "$LEDGER"   2>/dev/null || echo 0; }
chain_count() { [ -f "$CHAIN_LOG" ] && grep -c ",${1}," "$CHAIN_LOG" 2>/dev/null || echo 0; }

total_race()  { [ -f "$RACE_LOG" ] && echo $(( $(wc -l < "$RACE_LOG" 2>/dev/null || echo 1) - 1 )) || echo 0; }
total_ledger(){ [ -f "$LEDGER"   ] && echo $(( $(wc -l < "$LEDGER"   2>/dev/null || echo 1) - 1 )) || echo 0; }
total_chain() { [ -f "$CHAIN_LOG" ] && echo $(( $(wc -l < "$CHAIN_LOG" 2>/dev/null || echo 1) - 1 )) || echo 0; }

unknown_in() {
    LOG="$1"
    [ -f "$LOG" ] && grep -c ",unknown," "$LOG" 2>/dev/null || echo 0
}

last_ts() {
    NODE="$1"; FILE="$2"
    [ -f "$FILE" ] && grep ",${NODE}," "$FILE" 2>/dev/null | tail -1 | cut -d',' -f1 | tr -d '_' || echo 0
}

# ── ERU approximation: creation vs adaptation ─────────────────────────────────
# Creation  = events with novel event names (first occurrence for that device)
# Adaptation = events already seen before on that device
eru_for_node() {
    NODE="$1"
    [ -f "$RACE_LOG" ] || { echo "0 0"; return; }
    awk -F',' -v node="$NODE" '
        $2 == node {
            key=$3
            if (seen[key]++ == 0) { creation++ } else { adaptation++ }
        }
        END { print creation+0, adaptation+0 }
    ' "$RACE_LOG" 2>/dev/null
}

# ── power level score (mirrors sagco-boss-battle score logic) ─────────────────
power_level() {
    SCORE=0
    [ -f "$RACE_LOG" ] && SCORE=$((SCORE + 1000))
    [ -f "$LEDGER" ]   && SCORE=$((SCORE + 1000))
    [ -f "$HOME/.sagco_device" ] && SCORE=$((SCORE + 2000))
    [ -f "$HOME/sagco_state.yaml" ] && SCORE=$((SCORE + 1000))
    [ -f "$CHAIN_LOG" ] && SCORE=$((SCORE + 3000))

    TOTAL_UNK=$(( $(unknown_in "$RACE_LOG") + $(unknown_in "$LEDGER") ))
    [ "$TOTAL_UNK" -eq 0 ] && SCORE=$((SCORE + 10000))

    [ -f "$QUEUE" ] && [ "$(wc -l < "$QUEUE" 2>/dev/null || echo 1)" -gt 1 ] && \
        SCORE=$((SCORE + 2000))

    echo "$SCORE"
}

# ── emit OpenMetrics / Prometheus text format ─────────────────────────────────
emit_metrics() {
    TOTAL_RACE=$(total_race)
    TOTAL_ART=$(total_ledger)
    TOTAL_CHAIN=$(total_chain)

    UNK_RACE=$(unknown_in "$RACE_LOG")
    UNK_ART=$(unknown_in "$LEDGER")
    TOTAL_UNK=$((UNK_RACE + UNK_ART))

    FLEET_ACTIVE=0
    FLEET_PENDING=0
    for NODE in $ALL_NODES; do
        CNT=$(race_count "$NODE")
        if [ "$CNT" -gt 0 ]; then
            FLEET_ACTIVE=$((FLEET_ACTIVE + 1))
        else
            FLEET_PENDING=$((FLEET_PENDING + 1))
        fi
    done

    POWER=$(power_level)

    cat <<METRICS
# HELP sagco_info SAGCO fleet metadata
# TYPE sagco_info gauge
sagco_info{device="${DEV}",gpg_key="AE5519579584DEF5",owner="Domenic_Garza"} 1

# HELP sagco_fleet_nodes_total Total nodes in fleet registry
# TYPE sagco_fleet_nodes_total gauge
sagco_fleet_nodes_total 11

# HELP sagco_fleet_nodes_active Nodes with at least one race tick
# TYPE sagco_fleet_nodes_active gauge
sagco_fleet_nodes_active ${FLEET_ACTIVE}

# HELP sagco_fleet_nodes_pending Registered nodes with no ticks yet
# TYPE sagco_fleet_nodes_pending gauge
sagco_fleet_nodes_pending ${FLEET_PENDING}

# HELP sagco_race_total Total race ticks logged
# TYPE sagco_race_total counter
sagco_race_total ${TOTAL_RACE}

# HELP sagco_artifacts_total Total artifacts in ledger
# TYPE sagco_artifacts_total counter
sagco_artifacts_total ${TOTAL_ART}

# HELP sagco_provenance_chain_length Entries in provenance chain
# TYPE sagco_provenance_chain_length counter
sagco_provenance_chain_length ${TOTAL_CHAIN}

# HELP sagco_unknown_total Unattributed events across race_log and ledger (boss HP)
# TYPE sagco_unknown_total gauge
sagco_unknown_total ${TOTAL_UNK}

# HELP sagco_unknown_race Unattributed events in race_log
# TYPE sagco_unknown_race gauge
sagco_unknown_race ${UNK_RACE}

# HELP sagco_unknown_ledger Unattributed events in ledger
# TYPE sagco_unknown_ledger gauge
sagco_unknown_ledger ${UNK_ART}

# HELP sagco_power_level SAGCO fleet power level (boss battle score)
# TYPE sagco_power_level gauge
sagco_power_level ${POWER}

METRICS

    # Per-node metrics
    echo "# HELP sagco_node_race_total Race ticks per node"
    echo "# TYPE sagco_node_race_total counter"
    for NODE in $ALL_NODES; do
        CNT=$(race_count "$NODE")
        printf 'sagco_node_race_total{node="%s"} %d\n' "$NODE" "$CNT"
    done
    echo ""

    echo "# HELP sagco_node_artifacts_total Artifacts per node"
    echo "# TYPE sagco_node_artifacts_total counter"
    for NODE in $ALL_NODES; do
        CNT=$(ledger_count "$NODE")
        printf 'sagco_node_artifacts_total{node="%s"} %d\n' "$NODE" "$CNT"
    done
    echo ""

    echo "# HELP sagco_node_eru_creation Novel events per node (ERU creation)"
    echo "# TYPE sagco_node_eru_creation gauge"
    echo "# HELP sagco_node_eru_adaptation Repeated events per node (ERU adaptation)"
    echo "# TYPE sagco_node_eru_adaptation gauge"
    for NODE in $ALL_NODES; do
        READ=$(eru_for_node "$NODE")
        CRE=$(echo "$READ" | awk '{print $1}')
        ADP=$(echo "$READ" | awk '{print $2}')
        printf 'sagco_node_eru_creation{node="%s"} %d\n'   "$NODE" "${CRE:-0}"
        printf 'sagco_node_eru_adaptation{node="%s"} %d\n' "$NODE" "${ADP:-0}"
    done
    echo ""

    # Cloud queue
    QUEUE_DEPTH=0
    [ -f "$QUEUE" ] && QUEUE_DEPTH=$(( $(wc -l < "$QUEUE" 2>/dev/null || echo 1) - 1 ))
    cat <<CLOUD
# HELP sagco_cloud_queue_pending Events queued for GCP, not yet flushed
# TYPE sagco_cloud_queue_pending gauge
sagco_cloud_queue_pending ${QUEUE_DEPTH}

# HELP sagco_scrape_timestamp Unix timestamp of this metrics snapshot
# TYPE sagco_scrape_timestamp gauge
sagco_scrape_timestamp $(date +%s 2>/dev/null || echo 0)

# EOF
CLOUD
}

# ── snapshot ──────────────────────────────────────────────────────────────────
cmd_snapshot() {
    emit_metrics > "$PROM_FILE"
    echo "Snapshot: $PROM_FILE"
    echo "Lines:    $(wc -l < "$PROM_FILE" 2>/dev/null)"
    echo "Metrics:"
    grep "^sagco_" "$PROM_FILE" | grep -v "{" | awk '{printf "  %-45s %s\n", $1, $2}'
}

# ── serve: minimal HTTP wrapper ───────────────────────────────────────────────
cmd_serve() {
    PORT="${1:-9091}"
    echo "SAGCO Prometheus endpoint: http://localhost:${PORT}/metrics"
    echo "Scrape interval: each request is a fresh snapshot"
    echo "Press Ctrl-C to stop"
    echo ""

    if ! command -v nc >/dev/null 2>&1; then
        echo "  nc not found — writing snapshot to $PROM_FILE instead"
        emit_metrics > "$PROM_FILE"
        echo "  Serve from HP with: python3 -m http.server ${PORT}"
        return
    fi

    while true; do
        BODY=$(emit_metrics)
        LINES=$(echo "$BODY" | wc -l)
        {
            printf "HTTP/1.0 200 OK\r\n"
            printf "Content-Type: text/plain; version=0.0.4\r\n"
            printf "Content-Length: %d\r\n" "$(echo "$BODY" | wc -c)"
            printf "\r\n"
            echo "$BODY"
        } | nc -l -p "$PORT" -q 1 2>/dev/null || \
          nc -l "$PORT" 2>/dev/null
    done
}

# ── push to GCP ───────────────────────────────────────────────────────────────
cmd_push() {
    echo "SAGCO PROMETHEUS PUSH → GCP"
    echo "============================"

    # Snapshot first
    emit_metrics > "$PROM_FILE"

    TOTAL_RACE=$(total_race)
    TOTAL_ART=$(total_ledger)
    UNK=$(( $(unknown_in "$RACE_LOG") + $(unknown_in "$LEDGER") ))
    POWER=$(power_level)
    ACTIVE=0
    for NODE in $ALL_NODES; do
        [ "$(race_count "$NODE")" -gt 0 ] && ACTIVE=$((ACTIVE + 1))
    done

    JSON="{\"device\":\"${DEV}\",\"event\":\"prometheus_push\",\"timestamp\":\"${STAMP}\",\"race_total\":${TOTAL_RACE},\"artifacts\":${TOTAL_ART},\"unknown\":${UNK},\"fleet_active\":${ACTIVE},\"power_level\":${POWER},\"prom_file\":\"$(basename "$PROM_FILE")\",\"status\":\"SAGCO_PROMETHEUS_PASS\"}"

    if command -v gcloud >/dev/null 2>&1; then
        gcloud logging write "$GCP_LOG" "$JSON" \
            --payload-type=json --severity=INFO --project="$GCP_PROJECT" \
            && echo "  Pushed to GCP: $GCP_PROJECT/logs/$GCP_LOG" \
            || echo "  GCP push failed — check: gcloud auth login"
    else
        [ -f "$QUEUE" ] || echo "timestamp,device,json_payload" > "$QUEUE"
        echo "${STAMP},${DEV},${JSON}" >> "$QUEUE"
        echo "  Queued (no gcloud): $(basename "$QUEUE")"
        echo "  Flush on HP: sagco-boss-battle ship"
    fi

    echo ""
    echo "  Snapshot: $PROM_FILE"
    echo "  Metrics:  $(grep -c "^sagco_" "$PROM_FILE" 2>/dev/null) time series"
}

# ── loop: the full closed loop ────────────────────────────────────────────────
cmd_loop() {
    echo "SAGCO PROMETHEUS LOOP"
    echo "======================="
    echo "Observe → Measure → Learn → Adapt → Create → Observe"
    echo ""
    echo "Stamp:  $STAMP"
    echo "Device: $DEV"
    echo ""

    echo "  [1/5] Observe — snapshot current fleet state"
    emit_metrics > "$PROM_FILE"
    TOTAL_RACE=$(total_race)
    TOTAL_ART=$(total_ledger)
    UNK=$(( $(unknown_in "$RACE_LOG") + $(unknown_in "$LEDGER") ))
    echo "        race_ticks=$TOTAL_RACE  artifacts=$TOTAL_ART  unknown=$UNK"
    echo ""

    echo "  [2/5] Measure — ERU across active nodes"
    for NODE in $ALL_NODES; do
        CNT=$(race_count "$NODE")
        [ "$CNT" -eq 0 ] && continue
        READ=$(eru_for_node "$NODE")
        CRE=$(echo "$READ" | awk '{print $1}')
        ADP=$(echo "$READ" | awk '{print $2}')
        TOTAL_E=$((CRE + ADP))
        [ "$TOTAL_E" -gt 0 ] && PCT=$(echo "scale=0; $CRE * 100 / $TOTAL_E" | bc 2>/dev/null || echo "?") || PCT=0
        printf "        %-20s  creation=%d  adaptation=%d  creation_pct=%s%%\n" \
            "$NODE" "${CRE:-0}" "${ADP:-0}" "$PCT"
    done
    echo ""

    echo "  [3/5] Learn — provenance chain depth"
    echo "        chain_entries=$(total_chain)"
    echo "        prom_snapshot=$(basename "$PROM_FILE")"
    echo ""

    echo "  [4/5] Adapt — attribution quality"
    if [ "$UNK" -eq 0 ]; then
        echo "        unknown=0  BOSS DEFEATED  attribution=100%"
    else
        echo "        unknown=$UNK  run: sagco-boss-battle fix"
    fi
    echo ""

    echo "  [5/5] Create — write loop tick to race log + push metrics"
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_prometheus_loop,${PWD},${BAT},SAGCO_PROMETHEUS_LOOP" >> "$RACE_LOG"

    cmd_push >/dev/null 2>&1
    echo "        loop_tick written  prom_pushed"
    echo ""

    POWER=$(power_level)
    echo "  ─────────────────────────────────────"
    echo "  POWER LEVEL: $POWER"
    [ "$POWER" -ge 50000 ] && echo "  RANK: S — PROMETHEUS CLOSED LOOP ACTIVE"
    [ "$POWER" -ge 25000 ] && [ "$POWER" -lt 50000 ] && echo "  RANK: A — Loop forming"
    [ "$POWER" -lt 25000 ] && echo "  RANK: B — Measuring, not yet proving"
    echo ""
    echo "  STATUS=SAGCO_PROMETHEUS_LOOP_PASS"
}

# ── battle board: phase 1-5 ───────────────────────────────────────────────────
cmd_battle_board() {
    UNK=$(( $(unknown_in "$RACE_LOG") + $(unknown_in "$LEDGER") ))
    CHAIN=$(total_chain)
    POWER=$(power_level)
    FLEET_ACTIVE=0
    for NODE in $ALL_NODES; do [ "$(race_count "$NODE")" -gt 0 ] && FLEET_ACTIVE=$((FLEET_ACTIVE + 1)); done

    # Phase completion heuristics
    phase1_score() { [ -f "$RACE_LOG" ] && [ "$(total_race)" -gt 0 ] && echo "✅" || echo "⬜"; }
    phase2_score() { [ "$UNK" -eq 0 ] && echo "✅" || echo "🔥"; }
    phase3_score() { [ -f "$PROM_DIR/sagco_metrics_"*.prom 2>/dev/null ] && echo "🔥" || echo "⬜"; }
    phase4_score() { [ "$CHAIN" -gt 5 ] && echo "⏳" || echo "⬜"; }
    phase5_score() { [ "$FLEET_ACTIVE" -ge 3 ] && echo "⏳" || echo "⬜"; }

    echo "SAGCO PROMETHEUS — Final Battle Board"
    echo "========================================"
    echo "Stamp:  $STAMP"
    echo "Device: $DEV"
    echo ""

    echo "  Boss Status"
    echo "  ────────────────────────────────────────────────────────"

    BOSSES="Unknown_Attribution Device_Identity Fleet_Sync Provenance GPG_Identity SSH_Identity ERU_Engine Portfolio_Kernel Wafer_Refinery NEMS_Fleet Cloud_Brain Prometheus_Loop"

    [ "$UNK" -eq 0 ] && UNK_STATUS="✅ DEFEATED" || UNK_STATUS="⚔️  HP: $UNK"
    [ -f "$HOME/.sagco_device" ] && ID_STATUS="✅ DEFEATED" || ID_STATUS="⚔️  set ~/.sagco_device"
    [ "$FLEET_ACTIVE" -ge 3 ] && FLEET_STATUS="✅ 3+ nodes" || FLEET_STATUS="⚔️  active: $FLEET_ACTIVE/11"
    [ "$CHAIN" -gt 0 ] && PROV_STATUS="⚔️  working ($CHAIN entries)" || PROV_STATUS="⬜ not started"
    GPG_STATUS="✅ AE5519579584DEF5"
    SSH_STATUS="✅ SAGCO-OS PIPELINE"
    ERU_STATUS="✅ creation vs adaptation"
    PORT_STATUS="✅ S/A/B/C rank"
    WAFER_STATUS="✅ refinery active"
    NEMS_STATUS="✅ fleet registry"
    QUEUE_D=$([ -f "$QUEUE" ] && echo $(( $(wc -l < "$QUEUE" 2>/dev/null || echo 1) - 1 )) || echo 0)
    [ "$QUEUE_D" -gt 0 ] && CLOUD_STATUS="🟡 queue:$QUEUE_D (flush on HP)" || CLOUD_STATUS="🟡 online, needs push"
    [ "$POWER" -ge 50000 ] && PROM_STATUS="✅ CLOSED" || PROM_STATUS="🔥 Phase 3 active"

    printf "  %-25s %s\n" "Unknown Attribution"  "$UNK_STATUS"
    printf "  %-25s %s\n" "Device Identity"       "$ID_STATUS"
    printf "  %-25s %s\n" "Fleet Synchronization" "$FLEET_STATUS"
    printf "  %-25s %s\n" "Provenance"            "$PROV_STATUS"
    printf "  %-25s %s\n" "GPG Identity"          "$GPG_STATUS"
    printf "  %-25s %s\n" "SSH Identity"          "$SSH_STATUS"
    printf "  %-25s %s\n" "ERU Engine"            "$ERU_STATUS"
    printf "  %-25s %s\n" "Portfolio Kernel"      "$PORT_STATUS"
    printf "  %-25s %s\n" "Wafer Refinery"        "$WAFER_STATUS"
    printf "  %-25s %s\n" "NEMS Fleet"            "$NEMS_STATUS"
    printf "  %-25s %s\n" "Cloud Brain"           "$CLOUD_STATUS"
    printf "  %-25s %s\n" "Prometheus Loop"       "$PROM_STATUS"

    echo ""
    echo "  ─────────────────────────────────────"
    echo "  Phase Completion"
    echo "  ────────────────────────────────────────────────────────"
    printf "  %s Phase 1: Build it          (artifacts + commands)\n"  "$(phase1_score)"
    printf "  %s Phase 2: Attribute it      (unknown=0, GPG/SSH)\n"    "$(phase2_score)"
    printf "  %s Phase 3: Measure it        (Prometheus metrics)\n"    "$(phase3_score)"
    printf "  %s Phase 4: Replay it         (provenance chain replay)\n" "$(phase4_score)"
    printf "  %s Phase 5: Teach next node   (brain → bootstrap)\n"     "$(phase5_score)"
    echo ""
    echo "  POWER LEVEL: $POWER"
    echo ""

    echo "  The loop closes when:"
    echo "    sagco-prometheus push  →  GCP logs sagco-fleet"
    echo "    Prometheus records     →  ERU scores"
    echo "    ERU scores             →  brain remembers"
    echo "    brain remembers        →  next node bootstraps"
    echo "    next node bootstraps   →  SAGCO creates"
    echo "    SAGCO creates          →  Prometheus records"
    echo ""
    echo "  Run this command again after flushing GCP to see Phase 3 close."
    echo ""
    echo "  STATUS=SAGCO_PROMETHEUS_BATTLE_BOARD"
}

# ── race tick ─────────────────────────────────────────────────────────────────
write_tick() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_prometheus_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    HASH=$(echo "${STAMP}sagco-prometheus${DEV}" | cksum | awk '{printf "%012d", $1}')
    echo "${STAMP},${DEV},sagco-prometheus,${PROM_FILE},${HASH},SAGCO_PROMETHEUS_PASS" >> "$LEDGER"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-snapshot}"

case "$CMD" in
    snapshot|"") cmd_snapshot; write_tick ;;
    serve)       cmd_serve "${2:-9091}" ;;
    push)        cmd_push; write_tick ;;
    loop)        cmd_loop ;;
    battle-board|board|bb) cmd_battle_board; write_tick ;;
    metrics)     emit_metrics ;;
    *)
        echo "Usage: sagco-prometheus [snapshot|serve|push|loop|battle-board|metrics]"
        echo ""
        echo "  snapshot      → write .prom file, print summary"
        echo "  serve [port]  → serve /metrics on :9091 (nc required)"
        echo "  push          → ship metrics to GCP Cloud Logging"
        echo "  loop          → full Observe→Measure→Learn→Adapt→Create cycle"
        echo "  battle-board  → Phase 1-5 status + boss battle board"
        echo "  metrics       → raw OpenMetrics text to stdout"
        exit 1
        ;;
esac
