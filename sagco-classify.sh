#!/bin/sh
# sagco-classify — Artifact Classification Engine
# Turns raw discovery (237 artifacts) into typed categories
# Bridges: Inventory → Understanding → Refinery input
#
# Output categories:
#   SAGCO_COMMAND   RUST_KERNEL     PYTHON_MODULE
#   YAML_SYSTEM     YAML_DOCTRINE   YAML_CONFIG
#   MD_CASE_STUDY   MD_LEDGER       MD_SAGCO        MD_DOCS
#   PDF_FINANCE     PDF_CLIENT      PDF_ENGINEERING
#   XLSX_PORTFOLIO  XLSX_ESTIMATOR  JSON_DATA       UNKNOWN
#
# Usage:
#   sagco-classify              → classify repo + SAGCO dirs
#   sagco-classify <path>       → classify a specific directory
#   sagco-classify show         → show last classify report
#   sagco-classify --summary    → category counts only

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
REPO_ROOT="$(cd "$(dirname "$0")" 2>/dev/null && pwd || echo "$HOME")"
CLASSIFY_DIR="$HOME/sagco_classify"
# Stable live path (monitorable with: wc -l ~/sagco_classify.csv)
LIVE_CSV="$HOME/sagco_classify.csv"
INVENTORY="$CLASSIFY_DIR/classified_inventory_${STAMP}.csv"
REPORT="$CLASSIFY_DIR/classify_report_${STAMP}.md"
SCORE_YAML="$CLASSIFY_DIR/classify_score_${STAMP}.yaml"
LEDGER="$HOME/sagco_ledger.csv"

mkdir -p "$CLASSIFY_DIR"

# ── show last report ──────────────────────────────────────────────────────────
if [ "$1" = "show" ]; then
    LAST=$(ls -1t "$CLASSIFY_DIR"/classify_report_*.md 2>/dev/null | head -1)
    if [ -n "$LAST" ]; then cat "$LAST"; else echo "No classify report — run: sagco-classify"; fi
    exit 0
fi

# ── census: quick grep counts on stable CSV ───────────────────────────────────
if [ "$1" = "census" ]; then
    if [ ! -f "$LIVE_CSV" ]; then
        echo "No census data yet — run: sagco-classify fast"
        exit 1
    fi
    TOTAL=$(grep -c "^20" "$LIVE_CSV" 2>/dev/null || echo 0)
    echo "SAGCO ARTIFACT CENSUS"
    echo "====================="
    for CAT in SAGCO_COMMAND RUST_KERNEL RUST_MODULE PYTHON_MODULE SHELL_UTIL \
               YAML_SYSTEM YAML_DOCTRINE YAML_CONFIG \
               MD_CASE_STUDY MD_LEDGER MD_SAGCO MD_DOCS \
               PDF_FINANCE PDF_CLIENT PDF_ENGINEERING \
               XLSX_PORTFOLIO XLSX_ESTIMATOR CSV_DATA JSON_DATA UNKNOWN; do
        N=$(grep -c ",$CAT," "$LIVE_CSV" 2>/dev/null || echo 0)
        [ "$N" -gt 0 ] && printf "  %-22s %d\n" "$CAT" "$N"
    done
    echo "  ─────────────────────────"
    printf "  %-22s %d\n" "TOTAL" "$TOTAL"
    echo ""
    UNK=$(grep -c ",UNKNOWN," "$LIVE_CSV" 2>/dev/null || echo 0)
    [ "$UNK" -gt 0 ] && echo "  ANTIBODY TARGET: $UNK UNKNOWN files — run: sagco-antibody"
    exit 0
fi

# ── scan mode ─────────────────────────────────────────────────────────────────
# fast = targeted SAGCO dirs only, depth 3 (seconds)
# full = entire $HOME, depth 5 (minutes on large $HOME)
# <path> = specific directory

FAST=0
SCAN_TARGET="$REPO_ROOT"

case "$1" in
    fast|--fast)
        FAST=1
        SCAN_TARGET="$REPO_ROOT"
        ;;
    full|--full)
        FAST=0
        SCAN_TARGET="$HOME"
        ;;
    --summary)
        SCAN_TARGET="$REPO_ROOT"
        ;;
    "")
        FAST=1
        SCAN_TARGET="$REPO_ROOT"
        ;;
    *)
        SCAN_TARGET="$1"
        ;;
esac

MAX_DEPTH=$([ "$FAST" = "1" ] && echo 4 || echo 6)

