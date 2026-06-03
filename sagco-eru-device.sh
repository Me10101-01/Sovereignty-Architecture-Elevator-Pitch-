#!/bin/sh
# sagco-eru-device — Per-Device ERU Engine
# Breaks down Expected vs Actual work units by device
# Shows: creation_pct, adaptation_pct, eru_variance per ipad/zfold/termux/ish
#
# Usage: sagco-eru-device [--report]

ATTR="$HOME/sagco_attribution/attribution_log.csv"
RACE="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
OUT_DIR="$HOME/sagco_eru_device"
STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")

mkdir -p "$OUT_DIR"

# Devices to track
DEVICES="ipad zfold termux ish"

# ── count events per device ───────────────────────────────────────────────────
count_device_events() {
    DEV="$1"
    FILE="$2"
    grep -ci ",$DEV," "$FILE" 2>/dev/null || echo 0
}

count_device_type() {
    DEV="$1"
    FILE="$2"
    PATTERN="$3"
    grep -i ",$DEV," "$FILE" 2>/dev/null | grep -ci "$PATTERN" || echo 0
}

# ── per-device ERU calculation ────────────────────────────────────────────────
echo "SAGCO PER-DEVICE ERU ENGINE"
echo "==========================="
echo "Stamp: $STAMP"
echo ""

REPORT="$OUT_DIR/eru_device_${STAMP}.yaml"

cat > "$REPORT" << YAML_HEADER
timestamp: $STAMP
source: sagco-eru-device
mode: per_device_eru
devices:
YAML_HEADER

TOTAL_ALL=0
CREATES_ALL=0
FIXES_ALL=0

for DEV in $DEVICES; do

    # Count from race log (primary source)
    RACE_EVENTS=0
    if [ -f "$RACE" ]; then
        RACE_EVENTS=$(grep -ci ",$DEV," "$RACE" 2>/dev/null || echo 0)
    fi

    # Count from attribution log
    ATTR_EVENTS=0
    if [ -f "$ATTR" ]; then
        ATTR_EVENTS=$(grep -ci ",$DEV," "$ATTR" 2>/dev/null || echo 0)
    fi

    # Count from ledger
    LEDGER_EVENTS=0
    if [ -f "$LEDGER" ]; then
        LEDGER_EVENTS=$(grep -ci ",$DEV," "$LEDGER" 2>/dev/null || echo 0)
    fi

    TOTAL=$((RACE_EVENTS + ATTR_EVENTS + LEDGER_EVENTS))

    # Classify: creation vs adaptation from combined sources
    CREATES=0
    FIXES=0

    for SRC in "$RACE" "$ATTR" "$LEDGER"; do
        [ -f "$SRC" ] || continue
        C=$(grep -i ",$DEV," "$SRC" 2>/dev/null | grep -ci "created\|compile\|build\|install\|cargo\|nina\|pack\|audit\|wafer\|init" || echo 0)
        F=$(grep -i ",$DEV," "$SRC" 2>/dev/null | grep -ci "fixed\|pass\|success\|PASS\|repair\|resolve\|update\|sync" || echo 0)
        CREATES=$((CREATES + C))
        FIXES=$((FIXES + F))
    done

    DENOM=$((CREATES + FIXES))
    if [ "$DENOM" -gt 0 ]; then
        CREATE_PCT=$(echo "scale=1; $CREATES * 100 / $DENOM" | bc 2>/dev/null || echo "0")
        ADAPT_PCT=$(echo "scale=1; $FIXES * 100 / $DENOM" | bc 2>/dev/null || echo "0")
    else
        CREATE_PCT="0"
        ADAPT_PCT="0"
    fi

    # ERU variance: deviation from 50/50 baseline
    VARIANCE=$(echo "scale=1; ($CREATE_PCT - 50) * ($CREATE_PCT - 50) / 100" | bc 2>/dev/null || echo "0")

    # Score the device: S=highly active, A=active, B=moderate, C=light
    if [ "$TOTAL" -ge 10 ]; then SCORE="S"
    elif [ "$TOTAL" -ge 5 ]; then SCORE="A"
    elif [ "$TOTAL" -ge 2 ]; then SCORE="B"
    elif [ "$TOTAL" -ge 1 ]; then SCORE="C"
    else SCORE="-"
    fi

    TOTAL_ALL=$((TOTAL_ALL + TOTAL))
    CREATES_ALL=$((CREATES_ALL + CREATES))
    FIXES_ALL=$((FIXES_ALL + FIXES))

    # Print to terminal
    printf "  %-10s total=%-4s creates=%-4s fixes=%-4s  create_pct=%s%%  adapt_pct=%s%%  score=%s\n" \
        "$DEV" "$TOTAL" "$CREATES" "$FIXES" "$CREATE_PCT" "$ADAPT_PCT" "$SCORE"

    # Append to YAML report
    cat >> "$REPORT" << YAML_DEV
  $DEV:
    total_events: $TOTAL
    race_log_events: $RACE_EVENTS
    attribution_events: $ATTR_EVENTS
    ledger_events: $LEDGER_EVENTS
    creation_count: $CREATES
    adaptation_count: $FIXES
    creation_pct: $CREATE_PCT
    adaptation_pct: $ADAPT_PCT
    eru_variance: $VARIANCE
    score: $SCORE
YAML_DEV

done

# ── global summary ────────────────────────────────────────────────────────────
GLOBAL_DENOM=$((CREATES_ALL + FIXES_ALL))
if [ "$GLOBAL_DENOM" -gt 0 ]; then
    GLOBAL_CREATE=$(echo "scale=1; $CREATES_ALL * 100 / $GLOBAL_DENOM" | bc 2>/dev/null || echo "0")
    GLOBAL_ADAPT=$(echo "scale=1; $FIXES_ALL * 100 / $GLOBAL_DENOM" | bc 2>/dev/null || echo "0")
else
    GLOBAL_CREATE="0"
    GLOBAL_ADAPT="0"
fi

echo ""
echo "  ── GLOBAL ──────────────────────────────────────────────────────"
printf "  %-10s total=%-4s creates=%-4s fixes=%-4s  create_pct=%s%%  adapt_pct=%s%%\n" \
    "ALL" "$TOTAL_ALL" "$CREATES_ALL" "$FIXES_ALL" "$GLOBAL_CREATE" "$GLOBAL_ADAPT"

cat >> "$REPORT" << YAML_GLOBAL

global:
  total_events: $TOTAL_ALL
  creation_count: $CREATES_ALL
  adaptation_count: $FIXES_ALL
  creation_pct: $GLOBAL_CREATE
  adaptation_pct: $GLOBAL_ADAPT
  phase: $([ "$(echo "$GLOBAL_ADAPT > 60" | bc 2>/dev/null)" = "1" ] && echo "integration" || echo "construction")

status: SAGCO_ERU_DEVICE_PASS
YAML_GLOBAL

# ── log to main ledger ────────────────────────────────────────────────────────
MAIN_LEDGER="$HOME/sagco_ledger.csv"
DEV="${SAGCO_DEVICE:-unknown}"
HASH=$(echo "${STAMP}sagco-eru-device" | cksum | awk '{printf "%012d", $1}')
[ -f "$MAIN_LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$MAIN_LEDGER"
echo "${STAMP},${DEV},sagco-eru-device,${REPORT},${HASH},SAGCO_ERU_DEVICE_PASS" >> "$MAIN_LEDGER"

echo ""
echo "Report: $REPORT"
echo "STATUS=SAGCO_ERU_DEVICE_PASS"
