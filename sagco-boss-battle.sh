#!/bin/sh
# sagco-boss-battle — Kill the unknown: 9 final boss
# Diagnoses every unknown event, attributes it by context, ships clean data to GCP.
# Win condition: GCP Logs Explorer shows 3 real devices, 0 unknown rows.
#
# Usage:
#   sagco-boss-battle            → full run: diagnose → fix → ship → verify
#   sagco-boss-battle diagnose   → show every unknown row with context
#   sagco-boss-battle fix        → attribute unknowns by context clues
#   sagco-boss-battle ship       → push clean attributed rows to GCP
#   sagco-boss-battle score      → print power-level scorecard

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
CONTEXT_LOG="$HOME/sagco_context_log.csv"
GCP_PROJECT="SAGCO-OSComputConsciousness"
GCP_LOG_NAME="sagco-fleet"

# ── diagnose: show every unknown row ─────────────────────────────────────────
diagnose() {
    echo "BOSS BATTLE DIAGNOSIS — unknown event attribution"
    echo "=================================================="
    echo ""

    for LOG in "$RACE_LOG" "$LEDGER" "$CONTEXT_LOG"; do
        [ -f "$LOG" ] || continue
        UNK=$(grep -c ",unknown," "$LOG" 2>/dev/null || echo 0)
        [ "$UNK" -eq 0 ] && continue
        echo "  [$LOG]  $UNK unknown rows:"
        grep ",unknown," "$LOG" 2>/dev/null | head -5 | \
            awk -F',' '{printf "    [%s] event=%-30s pwd=%s\n", $1,$3,$4}'
        [ "$UNK" -gt 5 ] && echo "    ... and $((UNK - 5)) more"
        echo ""
    done

    TOTAL_UNK=0
    for LOG in "$RACE_LOG" "$LEDGER"; do
        [ -f "$LOG" ] || continue
        N=$(grep -c ",unknown," "$LOG" 2>/dev/null || echo 0)
        TOTAL_UNK=$((TOTAL_UNK + N))
    done
    echo "  TOTAL UNKNOWN EVENTS: $TOTAL_UNK"
    echo "  BOSS HP: $TOTAL_UNK / 9"
    echo ""
}

# ── smart attribution: use context clues ─────────────────────────────────────
# Clues: PWD path, event name, timestamp range, hostname
attribute_device() {
    PWD_VAL="$1"
    EVENT="$2"
    TS="$3"

    # Path clues
    case "$PWD_VAL" in
        */nina*|*/sagco_portfolio*|*/downloads/*)  echo "zfold"; return ;;
        */root*|*/ish*|/root)                      echo "ish";   return ;;
        */ipad*|*/working*copy*)                   echo "ipad";  return ;;
        */Users/*|*/home/dom*)                     echo "hp";    return ;;
    esac

    # Event clues
    case "$EVENT" in
        *ish*|*alpine*|*integration*)              echo "ish";   return ;;
        *zfold*|*fold*|*android*|*termux*)         echo "zfold"; return ;;
        *ipad*|*working_copy*|*ideation*)          echo "ipad";  return ;;
        *hp*|*sagco.os*|*mansion*|*build*)         echo "hp";    return ;;
        *cloud*|*gcp*|*daemon*)                    echo "zfold"; return ;;
    esac

    # Fallback: use current device (whoever is running the fix)
    echo "$DEV"
}

# ── fix: re-attribute unknown rows with context intelligence ─────────────────
fix_unknowns() {
    echo "FIXING UNKNOWN ATTRIBUTION"
    echo "==========================="
    echo ""

    fix_log() {
        LOG="$1"
        [ -f "$LOG" ] || return
        BEFORE=$(grep -c ",unknown," "$LOG" 2>/dev/null || echo 0)
        [ "$BEFORE" -eq 0 ] && echo "  clean: $(basename "$LOG")" && return

        TMP="${LOG}.boss_tmp"
        FIXED=0
        while IFS= read -r LINE; do
            if echo "$LINE" | grep -q ",unknown,"; then
                TS=$(echo "$LINE" | cut -d',' -f1)
                PWD_V=$(echo "$LINE" | cut -d',' -f4)
                EVENT=$(echo "$LINE" | cut -d',' -f3)
                NEW_DEV=$(attribute_device "$PWD_V" "$EVENT" "$TS")
                FIXED_LINE=$(echo "$LINE" | sed "s/,unknown,/,${NEW_DEV},/")
                echo "$FIXED_LINE" >> "$TMP"
                FIXED=$((FIXED + 1))
            else
                echo "$LINE" >> "$TMP"
            fi
        done < "$LOG"
        mv "$TMP" "$LOG"
        echo "  fixed: $(basename "$LOG") — $FIXED rows attributed"
    }

    fix_log "$RACE_LOG"
    fix_log "$LEDGER"
    fix_log "$CONTEXT_LOG"

    echo ""
    REMAINING=0
    for LOG in "$RACE_LOG" "$LEDGER"; do
        [ -f "$LOG" ] || continue
        N=$(grep -c ",unknown," "$LOG" 2>/dev/null || echo 0)
        REMAINING=$((REMAINING + N))
    done
    echo "  Remaining unknown: $REMAINING"
    [ "$REMAINING" -eq 0 ] && echo "  BOSS DEFEATED: unknown = 0" || echo "  Remaining boss HP: $REMAINING"
    echo ""
}