# ── classifier core ───────────────────────────────────────────────────────────
classify_file() {
    F="$1"
    FNAME=$(basename "$F")
    FNAME_LOWER=$(echo "$FNAME" | tr '[:upper:]' '[:lower:]')
    EXT="${FNAME##*.}"
    EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')

    case "$EXT_LOWER" in

        sh)
            echo "$FNAME_LOWER" | grep -q "^sagco-" && echo "SAGCO_COMMAND" || echo "SHELL_UTIL"
            ;;

        rs)
            echo "$FNAME_LOWER" | grep -q "main" && echo "RUST_KERNEL" || echo "RUST_MODULE"
            ;;

        py)
            echo "PYTHON_MODULE"
            ;;

        yaml|yml)
            # Peek at content signals (first 30 lines only — fast)
            HEAD=$(head -30 "$F" 2>/dev/null | tr '[:upper:]' '[:lower:]')
            if echo "$HEAD" | grep -q "timestamp:\|device:\|sagco_\|status:.*pass"; then
                echo "YAML_SYSTEM"
            elif echo "$HEAD" | grep -q "chromosome\|genome\|fitness:\|doctrine\|nervous_system\|skeleton"; then
                echo "YAML_DOCTRINE"
            elif echo "$HEAD" | grep -q "token:\|secret:\|password:\|bearer:\|api_key"; then
                echo "YAML_CONFIG"
            elif echo "$HEAD" | grep -q "score:\|rank:\|portfolio\|return_pct\|sharpe"; then
                echo "YAML_PORTFOLIO"
            else
                echo "YAML_SYSTEM"
            fi
            ;;

        md)
            HEAD=$(head -20 "$F" 2>/dev/null | tr '[:upper:]' '[:lower:]')
            if echo "$HEAD" | grep -q "risk.*none\|verified.*true\|audit\|qr.*code\|bell.*aroma\|client"; then
                echo "MD_CASE_STUDY"
            elif echo "$HEAD" | grep -q "timestamp,device\|sagco_ledger\|ledger\|evidence"; then
                echo "MD_LEDGER"
            elif echo "$HEAD" | grep -q "sagco\|status=sagco\|attribution\|eru\|mansion\|mri"; then
                echo "MD_SAGCO"
            elif echo "$FNAME_LOWER" | grep -q "complete\|deploy\|architecture\|brief\|readme"; then
                echo "MD_DOCS"
            else
                echo "MD_DOCS"
            fi
            ;;

        pdf)
            if echo "$FNAME_LOWER" | grep -q "inv\|invoice\|payment\|budget\|finance\|bank\|receipt"; then
                echo "PDF_FINANCE"
            elif echo "$FNAME_LOWER" | grep -q "audit\|verify\|compliance\|client\|report"; then
                echo "PDF_CLIENT"
            else
                echo "PDF_ENGINEERING"
            fi
            ;;

        xlsx|xls)
            if echo "$FNAME_LOWER" | grep -q "portfolio\|score\|chess\|invention\|bottleneck\|tier"; then
                echo "XLSX_PORTFOLIO"
            elif echo "$FNAME_LOWER" | grep -q "estimate\|budget\|invoice\|cost\|price"; then
                echo "XLSX_ESTIMATOR"
            else
                echo "XLSX_DATA"
            fi
            ;;

        csv)
            HEAD=$(head -1 "$F" 2>/dev/null | tr '[:upper:]' '[:lower:]')
            if echo "$HEAD" | grep -q "timestamp,device\|ledger\|attribution"; then
                echo "MD_LEDGER"
            elif echo "$HEAD" | grep -q "strategy,symbol\|return_pct\|score"; then
                echo "XLSX_PORTFOLIO"
            else
                echo "CSV_DATA"
            fi
            ;;

        json)
            echo "JSON_DATA"
            ;;

        txt)
            echo "$FNAME_LOWER" | grep -q "chess\|council" && echo "MD_CASE_STUDY" || echo "MD_DOCS"
            ;;

        rs|toml)
            echo "RUST_MODULE"
            ;;

        ps1)
            echo "SHELL_UTIL"
            ;;

        *)
            echo "UNKNOWN"
            ;;
    esac
}

# ── scan and classify ─────────────────────────────────────────────────────────
echo "SAGCO CLASSIFY — Artifact Classification Engine"
echo "================================================"
echo "Stamp:  $STAMP"
echo "Device: $DEV"
echo "Target: $SCAN_TARGET"
echo "Mode:   $([ "$FAST" = "1" ] && echo "fast (depth $MAX_DEPTH, repo only)" || echo "full (depth $MAX_DEPTH)")"
echo ""
echo "Writing live progress to: $LIVE_CSV"
echo "(Monitor with: wc -l ~/sagco_classify.csv)"
echo ""

# Write CSV header to both inventory and live path
HDR="timestamp,device,category,filename,path,size_bytes,ext"
echo "$HDR" > "$INVENTORY"
echo "$HDR" > "$LIVE_CSV"

