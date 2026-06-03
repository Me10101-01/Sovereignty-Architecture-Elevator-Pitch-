#!/bin/sh
# sagco-master-report — SAGCO Memory Consolidation Engine
# Reads master_timeline.csv + all device logs.
# Produces ONE unified brain report: who did what, when, and how it connects.
# This is memory. This is the proof that SAGCO-OS is one system, not many scripts.
#
# Usage:
#   sagco-master-report           → full consolidated report
#   sagco-master-report brief     → one-screen summary only
#   sagco-master-report device    → per-device breakdown table
#   sagco-master-report timeline  → chronological event replay

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
REPORT_DIR="$HOME/sagco_master_report"
REPORT="$REPORT_DIR/master_report_${STAMP}.md"
MASTER_TIMELINE="$HOME/sagco_sync_brain/master_timeline.csv"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
CONTEXT_LOG="$HOME/sagco_context_log.csv"
CORPUS_LOG="$HOME/SAGCO_OBSIDIAN_BRAIN/corpus_callosum.csv"
STATE_YAML="$HOME/sagco_state.yaml"
ANTIBODY_DIR="$HOME/sagco_antibody"
REFINERY_DIR="$HOME/sagco_refinery"

mkdir -p "$REPORT_DIR"
KNOWN_DEVICES="ish ipad termux zfold linux android"

# ── count helper ──────────────────────────────────────────────────────────────
cnt() { grep -c ",${1}," "$2" 2>/dev/null || echo 0; }
last_tick() { grep ",${1}," "$2" 2>/dev/null | tail -1 | cut -d',' -f1; }

# ── read state ────────────────────────────────────────────────────────────────
read_state() {
    RANK="?"
    COMMANDS="?"
    ERU_VAR="?"
    HEALTH="?"
    if [ -f "$STATE_YAML" ]; then
        RANK=$(grep "^portfolio_rank:" "$STATE_YAML" 2>/dev/null | awk '{print $2}')
        COMMANDS=$(grep "^commands:" "$STATE_YAML" 2>/dev/null | awk '{print $2}')
        ERU_VAR=$(grep "^eru_variance:" "$STATE_YAML" 2>/dev/null | awk '{print $2}')
    fi
    AB_LATEST=$(ls -1t "$ANTIBODY_DIR/"*.md 2>/dev/null | head -1)
    [ -n "$AB_LATEST" ] && HEALTH=$(grep "^SYSTEM_HEALTH=" "$AB_LATEST" 2>/dev/null | cut -d'=' -f2)
    REF_LATEST=$(ls -1t "$REFINERY_DIR/"*.yaml 2>/dev/null | head -1)
    REF_RANK=$([ -n "$REF_LATEST" ] && grep "^rank:" "$REF_LATEST" 2>/dev/null | awk '{print $2}' || echo "?")
}

# ── brief summary ─────────────────────────────────────────────────────────────
print_brief() {
    read_state
    echo "SAGCO MASTER REPORT — Brief"
    echo "============================"
    printf "  %-20s %s\n" "Stamp:"         "$STAMP"
    printf "  %-20s %s\n" "Device:"        "$DEV"
    printf "  %-20s %s\n" "Portfolio Rank:" "${RANK:-?}"
    printf "  %-20s %s\n" "Refinery Rank:" "${REF_RANK:-?}"
    printf "  %-20s %s\n" "Antibody Health:" "${HEALTH:-?}"
    printf "  %-20s %s\n" "ERU Variance:"  "${ERU_VAR:-?}"
    printf "  %-20s %s\n" "Commands:"      "${COMMANDS:-?}"
    echo ""

    echo "  BRAIN NODES:"
    for DEVICE in $KNOWN_DEVICES unknown; do
        RACE_CNT=$(cnt "$DEVICE" "$RACE_LOG")
        [ "$RACE_CNT" -eq 0 ] && continue
        LAST=$(last_tick "$DEVICE" "$RACE_LOG")
        BRAIN_CNT=$(ls -1 "$HOME/SAGCO_OBSIDIAN_BRAIN/nodes/${DEVICE}_"*.md 2>/dev/null | wc -l)
        ROLE="?"
        case "$DEVICE" in
            ish)    ROLE="integration" ;;
            ipad)   ROLE="ideation"    ;;
            termux) ROLE="compilation" ;;
            zfold)  ROLE="execution"   ;;
            linux)  ROLE="build"       ;;
            unknown) ROLE="⚠ unattributed" ;;
        esac
        printf "  %-10s %-15s ticks=%-5d nodes=%-4d last=%s\n" \
            "$DEVICE" "$ROLE" "$RACE_CNT" "$BRAIN_CNT" "${LAST:-never}"
    done
    echo ""
}

