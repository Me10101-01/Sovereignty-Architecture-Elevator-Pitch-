#!/bin/sh
# sagco-todo — SAGCO Corpus Task Scanner
# Reads all Acts, specs, and docs for declared Missing Bricks.
# Any node can run this and know what the fleet has left unfinished.
#
# The Book of Provenance is not just history.
# It is history + roadmap + specification + memory + task queue.
#
# Every Act with a "Missing Bricks" section declares:
#   - what exists (✅)
#   - what is partial (🟡)
#   - what is not built (⬜)
#   - what is blocked and why
#
# Usage:
#   sagco-todo                → full TODO across all Acts
#   sagco-todo unfinished     → only ⬜ and 🟡 items
#   sagco-todo blocked        → items with declared blockers
#   sagco-todo ready          → unblocked items that can start now
#   sagco-todo add <doc> <item> <status>  → declare a missing brick
#   sagco-todo next           → single highest-priority unblocked item

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
CORPUS_DIR="${SAGCO_CORPUS:-$PWD}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
TODO_CACHE="$HOME/sagco_fleet/sagco_todo_cache.csv"

mkdir -p "$HOME/sagco_fleet"

# ── scan a file for missing bricks table entries ──────────────────────────────
# Looks for markdown table rows after "## Missing Bricks" header
parse_missing_bricks() {
    FILE="$1"
    DOCNAME=$(basename "$FILE" .md)
    IN_TABLE=0
    IN_MISSING=0

    while IFS= read -r LINE; do
        # Enter missing bricks section
        echo "$LINE" | grep -qi "## missing bricks" && IN_MISSING=1 && continue
        # Exit if we hit another ## section
        echo "$LINE" | grep -q "^## " && [ "$IN_MISSING" -eq 1 ] && \
            [ -z "$(echo "$LINE" | grep -i 'missing')" ] && IN_MISSING=0 && continue
        [ "$IN_MISSING" -eq 0 ] && continue

        # Parse table rows: | Brick | Status | Depends On |
        echo "$LINE" | grep -q "^|" || continue
        echo "$LINE" | grep -q "---|---" && continue
        echo "$LINE" | grep -qi "brick\|status\|depends" && continue

        # Extract columns
        BRICK=$(echo "$LINE" | awk -F'|' '{print $2}' | sed 's/^ *//;s/ *$//')
        STATUS=$(echo "$LINE" | awk -F'|' '{print $3}' | sed 's/^ *//;s/ *$//')
        DEPENDS=$(echo "$LINE" | awk -F'|' '{print $4}' | sed 's/^ *//;s/ *$//')

        [ -z "$BRICK" ] && continue

        # Classify
        case "$STATUS" in
            *✅*) CLASS="done" ;;
            *🟡*) CLASS="partial" ;;
            *⬜*) CLASS="missing" ;;
            *🔴*) CLASS="blocked" ;;
            *)    CLASS="unknown" ;;
        esac

        printf "%s|%s|%s|%s|%s|%s\n" \
            "$DOCNAME" "$BRICK" "$STATUS" "$DEPENDS" "$CLASS" "$STAMP"
    done < "$FILE"
}

# ── scan all docs in corpus ───────────────────────────────────────────────────
scan_corpus() {
    find "$CORPUS_DIR" -maxdepth 2 \( -name "SAGCO*.md" -o -name "sagco-*.md" \) \
        -not -path '*/.git/*' 2>/dev/null | sort | while read F; do
        parse_missing_bricks "$F"
    done
}

# ── rebuild cache ─────────────────────────────────────────────────────────────
rebuild_cache() {
    echo "doc|brick|status|depends|class|cached_at" > "$TODO_CACHE"
    scan_corpus >> "$TODO_CACHE"
}

