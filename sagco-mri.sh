#!/bin/sh
# sagco-mri — SAGCO MRI Stack Scanner
# Locates and classifies the 5 core intelligence files:
#   1. oscillator_kernel  → proof math / verification engine
#   2. inv199_handoff     → field validation case study
#   3. sagco_framework    → doctrine YAML (genome/constitution)
#   4. bottleneck_map     → refinery database (Excel/CSV)
#   5. chess_map          → portfolio visualizer
#
# Usage:
#   sagco-mri             → full scan, write report
#   sagco-mri show        → show last report
#   sagco-mri --paths     → show search paths only

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
REPO_ROOT="$(cd "$(dirname "$0")" 2>/dev/null && pwd || echo "$HOME")"
MRI_DIR="$HOME/sagco_mri"
REPORT="$MRI_DIR/mri_report_${STAMP}.md"
SCORE_YAML="$MRI_DIR/mri_score_${STAMP}.yaml"
LEDGER="$HOME/sagco_ledger.csv"

mkdir -p "$MRI_DIR"

# ── show last report ──────────────────────────────────────────────────────────
if [ "$1" = "show" ]; then
    LAST=$(ls -1t "$MRI_DIR"/mri_report_*.md 2>/dev/null | head -1)
    if [ -n "$LAST" ]; then cat "$LAST"; else echo "No MRI report found — run: sagco-mri"; fi
    exit 0
fi

# ── search paths ──────────────────────────────────────────────────────────────
SEARCH_PATHS="$REPO_ROOT $HOME $HOME/Downloads $HOME/downloads $HOME/Dropbox $HOME/sagco_nina $HOME/sagco_wafer"

find_file() {
    PATTERN="$1"
    for DIR in $SEARCH_PATHS; do
        [ -d "$DIR" ] || continue
        RESULT=$(find "$DIR" -maxdepth 4 -iname "$PATTERN" 2>/dev/null | head -1)
        if [ -n "$RESULT" ]; then echo "$RESULT"; return; fi
    done
    echo ""
}

file_hash() {
    F="$1"
    [ -f "$F" ] || { echo "missing"; return; }
    sha256sum "$F" 2>/dev/null | cut -c1-16 || cksum "$F" | awk '{printf "%012d", $1}'
}

file_size() {
    F="$1"
    [ -f "$F" ] || { echo "0"; return; }
    wc -c < "$F" 2>/dev/null || echo "0"
}

file_lines() {
    F="$1"
    [ -f "$F" ] || { echo "0"; return; }
    wc -l < "$F" 2>/dev/null || echo "0"
}

# ── locate the 5 MRI files ────────────────────────────────────────────────────

# 1. Oscillator Kernel — analytic/symplectic solver, invariant checks, genesis lock
OSC=$(find_file "genesis_prime_core.rs")
[ -z "$OSC" ] && OSC=$(find_file "*oscillat*.rs")
[ -z "$OSC" ] && OSC=$(find_file "quantum_dna_splicer.rs")

# 2. INV199 Handoff — CUI circuits, burn rate, project field case study
INV=$(find_file "*INV199*")
[ -z "$INV" ] && INV=$(find_file "INV110592310.pdf")
[ -z "$INV" ] && INV=$(find_file "*handoff*")
[ -z "$INV" ] && INV=$(find_file "*INV1*.pdf")

# 3. SAGCO Framework YAML — doctrine (skeleton, nervous system, DNA, immune system)
FW=$(find_file "EMPIRE_GENOME_v1.7.yaml")
[ -z "$FW" ] && FW=$(find_file "*genome*.yaml")
[ -z "$FW" ] && FW=$(find_file "*framework*.yaml")
[ -z "$FW" ] && FW=$(find_file "ai_constitution.yaml")

# 4. Bottleneck Invention Map — 100 bottlenecks, inventions, algorithms, tier/value
BOT=$(find_file "*.xlsx")
[ -z "$BOT" ] && BOT=$(find_file "*bottleneck*.csv")
[ -z "$BOT" ] && BOT=$(find_file "*invention*.csv")
[ -z "$BOT" ] && BOT=$(find_file "*refinery*.csv")