# Walk files — excluded dirs that explode file count without useful artifacts
find "$SCAN_TARGET" -maxdepth "$MAX_DEPTH" -type f \
    ! -path "*/.git/*" \
    ! -path "*/node_modules/*" \
    ! -path "*/__pycache__/*" \
    ! -path "*/target/debug/*" \
    ! -path "*/target/release/*" \
    ! -path "*/.cargo/*" \
    ! -path "*/vendor/*" \
    ! -path "*/dist/*" \
    ! -path "*/.npm/*" \
    2>/dev/null | sort | while read -r F; do

    FNAME=$(basename "$F")
    EXT="${FNAME##*.}"
    EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')
    SIZE=$(wc -c < "$F" 2>/dev/null || echo 0)
    CAT=$(classify_file "$F")

    LINE="${STAMP},${DEV},${CAT},${FNAME},${F},${SIZE},${EXT_LOWER}"
    # Write to both archive inventory and live monitorable CSV
    echo "$LINE" >> "$INVENTORY"
    echo "$LINE" >> "$LIVE_CSV"

done

# Recount from inventory (since subshell loses vars)
TOTAL=$(grep -c "^20" "$INVENTORY" 2>/dev/null || echo 0)

count_cat() {
    grep -c ",$1," "$INVENTORY" 2>/dev/null || echo 0
}

SAGCO_CMD=$(count_cat "SAGCO_COMMAND")
RUST_K=$(count_cat "RUST_KERNEL")
RUST_M=$(count_cat "RUST_MODULE")
PYTHON=$(count_cat "PYTHON_MODULE")
YAML_SYS=$(count_cat "YAML_SYSTEM")
YAML_DOC=$(count_cat "YAML_DOCTRINE")
YAML_CFG=$(count_cat "YAML_CONFIG")
YAML_PORT=$(count_cat "YAML_PORTFOLIO")
MD_CASE=$(count_cat "MD_CASE_STUDY")
MD_LEDG=$(count_cat "MD_LEDGER")
MD_SAGCO_CT=$(count_cat "MD_SAGCO")
MD_DOCS=$(count_cat "MD_DOCS")
PDF_FIN=$(count_cat "PDF_FINANCE")
PDF_CLI=$(count_cat "PDF_CLIENT")
PDF_ENG=$(count_cat "PDF_ENGINEERING")
XLSX_PORT=$(count_cat "XLSX_PORTFOLIO")
XLSX_EST=$(count_cat "XLSX_ESTIMATOR")
XLSX_DATA=$(count_cat "XLSX_DATA")
CSV_DATA=$(count_cat "CSV_DATA")
JSON_DATA=$(count_cat "JSON_DATA")
SHELL_UTIL=$(count_cat "SHELL_UTIL")
UNKNOWN=$(count_cat "UNKNOWN")

# ── print summary ─────────────────────────────────────────────────────────────
echo "CLASSIFICATION RESULTS:"
echo ""
echo "  Engineering Code"
printf "    %-20s %d\n" "SAGCO_COMMAND"  "$SAGCO_CMD"
printf "    %-20s %d\n" "RUST_KERNEL"    "$RUST_K"
printf "    %-20s %d\n" "RUST_MODULE"    "$RUST_M"
printf "    %-20s %d\n" "PYTHON_MODULE"  "$PYTHON"
printf "    %-20s %d\n" "SHELL_UTIL"     "$SHELL_UTIL"
echo ""
echo "  System Intelligence"
printf "    %-20s %d\n" "YAML_SYSTEM"    "$YAML_SYS"
printf "    %-20s %d\n" "YAML_DOCTRINE"  "$YAML_DOC"
printf "    %-20s %d\n" "YAML_CONFIG"    "$YAML_CFG"
printf "    %-20s %d\n" "YAML_PORTFOLIO" "$YAML_PORT"
echo ""
echo "  Evidence Chain"
printf "    %-20s %d\n" "MD_CASE_STUDY"  "$MD_CASE"
printf "    %-20s %d\n" "MD_LEDGER"      "$MD_LEDG"
printf "    %-20s %d\n" "MD_SAGCO"       "$MD_SAGCO_CT"
printf "    %-20s %d\n" "MD_DOCS"        "$MD_DOCS"
echo ""
echo "  Client Deliverables"
printf "    %-20s %d\n" "PDF_FINANCE"    "$PDF_FIN"
printf "    %-20s %d\n" "PDF_CLIENT"     "$PDF_CLI"
printf "    %-20s %d\n" "PDF_ENGINEERING" "$PDF_ENG"
echo ""
echo "  Portfolio / Refinery"
printf "    %-20s %d\n" "XLSX_PORTFOLIO" "$XLSX_PORT"
printf "    %-20s %d\n" "XLSX_ESTIMATOR" "$XLSX_EST"
printf "    %-20s %d\n" "XLSX_DATA"      "$XLSX_DATA"
printf "    %-20s %d\n" "CSV_DATA"       "$CSV_DATA"
printf "    %-20s %d\n" "JSON_DATA"      "$JSON_DATA"
echo ""
printf "    %-20s %d\n" "UNKNOWN"        "$UNKNOWN"
echo "  ─────────────────────────"
printf "    %-20s %d\n" "TOTAL"          "$TOTAL"
echo ""

