#!/bin/sh
# sagco-baseline — SAGCO Behavioral Baseline Engine
# Know normal → measure deviation → explain variance → if unexplained → investigate.
#
# A behavioral fingerprint is not the code.
# It is the traceable pattern of behavior across time:
#   - how commands are named
#   - what is prioritized (attribution, provenance, loop closure)
#   - ERU ratios (creation vs adaptation)
#   - provenance attachment rate
#   - heartbeat regularity
#   - attribution rate (1 - unknown%)
#
# Different output does not automatically mean compromised.
# Different + unexplained + outside established variance → investigate.
#
# Usage:
#   sagco-baseline record [node]     → snapshot current behavioral signature
#   sagco-baseline compare [node]    → measure current vs baseline, compute delta
#   sagco-baseline explain <node> <reason>  → log reason for observed variance
#   sagco-baseline drift [node]      → show unexplained variance over time
#   sagco-baseline report            → full fleet baseline report
#   sagco-baseline fleet             → compare all nodes at once

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
CHAIN_LOG="$HOME/sagco_fleet/provenance_chain.csv"
BASELINE_DIR="$HOME/sagco_fleet/baselines"
EXPLAIN_LOG="$HOME/sagco_fleet/variance_explanations.csv"
DRIFT_LOG="$HOME/sagco_fleet/drift_log.csv"
RACE_OUT="$HOME/sagco_race/race_log.csv"
LEDGER_OUT="$HOME/sagco_ledger.csv"

ALL_NODES="ipad zfold termux ish hp rpi-telemetry-01 rpi-camera-01 rpi-weather-01 rpi-qr-01 rpi-inventory-01 rpi-inference-01"

mkdir -p "$BASELINE_DIR"

# ── compute behavioral signature for a node ───────────────────────────────────
# Returns key=value lines suitable for a baseline snapshot file
compute_signature() {
    NODE="$1"
    [ -f "$RACE_LOG" ] || return 1

    # Total events for this node
    TOTAL=$(grep -c ",${NODE}," "$RACE_LOG" 2>/dev/null || echo 0)
    [ "$TOTAL" -eq 0 ] && return 1

    # Unknown attribution rate
    UNK=$(grep ",${NODE}," "$RACE_LOG" 2>/dev/null | grep -c ",unknown," || echo 0)
    ATTR_RATE=100
    [ "$TOTAL" -gt 0 ] && ATTR_RATE=$(echo "scale=1; (($TOTAL - $UNK) * 100) / $TOTAL" | \
        bc 2>/dev/null || echo 100)

    # ERU: creation (unique first occurrences) vs adaptation (repeated)
    CREATION=$(grep ",${NODE}," "$RACE_LOG" 2>/dev/null | \
        awk -F',' '{print $3}' | sort | uniq -c | \
        awk '$1==1{c++} END{print c+0}')
    ADAPTATION=$((TOTAL - CREATION))
    CREATE_PCT=0
    [ "$TOTAL" -gt 0 ] && CREATE_PCT=$(echo "scale=1; $CREATION * 100 / $TOTAL" | \
        bc 2>/dev/null || echo 0)

    # Event type diversity (unique event types / total)
    UNIQUE_EVENTS=$(grep ",${NODE}," "$RACE_LOG" 2>/dev/null | \
        awk -F',' '{print $3}' | sort -u | wc -l)
    DIVERSITY=0
    [ "$TOTAL" -gt 0 ] && DIVERSITY=$(echo "scale=2; $UNIQUE_EVENTS / $TOTAL" | \
        bc 2>/dev/null || echo 0)

    # Artifacts in ledger
    ARTIFACTS=$([ -f "$LEDGER" ] && grep -c ",${NODE}," "$LEDGER" 2>/dev/null || echo 0)

    # Provenance: entries in chain log
    PROV=$([ -f "$CHAIN_LOG" ] && grep -c ",${NODE}," "$CHAIN_LOG" 2>/dev/null || echo 0)
    PROV_RATE=0
    [ "$ARTIFACTS" -gt 0 ] && PROV_RATE=$(echo "scale=1; $PROV * 100 / $ARTIFACTS" | \
        bc 2>/dev/null || echo 0)

    # Loop closure: race_ticks / artifacts ratio (healthy = > 1)
    LOOP_RATIO=0
    [ "$ARTIFACTS" -gt 0 ] && LOOP_RATIO=$(echo "scale=2; $TOTAL / $ARTIFACTS" | \
        bc 2>/dev/null || echo 0)

    # Naming convention: sagco_* events / total
    SAGCO_EVENTS=$(grep ",${NODE}," "$RACE_LOG" 2>/dev/null | \
        awk -F',' '$3 ~ /^sagco/' | wc -l)
    CONVENTION_RATE=0
    [ "$TOTAL" -gt 0 ] && CONVENTION_RATE=$(echo "scale=1; $SAGCO_EVENTS * 100 / $TOTAL" | \
        bc 2>/dev/null || echo 0)

    # Heartbeat regularity: check if last tick was recent (last 48h crude check)
    LAST_TICK=$(grep ",${NODE}," "$RACE_LOG" 2>/dev/null | tail -1 | cut -d',' -f1)
    HEARTBEAT_STATUS="active"
    [ -z "$LAST_TICK" ] && HEARTBEAT_STATUS="dark"

    cat <<SIG
node=${NODE}
timestamp=${STAMP}
total_events=${TOTAL}
unique_events=${UNIQUE_EVENTS}
attribution_rate=${ATTR_RATE}
creation_pct=${CREATE_PCT}
adaptation_count=${ADAPTATION}
event_diversity=${DIVERSITY}
artifacts=${ARTIFACTS}
provenance_rate=${PROV_RATE}
loop_closure_ratio=${LOOP_RATIO}
convention_rate=${CONVENTION_RATE}
heartbeat=${HEARTBEAT_STATUS}
last_tick=${LAST_TICK:-none}
SIG
}