# ── full TODO ─────────────────────────────────────────────────────────────────
cmd_full() {
    rebuild_cache
    echo "SAGCO TODO — Corpus Task Scanner"
    echo "=================================="
    echo "Stamp:  $STAMP"
    echo "Device: $DEV"
    echo "Corpus: $CORPUS_DIR"
    echo ""

    TOTAL=0; DONE=0; PARTIAL=0; MISSING=0; BLOCKED=0

    # Group by doc
    DOCS=$(tail -n +2 "$TODO_CACHE" 2>/dev/null | cut -d'|' -f1 | sort -u)
    echo "$DOCS" | while read DOC; do
        [ -z "$DOC" ] && continue
        echo "  [$DOC]"
        grep "^${DOC}|" "$TODO_CACHE" 2>/dev/null | while IFS='|' read D BRICK STATUS DEPENDS CLASS TS; do
            case "$CLASS" in
                done)    ICON="✅" ;;
                partial) ICON="🟡" ;;
                missing) ICON="⬜" ;;
                blocked) ICON="🔴" ;;
                *)       ICON="?" ;;
            esac
            printf "  %s %-45s" "$ICON" "$BRICK"
            [ -n "$DEPENDS" ] && printf " ← %s" "$DEPENDS"
            printf "\n"
        done
        echo ""
    done

    TOTAL=$(tail -n +2 "$TODO_CACHE" 2>/dev/null | wc -l)
    DONE=$(grep "|done|" "$TODO_CACHE" 2>/dev/null | wc -l)
    PARTIAL=$(grep "|partial|" "$TODO_CACHE" 2>/dev/null | wc -l)
    MISSING=$(grep "|missing|" "$TODO_CACHE" 2>/dev/null | wc -l)
    BLOCKED=$(grep "|blocked|" "$TODO_CACHE" 2>/dev/null | wc -l)

    echo "  ─────────────────────────────────────────────────────────"
    printf "  ✅ Done:     %d\n" "$DONE"
    printf "  🟡 Partial:  %d\n" "$PARTIAL"
    printf "  ⬜ Missing:  %d\n" "$MISSING"
    printf "  🔴 Blocked:  %d\n" "$BLOCKED"
    printf "  Total:       %d declared missing bricks\n" "$TOTAL"
    echo ""
    echo "  Run: sagco-todo ready  → what can start now"
    echo "       sagco-todo next   → single highest-priority item"
}

# ── unfinished only ───────────────────────────────────────────────────────────
cmd_unfinished() {
    rebuild_cache
    echo "SAGCO TODO — Unfinished Only"
    echo "=============================="
    echo ""
    grep "|partial|\||missing|" "$TODO_CACHE" 2>/dev/null | \
        while IFS='|' read DOC BRICK STATUS DEPENDS CLASS TS; do
            ICON="⬜"; [ "$CLASS" = "partial" ] && ICON="🟡"
            printf "  %s [%-35s] %s\n" "$ICON" "$DOC" "$BRICK"
            [ -n "$DEPENDS" ] && printf "       depends: %s\n" "$DEPENDS"
        done
}

# ── blocked items ─────────────────────────────────────────────────────────────
cmd_blocked() {
    rebuild_cache
    echo "SAGCO TODO — Blocked"
    echo "======================"
    echo ""
    # Items with BLOCKED_BY in status field or marked 🔴
    grep "|blocked\||🔴" "$TODO_CACHE" 2>/dev/null | \
        while IFS='|' read DOC BRICK STATUS DEPENDS CLASS TS; do
            printf "  🔴 [%-35s] %s\n" "$DOC" "$BRICK"
            [ -n "$DEPENDS" ] && printf "       blocked by: %s\n" "$DEPENDS"
        done

    echo ""
    # Also scan Acts for BLOCKED_BY= declarations
    echo "  Declared blockers in Acts:"
    find "$CORPUS_DIR" -maxdepth 2 -name "SAGCO*.md" -not -path '*/.git/*' 2>/dev/null | \
        xargs grep -h "BLOCKED_BY=" 2>/dev/null | \
        while read LINE; do
            printf "    %s\n" "$LINE"
        done
}

# ── ready: unblocked items that can start now ─────────────────────────────────
cmd_ready() {
    rebuild_cache
    echo "SAGCO TODO — Ready to Build"
    echo "============================"
    echo "Items with no declared blockers:"
    echo ""

    grep "|missing|\||partial|" "$TODO_CACHE" 2>/dev/null | \
        while IFS='|' read DOC BRICK STATUS DEPENDS CLASS TS; do
            # Skip if depends field mentions a blocker keyword
            BLOCKED_SIGNAL=$(echo "$DEPENDS" | grep -i "pending\|blocked\|hardware\|acquisition")
            [ -n "$BLOCKED_SIGNAL" ] && continue

            ICON="⬜"; [ "$CLASS" = "partial" ] && ICON="🟡"
            printf "  %s [%-35s] %s\n" "$ICON" "$DOC" "$BRICK"
            [ -n "$DEPENDS" ] && printf "       requires: %s\n" "$DEPENDS"
        done
    echo ""
}