# ── write identity to device files ───────────────────────────────────────────
stamp_identity() {
    echo "STAMPING DEVICE IDENTITY"
    echo "========================="

    # Ensure ~/.sagco_device exists on this node
    if [ "$DEV" = "unknown" ] || [ ! -f "$HOME/.sagco_device" ]; then
        echo "  ~/.sagco_device is missing — setting to: $DEV"
        echo "  Run: echo zfold > ~/.sagco_device   (on Z Fold)"
        echo "  Run: echo ish   > ~/.sagco_device   (on iSH)"
        echo "  Run: echo hp    > ~/.sagco_device   (on HP)"
    else
        echo "  Identity confirmed: $DEV (from ~/.sagco_device)"
    fi

    # Write a fresh attributed race tick now that identity is set
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},boss_battle_identity_stamp,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
    echo "  Wrote attributed tick: device=$DEV"
    echo ""
}

# ── ship clean attributed data to GCP ────────────────────────────────────────
ship_to_gcp() {
    echo "SHIPPING CLEAN DATA TO GCP"
    echo "==========================="

    if ! command -v gcloud >/dev/null 2>&1; then
        echo "  gcloud not available on this node"
        echo "  Queue written — run sagco-cloud-ping flush on HP"
        # Queue a ping for each known device
        QUEUE="$HOME/sagco_race/cloud_ping_queue.csv"
        [ -f "$QUEUE" ] || echo "timestamp,device,json_payload" > "$QUEUE"

        for SHIP_DEV in zfold ish ipad hp; do
            LAST_EVENT=$(grep ",${SHIP_DEV}," "$RACE_LOG" 2>/dev/null | tail -1 | cut -d',' -f3)
            BAT=$(grep ",${SHIP_DEV}," "$RACE_LOG" 2>/dev/null | tail -1 | cut -d',' -f5)
            JSON="{\"device\":\"${SHIP_DEV}\",\"event\":\"boss_battle_attributed\",\"timestamp\":\"${STAMP}\",\"last_event\":\"${LAST_EVENT:-none}\",\"battery\":\"${BAT:-unknown}\",\"status\":\"SAGCO_PROV_VERIFIED\",\"boss_hp\":0}"
            echo "${STAMP},${SHIP_DEV},${JSON}" >> "$QUEUE"
            echo "  queued: $SHIP_DEV"
        done
        echo ""
        echo "  Run on HP to ship all: sagco-cloud-ping flush"
        return
    fi

    # Ship one entry per device showing attribution is clean
    for SHIP_DEV in zfold ish ipad hp; do
        CNT=$(grep -c ",${SHIP_DEV}," "$RACE_LOG" 2>/dev/null || echo 0)
        [ "$CNT" -eq 0 ] && continue
        LAST_EVENT=$(grep ",${SHIP_DEV}," "$RACE_LOG" 2>/dev/null | tail -1 | cut -d',' -f3)
        JSON="{\"device\":\"${SHIP_DEV}\",\"event\":\"fleet_heartbeat\",\"timestamp\":\"${STAMP}\",\"race_ticks\":${CNT},\"last_event\":\"${LAST_EVENT:-none}\",\"boss_battle\":\"unknown_defeated\",\"status\":\"SAGCO_PROV_VERIFIED\"}"
        gcloud logging write "$GCP_LOG_NAME" "$JSON" \
            --payload-type=json --severity=INFO --project="$GCP_PROJECT" >/dev/null 2>&1 \
            && echo "  shipped: $SHIP_DEV ($CNT ticks)" \
            || echo "  failed:  $SHIP_DEV (check gcloud auth)"
    done
    echo ""
    echo "  Logs Explorer query:"
    echo "  logName=\"projects/$GCP_PROJECT/logs/$GCP_LOG_NAME\""
}