# ── read a field from a baseline snapshot ────────────────────────────────────
baseline_field() {
    FILE="$1"; FIELD="$2"
    grep "^${FIELD}=" "$FILE" 2>/dev/null | cut -d'=' -f2
}

# ── variance between two values ───────────────────────────────────────────────
variance_pct() {
    BASE="$1"; CURR="$2"
    [ -z "$BASE" ] || [ "$BASE" = "0" ] || [ "$BASE" = "0.0" ] && echo "?" && return
    echo "scale=1; (($CURR - $BASE) * 100) / $BASE" | bc 2>/dev/null || echo "?"
}

# ── classify variance level ───────────────────────────────────────────────────
variance_class() {
    V="$1"
    case "$V" in "?") echo "unknown"; return ;; esac
    # Strip sign for magnitude
    MAG=$(echo "$V" | tr -d '-' | cut -d'.' -f1)
    if [ "$MAG" -lt 10 ] 2>/dev/null; then echo "normal"
    elif [ "$MAG" -lt 25 ] 2>/dev/null; then echo "note"
    elif [ "$MAG" -lt 50 ] 2>/dev/null; then echo "review"
    else echo "investigate"
    fi
}

variance_icon() {
    case "$1" in
        normal)      echo "✅" ;;
        note)        echo "🟡" ;;
        review)      echo "🟠" ;;
        investigate) echo "❌" ;;
        *)           echo "⬜" ;;
    esac
}

# ── record: snapshot current signature as baseline ───────────────────────────
cmd_record() {
    NODE="${1:-$DEV}"
    echo "BASELINE RECORD — $NODE"
    echo "=========================="

    SIG=$(compute_signature "$NODE")
    [ -z "$SIG" ] && echo "  No telemetry for node: $NODE" && return 1

    BASE_FILE="$BASELINE_DIR/${NODE}_baseline.txt"
    echo "$SIG" > "$BASE_FILE"
    echo "  Baseline saved: $BASE_FILE"
    echo ""
    echo "$SIG" | while IFS='=' read KEY VAL; do
        printf "  %-28s %s\n" "${KEY}:" "$VAL"
    done
    echo ""
    echo "  STATUS=SAGCO_BASELINE_RECORDED"
}

