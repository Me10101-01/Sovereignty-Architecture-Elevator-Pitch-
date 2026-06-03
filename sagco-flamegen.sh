#!/bin/sh
# sagco-flamegen — FlameLang Evolutionary Token Generator
# Reads fleet telemetry → discovers recurring patterns → evolves FlameLang vocabulary.
#
# The loop:
#   Observation → Pattern → Token → Opcode → Behavior → Telemetry → Observation
#
# This is the difference between a static language (manually defined glyphs)
# and an evolutionary one (tokens emerge from what the fleet actually observes).
#
# FlameLang v1.0 = static: you define glyphs manually
# FlameLang v2.0 = evolutionary: fleet observations become the vocabulary
#
# Usage:
#   sagco-flamegen scan        → analyze race_log for recurring patterns
#   sagco-flamegen evolve      → generate tokens from high-frequency patterns
#   sagco-flamegen vocab       → show current evolved vocabulary
#   sagco-flamegen bind <tok> <cmd>  → bind a token to a SAGCO behavior
#   sagco-flamegen dispatch    → scan new telemetry, fire bound behaviors
#   sagco-flamegen report      → full evolutionary report

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
VOCAB_FILE="$HOME/sagco_fleet/flamelang_evolved_vocab.csv"
BIND_FILE="$HOME/sagco_fleet/flamelang_bindings.csv"
DISPATCH_LOG="$HOME/sagco_fleet/flamelang_dispatch.csv"
RACE_OUT="$HOME/sagco_race/race_log.csv"
LEDGER_OUT="$HOME/sagco_ledger.csv"

# Frequency threshold: event must appear this many times to earn a token
EVOLVE_THRESHOLD="${FLAMEGEN_THRESHOLD:-3}"

mkdir -p "$HOME/sagco_fleet"

# ── compress event name to short token ───────────────────────────────────────
# sagco_race_tick → rtk
# sagco_brain_checkpoint → brn_chk
# boss_battle_fix → btl_fix
compress_token() {
    EVENT="$1"
    echo "$EVENT" | sed \
        -e 's/sagco_//' \
        -e 's/_tick$//' \
        -e 's/race/rtk/' \
        -e 's/brain/brn/' \
        -e 's/cloud_ping/cpng/' \
        -e 's/node_register/nreg/' \
        -e 's/boss_battle/btl/' \
        -e 's/prometheus/prom/' \
        -e 's/attribution/attr/' \
        -e 's/checkpoint/chk/' \
        -e 's/heartbeat/hbt/' \
        -e 's/classify/cls/' \
        -e 's/refinery/rfn/' \
        -e 's/excavate/exc/' \
        -e 's/contract/ctr/' \
        -e 's/provision/prv/' \
        -e 's/identity/id/' \
        -e 's/provenance/prov/' \
        -e 's/antibody/abt/' \
        -e 's/verification/vfy/' \
        -e 's/_/-/g' | \
        cut -c1-12
}

# ── map token to wave frequency (Hz) ─────────────────────────────────────────
# Based on SAGCO sheet music model: opcode → MIDI → Hz
token_hz() {
    TOKEN="$1"
    # Simple hash to stable MIDI note (36-84), then to Hz
    MIDI=$(echo "$TOKEN" | cksum | awk '{print 36 + ($1 % 48)}')
    # Hz = 440 * 2^((MIDI-69)/12)
    echo "scale=1; 440 * e(($MIDI - 69) * 0.057762 * l(2))" | \
        bc -l 2>/dev/null | cut -c1-6 || echo "${MIDI}.0"
}

# ── scan: find recurring patterns in telemetry ───────────────────────────────
cmd_scan() {
    echo "FLAMEGEN SCAN — Fleet Telemetry Pattern Analysis"
    echo "================================================="
    echo "Threshold: $EVOLVE_THRESHOLD occurrences to earn a token"
    echo ""

    [ -f "$RACE_LOG" ] || { echo "  No race_log found."; return; }

    echo "  Top patterns in race_log:"
    printf "  %-35s %-8s %s\n" "EVENT" "COUNT" "TOKEN_CANDIDATE"
    echo "  ──────────────────────────────────────────────────────────"

    awk -F',' 'NR>1 {print $3}' "$RACE_LOG" 2>/dev/null | \
        sort | uniq -c | sort -rn | head -20 | \
        while read COUNT EVENT; do
            TOKEN=$(compress_token "$EVENT")
            MARKER=""
            [ "$COUNT" -ge "$EVOLVE_THRESHOLD" ] && MARKER="→ TOKEN"
            printf "  %-35s %-8d %s %s\n" "$EVENT" "$COUNT" "$TOKEN" "$MARKER"
        done

    echo ""
    echo "  Per-device pattern density:"
    printf "  %-15s %-8s %-8s %s\n" "DEVICE" "EVENTS" "UNIQUE" "DENSITY"
    echo "  ─────────────────────────────────────────────────"
    awk -F',' 'NR>1 {print $2}' "$RACE_LOG" 2>/dev/null | \
        sort | uniq -c | sort -rn | head -10 | \
        while read TOTAL DEV_NAME; do
            UNIQUE=$(grep ",${DEV_NAME}," "$RACE_LOG" 2>/dev/null | \
                awk -F',' '{print $3}' | sort -u | wc -l)
            [ "$UNIQUE" -gt 0 ] && DENSITY=$(echo "scale=1; $TOTAL / $UNIQUE" | \
                bc 2>/dev/null || echo "?") || DENSITY=1
            printf "  %-15s %-8d %-8d %.1f\n" "$DEV_NAME" "$TOTAL" "$UNIQUE" "$DENSITY"
        done
}

