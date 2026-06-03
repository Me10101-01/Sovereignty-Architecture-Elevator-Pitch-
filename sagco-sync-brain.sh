#!/bin/sh
# sagco-sync-brain — SAGCO Master Brain Synchronization Engine
# Corpus callosum: scans all device logs, merges by timestamp,
# detects duplicates, detects missing replay nodes, builds ONE master timeline.
#
# Usage:
#   sagco-sync-brain              → full merge + analysis
#   sagco-sync-brain scan         → scan all device logs (no merge)
#   sagco-sync-brain merge        → merge into master_timeline.csv
#   sagco-sync-brain diff         → show what each device has that others don't
#   sagco-sync-brain gaps         → detect missing replay windows per device
#   sagco-sync-brain health       → brain health score

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
SYNC_DIR="$HOME/sagco_sync_brain"
MASTER_TIMELINE="$SYNC_DIR/master_timeline.csv"
SYNC_REPORT="$SYNC_DIR/sync_report_${STAMP}.md"
CORPUS_LOG="$HOME/SAGCO_OBSIDIAN_BRAIN/corpus_callosum.csv"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
PWD_LOG="$HOME/sagco_race/pwd_log.csv"
CONTEXT_LOG="$HOME/sagco_context_log.csv"
DAEMON_LOG="$HOME/sagco_race/daemon_log.csv"
BRAIN_DIR="$HOME/SAGCO_OBSIDIAN_BRAIN/nodes"

mkdir -p "$SYNC_DIR" "$BRAIN_DIR"

KNOWN_DEVICES="ish ipad termux zfold linux android"

# ── scan: count entries per device in a log ───────────────────────────────────
count_device_entries() {
    LOG="$1"
    DEVICE="$2"
    [ -f "$LOG" ] || echo 0
    grep -c ",${DEVICE}," "$LOG" 2>/dev/null || echo 0
}

last_device_tick() {
    LOG="$1"
    DEVICE="$2"
    [ -f "$LOG" ] || { echo "never"; return; }
    LAST=$(grep ",${DEVICE}," "$LOG" 2>/dev/null | tail -1 | cut -d',' -f1)
    echo "${LAST:-never}"
}

# ── scan all device logs ──────────────────────────────────────────────────────
scan_logs() {
    echo "BRAIN SCAN — all device logs"
    echo "============================="
    echo ""

    LOGS="$RACE_LOG $LEDGER $PWD_LOG $CONTEXT_LOG $CORPUS_LOG $DAEMON_LOG"

    for LOG in $LOGS; do
        [ -f "$LOG" ] || continue
        TOTAL=$(($(wc -l < "$LOG" 2>/dev/null || echo 1) - 1))
        printf "  %-45s %d rows\n" "$(basename "$LOG")" "$TOTAL"
    done
    echo ""

    echo "  Per-device breakdown:"
    for DEVICE in $KNOWN_DEVICES; do
        RACE_CNT=$(count_device_entries "$RACE_LOG" "$DEVICE")
        LEDGER_CNT=$(count_device_entries "$LEDGER" "$DEVICE")
        BRAIN_CNT=$(ls -1 "$BRAIN_DIR/${DEVICE}_"*.md 2>/dev/null | wc -l)
        LAST=$(last_device_tick "$RACE_LOG" "$DEVICE")

        if [ "$((RACE_CNT + LEDGER_CNT))" -gt 0 ]; then
            printf "  %-10s  race=%-5d ledger=%-5d brain_nodes=%-4d last=%s\n" \
                "$DEVICE" "$RACE_CNT" "$LEDGER_CNT" "$BRAIN_CNT" "$LAST"
        fi
    done

    UNKNOWN_CNT=$(count_device_entries "$RACE_LOG" "unknown")
    [ "$UNKNOWN_CNT" -gt 0 ] && printf "  %-10s  race=%-5d (attribution gap!)\n" "unknown" "$UNKNOWN_CNT"
    echo ""
}

