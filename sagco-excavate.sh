#!/bin/sh
# sagco-excavate — SAGCO Provenance Archaeologist
# The attribution engine is no longer creating provenance.
# It is discovering provenance that already exists.
#
# Every artifact that contains STATUS=SAGCO_*, DEVICE=, TIMESTAMP=,
# GPG_KEY=, SSH_KEY=, TEAM= already carries its own identity.
# This is a migration problem, not an invention problem.
#
# Usage:
#   sagco-excavate scan              → find all artifacts with embedded provenance
#   sagco-excavate extract <file>    → pull every provenance field from one file
#   sagco-excavate diff              → ledger vs discoverable artifacts (the gap)
#   sagco-excavate migrate           → scan → extract → register → verify
#   sagco-excavate report            → full excavation report
#
# What it finds:
#   Gen 1: script.sh — no identity, no timestamp
#   Gen 2: sagco-cell — STATUS= TIMESTAMP= already embedded
#   Gen 3: full DNA — DEVICE + GPG + SSH + TEAM + TIMESTAMP + HASH

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
LEDGER="$HOME/sagco_ledger.csv"
RACE_LOG="$HOME/sagco_race/race_log.csv"
CHAIN_LOG="$HOME/sagco_fleet/provenance_chain.csv"
EXCAVATION_LOG="$HOME/sagco_fleet/excavation_log.csv"
REPO="${1:-$PWD}"

mkdir -p "$HOME/sagco_fleet"

# ── provenance pattern matchers ───────────────────────────────────────────────
# Returns value or empty string
extract_field() {
    FILE="$1"; PATTERN="$2"
    grep -m1 "$PATTERN" "$FILE" 2>/dev/null | \
        sed 's/.*'"$PATTERN"'[=: ]*//' | \
        sed 's/["'"'"'#]//g' | \
        tr -d ' \r' | head -1
}

# ── generation classifier ─────────────────────────────────────────────────────
# Gen 1: no provenance markers at all
# Gen 2: has STATUS= or TIMESTAMP= but missing device/gpg
# Gen 3: has device + identity + timestamp (full DNA)
classify_gen() {
    FILE="$1"
    HAS_STATUS=$(grep -c "STATUS=SAGCO_" "$FILE" 2>/dev/null || echo 0)
    HAS_DEVICE=$(grep -c "DEVICE=" "$FILE" 2>/dev/null || echo 0)
    HAS_GPG=$(grep -c -i "gpg_key\|GPG_KEY\|AE5519" "$FILE" 2>/dev/null || echo 0)
    HAS_TS=$(grep -c "TIMESTAMP=\|timestamp:\|_[0-9]\{8\}_" "$FILE" 2>/dev/null || echo 0)

    if [ "$HAS_DEVICE" -gt 0 ] && [ "$HAS_GPG" -gt 0 ] && [ "$HAS_TS" -gt 0 ]; then
        echo 3
    elif [ "$HAS_STATUS" -gt 0 ] || [ "$HAS_TS" -gt 0 ]; then
        echo 2
    else
        echo 1
    fi
}

# ── extract all provenance fields from one file ───────────────────────────────
cmd_extract() {
    FILE="$1"
    [ -f "$FILE" ] || { echo "  ERROR: file not found: $FILE"; return 1; }

    echo "SAGCO EXCAVATION — $FILE"
    echo "=============================="

    STATUS_V=$(extract_field "$FILE" "STATUS=SAGCO_")
    DEVICE_V=$(extract_field "$FILE" "DEVICE=")
    TEAM_V=$(extract_field "$FILE" "TEAM=")
    TS_V=$(extract_field "$FILE" "TIMESTAMP=")
    GPG_V=$(extract_field "$FILE" "GPG_KEY=\|gpg_key:")
    SSH_V=$(extract_field "$FILE" "SSH_KEY=\|ssh_key:")
    REPORT_V=$(extract_field "$FILE" "REPORT=")
    HASH_V=$(extract_field "$FILE" "HASH=")

    GEN=$(classify_gen "$FILE")

    printf "  %-18s %s\n" "generation:"  "Gen $GEN"
    printf "  %-18s %s\n" "status:"      "${STATUS_V:-not found}"
    printf "  %-18s %s\n" "device:"      "${DEVICE_V:-not found}"
    printf "  %-18s %s\n" "team:"        "${TEAM_V:-not found}"
    printf "  %-18s %s\n" "timestamp:"   "${TS_V:-not found}"
    printf "  %-18s %s\n" "gpg_key:"     "${GPG_V:-not found}"
    printf "  %-18s %s\n" "ssh_key:"     "${SSH_V:-not found}"
    printf "  %-18s %s\n" "report:"      "${REPORT_V:-not found}"
    printf "  %-18s %s\n" "hash:"        "${HASH_V:-not found}"
    echo ""

    case "$GEN" in
        3) echo "  ✅ Gen 3 — full provenance DNA present" ;;
        2) echo "  🟡 Gen 2 — partial provenance, migration needed" ;;
        1) echo "  ⬜ Gen 1 — no provenance markers found" ;;
    esac
}