# ── evolve: generate tokens from patterns above threshold ────────────────────
cmd_evolve() {
    echo "FLAMEGEN EVOLVE — Token Emergence"
    echo "==================================="
    echo ""

    [ -f "$RACE_LOG" ] || { echo "  No race_log — nothing to evolve from."; return; }

    [ -f "$VOCAB_FILE" ] || \
        echo "timestamp,token,full_event,count,first_seen,device,hz,status" > "$VOCAB_FILE"

    NEW=0; EXISTING=0

    awk -F',' 'NR>1 {print $3}' "$RACE_LOG" 2>/dev/null | \
        sort | uniq -c | sort -rn | \
        while read COUNT EVENT; do
            [ "$COUNT" -lt "$EVOLVE_THRESHOLD" ] && continue

            TOKEN=$(compress_token "$EVENT")
            HZ=$(token_hz "$TOKEN")

            # Find first occurrence
            FIRST=$(grep ",$EVENT," "$RACE_LOG" 2>/dev/null | head -1 | cut -d',' -f1)
            # Find which device runs this most
            TOP_DEV=$(grep ",$EVENT," "$RACE_LOG" 2>/dev/null | \
                awk -F',' '{print $2}' | sort | uniq -c | sort -rn | \
                head -1 | awk '{print $2}')

            # Skip if already in vocab
            if [ -f "$VOCAB_FILE" ] && grep -q ",$TOKEN," "$VOCAB_FILE" 2>/dev/null; then
                printf "  🔵 %-12s  already evolved (count=%d)\n" "$TOKEN" "$COUNT"
                continue
            fi

            echo "${STAMP},${TOKEN},${EVENT},${COUNT},${FIRST:-$STAMP},${TOP_DEV:-unknown},${HZ},EVOLVED" \
                >> "$VOCAB_FILE"
            printf "  ✅ %-12s  ← %-30s (n=%d  Hz=%.1f)\n" \
                "$TOKEN" "$EVENT" "$COUNT" "${HZ:-0}"
            NEW=$((NEW + 1))
        done

    echo ""
    echo "  Vocab file: $VOCAB_FILE"
    [ "$NEW" -eq 0 ] && echo "  (no new tokens — run more race ticks to build frequency)"
}

# ── vocab: show current evolved vocabulary ───────────────────────────────────
cmd_vocab() {
    echo "FLAMELANG EVOLVED VOCABULARY"
    echo "============================="
    echo ""

    if [ ! -f "$VOCAB_FILE" ] || [ "$(wc -l < "$VOCAB_FILE")" -le 1 ]; then
        echo "  No evolved tokens yet."
        echo "  Run: sagco-flamegen evolve"
        echo ""
        echo "  FlameLang v1.0 static tokens (from spec):"
        printf "  %-12s %-8s %s\n" "TOKEN" "HZ" "MEANING"
        echo "  ─────────────────────────────────────────"
        printf "  %-12s %-8s %s\n" "⟐"   "432"  "temporal modifier"
        printf "  %-12s %-8s %s\n" "🔥"  "528"  "flamelang namespace"
        printf "  %-12s %-8s %s\n" "⚔"   "639"  "command ready"
        printf "  %-12s %-8s %s\n" "🧠"  "741"  "right hemisphere"
        return
    fi

    printf "  %-14s %-30s %-8s %-8s %-8s %s\n" \
        "TOKEN" "EMERGED_FROM" "COUNT" "HZ" "DEVICE" "STATUS"
    echo "  ──────────────────────────────────────────────────────────────────"
    tail -n +2 "$VOCAB_FILE" 2>/dev/null | sort -t',' -k4 -rn | \
        while IFS=',' read TS TOKEN EVENT COUNT FIRST DEV HZ STAT; do
            BOUND=""
            [ -f "$BIND_FILE" ] && grep -q ",${TOKEN}," "$BIND_FILE" 2>/dev/null && BOUND="⚡"
            printf "  %-14s %-30s %-8s %-8s %-8s %s\n" \
                "$TOKEN$BOUND" "$EVENT" "$COUNT" "$HZ" "$DEV" "$STAT"
        done
    echo ""

    TOTAL=$(grep -c "EVOLVED" "$VOCAB_FILE" 2>/dev/null || echo 0)
    BOUND_COUNT=$([ -f "$BIND_FILE" ] && grep -c "BOUND" "$BIND_FILE" 2>/dev/null || echo 0)
    echo "  Total tokens: $TOTAL   Bound to behaviors: $BOUND_COUNT   ⚡ = behavior bound"
}