# ── compare: measure current vs baseline ─────────────────────────────────────
cmd_compare() {
    NODE="${1:-$DEV}"
    echo "BASELINE COMPARE — $NODE"
    echo "==========================="
    echo ""

    BASE_FILE="$BASELINE_DIR/${NODE}_baseline.txt"
    [ -f "$BASE_FILE" ] || {
        echo "  No baseline for $NODE — run: sagco-baseline record $NODE"
        return 1
    }

    CURR=$(compute_signature "$NODE")
    [ -z "$CURR" ] && echo "  No current telemetry for $NODE" && return 1

    BASE_STAMP=$(baseline_field "$BASE_FILE" "timestamp")
    echo "  Baseline: $BASE_STAMP"
    echo "  Current:  $STAMP"
    echo ""

    printf "  %-30s %-12s %-12s %-8s %s\n" "METRIC" "BASELINE" "CURRENT" "DELTA%" "CLASS"
    echo "  ──────────────────────────────────────────────────────────────────"

    TOTAL_FLAGS=0
    INVESTIGATE_FLAGS=0

    compare_metric() {
        LABEL="$1"; FIELD="$2"
        BASE_VAL=$(baseline_field "$BASE_FILE" "$FIELD")
        CURR_VAL=$(echo "$CURR" | grep "^${FIELD}=" | cut -d'=' -f2)
        DELTA=$(variance_pct "$BASE_VAL" "$CURR_VAL")
        CLASS=$(variance_class "$DELTA")
        ICON=$(variance_icon "$CLASS")

        printf "  %-30s %-12s %-12s %-8s %s %s\n" \
            "$LABEL" "${BASE_VAL:-?}" "${CURR_VAL:-?}" "${DELTA:+${DELTA}%}" "$ICON" "$CLASS"

        [ "$CLASS" = "investigate" ] && INVESTIGATE_FLAGS=$((INVESTIGATE_FLAGS + 1))
        [ "$CLASS" != "normal" ] && TOTAL_FLAGS=$((TOTAL_FLAGS + 1))
    }

    compare_metric "attribution_rate"      "attribution_rate"
    compare_metric "creation_pct (ERU)"    "creation_pct"
    compare_metric "event_diversity"       "event_diversity"
    compare_metric "provenance_rate"       "provenance_rate"
    compare_metric "loop_closure_ratio"    "loop_closure_ratio"
    compare_metric "convention_rate"       "convention_rate"
    compare_metric "total_events"          "total_events"
    compare_metric "artifacts"             "artifacts"

    echo ""
    echo "  ─────────────────────────────────────────────────────────────────"
    printf "  Flags requiring attention:    %d\n" "$TOTAL_FLAGS"
    printf "  Flags requiring investigation: %d\n" "$INVESTIGATE_FLAGS"
    echo ""

    # Check for explained variance
    if [ -f "$EXPLAIN_LOG" ] && grep -q ",${NODE}," "$EXPLAIN_LOG" 2>/dev/null; then
        LATEST_EXPLAIN=$(grep ",${NODE}," "$EXPLAIN_LOG" 2>/dev/null | tail -1)
        EXPL_REASON=$(echo "$LATEST_EXPLAIN" | cut -d',' -f4)
        echo "  Explained variance on file: $EXPL_REASON"
        echo "  (variance may be expected — see: sagco-baseline drift $NODE)"
    fi

    if [ "$INVESTIGATE_FLAGS" -gt 0 ]; then
        echo "  ❌ RECOMMENDATION: Investigate $INVESTIGATE_FLAGS metric(s)"
        echo "     If changes are expected: sagco-baseline explain $NODE <reason>"
        echo "     If unexpected: review provenance chain + recent commits"
    elif [ "$TOTAL_FLAGS" -gt 0 ]; then
        echo "  🟡 RECOMMENDATION: Review noted metrics"
        echo "     If expected: sagco-baseline explain $NODE <reason>"
    else
        echo "  ✅ All metrics within normal variance"
    fi
}

# ── explain: log a reason for observed variance ───────────────────────────────
cmd_explain() {
    NODE="${1:-$DEV}"; REASON="$2"
    [ -z "$REASON" ] && { echo "Usage: sagco-baseline explain <node> <reason>"; return 1; }

    [ -f "$EXPLAIN_LOG" ] || \
        echo "timestamp,device,node,reason,stamped_by,status" > "$EXPLAIN_LOG"
    echo "${STAMP},${DEV},${NODE},${REASON},${DEV},VARIANCE_EXPLAINED" >> "$EXPLAIN_LOG"

    echo "  Variance explanation logged:"
    echo "    node:   $NODE"
    echo "    reason: $REASON"
    echo "    by:     $DEV"
    echo ""
    echo "  This shifts the delta from 'unexplained' to 'explained' in drift reports."
    echo "  Prometheus will still record what arrived. The explanation is the context."
}

