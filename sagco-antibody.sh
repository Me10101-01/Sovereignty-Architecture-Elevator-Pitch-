#!/bin/sh
# sagco-antibody — UNKNOWN Artifact Antibody Engine
# Asks: "Why are these files unknown?" instead of just counting them
# Peeks deeper into UNKNOWN entries, tries harder to reclassify
# Unresolvable files → antibody record (why + suggested action)
#
# Usage:
#   sagco-antibody              → process all UNKNOWN from ~/sagco_classify.csv
#   sagco-antibody <csv>        → process specific classified inventory
#   sagco-antibody show         → show last antibody report

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
LIVE_CSV="$HOME/sagco_classify.csv"
AB_DIR="$HOME/sagco_antibody"
REPORT="$AB_DIR/antibody_report_${STAMP}.md"
RECLASSIFIED="$AB_DIR/reclassified_${STAMP}.csv"
LEDGER="$HOME/sagco_ledger.csv"

mkdir -p "$AB_DIR"

# ── show last report ──────────────────────────────────────────────────────────
if [ "$1" = "show" ]; then
    LAST=$(ls -1t "$AB_DIR"/antibody_report_*.md 2>/dev/null | head -1)
    if [ -n "$LAST" ]; then cat "$LAST"; else echo "No antibody report — run: sagco-antibody"; fi
    exit 0
fi

# ── find source inventory ─────────────────────────────────────────────────────
if [ -n "$1" ] && [ -f "$1" ]; then
    SOURCE="$1"
elif [ -f "$LIVE_CSV" ]; then
    SOURCE="$LIVE_CSV"
else
    echo "No classified inventory found — run: sagco-classify fast"
    exit 1
fi

echo "SAGCO ANTIBODY ENGINE — UNKNOWN Classifier"
echo "==========================================="
echo "Stamp:  $STAMP"
echo "Device: $DEV"
echo "Source: $SOURCE"
echo ""

# ── deep classifier: peek into content ───────────────────────────────────────
deep_classify() {
    F="$1"
    FNAME=$(basename "$F")
    FNAME_LOWER=$(echo "$FNAME" | tr '[:upper:]' '[:lower:]')

    [ -f "$F" ] || { echo "MISSING_FILE"; return; }

    # Read first 50 lines for content signals
    CONTENT=$(head -50 "$F" 2>/dev/null | tr '[:upper:]' '[:lower:]')
    SIZE=$(wc -c < "$F" 2>/dev/null || echo 0)

    # Binary file check (high non-printable ratio → binary artifact)
    if file "$F" 2>/dev/null | grep -qi "binary\|executable\|ELF\|zip\|archive\|image\|PNG\|JPEG"; then
        EXT="${FNAME##*.}"
        case "$EXT" in
            zip|gz|tar|tgz) echo "ARCHIVE_ARTIFACT" ;;
            png|jpg|jpeg|gif|svg|ico) echo "IMAGE_ASSET" ;;
            *) echo "BINARY_ARTIFACT" ;;
        esac
        return
    fi

    # Filename-based deep signals
    if echo "$FNAME_LOWER" | grep -q "dockerfile"; then
        echo "DOCKER_CONFIG"; return
    fi
    if echo "$FNAME_LOWER" | grep -q "\.env\|\.gitignore\|\.gitattributes\|\.editorconfig"; then
        echo "ENV_CONFIG"; return
    fi
    if echo "$FNAME_LOWER" | grep -q "package\.json\|package-lock\|tsconfig\|jest\.config"; then
        echo "NODE_CONFIG"; return
    fi
    if echo "$FNAME_LOWER" | grep -q "cargo\.toml\|cargo\.lock"; then
        echo "RUST_CONFIG"; return
    fi
    if echo "$FNAME_LOWER" | grep -q "makefile\|cmake\|gradle\|pom\.xml"; then
        echo "BUILD_CONFIG"; return
    fi
    if echo "$FNAME_LOWER" | grep -q "\.lock$"; then
        echo "LOCK_FILE"; return
    fi
    if echo "$FNAME_LOWER" | grep -q "license\|licence\|copying"; then
        echo "LICENSE_FILE"; return
    fi
    if echo "$FNAME_LOWER" | grep -q "readme"; then
        echo "MD_DOCS"; return
    fi

    # Content-based deep signals
    if echo "$CONTENT" | grep -q "pragma solidity\|contract \|mapping("; then
        echo "SOLIDITY_CONTRACT"; return
    fi
    if echo "$CONTENT" | grep -q "from anthropic\|import anthropic\|claude-\|claude_"; then
        echo "AI_INTEGRATION"; return
    fi
    if echo "$CONTENT" | grep -q "sagco_\|sagco-\|status=sagco"; then
        echo "SAGCO_ARTIFACT"; return
    fi
    if echo "$CONTENT" | grep -q "#!/bin/sh\|#!/bin/bash\|#!/usr/bin/env sh"; then
        echo "SHELL_UTIL"; return
    fi
    if echo "$CONTENT" | grep -q "#!/usr/bin/env python\|import os\|import sys\|def "; then
        echo "PYTHON_MODULE"; return
    fi
    if echo "$CONTENT" | grep -q "fn main\|use std::\|impl \|pub struct\|pub fn "; then
        echo "RUST_MODULE"; return
    fi
    if echo "$CONTENT" | grep -q "docker\|container\|image:\|services:"; then
        echo "DOCKER_CONFIG"; return
    fi
    if echo "$CONTENT" | grep -q "apiversion:\|kind:\|metadata:\|spec:"; then
        echo "K8S_MANIFEST"; return
    fi
    if echo "$CONTENT" | grep -q "discord\|webhook\|bot_token\|channel_id"; then
        echo "DISCORD_CONFIG"; return
    fi
    if echo "$CONTENT" | grep -q "invoice\|amount.*due\|payment\|total.*\$\|usd"; then
        echo "PDF_FINANCE"; return
    fi
    if echo "$CONTENT" | grep -q "constitution\|governance\|dao\|vote\|proposal"; then
        echo "GOVERNANCE_DOC"; return
    fi

    # Size-based fallback
    if [ "$SIZE" -lt 100 ]; then
        echo "MICRO_FILE"; return
    fi

    echo "UNRESOLVABLE"
}