# ── bind: attach a behavior to a token ───────────────────────────────────────
cmd_bind() {
    TOKEN="$1"; CMD="$2"
    [ -z "$TOKEN" ] || [ -z "$CMD" ] && {
        echo "Usage: sagco-flamegen bind <token> <sagco-command>"
        echo "Example: sagco-flamegen bind btl-fix 'sagco-boss-battle fix'"
        return 1
    }

    [ -f "$BIND_FILE" ] || \
        echo "timestamp,token,command,device,status" > "$BIND_FILE"

    # Remove old binding for this token
    TMP="${BIND_FILE}.tmp"
    grep -v ",${TOKEN}," "$BIND_FILE" 2>/dev/null > "$TMP" && mv "$TMP" "$BIND_FILE"

    echo "${STAMP},${TOKEN},${CMD},${DEV},BOUND" >> "$BIND_FILE"
    echo "  Bound: $TOKEN → $CMD"
    echo ""
    echo "  WHEN $TOKEN appears in telemetry"
    echo "  THEN $CMD"
    echo ""
    echo "  Activate: sagco-flamegen dispatch"
}

# ── dispatch: scan latest telemetry, fire bound behaviors ────────────────────
cmd_dispatch() {
    echo "FLAMEGEN DISPATCH — Behavior Firing"
    echo "====================================="
    echo ""

    [ -f "$BIND_FILE" ] || { echo "  No bindings defined. Run: sagco-flamegen bind"; return; }
    [ -f "$RACE_LOG" ] || { echo "  No race_log."; return; }

    [ -f "$DISPATCH_LOG" ] || \
        echo "timestamp,token,event,command,fired,status" > "$DISPATCH_LOG"

    # Get last 50 events from race_log
    RECENT=$(tail -50 "$RACE_LOG" 2>/dev/null | awk -F',' '{print $3}')

    FIRED=0

    tail -n +2 "$BIND_FILE" 2>/dev/null | while IFS=',' read TS TOKEN CMD DEV STAT; do
        [ "$STAT" = "BOUND" ] || continue

        # Find the full event that maps to this token
        MATCHED_EVENT=$(tail -n +2 "$VOCAB_FILE" 2>/dev/null | \
            awk -F',' -v t="$TOKEN" '$2==t{print $3}' | head -1)
        [ -z "$MATCHED_EVENT" ] && continue

        # Check if this event appeared in recent telemetry
        if echo "$RECENT" | grep -q "$MATCHED_EVENT"; then
            echo "  ⚡ TOKEN: $TOKEN"
            echo "     event: $MATCHED_EVENT"
            echo "     firing: $CMD"

            # Record dispatch
            echo "${STAMP},${TOKEN},${MATCHED_EVENT},${CMD},YES,SAGCO_DISPATCH_FIRED" \
                >> "$DISPATCH_LOG"

            # Fire it (dry-run safe: just echo the command)
            if [ "${FLAMEGEN_DRY_RUN:-1}" = "1" ]; then
                echo "     [DRY-RUN] would execute: $CMD"
                echo "     set FLAMEGEN_DRY_RUN=0 to enable live dispatch"
            else
                eval "$CMD" 2>/dev/null && \
                    echo "     FIRED: $CMD" || \
                    echo "     FAILED: $CMD"
            fi
            echo ""
        fi
    done

    echo "  Dispatch log: $DISPATCH_LOG"
}