# ── next: single highest priority item ───────────────────────────────────────
cmd_next() {
    rebuild_cache

    # Priority: partial first (already started), then missing with no blocker
    NEXT=$(grep "|partial|" "$TODO_CACHE" 2>/dev/null | \
        grep -v "pending\|blocked\|hardware\|acquisition" | head -1)
    [ -z "$NEXT" ] && NEXT=$(grep "|missing|" "$TODO_CACHE" 2>/dev/null | \
        grep -v "pending\|blocked\|hardware\|acquisition" | head -1)

    [ -z "$NEXT" ] && echo "  No ready items found." && return

    DOC=$(echo "$NEXT" | cut -d'|' -f1)
    BRICK=$(echo "$NEXT" | cut -d'|' -f2)
    STATUS=$(echo "$NEXT" | cut -d'|' -f3)
    DEPENDS=$(echo "$NEXT" | cut -d'|' -f4)

    echo "SAGCO NEXT BRICK"
    echo "================="
    printf "  Source:  %s\n" "$DOC"
    printf "  Brick:   %s\n" "$BRICK"
    printf "  Status:  %s\n" "$STATUS"
    [ -n "$DEPENDS" ] && printf "  Needs:   %s\n" "$DEPENDS"
    echo ""
    echo "  This is the highest-priority unblocked item in the corpus."
}

# ── add: declare a missing brick to a doc ────────────────────────────────────
cmd_add() {
    DOC="$1"; BRICK="$2"; STATUS_ARG="${3:-⬜ not built}"
    [ -z "$DOC" ] || [ -z "$BRICK" ] && {
        echo "Usage: sagco-todo add <doc_name> <brick> [status]"
        return 1
    }

    FILE=$(find "$CORPUS_DIR" -maxdepth 2 -name "${DOC}*" -not -path '*/.git/*' 2>/dev/null | head -1)
    [ -z "$FILE" ] && { echo "  Doc not found: $DOC"; return 1; }

    # Check if Missing Bricks section exists
    if ! grep -q "## Missing Bricks" "$FILE" 2>/dev/null; then
        cat >> "$FILE" << BRICKS

---

## Missing Bricks

| Brick | Status | Depends On |
|---|---|---|
BRICKS
    fi

    # Append the new row
    echo "| $BRICK | $STATUS_ARG | — |" >> "$FILE"
    echo "  Added to $FILE:"
    echo "  | $BRICK | $STATUS_ARG | — |"
}

# ── race tick ─────────────────────────────────────────────────────────────────
write_tick() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_todo_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
    HASH=$(echo "${STAMP}sagco-todo${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-todo,${TODO_CACHE},${HASH},SAGCO_TODO_PASS" >> "$LEDGER"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-full}"

case "$CMD" in
    full|"")    cmd_full;             write_tick ;;
    unfinished) cmd_unfinished;       write_tick ;;
    blocked)    cmd_blocked;          write_tick ;;
    ready)      cmd_ready;            write_tick ;;
    next)       cmd_next;             write_tick ;;
    add)        cmd_add "${2:-}" "${3:-}" "${4:-}"; write_tick ;;
    *)
        echo "Usage: sagco-todo [full|unfinished|blocked|ready|next|add]"
        echo ""
        echo "  full         all declared missing bricks across corpus"
        echo "  unfinished   ⬜ missing + 🟡 partial only"
        echo "  blocked      items with declared blockers"
        echo "  ready        unblocked items that can start now"
        echo "  next         single highest-priority unblocked item"
        echo "  add <doc> <brick> [status]  declare a missing brick"
        echo ""
        echo "  The Acts are the source of truth."
        echo "  Missing Bricks sections are the task queue."
        echo "  Any node can read this and know what to build next."
        exit 1
        ;;
esac