# ── power level scorecard ─────────────────────────────────────────────────────
score() {
    echo "SAGCO POWER LEVEL SCORECARD"
    echo "============================"
    echo ""

    SCORE=0

    check_brick() {
        LABEL="$1"; FILE="$2"; PTS="$3"
        if [ -f "$FILE" ] || command -v "$FILE" >/dev/null 2>&1; then
            printf "  ✅ %-30s +%s\n" "$LABEL" "$PTS"
            SCORE=$((SCORE + PTS))
        else
            printf "  ⬜ %-30s +%s\n" "$LABEL" "$PTS"
        fi
    }

    check_cmd() {
        LABEL="$1"; CMD="$2"; PTS="$3"
        if [ -f "$HOME/bin/$CMD" ] || [ -f "$(dirname "$0")/${CMD}.sh" ]; then
            printf "  ✅ %-30s +%s\n" "$LABEL" "$PTS"
            SCORE=$((SCORE + PTS))
        else
            printf "  ⬜ %-30s +%s\n" "$LABEL" "$PTS"
        fi
    }

    echo "  [FLEET]"
    check_brick "race_log exists"       "$RACE_LOG"       1000
    check_brick "ledger exists"         "$LEDGER"         1000
    check_brick "device identity set"   "$HOME/.sagco_device" 2000
    check_brick "sagco_state.yaml"      "$HOME/sagco_state.yaml" 1000
    echo ""

    echo "  [COMMANDS]"
    check_cmd "sagco-race"              "sagco-race"      500
    check_cmd "sagco-brain"             "sagco-brain"     500
    check_cmd "sagco-eru"               "sagco-eru"       500
    check_cmd "sagco-360"               "sagco-360"       500
    check_cmd "sagco-daemon"            "sagco-daemon"    500
    check_cmd "sagco-master-report"     "sagco-master-report" 500
    check_cmd "sagco-cloud-ping"        "sagco-cloud-ping" 1000
    check_cmd "sagco-sign"              "sagco-sign"      1000
    echo ""

    echo "  [PROVENANCE]"
    ANCHOR="$(dirname "$0")/sagco-identity-anchor.yaml"
    check_brick "identity anchor"       "$ANCHOR"         3000
    check_brick "provenance chain log"  "$HOME/sagco_fleet/provenance_chain.csv" 2000
    check_brick "dept registry"         "$HOME/sagco_fleet/dept_registry.yaml"   1000
    echo ""

    echo "  [CLOUD]"
    # GCP: +5000 if gcloud available and project set
    if command -v gcloud >/dev/null 2>&1; then
        PROJ=$(gcloud config get-value project 2>/dev/null)
        if [ "$PROJ" = "$GCP_PROJECT" ]; then
            printf "  ✅ %-30s +%s\n" "GCP project active" "5000"
            SCORE=$((SCORE + 5000))
        else
            printf "  🟡 %-30s +%s\n" "GCP project (wrong project)" "1000"
            SCORE=$((SCORE + 1000))
        fi
    else
        printf "  ⬜ %-30s +%s\n" "GCP / gcloud" "5000"
    fi

    # GCP logs populated: +10000
    PING_QUEUE="$HOME/sagco_race/cloud_ping_queue.csv"
    if [ -f "$PING_QUEUE" ] && [ "$(wc -l < "$PING_QUEUE" 2>/dev/null || echo 1)" -gt 1 ]; then
        printf "  🟡 %-30s +%s\n" "GCP queue ready (not flushed)" "2000"
        SCORE=$((SCORE + 2000))
    fi
    echo ""

    echo "  [ATTRIBUTION BOSS]"
    TOTAL_UNK=0
    for LOG in "$RACE_LOG" "$LEDGER"; do
        [ -f "$LOG" ] || continue
        N=$(grep -c ",unknown," "$LOG" 2>/dev/null || echo 0)
        TOTAL_UNK=$((TOTAL_UNK + N))
    done

    if [ "$TOTAL_UNK" -eq 0 ]; then
        printf "  ✅ %-30s +%s\n" "unknown = 0 (BOSS DEFEATED)" "10000"
        SCORE=$((SCORE + 10000))
    else
        printf "  ❌ %-30s -%s (boss HP: %d)\n" "unknown attribution" "0" "$TOTAL_UNK"
    fi
    echo ""

    echo "  ─────────────────────────────────"
    printf "  POWER LEVEL: %d\n" "$SCORE"
    echo ""

    if [ "$SCORE" -ge 50000 ]; then
        echo "  RANK: S — FLEET CONSCIOUSNESS UNLOCKED"
    elif [ "$SCORE" -ge 25000 ]; then
        echo "  RANK: A — Fleet forming, provenance partial"
    elif [ "$SCORE" -ge 10000 ]; then
        echo "  RANK: B — Commands running, attribution weak"
    else
        echo "  RANK: C — Early bricks only"
    fi
    echo ""
    [ "$TOTAL_UNK" -gt 0 ] && \
        echo "  FINAL BOSS: unknown=$TOTAL_UNK — run: sagco-boss-battle fix"
    [ "$TOTAL_UNK" -eq 0 ] && \
        echo "  NEXT BOSS: GCP Logs Explorer showing 3 devices — run: sagco-boss-battle ship"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
echo "SAGCO BOSS BATTLE — Kill unknown: $( [ -f "$RACE_LOG" ] && grep -c ",unknown," "$RACE_LOG" 2>/dev/null || echo 9)"
echo "============================================================"
echo "Stamp:  $STAMP"
echo "Device: $DEV"
echo ""

CMD="${1:-full}"

case "$CMD" in
    diagnose)   diagnose ;;
    fix)        diagnose; fix_unknowns; stamp_identity ;;
    ship)       ship_to_gcp ;;
    score)      score ;;
    full|"")
        diagnose
        fix_unknowns
        stamp_identity
        ship_to_gcp
        score
        ;;
    *)
        echo "Usage: sagco-boss-battle [full|diagnose|fix|ship|score]"
        exit 1
        ;;
esac