# ── antibody reason mapper ────────────────────────────────────────────────────
antibody_reason() {
    NEW_CAT="$1"
    case "$NEW_CAT" in
        ARCHIVE_ARTIFACT)   echo "Binary archive — not a text artifact, skip classification" ;;
        BINARY_ARTIFACT)    echo "Binary/compiled file — classify by purpose, not content" ;;
        IMAGE_ASSET)        echo "Image asset — no text classification possible" ;;
        DOCKER_CONFIG)      echo "Docker infrastructure file" ;;
        ENV_CONFIG)         echo "Environment configuration — may contain secrets" ;;
        NODE_CONFIG)        echo "Node.js/TypeScript project config" ;;
        RUST_CONFIG)        echo "Rust project config — pairs with RUST_KERNEL" ;;
        BUILD_CONFIG)       echo "Build system config — infrastructure layer" ;;
        LOCK_FILE)          echo "Dependency lock file — auto-generated, skip" ;;
        LICENSE_FILE)       echo "License or legal notice file" ;;
        SOLIDITY_CONTRACT)  echo "Smart contract — blockchain/DAO infrastructure" ;;
        AI_INTEGRATION)     echo "Claude/Anthropic AI integration code" ;;
        SAGCO_ARTIFACT)     echo "SAGCO-OS generated artifact — add to SAGCO_COMMAND category" ;;
        K8S_MANIFEST)       echo "Kubernetes deployment manifest — infrastructure layer" ;;
        DISCORD_CONFIG)     echo "Discord bot configuration" ;;
        GOVERNANCE_DOC)     echo "DAO/governance document" ;;
        MICRO_FILE)         echo "File under 100 bytes — stub, placeholder, or empty" ;;
        UNRESOLVABLE)       echo "Cannot classify — needs manual review or new pattern" ;;
        *)                  echo "Reclassified to $NEW_CAT" ;;
    esac
}

# ── process UNKNOWN entries ───────────────────────────────────────────────────
UNKNOWN_COUNT=$(grep -c ",UNKNOWN," "$SOURCE" 2>/dev/null || echo 0)
echo "UNKNOWN artifacts to process: $UNKNOWN_COUNT"
echo ""

if [ "$UNKNOWN_COUNT" -eq 0 ]; then
    echo "No UNKNOWN artifacts — system fully classified."
    echo "STATUS=SAGCO_ANTIBODY_PASS"
    exit 0
fi

# Write reclassified CSV header
echo "timestamp,device,old_category,new_category,reason,filename,path" > "$RECLASSIFIED"

RECLASSIFIED_CT=0
UNRESOLVABLE_CT=0
BINARY_CT=0
MICRO_CT=0

echo "ANTIBODY PROCESSING:"
echo ""