# ── per-device table ──────────────────────────────────────────────────────────
print_device_table() {
    read_state
    echo "PER-DEVICE BREAKDOWN"
    echo "===================="
    echo ""
    printf "  %-10s %-15s %-8s %-8s %-8s %-8s %-20s\n" \
        "Device" "Role" "Race" "Ledger" "Brain" "Context" "Last Seen"
    echo "  ─────────────────────────────────────────────────────────────────────────────"

    TOTAL_RACE=0
    TOTAL_LEDGER=0
    for DEVICE in $KNOWN_DEVICES unknown; do
        RACE_CNT=$(cnt "$DEVICE" "$RACE_LOG")
        LEDGER_CNT=$(cnt "$DEVICE" "$LEDGER")
        BRAIN_CNT=$(ls -1 "$HOME/SAGCO_OBSIDIAN_BRAIN/nodes/${DEVICE}_"*.md 2>/dev/null | wc -l)
        CTX_CNT=$(cnt "$DEVICE" "$CONTEXT_LOG")
        LAST=$(last_tick "$DEVICE" "$RACE_LOG")
        [ "$((RACE_CNT + LEDGER_CNT))" -eq 0 ] && continue

        ROLE="?"
        case "$DEVICE" in
            ish)    ROLE="integration" ;;
            ipad)   ROLE="ideation"    ;;
            termux) ROLE="compilation" ;;
            zfold)  ROLE="execution"   ;;
            linux)  ROLE="build"       ;;
            unknown) ROLE="UNATTRIBUTED" ;;
        esac

        printf "  %-10s %-15s %-8d %-8d %-8d %-8d %-20s\n" \
            "$DEVICE" "$ROLE" "$RACE_CNT" "$LEDGER_CNT" "$BRAIN_CNT" "$CTX_CNT" "${LAST:-never}"

        TOTAL_RACE=$((TOTAL_RACE + RACE_CNT))
        TOTAL_LEDGER=$((TOTAL_LEDGER + LEDGER_CNT))
    done
    echo "  ─────────────────────────────────────────────────────────────────────────────"
    printf "  %-10s %-15s %-8d %-8d\n" "TOTAL" "" "$TOTAL_RACE" "$TOTAL_LEDGER"
    echo ""

    UNKNOWN_R=$(cnt "unknown" "$RACE_LOG")
    if [ "$UNKNOWN_R" -gt 0 ] && [ "$TOTAL_RACE" -gt 0 ]; then
        PCT=$(echo "scale=1; $UNKNOWN_R * 100 / $TOTAL_RACE" | bc 2>/dev/null || echo "?")
        echo "  ⚠  ATTRIBUTION GAP: ${UNKNOWN_R} unknown ticks = ${PCT}% of total"
        echo "  FIX: echo <device> > ~/.sagco_device && sagco-identity detect"
        echo ""
    fi
}

# ── chronological event replay ────────────────────────────────────────────────
print_timeline() {
    echo "MASTER TIMELINE — last 30 events"
    echo "=================================="
    SOURCE="$MASTER_TIMELINE"
    [ -f "$SOURCE" ] || SOURCE="$RACE_LOG"

    [ -f "$SOURCE" ] && tail -30 "$SOURCE" | grep -v "^timestamp" | \
        awk -F',' '{printf "  [%s] %-10s %-35s\n", $1, $2, $3}' \
        || echo "  (no timeline — run sagco-sync-brain first)"
    echo ""
}