# 5. Chess Map — portfolio visualizer, inventions mapped to chess positions
CHESS=$(find_file "chess_council_architecture.txt")
[ -z "$CHESS" ] && CHESS=$(find_file "chess_council_architecture*.txt")
[ -z "$CHESS" ] && CHESS=$(find_file "*chess*.yaml")

# ── score each file ───────────────────────────────────────────────────────────
score_file() {
    F="$1"
    ROLE="$2"
    if [ -f "$F" ]; then echo "FOUND[$ROLE]"; else echo "MISSING[$ROLE]"; fi
}

OSC_STATUS=$(score_file "$OSC" "oscillator_kernel")
INV_STATUS=$(score_file "$INV" "inv199_handoff")
FW_STATUS=$(score_file "$FW" "sagco_framework")
BOT_STATUS=$(score_file "$BOT" "bottleneck_map")
CHESS_STATUS=$(score_file "$CHESS" "chess_map")

FOUND=0
for S in "$OSC_STATUS" "$INV_STATUS" "$FW_STATUS" "$BOT_STATUS" "$CHESS_STATUS"; do
    echo "$S" | grep -q "^FOUND" && FOUND=$((FOUND + 1))
done
MISSING=$((5 - FOUND))

# ── determine core use ────────────────────────────────────────────────────────
CORE_USE=""
[ -f "$OSC" ]   && CORE_USE="${CORE_USE}proof_engine "
[ -f "$INV" ]   && CORE_USE="${CORE_USE}field_validation "
[ -f "$FW" ]    && CORE_USE="${CORE_USE}doctrine "
[ -f "$BOT" ]   && CORE_USE="${CORE_USE}portfolio_refinery "
[ -f "$CHESS" ] && CORE_USE="${CORE_USE}portfolio_visualizer "
CORE_USE=$(echo "$CORE_USE" | sed 's/ $//' | tr ' ' '+')
[ -z "$CORE_USE" ] && CORE_USE="none_found"

# ── print terminal summary ────────────────────────────────────────────────────
echo "SAGCO MRI STACK SCANNER"
echo "========================"
echo "Stamp:  $STAMP"
echo "Device: $DEV"
echo "Repo:   $REPO_ROOT"
echo ""
echo "MRI FILE SCAN:"
echo ""

print_mri_line() {
    NUM="$1"; LABEL="$2"; PATH="$3"; STATUS="$4"
    if [ -f "$PATH" ]; then
        SZ=$(file_size "$PATH")
        LN=$(file_lines "$PATH")
        HSH=$(file_hash "$PATH")
        printf "  [%s] %-22s FOUND    %6d bytes  %5d lines  hash=%s\n" "$NUM" "$LABEL" "$SZ" "$LN" "$HSH"
        printf "       %s\n" "$PATH"
    else
        printf "  [%s] %-22s MISSING  (not found in search paths)\n" "$NUM" "$LABEL"
    fi
    echo ""
}

print_mri_line "1" "oscillator_kernel"  "$OSC"   "$OSC_STATUS"
print_mri_line "2" "inv199_handoff"     "$INV"   "$INV_STATUS"
print_mri_line "3" "sagco_framework"    "$FW"    "$FW_STATUS"
print_mri_line "4" "bottleneck_map"     "$BOT"   "$BOT_STATUS"
print_mri_line "5" "chess_map"          "$CHESS" "$CHESS_STATUS"

echo "RESULTS:"
echo "  HELPFUL_FILES=$FOUND"
echo "  MISSING_FILES=$MISSING"
echo "  CORE_USE=$CORE_USE"
echo ""

# ── write markdown report ─────────────────────────────────────────────────────
cat > "$REPORT" << HEADER
# SAGCO MRI Stack Report
Generated: $STAMP
Device: $DEV
Status: $([ "$FOUND" -ge 3 ] && echo "OPERATIONAL" || echo "PARTIAL")

## MRI File Registry

| # | Role | Status | File | Hash |
|---|------|--------|------|------|
HEADER