grep ",UNKNOWN," "$SOURCE" | while IFS=, read -r TS DV CAT FNAME FPATH SZ EXT; do
    NEW_CAT=$(deep_classify "$FPATH")
    REASON=$(antibody_reason "$NEW_CAT")

    echo "${STAMP},${DEV},UNKNOWN,${NEW_CAT},${REASON},${FNAME},${FPATH}" >> "$RECLASSIFIED"

    case "$NEW_CAT" in
        UNRESOLVABLE)
            printf "  [UNRESOLVABLE] %-40s — %s\n" "$FNAME" "$REASON"
            ;;
        MICRO_FILE)
            printf "  [MICRO]        %-40s — %s bytes\n" "$FNAME" "$SZ"
            ;;
        BINARY_ARTIFACT|ARCHIVE_ARTIFACT|IMAGE_ASSET)
            printf "  [BINARY]       %-40s — %s\n" "$FNAME" "$NEW_CAT"
            ;;
        *)
            printf "  [RECLASSIFIED] %-40s → %s\n" "$FNAME" "$NEW_CAT"
            ;;
    esac
done

# Recount results
RECLASSIFIED_CT=$(grep -vc "UNRESOLVABLE\|MICRO_FILE\|BINARY_ARTIFACT\|ARCHIVE_ARTIFACT\|IMAGE_ASSET" "$RECLASSIFIED" 2>/dev/null || echo 0)
RECLASSIFIED_CT=$((RECLASSIFIED_CT - 1))  # subtract header
UNRESOLVABLE_CT=$(grep -c ",UNRESOLVABLE," "$RECLASSIFIED" 2>/dev/null || echo 0)
BINARY_CT=$(grep -c ",BINARY_ARTIFACT,\|,ARCHIVE_ARTIFACT,\|,IMAGE_ASSET," "$RECLASSIFIED" 2>/dev/null || echo 0)
MICRO_CT=$(grep -c ",MICRO_FILE," "$RECLASSIFIED" 2>/dev/null || echo 0)

echo ""
echo "ANTIBODY RESULTS:"
printf "  %-22s %d\n" "Reclassified"   "$RECLASSIFIED_CT"
printf "  %-22s %d\n" "Binary/Archive" "$BINARY_CT"
printf "  %-22s %d\n" "Micro files"    "$MICRO_CT"
printf "  %-22s %d\n" "Unresolvable"   "$UNRESOLVABLE_CT"
echo ""

# ── write antibody report ─────────────────────────────────────────────────────
cat > "$REPORT" << RPT
# SAGCO Antibody Report — UNKNOWN Classifier
Generated: $STAMP
Device: $DEV
Source: $SOURCE

## Antibody Results

| Outcome | Count |
|---------|-------|
| Reclassified | $RECLASSIFIED_CT |
| Binary/Archive | $BINARY_CT |
| Micro files (<100b) | $MICRO_CT |
| Unresolvable | $UNRESOLVABLE_CT |
| **Total processed** | **$UNKNOWN_COUNT** |

## Reclassified Inventory

See: $RECLASSIFIED

## Unresolvable Files

These need manual pattern additions to sagco-classify:

$(grep ",UNRESOLVABLE," "$RECLASSIFIED" 2>/dev/null | awk -F',' '{print "- " $6 " (" $7 ")"}')

## Pattern Recommendations

Add these to sagco-classify classify_file() if seeing repeating unknowns:
- New extension? → add case to classify_file() EXT block
- New content pattern? → add grep signal to relevant category

STATUS=SAGCO_ANTIBODY_PASS
RPT

# ── update live CSV: replace UNKNOWN entries with reclassified ones ──────────
if [ "$RECLASSIFIED_CT" -gt 0 ] && [ -f "$LIVE_CSV" ]; then
    # Simple pass: for each reclassified entry, update the category in live CSV
    grep ",UNKNOWN," "$RECLASSIFIED" | while IFS=, read -r TS DV OLD NEW REASON FNAME FPATH; do
        if [ "$NEW" != "UNRESOLVABLE" ]; then
            # Replace UNKNOWN with new category for this filename in live CSV
            sed -i "s|,UNKNOWN,${FNAME},|,${NEW},${FNAME},|g" "$LIVE_CSV" 2>/dev/null
        fi
    done
    echo "Live CSV updated: $LIVE_CSV"
fi

# ── ledger + race ─────────────────────────────────────────────────────────────
HASH=$(echo "${STAMP}sagco-antibody" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${DEV},sagco-antibody,${REPORT},${HASH},SAGCO_ANTIBODY_PASS" >> "$LEDGER"

RACE_OUT="$HOME/sagco_race/race_log.csv"
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
mkdir -p "$(dirname "$RACE_OUT")"
[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${DEV},sagco_antibody,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

echo "Report: $REPORT"
echo "Reclassified: $RECLASSIFIED"
echo ""
echo "STATUS=SAGCO_ANTIBODY_PASS"
echo "UNKNOWN_PROCESSED=$UNKNOWN_COUNT"
echo "RECLASSIFIED=$RECLASSIFIED_CT"
echo "UNRESOLVABLE=$UNRESOLVABLE_CT"