# ── scan: find all files with embedded provenance ────────────────────────────
cmd_scan() {
    echo "SAGCO EXCAVATION SCAN"
    echo "======================="
    echo "Root:   $REPO"
    echo "Stamp:  $STAMP"
    echo ""

    GEN1=0; GEN2=0; GEN3=0; TOTAL=0

    printf "  %-50s %s\n" "FILE" "GEN"
    echo "  ──────────────────────────────────────────────────────────"

    find "$REPO" -type f \( -name "*.sh" -o -name "*.yaml" -o -name "*.yml" \
        -o -name "*.md" -o -name "*.rs" -o -name "*.py" -o -name "*.html" \) \
        -not -path '*/.git/*' 2>/dev/null | sort | while read FILE; do

        GEN=$(classify_gen "$FILE")
        TOTAL=$((TOTAL + 1))

        case "$GEN" in
            3) printf "  %-50s Gen 3 ✅\n" "$(basename "$FILE")" ; echo "$FILE" >> /tmp/sagco_exc_gen3 ;;
            2) printf "  %-50s Gen 2 🟡\n" "$(basename "$FILE")" ; echo "$FILE" >> /tmp/sagco_exc_gen2 ;;
            1) : ;; # Silent for gen1 — too many
        esac
    done

    G3=$(wc -l < /tmp/sagco_exc_gen3 2>/dev/null || echo 0)
    G2=$(wc -l < /tmp/sagco_exc_gen2 2>/dev/null || echo 0)
    G1=$(($(find "$REPO" -type f \( -name "*.sh" -o -name "*.yaml" -o -name "*.md" \) \
        -not -path '*/.git/*' 2>/dev/null | wc -l) - G3 - G2))

    echo ""
    echo "  ─────────────────────────────────────────────────────────"
    printf "  Gen 3 (full DNA):     %d files ✅\n" "$G3"
    printf "  Gen 2 (partial):      %d files 🟡\n" "$G2"
    printf "  Gen 1 (no markers):   %d files ⬜\n" "$G1"
    echo ""
    echo "  Gen 3 artifacts already carry:"
    echo "    DEVICE + GPG_KEY + SSH_KEY + TIMESTAMP"
    echo "  Gen 2 artifacts need:"
    echo "    device attribution + identity link"
    echo "  Gen 1 artifacts need:"
    echo "    full migration or are external/library files"
    echo ""

    rm -f /tmp/sagco_exc_gen3 /tmp/sagco_exc_gen2
}

# ── diff: ledger vs discoverable (the migration gap) ─────────────────────────
cmd_diff() {
    echo "SAGCO EXCAVATION DIFF"
    echo "======================="
    echo "The gap between what's in the ledger and what's discoverable."
    echo ""

    # Count artifacts known to ledger
    LEDGER_COUNT=0
    [ -f "$LEDGER" ] && LEDGER_COUNT=$(( $(wc -l < "$LEDGER" 2>/dev/null || echo 1) - 1 ))

    # Count discoverable Gen 2+3 artifacts in repo
    DISCOVERABLE=$(find "$REPO" -type f \( -name "sagco-*.sh" -o -name "sagco-*.yaml" \
        -o -name "SAGCO*.md" \) -not -path '*/.git/*' 2>/dev/null | wc -l)

    # Count Gen 3 (full DNA)
    GEN3=0
    for FILE in $(find "$REPO" -type f \( -name "sagco-*.sh" -o -name "sagco-*.yaml" -o -name "SAGCO*.md" \) \
        -not -path '*/.git/*' 2>/dev/null); do
        [ "$(classify_gen "$FILE")" -eq 3 ] && GEN3=$((GEN3 + 1))
    done

    # Unknown in ledger
    UNK_LEDGER=$([ -f "$LEDGER" ] && grep -c ",unknown," "$LEDGER" 2>/dev/null || echo 0)

    GAP=$((DISCOVERABLE - LEDGER_COUNT))
    [ "$GAP" -lt 0 ] && GAP=0

    printf "  %-35s %d\n" "Artifacts in ledger:"         "$LEDGER_COUNT"
    printf "  %-35s %d\n" "Discoverable SAGCO artifacts:" "$DISCOVERABLE"
    printf "  %-35s %d\n" "Gen 3 (full DNA):"            "$GEN3"
    printf "  %-35s %d\n" "Unknown in ledger:"           "$UNK_LEDGER"
    printf "  %-35s %d\n" "Migration gap:"               "$GAP"
    echo ""

    if [ "$GAP" -eq 0 ] && [ "$UNK_LEDGER" -eq 0 ]; then
        echo "  ✅ No gap — ledger matches discoverable artifacts"
        echo "  ✅ No unknowns — attribution complete"
    else
        [ "$GAP" -gt 0 ] && echo "  🟡 Gap: $GAP artifacts discoverable but not in ledger"
        [ "$UNK_LEDGER" -gt 0 ] && echo "  ❌ $UNK_LEDGER unknown rows in ledger — run sagco-boss-battle fix"
        echo ""
        echo "  Recommended: sagco-excavate migrate"
    fi
}