# ── full evolutionary report ──────────────────────────────────────────────────
cmd_report() {
    echo "FLAMELANG EVOLUTION REPORT"
    echo "==========================="
    echo "Stamp:  $STAMP"
    echo "Device: $DEV"
    echo ""

    echo "  The Evolutionary Cycle"
    echo "  ──────────────────────────────────────────────────────"
    echo ""
    echo "  Source Code         (sagco commands, Rust, shell)"
    echo "       ↓"
    echo "  Execution            (race ticks, artifacts, telemetry)"
    echo "       ↓"
    echo "  Pattern Detection    (this scan)"
    echo "       ↓"
    echo "  Token Emergence      (compress_token, threshold-gated)"
    echo "       ↓"
    echo "  Vocabulary Growth    (flamelang_evolved_vocab.csv)"
    echo "       ↓"
    echo "  Behavior Binding     (WHEN token THEN command)"
    echo "       ↓"
    echo "  Dispatch + New Ticks (loop closes)"
    echo ""

    echo "  Current Vocabulary State"
    echo "  ──────────────────────────────────────────────────────"

    TOTAL_EVENTS=0
    UNIQUE_EVENTS=0
    [ -f "$RACE_LOG" ] && {
        TOTAL_EVENTS=$(( $(wc -l < "$RACE_LOG" 2>/dev/null || echo 1) - 1 ))
        UNIQUE_EVENTS=$(awk -F',' 'NR>1{print $3}' "$RACE_LOG" 2>/dev/null | sort -u | wc -l)
    }
    EVOLVED=$([ -f "$VOCAB_FILE" ] && grep -c "EVOLVED" "$VOCAB_FILE" 2>/dev/null || echo 0)
    BOUND=$([ -f "$BIND_FILE" ] && grep -c "BOUND" "$BIND_FILE" 2>/dev/null || echo 0)
    DISPATCHED=$([ -f "$DISPATCH_LOG" ] && grep -c "FIRED" "$DISPATCH_LOG" 2>/dev/null || echo 0)

    printf "  %-35s %d\n" "Total telemetry events:"     "$TOTAL_EVENTS"
    printf "  %-35s %d\n" "Unique event types:"         "$UNIQUE_EVENTS"
    printf "  %-35s %d\n" "Evolved tokens:"             "$EVOLVED"
    printf "  %-35s %d\n" "Tokens with behavior binds:" "$BOUND"
    printf "  %-35s %d\n" "Dispatch fires:"             "$DISPATCHED"
    echo ""

    COVERAGE=0
    [ "$UNIQUE_EVENTS" -gt 0 ] && \
        COVERAGE=$(echo "scale=0; $EVOLVED * 100 / $UNIQUE_EVENTS" | bc 2>/dev/null || echo 0)
    echo "  Token coverage: ${COVERAGE}% of unique event types have a token"
    echo ""

    if [ "$EVOLVED" -gt 0 ]; then
        echo "  Most frequent evolved tokens:"
        tail -n +2 "$VOCAB_FILE" 2>/dev/null | sort -t',' -k4 -rn | head -5 | \
            awk -F',' '{printf "  %-14s count=%-8s hz=%s\n", $2, $4, $7}'
    fi

    echo ""
    echo "  STATUS=SAGCO_FLAMEGEN_REPORT_COMPLETE"
}

# ── race tick ─────────────────────────────────────────────────────────────────
write_tick() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
    echo "${STAMP},${DEV},sagco_flamegen_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"
    HASH=$(echo "${STAMP}sagco-flamegen${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER_OUT" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER_OUT"
    echo "${STAMP},${DEV},sagco-flamegen,${VOCAB_FILE},${HASH},SAGCO_FLAMEGEN_PASS" >> "$LEDGER_OUT"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-report}"

case "$CMD" in
    scan)      cmd_scan;              write_tick ;;
    evolve)    cmd_evolve;            write_tick ;;
    vocab)     cmd_vocab;             write_tick ;;
    bind)      cmd_bind "${2:-}" "${3:-}"; write_tick ;;
    dispatch)  cmd_dispatch;          write_tick ;;
    report|"") cmd_report;            write_tick ;;
    *)
        echo "Usage: sagco-flamegen [scan|evolve|vocab|bind|dispatch|report]"
        echo ""
        echo "  scan            analyze race_log for recurring patterns"
        echo "  evolve          generate tokens from high-frequency patterns"
        echo "  vocab           show current evolved vocabulary"
        echo "  bind <tok> <c>  WHEN token THEN sagco-command"
        echo "  dispatch        fire bound behaviors from latest telemetry"
        echo "  report          full evolutionary report"
        echo ""
        echo "  FLAMEGEN_THRESHOLD=3   (default: 3 occurrences = token)"
        echo "  FLAMEGEN_DRY_RUN=0     (default: 1 = dry run, 0 = live fire)"
        exit 1
        ;;
esac