# ── merge all logs into master timeline ───────────────────────────────────────
merge_timeline() {
    echo "MERGING — building master_timeline.csv"
    echo "======================================="

    [ -f "$MASTER_TIMELINE" ] || echo "timestamp,device,event,source_log,pwd,battery,status" > "$MASTER_TIMELINE"

    EXISTING_ROWS=$(wc -l < "$MASTER_TIMELINE" 2>/dev/null || echo 1)
    NEW_ROWS=0
    DUPS=0

    merge_log() {
        SRC_LOG="$1"
        SRC_NAME="$2"
        [ -f "$SRC_LOG" ] || return

        while IFS=',' read -r TS DEV_R EVENT REST; do
            [ "$TS" = "timestamp" ] && continue
            [ -z "$TS" ] && continue

            # Dedup: check if this stamp+device+event already in master
            KEY="${TS},${DEV_R},${EVENT}"
            if grep -q "^${TS},${DEV_R}," "$MASTER_TIMELINE" 2>/dev/null; then
                DUPS=$((DUPS + 1))
                continue
            fi

            # Extract pwd + battery from REST (varies by log format)
            PWD_F=$(echo "$REST" | cut -d',' -f1)
            BAT_F=$(echo "$REST" | cut -d',' -f2)

            echo "${TS},${DEV_R},${EVENT},${SRC_NAME},${PWD_F},${BAT_F},MERGED" >> "$MASTER_TIMELINE"
            NEW_ROWS=$((NEW_ROWS + 1))
        done < "$SRC_LOG"
    }

    merge_log "$RACE_LOG"    "race_log"
    merge_log "$LEDGER"      "ledger"
    merge_log "$CORPUS_LOG"  "corpus"
    merge_log "$PWD_LOG"     "pwd_log"

    # Sort master timeline by timestamp (in-place via temp)
    SORTED="$SYNC_DIR/master_timeline_sorted_tmp.csv"
    HEADER=$(head -1 "$MASTER_TIMELINE")
    { echo "$HEADER"; tail -n +2 "$MASTER_TIMELINE" | sort; } > "$SORTED" && mv "$SORTED" "$MASTER_TIMELINE"

    FINAL_ROWS=$(($(wc -l < "$MASTER_TIMELINE" 2>/dev/null || echo 1) - 1))
    echo "  New rows merged: $NEW_ROWS"
    echo "  Duplicates skipped: $DUPS"
    echo "  Total master timeline rows: $FINAL_ROWS"
    echo "  Master: $MASTER_TIMELINE"
    echo ""
}

# ── diff: what each device has vs others ─────────────────────────────────────
diff_devices() {
    echo "DEVICE DIFF — unique events per lobe"
    echo "======================================"
    [ -f "$MASTER_TIMELINE" ] || { echo "  (run sagco-sync-brain merge first)"; return; }

    for DEVICE in $KNOWN_DEVICES; do
        CNT=$(grep -c ",${DEVICE}," "$MASTER_TIMELINE" 2>/dev/null || echo 0)
        [ "$CNT" -eq 0 ] && continue
        echo "  [${DEVICE}] ${CNT} events"
        grep ",${DEVICE}," "$MASTER_TIMELINE" 2>/dev/null | \
            cut -d',' -f3 | sort | uniq -c | sort -rn | head -5 | \
            awk '{printf "    %3d × %s\n", $1, $2}'
        echo ""
    done
}