# ── migrate: retroactively register discoverable artifacts ────────────────────
cmd_migrate() {
    echo "SAGCO EXCAVATION MIGRATE"
    echo "=========================="
    echo "Discovering provenance that already exists."
    echo ""

    [ -f "$EXCAVATION_LOG" ] || \
        echo "timestamp,device,file,generation,status_field,device_field,gpg_field,registered" \
        > "$EXCAVATION_LOG"
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"

    REGISTERED=0; SKIPPED=0; GEN1_SKIP=0

    for FILE in $(find "$REPO" -type f \( -name "sagco-*.sh" -o -name "sagco-*.yaml" \
        -o -name "SAGCO*.md" -o -name "bellaroma*.html" \) \
        -not -path '*/.git/*' 2>/dev/null | sort); do

        FNAME=$(basename "$FILE")
        GEN=$(classify_gen "$FILE")

        # Skip Gen 1 — no embedded identity to migrate
        if [ "$GEN" -eq 1 ]; then
            GEN1_SKIP=$((GEN1_SKIP + 1))
            continue
        fi

        # Skip if already in ledger
        if [ -f "$LEDGER" ] && grep -q ",$FNAME," "$LEDGER" 2>/dev/null; then
            SKIPPED=$((SKIPPED + 1))
            continue
        fi

        # Extract fields
        STATUS_V=$(extract_field "$FILE" "STATUS=SAGCO_")
        DEVICE_V=$(extract_field "$FILE" "DEVICE=")
        GPG_V=$(extract_field "$FILE" "GPG_KEY=\|gpg_key:")
        TS_V=$(extract_field "$FILE" "TIMESTAMP=")

        # Device fallback: Gen 2 artifacts without explicit device → current device
        [ -z "$DEVICE_V" ] || [ "$DEVICE_V" = "notfound" ] && DEVICE_V="$DEV"

        # Status fallback
        [ -z "$STATUS_V" ] && STATUS_V="SAGCO_EXCAVATED_GEN${GEN}"

        # Hash the file
        HASH=$(sha256sum "$FILE" 2>/dev/null | cut -c1-16 || \
               cksum "$FILE" | awk '{printf "%016d", $1}')

        # Register in ledger
        echo "${STAMP},${DEVICE_V},sagco-excavate,${FNAME},${HASH},${STATUS_V}" >> "$LEDGER"

        # Excavation log
        echo "${STAMP},${DEVICE_V},${FNAME},${GEN},${STATUS_V},${DEVICE_V},${GPG_V:-none},REGISTERED" \
            >> "$EXCAVATION_LOG"

        printf "  ✅ Gen %d  %-40s device=%-10s\n" "$GEN" "$FNAME" "$DEVICE_V"
        REGISTERED=$((REGISTERED + 1))
    done

    echo ""
    echo "  ─────────────────────────────────────────────────────"
    printf "  Registered:  %d\n" "$REGISTERED"
    printf "  Skipped:     %d (already in ledger)\n" "$SKIPPED"
    printf "  Gen 1:       %d (no embedded identity — skipped)\n" "$GEN1_SKIP"
    echo ""
    echo "  Excavation log: $EXCAVATION_LOG"
    echo "  STATUS=SAGCO_EXCAVATION_MIGRATION_COMPLETE"
}