# ── write markdown report ─────────────────────────────────────────────────────
cat > "$REPORT" << RPT
# SAGCO Classify Report
Generated: $STAMP
Device: $DEV
Target: $SCAN_TARGET

## Artifact Classification Summary

| Category | Count | Layer |
|----------|-------|-------|
| SAGCO_COMMAND | $SAGCO_CMD | Runtime |
| RUST_KERNEL | $RUST_K | Runtime |
| RUST_MODULE | $RUST_M | Runtime |
| PYTHON_MODULE | $PYTHON | Runtime |
| SHELL_UTIL | $SHELL_UTIL | Runtime |
| YAML_SYSTEM | $YAML_SYS | Intelligence |
| YAML_DOCTRINE | $YAML_DOC | Intelligence |
| YAML_CONFIG | $YAML_CFG | Intelligence |
| YAML_PORTFOLIO | $YAML_PORT | Intelligence |
| MD_CASE_STUDY | $MD_CASE | Evidence |
| MD_LEDGER | $MD_LEDG | Evidence |
| MD_SAGCO | $MD_SAGCO_CT | Evidence |
| MD_DOCS | $MD_DOCS | Evidence |
| PDF_FINANCE | $PDF_FIN | Client |
| PDF_CLIENT | $PDF_CLI | Client |
| PDF_ENGINEERING | $PDF_ENG | Client |
| XLSX_PORTFOLIO | $XLSX_PORT | Refinery |
| XLSX_ESTIMATOR | $XLSX_EST | Refinery |
| CSV_DATA | $CSV_DATA | Refinery |
| JSON_DATA | $JSON_DATA | Data |
| UNKNOWN | $UNKNOWN | — |
| **TOTAL** | **$TOTAL** | |

## Inventory

See: $INVENTORY

## Next Step: Wafer Refinery

Feed classified types into sagco-wafer-refinery:
- SAGCO_COMMAND → command_count metric
- YAML_DOCTRINE → doctrine health score
- MD_CASE_STUDY → client deliverable count
- PDF_FINANCE → invoice tracking
- XLSX_PORTFOLIO → portfolio refinery input

STATUS=SAGCO_CLASSIFY_PASS
RPT

# ── write score YAML ──────────────────────────────────────────────────────────
cat > "$SCORE_YAML" << SYAML
timestamp: $STAMP
device: $DEV
total_artifacts: $TOTAL
categories:
  runtime:
    sagco_commands: $SAGCO_CMD
    rust_kernel: $RUST_K
    rust_modules: $RUST_M
    python_modules: $PYTHON
    shell_utils: $SHELL_UTIL
  intelligence:
    yaml_system: $YAML_SYS
    yaml_doctrine: $YAML_DOC
    yaml_config: $YAML_CFG
    yaml_portfolio: $YAML_PORT
  evidence:
    md_case_study: $MD_CASE
    md_ledger: $MD_LEDG
    md_sagco: $MD_SAGCO_CT
    md_docs: $MD_DOCS
  client:
    pdf_finance: $PDF_FIN
    pdf_client: $PDF_CLI
    pdf_engineering: $PDF_ENG
  refinery:
    xlsx_portfolio: $XLSX_PORT
    xlsx_estimator: $XLSX_EST
    csv_data: $CSV_DATA
    json_data: $JSON_DATA
  unknown: $UNKNOWN
inventory_csv: $INVENTORY
status: SAGCO_CLASSIFY_PASS
SYAML

# ── ledger + race ─────────────────────────────────────────────────────────────
HASH=$(echo "${STAMP}sagco-classify" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${DEV},sagco-classify,${INVENTORY},${HASH},SAGCO_CLASSIFY_PASS" >> "$LEDGER"

RACE_OUT="$HOME/sagco_race/race_log.csv"
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
mkdir -p "$(dirname "$RACE_OUT")"
[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${DEV},sagco_classify,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

echo "Inventory: $INVENTORY"
echo "Report:    $REPORT"
echo "Score:     $SCORE_YAML"
echo ""
echo "STATUS=SAGCO_CLASSIFY_PASS"
echo "ARTIFACT_COUNT=$TOTAL"