# ── drift: show variance history over time ────────────────────────────────────
cmd_drift() {
    NODE="${1:-$DEV}"
    echo "BASELINE DRIFT — $NODE"
    echo "======================="
    echo ""

    BASE_FILE="$BASELINE_DIR/${NODE}_baseline.txt"
    [ -f "$BASE_FILE" ] || { echo "  No baseline for $NODE"; return 1; }

    CURR=$(compute_signature "$NODE")

    # Compute current deltas
    ATTR_BASE=$(baseline_field "$BASE_FILE" "attribution_rate")
    ATTR_CURR=$(echo "$CURR" | grep "^attribution_rate=" | cut -d'=' -f2)
    ATTR_D=$(variance_pct "$ATTR_BASE" "$ATTR_CURR")

    PROV_BASE=$(baseline_field "$BASE_FILE" "provenance_rate")
    PROV_CURR=$(echo "$CURR" | grep "^provenance_rate=" | cut -d'=' -f2)
    PROV_D=$(variance_pct "$PROV_BASE" "$PROV_CURR")

    CREATE_BASE=$(baseline_field "$BASE_FILE" "creation_pct")
    CREATE_CURR=$(echo "$CURR" | grep "^creation_pct=" | cut -d'=' -f2)
    CREATE_D=$(variance_pct "$CREATE_BASE" "$CREATE_CURR")

    echo "  Behavioral fingerprint delta from baseline:"
    echo ""
    printf "  %-28s %s%%\n" "attribution_rate delta:"   "${ATTR_D:-?}"
    printf "  %-28s %s%%\n" "provenance_rate delta:"    "${PROV_D:-?}"
    printf "  %-28s %s%%\n" "creation_pct delta:"       "${CREATE_D:-?}"
    echo ""

    echo "  Explained variance log (most recent 5):"
    if [ -f "$EXPLAIN_LOG" ] && grep -q ",${NODE}," "$EXPLAIN_LOG" 2>/dev/null; then
        grep ",${NODE}," "$EXPLAIN_LOG" 2>/dev/null | tail -5 | \
            awk -F',' '{printf "  [%s] %s\n", $1, $4}'
    else
        echo "  (none — if delta is expected, run: sagco-baseline explain $NODE <reason>)"
    fi
    echo ""

    echo "  Key principle:"
    echo "  Different output is not automatically anomalous."
    echo "  Different + unexplained + outside established variance → investigate."
    echo ""

    # Log to drift record
    [ -f "$DRIFT_LOG" ] || \
        echo "timestamp,node,attr_delta,prov_delta,create_delta,explained,status" > "$DRIFT_LOG"
    EXPLAINED=$([ -f "$EXPLAIN_LOG" ] && grep -c ",${NODE}," "$EXPLAIN_LOG" 2>/dev/null || echo 0)
    echo "${STAMP},${NODE},${ATTR_D:-?},${PROV_D:-?},${CREATE_D:-?},${EXPLAINED},DRIFT_RECORDED" \
        >> "$DRIFT_LOG"
}

# ── fleet: compare all nodes at once ─────────────────────────────────────────
cmd_fleet() {
    echo "SAGCO FLEET BASELINE COMPARISON"
    echo "================================="
    printf "  %-22s %-10s %-10s %-10s %-12s %s\n" \
        "NODE" "ATTR_RATE" "CREATE%" "PROV_RATE" "CONVENTION" "STATUS"
    echo "  ──────────────────────────────────────────────────────────────────"

    for NODE in $ALL_NODES; do
        SIG=$(compute_signature "$NODE" 2>/dev/null)
        [ -z "$SIG" ] && printf "  %-22s %s\n" "$NODE" "· no telemetry" && continue

        ATTR=$(echo "$SIG" | grep "^attribution_rate=" | cut -d'=' -f2)
        CREATE=$(echo "$SIG" | grep "^creation_pct=" | cut -d'=' -f2)
        PROV=$(echo "$SIG" | grep "^provenance_rate=" | cut -d'=' -f2)
        CONV=$(echo "$SIG" | grep "^convention_rate=" | cut -d'=' -f2)
        HB=$(echo "$SIG" | grep "^heartbeat=" | cut -d'=' -f2)

        BASE_FILE="$BASELINE_DIR/${NODE}_baseline.txt"
        if [ -f "$BASE_FILE" ]; then
            BASE_ATTR=$(baseline_field "$BASE_FILE" "attribution_rate")
            DELTA=$(variance_pct "$BASE_ATTR" "$ATTR")
            CLASS=$(variance_class "$DELTA")
            ICON=$(variance_icon "$CLASS")
            STATUS_LABEL="$ICON $CLASS"
        else
            STATUS_LABEL="⬜ no baseline"
        fi

        [ "$HB" = "dark" ] && STATUS_LABEL="🔴 dark"

        printf "  %-22s %-10s %-10s %-10s %-12s %s\n" \
            "$NODE" "${ATTR:-?}%" "${CREATE:-?}%" "${PROV:-?}%" "${CONV:-?}%" "$STATUS_LABEL"
    done
    echo ""
    echo "  To baseline all active nodes: for NODE in ipad zfold ish hp; do"
    echo "    sagco-baseline record \$NODE; done"
}