# ── full report ───────────────────────────────────────────────────────────────
cmd_report() {
    echo "SAGCO EXCAVATION REPORT"
    echo "========================="
    echo "Stamp:  $STAMP"
    echo "Device: $DEV"
    echo ""

    # Count by generation across all SAGCO artifacts
    G1=0; G2=0; G3=0
    for FILE in $(find "$REPO" -type f \( -name "sagco-*.sh" -o -name "sagco-*.yaml" \
        -o -name "SAGCO*.md" \) -not -path '*/.git/*' 2>/dev/null); do
        GEN=$(classify_gen "$FILE")
        case "$GEN" in
            1) G1=$((G1+1)) ;; 2) G2=$((G2+1)) ;; 3) G3=$((G3+1)) ;;
        esac
    done
    TOTAL=$((G1 + G2 + G3))

    echo "  Generation Distribution"
    echo "  ──────────────────────────────────────────────────────"
    printf "  %-35s %d/%d\n" "Gen 3 (full DNA — DEVICE+GPG+TS):" "$G3" "$TOTAL"
    printf "  %-35s %d/%d\n" "Gen 2 (partial — STATUS/TS):"       "$G2" "$TOTAL"
    printf "  %-35s %d/%d\n" "Gen 1 (no markers):"                "$G1" "$TOTAL"
    echo ""

    G3_PCT=0
    [ "$TOTAL" -gt 0 ] && G3_PCT=$(echo "scale=0; $G3 * 100 / $TOTAL" | bc 2>/dev/null || echo 0)
    echo "  Gen 3 adoption: ${G3_PCT}%"
    echo ""

    echo "  Key Insight"
    echo "  ──────────────────────────────────────────────────────"
    echo "  The attribution engine is not creating provenance."
    echo "  It is discovering provenance that already exists."
    echo ""
    echo "  Gen 2+ artifacts already carry:"

    # Find the most common embedded fields across Gen 2/3
    HAS_STATUS=$(find "$REPO" -name "sagco-*.sh" -not -path '*/.git/*' \
        -exec grep -l "STATUS=SAGCO_" {} \; 2>/dev/null | wc -l)
    HAS_DEVICE=$(find "$REPO" -name "sagco-*.sh" -not -path '*/.git/*' \
        -exec grep -l "DEVICE=" {} \; 2>/dev/null | wc -l)
    HAS_GPG=$(find "$REPO" -name "sagco-*.sh" -not -path '*/.git/*' \
        -exec grep -l -i "gpg_key\|AE5519" {} \; 2>/dev/null | wc -l)
    HAS_SSH=$(find "$REPO" -name "sagco-*.sh" -not -path '*/.git/*' \
        -exec grep -l -i "ssh_key\|SAGCO-OS PIPELINE" {} \; 2>/dev/null | wc -l)

    printf "    STATUS=SAGCO_*   in %d scripts\n"  "$HAS_STATUS"
    printf "    DEVICE=          in %d scripts\n"  "$HAS_DEVICE"
    printf "    GPG_KEY=         in %d scripts\n"  "$HAS_GPG"
    printf "    SSH_KEY=         in %d scripts\n"  "$HAS_SSH"
    echo ""

    echo "  Migration Status"
    echo "  ──────────────────────────────────────────────────────"
    cmd_diff | grep -v "^SAGCO\|^===\|^The gap" | head -10

    echo ""
    echo "  This is a migration problem, not an invention problem."
    echo "  The fleet is already recording who/what/when/where."
    echo "  STATUS=SAGCO_EXCAVATION_REPORT_COMPLETE"
}

# ── race tick ─────────────────────────────────────────────────────────────────
write_tick() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_excavate_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
    HASH=$(echo "${STAMP}sagco-excavate${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-excavate,${EXCAVATION_LOG},${HASH},SAGCO_EXCAVATE_PASS" >> "$LEDGER"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-report}"

case "$CMD" in
    scan)           cmd_scan;             write_tick ;;
    extract)        cmd_extract "${2:-}";  write_tick ;;
    diff)           cmd_diff;             write_tick ;;
    migrate)        cmd_migrate;          write_tick ;;
    report|"")      cmd_report;           write_tick ;;
    *)
        echo "Usage: sagco-excavate [scan|extract <file>|diff|migrate|report]"
        echo ""
        echo "  scan           find all artifacts with embedded provenance"
        echo "  extract <file> pull every provenance field from one file"
        echo "  diff           ledger vs discoverable (the migration gap)"
        echo "  migrate        register all discoverable artifacts retroactively"
        echo "  report         full excavation report with generation breakdown"
        exit 1
        ;;
esac
