#!/bin/sh
# sagco-refinery — Typed Artifact Refinery
# Consumes sagco-classify output (classified_inventory.csv)
# Weighs categories, produces refinery_score.yaml + report
# This is the jump from Inventory to Understanding
#
# Usage:
#   sagco-refinery              → refine last classify run
#   sagco-refinery <inventory>  → refine a specific inventory CSV

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
CLASSIFY_DIR="$HOME/sagco_classify"
REFINERY_DIR="$HOME/sagco_refinery"
LEDGER="$HOME/sagco_ledger.csv"

mkdir -p "$REFINERY_DIR"

# ── find inventory to refine ──────────────────────────────────────────────────
if [ -n "$1" ] && [ -f "$1" ]; then
    INVENTORY="$1"
else
    INVENTORY=$(ls -1t "$CLASSIFY_DIR"/classified_inventory_*.csv 2>/dev/null | head -1)
fi

if [ -z "$INVENTORY" ] || [ ! -f "$INVENTORY" ]; then
    echo "No classified inventory found — run: sagco-classify"
    echo "Then: sagco-refinery"
    exit 1
fi

REPORT="$REFINERY_DIR/refinery_report_${STAMP}.md"
SCORE="$REFINERY_DIR/refinery_score_${STAMP}.yaml"

echo "SAGCO REFINERY — Typed Artifact Weighing"
echo "========================================="
echo "Stamp:     $STAMP"
echo "Device:    $DEV"
echo "Inventory: $INVENTORY"
echo ""

# ── read counts from inventory ────────────────────────────────────────────────
count_cat() {
    grep -c ",$1," "$INVENTORY" 2>/dev/null || echo 0
}

SAGCO_CMD=$(count_cat "SAGCO_COMMAND")
RUST_KERNEL=$(count_cat "RUST_KERNEL")
RUST_MOD=$(count_cat "RUST_MODULE")
PYTHON=$(count_cat "PYTHON_MODULE")
YAML_SYS=$(count_cat "YAML_SYSTEM")
YAML_DOC=$(count_cat "YAML_DOCTRINE")
MD_CASE=$(count_cat "MD_CASE_STUDY")
MD_LEDG=$(count_cat "MD_LEDGER")
MD_SAGCO=$(count_cat "MD_SAGCO")
PDF_FIN=$(count_cat "PDF_FINANCE")
PDF_CLI=$(count_cat "PDF_CLIENT")
PDF_ENG=$(count_cat "PDF_ENGINEERING")
XLSX_PORT=$(count_cat "XLSX_PORTFOLIO")
TOTAL=$(grep -c "^20" "$INVENTORY" 2>/dev/null || echo 1)

# ── weighted scoring ──────────────────────────────────────────────────────────
# Weight table: how much each category contributes to the refinery score
# Runtime: 3pts each  |  Evidence: 4pts each  |  Client: 5pts each
# Intelligence: 2pts  |  Portfolio: 4pts

RUNTIME_SCORE=$(echo "scale=0; ($SAGCO_CMD * 3) + ($RUST_KERNEL * 3) + ($RUST_MOD * 2) + ($PYTHON * 2)" | bc 2>/dev/null || echo 0)
EVIDENCE_SCORE=$(echo "scale=0; ($MD_CASE * 5) + ($MD_LEDG * 4) + ($MD_SAGCO * 3)" | bc 2>/dev/null || echo 0)
CLIENT_SCORE=$(echo "scale=0; ($PDF_CLI * 5) + ($PDF_ENG * 3) + ($PDF_FIN * 2)" | bc 2>/dev/null || echo 0)
INTEL_SCORE=$(echo "scale=0; ($YAML_SYS * 2) + ($YAML_DOC * 3)" | bc 2>/dev/null || echo 0)
PORTFOLIO_SCORE=$(echo "scale=0; ($XLSX_PORT * 4)" | bc 2>/dev/null || echo 0)

TOTAL_SCORE=$(echo "scale=0; $RUNTIME_SCORE + $EVIDENCE_SCORE + $CLIENT_SCORE + $INTEL_SCORE + $PORTFOLIO_SCORE" | bc 2>/dev/null || echo 0)

# Classification rate: what % of artifacts got a meaningful category
UNCLASSIFIED=$(count_cat "UNKNOWN")
CLASSIFIED=$((TOTAL - UNCLASSIFIED))
CLASS_RATE=0
if [ "$TOTAL" -gt 0 ]; then
    CLASS_RATE=$(echo "scale=1; $CLASSIFIED * 100 / $TOTAL" | bc 2>/dev/null || echo 0)
fi

# Rank the refinery
if [ "$TOTAL_SCORE" -ge 100 ] && [ "$(echo "$CLASS_RATE > 80" | bc 2>/dev/null)" = "1" ]; then
    RANK="S"
elif [ "$TOTAL_SCORE" -ge 50 ]; then
    RANK="A"
elif [ "$TOTAL_SCORE" -ge 20 ]; then
    RANK="B"
elif [ "$TOTAL_SCORE" -ge 5 ]; then
    RANK="C"
else
    RANK="D"
fi

# ── print results ─────────────────────────────────────────────────────────────
echo "LAYER SCORES:"
printf "  %-22s %d points  (%d commands, %d Rust, %d Python)\n" \
    "Runtime" "$RUNTIME_SCORE" "$SAGCO_CMD" "$((RUST_KERNEL + RUST_MOD))" "$PYTHON"