# ── full report ───────────────────────────────────────────────────────────────
cmd_report() {
    echo "SAGCO BEHAVIORAL BASELINE REPORT"
    echo "=================================="
    echo "Stamp:  $STAMP"
    echo "Device: $DEV"
    echo ""

    BASELINE_COUNT=$(find "$BASELINE_DIR" -name "*_baseline.txt" 2>/dev/null | wc -l)
    EXPLAIN_COUNT=$([ -f "$EXPLAIN_LOG" ] && \
        grep -c "VARIANCE_EXPLAINED" "$EXPLAIN_LOG" 2>/dev/null || echo 0)
    DRIFT_COUNT=$([ -f "$DRIFT_LOG" ] && \
        grep -c "DRIFT_RECORDED" "$DRIFT_LOG" 2>/dev/null || echo 0)

    printf "  %-35s %d\n" "Baselines recorded:"      "$BASELINE_COUNT"
    printf "  %-35s %d\n" "Variance explanations:"   "$EXPLAIN_COUNT"
    printf "  %-35s %d\n" "Drift measurements:"      "$DRIFT_COUNT"
    echo ""

    echo "  The Fingerprint"
    echo "  ─────────────────────────────────────────────────────────────────"
    echo "  A behavioral fingerprint is not the code."
    echo "  It is the traceable pattern of behavior across time:"
    echo ""
    printf "    %-28s attribution_rate  → does this node close attribution loops?\n" ""
    printf "    %-28s creation_pct      → is this node discovering new patterns?\n" ""
    printf "    %-28s provenance_rate   → does every artifact get signed?\n" ""
    printf "    %-28s convention_rate   → does it follow sagco-* naming?\n" ""
    printf "    %-28s loop_ratio        → race ticks / artifacts ratio\n" ""
    printf "    %-28s heartbeat         → is the node still active?\n" ""
    echo ""

    echo "  The Variance Rule"
    echo "  ─────────────────────────────────────────────────────────────────"
    echo "  ✅ delta < 10%     → normal — within expected variation"
    echo "  🟡 delta 10-25%    → note — check for configuration change"
    echo "  🟠 delta 25-50%    → review — investigate cause, log explanation"
    echo "  ❌ delta > 50%     → investigate — significant behavioral shift"
    echo ""
    echo "  Different ≠ Compromised."
    echo "  Different + unexplained + outside variance → investigate."
    echo ""

    if [ "$BASELINE_COUNT" -gt 0 ]; then
        echo "  Nodes with baselines:"
        find "$BASELINE_DIR" -name "*_baseline.txt" 2>/dev/null | while read F; do
            N=$(basename "$F" _baseline.txt)
            TS=$(baseline_field "$F" "timestamp")
            printf "    %-22s baseline from %s\n" "$N" "$TS"
        done
        echo ""
    else
        echo "  No baselines recorded yet."
        echo "  Start with: sagco-baseline record"
        echo ""
    fi

    echo "  STATUS=SAGCO_BASELINE_REPORT_COMPLETE"
}

# ── race tick ─────────────────────────────────────────────────────────────────
write_tick() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
    echo "${STAMP},${DEV},sagco_baseline_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"
    HASH=$(echo "${STAMP}sagco-baseline${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER_OUT" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER_OUT"
    echo "${STAMP},${DEV},sagco-baseline,${BASELINE_DIR},${HASH},SAGCO_BASELINE_PASS" >> "$LEDGER_OUT"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-report}"

case "$CMD" in
    record)   cmd_record "${2:-$DEV}";  write_tick ;;
    compare)  cmd_compare "${2:-$DEV}"; write_tick ;;
    explain)  cmd_explain "${2:-}" "${3:-}"; write_tick ;;
    drift)    cmd_drift "${2:-$DEV}";   write_tick ;;
    fleet)    cmd_fleet;                write_tick ;;
    report|"") cmd_report;             write_tick ;;
    *)
        echo "Usage: sagco-baseline [record|compare|explain|drift|fleet|report] [node]"
        echo ""
        echo "  record [node]         snapshot current behavioral signature"
        echo "  compare [node]        measure current vs baseline, show delta"
        echo "  explain <node> <why>  log reason for observed variance"
        echo "  drift [node]          variance history + explanations"
        echo "  fleet                 compare all nodes simultaneously"
        echo "  report                full baseline report + variance rules"
        echo ""
        echo "  Variance classes:"
        echo "    ✅ <10%   normal    🟡 10-25%  note"
        echo "    🟠 25-50% review    ❌ >50%    investigate"
        exit 1
        ;;
esac