# ── gap detection: missing replay windows ────────────────────────────────────
detect_gaps() {
    echo "GAP ANALYSIS — missing replay nodes per device"
    echo "================================================"
    [ -f "$MASTER_TIMELINE" ] || { echo "  (run sagco-sync-brain merge first)"; return; }

    for DEVICE in $KNOWN_DEVICES; do
        CNT=$(grep -c ",${DEVICE}," "$MASTER_TIMELINE" 2>/dev/null || echo 0)
        [ "$CNT" -eq 0 ] && continue

        echo "  [${DEVICE}]"

        PREV_TS=""
        GAPS=0
        grep ",${DEVICE}," "$MASTER_TIMELINE" 2>/dev/null | cut -d',' -f1 | sort | \
        while read -r TS; do
            if [ -n "$PREV_TS" ]; then
                P_DATE=$(echo "$PREV_TS" | cut -c1-8)
                C_DATE=$(echo "$TS" | cut -c1-8)
                if [ "$P_DATE" != "$C_DATE" ]; then
                    P_YMD=$(echo "$P_DATE" | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')
                    C_YMD=$(echo "$C_DATE" | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')
                    P_EP=$(date -d "$P_YMD" +%s 2>/dev/null || echo 0)
                    C_EP=$(date -d "$C_YMD" +%s 2>/dev/null || echo 0)
                    DIFF=$(( (C_EP - P_EP) / 86400 ))
                    if [ "$DIFF" -gt 1 ] 2>/dev/null; then
                        printf "    GAP: %d day(s) silent  %s → %s\n" "$DIFF" "$PREV_TS" "$TS"
                    fi
                fi
            fi
            PREV_TS="$TS"
        done

        BRAIN_NODES=$(ls -1 "$BRAIN_DIR/${DEVICE}_"*.md 2>/dev/null | wc -l)
        printf "    brain_nodes: %d  |  timeline_rows: %d\n" "$BRAIN_NODES" "$CNT"
        echo ""
    done

    UNKNOWN_CNT=$(grep -c ",unknown," "$MASTER_TIMELINE" 2>/dev/null || echo 0)
    if [ "$UNKNOWN_CNT" -gt 0 ]; then
        echo "  ATTRIBUTION GAP: $UNKNOWN_CNT rows with device=unknown"
        echo "  FIX: echo <device> > ~/.sagco_device && export SAGCO_DEVICE=<device>"
        echo ""
    fi
}

# ── brain health score ────────────────────────────────────────────────────────
brain_health() {
    echo "BRAIN HEALTH SCORE"
    echo "==================="
    SCORE=0
    MAX=10
    ISSUES=""

    # Check 1: race log exists and has entries
    if [ -f "$RACE_LOG" ]; then
        ROWS=$(($(wc -l < "$RACE_LOG" 2>/dev/null || echo 1) - 1))
        if [ "$ROWS" -gt 10 ]; then
            SCORE=$((SCORE + 2))
            printf "  [+2] Race log active: %d ticks\n" "$ROWS"
        else
            printf "  [-] Race log sparse: %d ticks\n" "$ROWS"
            ISSUES="${ISSUES}sparse_race_log "
        fi
    else
        echo "  [-] Race log missing"
        ISSUES="${ISSUES}no_race_log "
    fi

    # Check 2: master timeline exists
    if [ -f "$MASTER_TIMELINE" ]; then
        MT_ROWS=$(($(wc -l < "$MASTER_TIMELINE" 2>/dev/null || echo 1) - 1))
        SCORE=$((SCORE + 1))
        printf "  [+1] Master timeline: %d events\n" "$MT_ROWS"
    else
        echo "  [-] Master timeline not built yet"
        ISSUES="${ISSUES}no_master_timeline "
    fi

    # Check 3: multiple devices present
    ACTIVE_DEVICES=0
    for DEVICE in $KNOWN_DEVICES; do
        CNT=$(count_device_entries "$RACE_LOG" "$DEVICE")
        [ "$CNT" -gt 0 ] && ACTIVE_DEVICES=$((ACTIVE_DEVICES + 1))
    done
    if [ "$ACTIVE_DEVICES" -ge 2 ]; then
        SCORE=$((SCORE + 3))
        printf "  [+3] Multi-brain active: %d devices\n" "$ACTIVE_DEVICES"
    elif [ "$ACTIVE_DEVICES" -eq 1 ]; then
        SCORE=$((SCORE + 1))
        printf "  [+1] Single-brain: 1 device (add second device for entanglement)\n"
        ISSUES="${ISSUES}single_device "
    else
        echo "  [-] No device attribution found"
        ISSUES="${ISSUES}no_device_attribution "
    fi

    # Check 4: unknown attribution
    UNKNOWN_CNT=$(count_device_entries "$RACE_LOG" "unknown")
    if [ "$UNKNOWN_CNT" -eq 0 ]; then
        SCORE=$((SCORE + 2))
        echo "  [+2] Attribution clean: no unknown devices"
    else
        printf "  [-] Attribution gap: %d unknown ticks\n" "$UNKNOWN_CNT"
        ISSUES="${ISSUES}unknown_attribution "
    fi

    # Check 5: corpus callosum active
    if [ -f "$CORPUS_LOG" ]; then
        CC_ROWS=$(($(wc -l < "$CORPUS_LOG" 2>/dev/null || echo 1) - 1))
        SCORE=$((SCORE + 1))
        printf "  [+1] Corpus callosum: %d nodes\n" "$CC_ROWS"
    else
        echo "  [-] Corpus callosum empty — run sagco-brain"
        ISSUES="${ISSUES}no_corpus "
    fi

    # Check 6: context log active
    if [ -f "$CONTEXT_LOG" ] && [ "$(wc -l < "$CONTEXT_LOG" 2>/dev/null || echo 0)" -gt 1 ]; then
        SCORE=$((SCORE + 1))
        echo "  [+1] Context log active"
    else
        echo "  [-] Context log empty — run sagco-brain"
        ISSUES="${ISSUES}no_context_log "
    fi

    # Rank
    echo ""
    echo "  ─────────────────────────────"
    printf "  BRAIN SCORE: %d / %d\n" "$SCORE" "$MAX"

    if [ "$SCORE" -ge 9 ]; then
        BRAIN_RANK="ENTANGLED"
    elif [ "$SCORE" -ge 6 ]; then
        BRAIN_RANK="SYNCED"
    elif [ "$SCORE" -ge 3 ]; then
        BRAIN_RANK="PARTIAL"
    else
        BRAIN_RANK="ISOLATED"
    fi
    printf "  BRAIN RANK:  %s\n" "$BRAIN_RANK"
    [ -n "$ISSUES" ] && printf "  ISSUES:      %s\n" "$ISSUES"
    echo ""
    echo "STATUS=SAGCO_BRAIN_${BRAIN_RANK}"
}

# ── write sync report ─────────────────────────────────────────────────────────
write_report() {
    MT_ROWS=$(($(wc -l < "$MASTER_TIMELINE" 2>/dev/null || echo 1) - 1))

    cat > "$SYNC_REPORT" << RPT
# SAGCO Brain Sync Report
Generated: $STAMP
Device: $DEV

## Master Timeline
- File: $MASTER_TIMELINE
- Total events: $MT_ROWS

## Device Activity
RPT

    for DEVICE in $KNOWN_DEVICES; do
        CNT=$(count_device_entries "$RACE_LOG" "$DEVICE")
        LAST=$(last_device_tick "$RACE_LOG" "$DEVICE")
        [ "$CNT" -gt 0 ] && printf "- %-10s  %d race ticks   last: %s\n" "$DEVICE" "$CNT" "$LAST" >> "$SYNC_REPORT"
    done

    cat >> "$SYNC_REPORT" << RPT2

## Brain Architecture
\`\`\`
zfold brain  = execution lobe
iPad brain   = planning/visual lobe
Corpus      = SAGCO_OBSIDIAN_BRAIN/nodes/*.md
Heartbeat   = sagco_race/race_log.csv
Sync bridge = sagco_sync_brain/master_timeline.csv
\`\`\`

STATUS=SAGCO_BRAIN_SYNC_PASS
RPT2

    echo "  Report: $SYNC_REPORT"
}

# ── ledger + race ─────────────────────────────────────────────────────────────
write_ledger() {
    HASH=$(echo "${STAMP}sagco-sync-brain${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-sync-brain,${SYNC_REPORT},${HASH},SAGCO_BRAIN_SYNC_PASS" >> "$LEDGER"
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$HOME/sagco_race/race_log.csv" ] || echo "timestamp,device,event,pwd,battery,status" > "$HOME/sagco_race/race_log.csv"
    echo "${STAMP},${DEV},sagco_sync_brain,${PWD},${BAT},SAGCO_RACE_TICK" >> "$HOME/sagco_race/race_log.csv"
}

# ── header ────────────────────────────────────────────────────────────────────
echo "SAGCO SYNC BRAIN — Corpus Callosum Engine"
echo "=========================================="
echo "Stamp:   $STAMP"
echo "Device:  $DEV"
echo ""

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-full}"

case "$CMD" in
    scan)
        scan_logs
        ;;
    merge)
        merge_timeline
        ;;
    diff)
        diff_devices
        ;;
    gaps)
        detect_gaps
        ;;
    health)
        brain_health
        ;;
    full|"")
        scan_logs
        merge_timeline
        diff_devices
        detect_gaps
        brain_health
        write_report
        write_ledger
        echo ""
        echo "STATUS=SAGCO_BRAIN_SYNC_PASS"
        ;;
    *)
        echo "Usage: sagco-sync-brain [full|scan|merge|diff|gaps|health]"
        exit 1
        ;;
esac