mri_row() {
    NUM="$1"; ROLE="$2"; F="$3"
    if [ -f "$F" ]; then
        HSH=$(file_hash "$F")
        FNAME=$(basename "$F")
        printf "| %s | %s | FOUND | %s | %s |\n" "$NUM" "$ROLE" "$FNAME" "$HSH"
    else
        printf "| %s | %s | MISSING | — | — |\n" "$NUM" "$ROLE"
    fi
}

{
mri_row "1" "oscillator_kernel" "$OSC"
mri_row "2" "inv199_handoff" "$INV"
mri_row "3" "sagco_framework" "$FW"
mri_row "4" "bottleneck_map" "$BOT"
mri_row "5" "chess_map" "$CHESS"
} >> "$REPORT"

cat >> "$REPORT" << SUMMARY

## Core Use Mapping

\`\`\`
oscillator_kernel  → sagco-verify  (proof math, invariant checks, energy drift)
inv199_handoff     → field_validation (CUI circuits, burn rate, project health)
sagco_framework    → doctrine      (skeleton, nervous system, DNA, immune system)
bottleneck_map     → portfolio_refinery (100 bottlenecks, tier/value table)
chess_map          → portfolio_visualizer (inventions → chess positions)
\`\`\`

## Summary

- HELPFUL_FILES: $FOUND / 5
- CORE_USE: $CORE_USE
- MISSING: $MISSING file(s) $([ "$MISSING" -gt 0 ] && echo "(add to repo or Dropbox sync path)")

## Next Brick

$([ -f "$OSC" ] && echo "- sagco-verify: wire genesis_prime_core.rs as verification engine" || echo "- oscillator_kernel: upload genesis_prime_core.rs to repo")
$([ -z "$BOT" ] && echo "- bottleneck_map: upload Excel to repo root or ~/sagco_nina/" || echo "- bottleneck_map: parse Excel → CSV for sagco-wafer-refinery")
$([ -f "$FW" ] && echo "- sagco-framework: EMPIRE_GENOME_v1.7.yaml wired into sagco-state" || echo "- sagco_framework: locate genome YAML")

STATUS=SAGCO_MRI_PASS
SUMMARY

# ── write score YAML ──────────────────────────────────────────────────────────
cat > "$SCORE_YAML" << YAML
timestamp: $STAMP
device: $DEV
helpful_files: $FOUND
missing_files: $MISSING
core_use: $CORE_USE

files:
  oscillator_kernel:
    path: "${OSC:-missing}"
    found: $([ -f "$OSC" ] && echo "true" || echo "false")
    maps_to: sagco-verify
  inv199_handoff:
    path: "${INV:-missing}"
    found: $([ -f "$INV" ] && echo "true" || echo "false")
    maps_to: field_validation
  sagco_framework:
    path: "${FW:-missing}"
    found: $([ -f "$FW" ] && echo "true" || echo "false")
    maps_to: doctrine
  bottleneck_map:
    path: "${BOT:-missing}"
    found: $([ -f "$BOT" ] && echo "true" || echo "false")
    maps_to: portfolio_refinery
  chess_map:
    path: "${CHESS:-missing}"
    found: $([ -f "$CHESS" ] && echo "true" || echo "false")
    maps_to: portfolio_visualizer

status: SAGCO_MRI_PASS
YAML

# ── ledger entry ──────────────────────────────────────────────────────────────
HASH=$(echo "${STAMP}sagco-mri" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${DEV},sagco-mri,${REPORT},${HASH},SAGCO_MRI_PASS" >> "$LEDGER"

# ── race log ──────────────────────────────────────────────────────────────────
RACE_OUT="$HOME/sagco_race/race_log.csv"
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
mkdir -p "$HOME/sagco_race"
[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${DEV},sagco_mri_scan,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

echo "Report:  $REPORT"
echo "Score:   $SCORE_YAML"
echo ""
echo "STATUS=SAGCO_MRI_PASS"
echo "HELPFUL_FILES=$FOUND"
echo "CORE_USE=$CORE_USE"