# ── write markdown report ─────────────────────────────────────────────────────
write_report() {
    read_state

    TOTAL_RACE=$(($(wc -l < "$RACE_LOG" 2>/dev/null || echo 1) - 1))
    TOTAL_LEDGER=$(($(wc -l < "$LEDGER" 2>/dev/null || echo 1) - 1))
    MT_ROWS=0
    [ -f "$MASTER_TIMELINE" ] && MT_ROWS=$(($(wc -l < "$MASTER_TIMELINE" 2>/dev/null || echo 1) - 1))

    cat > "$REPORT" << MD
# SAGCO Master Report
Generated: $STAMP
Device: $DEV

## System State

| Metric | Value |
|--------|-------|
| Portfolio Rank | ${RANK:-?} |
| Refinery Rank | ${REF_RANK:-?} |
| Antibody Health | ${HEALTH:-?} |
| ERU Variance | ${ERU_VAR:-?} |
| Total Race Ticks | $TOTAL_RACE |
| Total Ledger Rows | $TOTAL_LEDGER |
| Master Timeline Events | $MT_ROWS |

## Brain Node Registry

| Device | Role | Race Ticks | Ledger Rows | Brain Nodes | Last Seen |
|--------|------|-----------|-------------|-------------|-----------|
MD

    for DEVICE in $KNOWN_DEVICES unknown; do
        RACE_CNT=$(cnt "$DEVICE" "$RACE_LOG")
        LEDGER_CNT=$(cnt "$DEVICE" "$LEDGER")
        BRAIN_CNT=$(ls -1 "$HOME/SAGCO_OBSIDIAN_BRAIN/nodes/${DEVICE}_"*.md 2>/dev/null | wc -l)
        LAST=$(last_tick "$DEVICE" "$RACE_LOG")
        [ "$((RACE_CNT + LEDGER_CNT))" -eq 0 ] && continue
        ROLE="?"
        case "$DEVICE" in
            ish)    ROLE="integration" ;;
            ipad)   ROLE="ideation"    ;;
            termux) ROLE="compilation" ;;
            zfold)  ROLE="execution"   ;;
            linux)  ROLE="build"       ;;
            unknown) ROLE="⚠ unattributed" ;;
        esac
        printf "| %-10s | %-15s | %-9d | %-11d | %-11d | %-17s |\n" \
            "$DEVICE" "$ROLE" "$RACE_CNT" "$LEDGER_CNT" "$BRAIN_CNT" "${LAST:-never}" >> "$REPORT"
    done

    cat >> "$REPORT" << MD2

## Architecture

\`\`\`
zfold  = execution lobe         → sagco-race, nina-trader
iPad   = planning/visual lobe   → doctrine, QR audits, git push
Corpus = SAGCO_OBSIDIAN_BRAIN/  → memory (nodes/*.md)
Bridge = sagco_race/race_log.csv + sagco_ledger.csv + sagco_context_log.csv
Sync   = sagco-sync-brain → master_timeline.csv
\`\`\`

## Pipeline
\`\`\`
sagco-pwd → sagco-race → sagco-brain → sagco-sync-brain → sagco-master-report
\`\`\`

STATUS=SAGCO_MASTER_REPORT_PASS
MD2

    echo "  Report: $REPORT"
}

# ── ledger ────────────────────────────────────────────────────────────────────
write_ledger() {
    HASH=$(echo "${STAMP}sagco-master-report${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-master-report,${REPORT},${HASH},SAGCO_MASTER_REPORT_PASS" >> "$LEDGER"
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_master_report,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-full}"

echo "SAGCO MASTER REPORT — Memory Consolidation"
echo "============================================"
echo "Stamp:   $STAMP"
echo "Device:  $DEV"
echo ""

case "$CMD" in
    brief)
        print_brief
        ;;
    device)
        print_device_table
        ;;
    timeline)
        print_timeline
        ;;
    full|"")
        print_brief
        print_device_table
        print_timeline
        write_report
        write_ledger
        echo "STATUS=SAGCO_MASTER_REPORT_PASS"
        ;;
    *)
        echo "Usage: sagco-master-report [full|brief|device|timeline]"
        exit 1
        ;;
esac