printf "  %-22s %d points  (%d case studies, %d ledgers)\n" \
    "Evidence" "$EVIDENCE_SCORE" "$MD_CASE" "$MD_LEDG"
printf "  %-22s %d points  (%d client, %d engineering)\n" \
    "Client" "$CLIENT_SCORE" "$PDF_CLI" "$PDF_ENG"
printf "  %-22s %d points  (%d system, %d doctrine)\n" \
    "Intelligence" "$INTEL_SCORE" "$YAML_SYS" "$YAML_DOC"
printf "  %-22s %d points  (%d portfolio)\n" \
    "Portfolio" "$PORTFOLIO_SCORE" "$XLSX_PORT"
echo ""
echo "  ─────────────────────────────────────"
printf "  %-22s %d\n" "TOTAL SCORE" "$TOTAL_SCORE"
printf "  %-22s %s\n" "RANK" "$RANK"
printf "  %-22s %s%% (%d / %d)\n" "CLASSIFICATION RATE" "$CLASS_RATE" "$CLASSIFIED" "$TOTAL"
echo ""

# ── bottleneck signal ─────────────────────────────────────────────────────────
echo "BOTTLENECK ANALYSIS:"
if [ "$UNCLASSIFIED" -gt "$CLASSIFIED" ] 2>/dev/null; then
    echo "  Discovery Rate >> Classification Rate"
    echo "  BOTTLENECK: $UNCLASSIFIED unclassified artifacts"
    echo "  ACTION: add content signal patterns to sagco-classify"
elif [ "$MD_CASE" -eq 0 ]; then
    echo "  BOTTLENECK: no MD_CASE_STUDY files found"
    echo "  ACTION: QR audit outputs → Bell_Aroma_*.md are your strongest client evidence"
elif [ "$XLSX_PORT" -eq 0 ]; then
    echo "  BOTTLENECK: no XLSX_PORTFOLIO detected"
    echo "  ACTION: upload bottleneck invention map Excel to repo root"
else
    echo "  No major bottleneck detected — classification rate: ${CLASS_RATE}%"
fi
echo ""

# ── write markdown report ─────────────────────────────────────────────────────
cat > "$REPORT" << RPT
# SAGCO Refinery Report
Generated: $STAMP
Device: $DEV
Rank: $RANK
Total Score: $TOTAL_SCORE

## Layer Scores

| Layer | Score | Key Artifacts |
|-------|-------|---------------|
| Runtime | $RUNTIME_SCORE | $SAGCO_CMD commands, $((RUST_KERNEL+RUST_MOD)) Rust files |
| Evidence | $EVIDENCE_SCORE | $MD_CASE case studies, $MD_LEDG ledgers |
| Client | $CLIENT_SCORE | $PDF_CLI client PDFs, $PDF_ENG engineering PDFs |
| Intelligence | $INTEL_SCORE | $YAML_SYS system YAMLs, $YAML_DOC doctrine |
| Portfolio | $PORTFOLIO_SCORE | $XLSX_PORT portfolio sheets |
| **TOTAL** | **$TOTAL_SCORE** | Rank: **$RANK** |

## Classification Rate

- Total artifacts: $TOTAL
- Classified: $CLASSIFIED
- Unclassified: $UNCLASSIFIED
- Rate: ${CLASS_RATE}%

## Refinery Input → Wafer Output

\`\`\`
SAGCO_COMMAND ($SAGCO_CMD)  →  command_inventory
MD_CASE_STUDY ($MD_CASE)   →  client_deliverables
YAML_DOCTRINE ($YAML_DOC)  →  doctrine_health
PDF_FINANCE ($PDF_FIN)     →  invoice_tracking
XLSX_PORTFOLIO ($XLSX_PORT) →  portfolio_refinery
\`\`\`

STATUS=SAGCO_REFINERY_PASS
RPT

# ── write score YAML ──────────────────────────────────────────────────────────
cat > "$SCORE" << SYAML
timestamp: $STAMP
device: $DEV
inventory_source: $INVENTORY
total_artifacts: $TOTAL
classified: $CLASSIFIED
unclassified: $UNCLASSIFIED
classification_rate_pct: $CLASS_RATE
scores:
  runtime: $RUNTIME_SCORE
  evidence: $EVIDENCE_SCORE
  client: $CLIENT_SCORE
  intelligence: $INTEL_SCORE
  portfolio: $PORTFOLIO_SCORE
  total: $TOTAL_SCORE
rank: $RANK
bottleneck: $([ "$UNCLASSIFIED" -gt "$CLASSIFIED" ] 2>/dev/null && echo "classification_gap" || echo "none")
status: SAGCO_REFINERY_PASS
SYAML

# ── ledger + race ─────────────────────────────────────────────────────────────
HASH=$(echo "${STAMP}sagco-refinery" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${DEV},sagco-refinery,${SCORE},${HASH},SAGCO_REFINERY_PASS" >> "$LEDGER"

RACE_OUT="$HOME/sagco_race/race_log.csv"
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
mkdir -p "$(dirname "$RACE_OUT")"
[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${DEV},sagco_refinery,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

echo "Report: $REPORT"
echo "Score:  $SCORE"
echo ""
echo "STATUS=SAGCO_REFINERY_PASS"
echo "RANK=$RANK"
echo "CLASSIFICATION_RATE=${CLASS_RATE}%"
