#!/bin/sh
# sagco-race — SAGCO Heartbeat Writer
# Every meaningful action writes a race tick. This IS the pulse of SAGCO-OS.
# "If it happened and wasn't ticked, it didn't happen."
#
# Usage:
#   sagco-race                           → tick with no event tag
#   sagco-race zfold "build_test_pass"   → tick as zfold with event label
#   sagco-race ipad "qr_audit_complete"  → tick as ipad
#   sagco-race show                      → tail last 20 ticks
#   sagco-race show zfold                → show only zfold ticks
#   sagco-race count                     → per-device tick count
#   sagco-race gap                       → detect gaps > 24h between ticks

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
NOW_EPOCH=$(date +%s 2>/dev/null || echo 0)
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_OUT="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"

mkdir -p "$HOME/sagco_race"

# ── dispatch subcommands ──────────────────────────────────────────────────────
CMD="${1:-tick}"

case "$CMD" in

    show)
        FILTER="${2:-}"
        echo "RACE LOG — last 20 ticks${FILTER:+ (device=$FILTER)}"
        echo "================================="
        if [ -z "$FILTER" ]; then
            [ -f "$RACE_OUT" ] && tail -20 "$RACE_OUT" | \
                awk -F',' '{printf "  [%s] %-10s  %-30s  bat=%-5s\n", $1,$2,$3,$5}' \
                || echo "  (no race log yet)"
        else
            [ -f "$RACE_OUT" ] && grep ",${FILTER}," "$RACE_OUT" | tail -20 | \
                awk -F',' '{printf "  [%s] %-30s  bat=%-5s\n", $1,$3,$5}' \
                || echo "  (no ticks for device: $FILTER)"
        fi
        exit 0
        ;;

    count)
        echo "RACE TICK COUNT — per device"
        echo "============================="
        [ -f "$RACE_OUT" ] || { echo "  (no race log)"; exit 0; }
        for DEVICE in ish ipad termux zfold linux android unknown; do
            CNT=$(grep -c ",${DEVICE}," "$RACE_OUT" 2>/dev/null || echo 0)
            [ "$CNT" -gt 0 ] && printf "  %-12s %d ticks\n" "$DEVICE" "$CNT"
        done
        TOTAL=$(($(wc -l < "$RACE_OUT" 2>/dev/null || echo 1) - 1))
        echo "  ──────────────"
        printf "  %-12s %d ticks\n" "TOTAL" "$TOTAL"
        exit 0
        ;;

    gap)
        echo "GAP ANALYSIS — detecting silent periods > 24h"
        echo "=============================================="
        [ -f "$RACE_OUT" ] || { echo "  (no race log)"; exit 0; }

        PREV_STAMP=""
        PREV_DEV=""
        GAPS=0
        while IFS=',' read -r TS DEV_R EVENT PWD_R BAT STATUS_R; do
            [ "$TS" = "timestamp" ] && continue
            [ -z "$PREV_STAMP" ] && { PREV_STAMP="$TS"; PREV_DEV="$DEV_R"; continue; }

            # Compare timestamps (YYYYMMDD_HHMMSS → epoch approximate)
            P_DATE=$(echo "$PREV_STAMP" | cut -d'_' -f1)
            C_DATE=$(echo "$TS" | cut -d'_' -f1)
            if [ "$P_DATE" != "$C_DATE" ]; then
                P_EPOCH=$(date -d "$(echo "$P_DATE" | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')" +%s 2>/dev/null || echo 0)
                C_EPOCH=$(date -d "$(echo "$C_DATE" | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')" +%s 2>/dev/null || echo 0)
                DIFF=$(( (C_EPOCH - P_EPOCH) / 86400 ))
                if [ "$DIFF" -gt 1 ] 2>/dev/null; then
                    echo "  GAP: ${DIFF} days between $PREV_STAMP ($PREV_DEV) → $TS ($DEV_R)"
                    GAPS=$((GAPS + 1))
                fi
            fi
            PREV_STAMP="$TS"
            PREV_DEV="$DEV_R"
        done < "$RACE_OUT"

        [ "$GAPS" -eq 0 ] && echo "  No gaps > 24h detected"
        echo "  Total gaps found: $GAPS"
        exit 0
        ;;

    tick|*)
        # Positional: sagco-race [device] [event]
        # If first arg is a device name, use it
        TICK_DEV="$DEV"
        TICK_EVENT="sagco_race_tick"

        if [ "$CMD" != "tick" ]; then
            case "$CMD" in
                ish|ipad|termux|zfold|linux|android) TICK_DEV="$CMD" ;;
                *) TICK_EVENT="$CMD" ;;
            esac
        fi
        [ -n "$2" ] && TICK_EVENT="$2"
        ;;
esac

# ── write tick ────────────────────────────────────────────────────────────────
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)

[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${TICK_DEV},${TICK_EVENT},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

HASH=$(echo "${STAMP}sagco-race${TICK_DEV}${TICK_EVENT}" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${TICK_DEV},sagco-race,${TICK_EVENT},${HASH},SAGCO_RACE_TICK" >> "$LEDGER"

echo "SAGCO RACE TICK"
echo "==============="
printf "  %-12s %s\n" "Stamp:"  "$STAMP"
printf "  %-12s %s\n" "Device:" "$TICK_DEV"
printf "  %-12s %s\n" "Event:"  "$TICK_EVENT"
printf "  %-12s %s\n" "PWD:"    "$PWD"
printf "  %-12s %s%%\n" "Battery:" "$BAT"
echo ""
echo "STATUS=SAGCO_RACE_TICK"
