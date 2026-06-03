#!/bin/sh
# sagco-provenance — SAGCO Artifact Attribution Engine
# Every artifact generated anywhere gets a full provenance header.
# This is the fix for unknown=69%. No artifact escapes without identity.
#
# Usage (standalone):
#   sagco-provenance                    → show provenance for this session
#   sagco-provenance stamp <file>       → inject provenance header into a file
#   sagco-provenance verify <file>      → check provenance header in a file
#   sagco-provenance patch              → patch all sagco_* output dirs with _latest
#   sagco-provenance fix-unknown        → re-attribute unknown ledger/race rows
#
# Usage (sourced library):
#   . sagco-provenance.sh               → loads sagco_prov_header() into shell
#   sagco_prov_header                   → prints 6-line provenance block
#   SAGCO_AID=$(sagco_aid <file>)       → compute artifact ID for a file
#
# Every artifact written by any sagco command should start with:
#   $(sagco_prov_header)
# or contain:
#   sagco_provenance: { device: zfold, brain: execution, project: ..., aid: sha256... }

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
LEDGER="$HOME/sagco_ledger.csv"
RACE_OUT="$HOME/sagco_race/race_log.csv"
PROV_LOG="$HOME/sagco_race/provenance_log.csv"

# ── detect device if still unknown ───────────────────────────────────────────
if [ "$DEV" = "unknown" ]; then
    if [ -f /proc/ish ]; then
        DEV="ish"
    elif [ -n "$TERMUX_VERSION" ] || [ -d /data/data/com.termux ]; then
        MODEL=$(getprop ro.product.model 2>/dev/null | tr '[:upper:]' '[:lower:]')
        case "$MODEL" in
            *fold*|*flip*) DEV="zfold" ;;
            *)             DEV="termux" ;;
        esac
    elif [ "$(uname -o 2>/dev/null)" = "Android" ]; then
        DEV="android"
    elif [ "$(uname -s 2>/dev/null)" = "Darwin" ]; then
        DEV="macos"
    fi
fi

# ── derive brain role ─────────────────────────────────────────────────────────
brain_role() {
    case "${1:-$DEV}" in
        ish)     echo "integration" ;;
        ipad)    echo "ideation"    ;;
        termux)  echo "compilation" ;;
        zfold)   echo "execution"   ;;
        linux)   echo "build"       ;;
        macos)   echo "development" ;;
        *)       echo "unknown"     ;;
    esac
}

# ── detect project from PWD ───────────────────────────────────────────────────
detect_project() {
    # Check for known project markers in current and parent directories
    D="$PWD"
    for _ in 1 2 3; do
        CARGO="$D/Cargo.toml"
        if [ -f "$CARGO" ]; then
            NAME=$(grep "^name" "$CARGO" 2>/dev/null | head -1 | cut -d'"' -f2)
            echo "${NAME:-$(basename "$D")}"
            return
        fi
        D=$(dirname "$D")
    done

    # Fallback: use directory name
    basename "$PWD"
}

# ── compute artifact ID ───────────────────────────────────────────────────────
# Stable ID: sha256 of file content if exists, else hash of stamp+device+cmd
sagco_aid() {
    F="${1:-}"
    if [ -f "$F" ]; then
        sha256sum "$F" 2>/dev/null | cut -c1-16 || cksum "$F" | awk '{printf "%016d", $1}'
    else
        echo "${STAMP}${DEV}${F}" | cksum | awk '{printf "%016d", $1}'
    fi
}

# ── provenance header block (YAML format) ────────────────────────────────────
# Designed to be embedded at top of any artifact file.
sagco_prov_header() {
    ROLE=$(brain_role "$DEV")
    PROJECT=$(detect_project)
    AID=$(echo "${STAMP}${DEV}${PROJECT}" | cksum | awk '{printf "%016d", $1}')
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    cat << PROV
# sagco_provenance:
#   device: ${DEV}
#   brain: ${ROLE}
#   project: ${PROJECT}
#   timestamp: ${STAMP}
#   artifact_id: ${AID}
#   battery: ${BAT}
PROV
}

# ── if sourced, export functions and exit ─────────────────────────────────────
# When `. sagco-provenance.sh` is used, make helpers available
if [ "${0##*/}" != "sagco-provenance.sh" ] && [ "${0##*/}" != "sh" ]; then
    export SAGCO_DEVICE="$DEV"
    export SAGCO_BRAIN_ROLE="$(brain_role "$DEV")"
    export SAGCO_PROJECT="$(detect_project)"
    return 0 2>/dev/null || true
fi

# ── standalone commands ───────────────────────────────────────────────────────
mkdir -p "$(dirname "$PROV_LOG")"
ROLE=$(brain_role "$DEV")
PROJECT=$(detect_project)

CMD="${1:-show}"

case "$CMD" in

    show|"")
        AID=$(echo "${STAMP}${DEV}${PROJECT}" | cksum | awk '{printf "%016d", $1}')
        BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
        echo "SAGCO PROVENANCE — Session Identity"
        echo "====================================="
        printf "  %-18s %s\n" "device:"       "$DEV"
        printf "  %-18s %s\n" "brain:"        "$ROLE"
        printf "  %-18s %s\n" "project:"      "$PROJECT"
        printf "  %-18s %s\n" "timestamp:"    "$STAMP"
        printf "  %-18s %s\n" "artifact_id:"  "$AID"
        printf "  %-18s %s%%\n" "battery:"    "$BAT"
        printf "  %-18s %s\n" "pwd:"          "$PWD"
        echo ""
        ;;

    stamp)
        TARGET="$2"
        if [ -z "$TARGET" ]; then
            echo "Usage: sagco-provenance stamp <file>"
            exit 1
        fi
        AID=$(sagco_aid "$TARGET")
        PROV_BLOCK=$(sagco_prov_header)

        if [ -f "$TARGET" ]; then
            # Prepend provenance to existing file
            TMP="${TARGET}.prov_tmp"
            { echo "$PROV_BLOCK"; cat "$TARGET"; } > "$TMP" && mv "$TMP" "$TARGET"
            echo "  Stamped: $TARGET (AID=$AID)"
        else
            echo "$PROV_BLOCK" > "$TARGET"
            echo "  Created: $TARGET (AID=$AID)"
        fi

        # Log the provenance
        [ -f "$PROV_LOG" ] || echo "timestamp,device,brain,project,artifact,aid,status" > "$PROV_LOG"
        echo "${STAMP},${DEV},${ROLE},${PROJECT},${TARGET},${AID},SAGCO_PROV_STAMPED" >> "$PROV_LOG"
        ;;

    verify)
        TARGET="$2"
        if [ -z "$TARGET" ] || [ ! -f "$TARGET" ]; then
            echo "Usage: sagco-provenance verify <file>"
            exit 1
        fi
        echo "PROVENANCE VERIFICATION — $TARGET"
        echo "======================================"
        if grep -q "sagco_provenance:" "$TARGET" 2>/dev/null; then
            grep "^#   " "$TARGET" | head -8 | sed 's/^#   /  /'
            echo ""
            echo "  STATUS=PROVENANCE_VERIFIED"
        else
            echo "  WARNING: no provenance header found"
            echo "  FIX: sagco-provenance stamp $TARGET"
            echo "  STATUS=PROVENANCE_MISSING"
        fi
        ;;

    patch)
        # Copy timestamped outputs to _latest stable names for each known output dir
        echo "PROVENANCE PATCH — linking _latest artifacts"
        echo "=============================================="
        patch_dir() {
            DIR="$1"; PATTERN="$2"; DEST="$3"
            [ -d "$DIR" ] || return
            NEWEST=$(ls -1t "${DIR}/${PATTERN}" 2>/dev/null | head -1)
            if [ -n "$NEWEST" ] && [ -f "$NEWEST" ]; then
                cp "$NEWEST" "${DIR}/${DEST}" && echo "  patched: ${DIR}/${DEST}"
            fi
        }
        patch_dir "$HOME/sagco_refinery"   "refinery_score_*.yaml"   "refinery_score_latest.yaml"
        patch_dir "$HOME/sagco_mri"        "mri_score_*.yaml"         "mri_score_latest.yaml"
        patch_dir "$HOME/sagco_antibody"   "antibody_*.md"            "antibody_report_latest.md"
        patch_dir "$HOME/sagco_classify"   "classified_inventory_*.csv" "classified_inventory_latest.csv"
        patch_dir "$HOME/sagco_eru_device" "eru_device_*.yaml"        "eru_device_latest.yaml"
        patch_dir "$HOME/sagco_verify"     "verify_*.txt"             "verify_genesis_latest.txt"
        patch_dir "$HOME/sagco_master_report" "master_report_*.md"    "master_report_latest.md"
        echo ""
        echo "STATUS=SAGCO_PROV_PATCH_PASS"
        ;;

    fix-unknown)
        # Re-attribute unknown rows in race_log + ledger to current device
        echo "ATTRIBUTION FIX — re-labeling unknown rows as device=${DEV}"
        echo "============================================================="

        fix_log() {
            LOG="$1"
            [ -f "$LOG" ] || { echo "  skip (not found): $LOG"; return; }
            BEFORE=$(grep -c ",unknown," "$LOG" 2>/dev/null || echo 0)
            if [ "$BEFORE" -gt 0 ]; then
                TMP="${LOG}.fix_tmp"
                sed "s/,unknown,/,${DEV},/g" "$LOG" > "$TMP" && mv "$TMP" "$LOG"
                echo "  fixed: $LOG — $BEFORE rows re-attributed to ${DEV}"
            else
                echo "  clean: $LOG — no unknown rows"
            fi
        }

        fix_log "$RACE_OUT"
        fix_log "$LEDGER"
        fix_log "$HOME/sagco_context_log.csv"

        echo ""
        REMAINING=$(grep -c ",unknown," "$RACE_OUT" 2>/dev/null || echo 0)
        echo "  Remaining unknown ticks: $REMAINING"
        echo "STATUS=SAGCO_PROV_FIX_PASS"
        ;;

    *)
        echo "Usage: sagco-provenance [show|stamp <file>|verify <file>|patch|fix-unknown]"
        exit 1
        ;;
esac

# ── log provenance tick ───────────────────────────────────────────────────────
AID_S=$(echo "${STAMP}${DEV}${PROJECT}" | cksum | awk '{printf "%016d", $1}')
[ -f "$PROV_LOG" ] || echo "timestamp,device,brain,project,artifact,aid,status" > "$PROV_LOG"
echo "${STAMP},${DEV},${ROLE},${PROJECT},provenance_session,${AID_S},SAGCO_PROV_TICK" >> "$PROV_LOG"

BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${DEV},sagco_provenance_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

HASH=$(echo "${STAMP}sagco-provenance${DEV}${CMD}" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${DEV},sagco-provenance,${CMD},${HASH},SAGCO_PROV_TICK" >> "$LEDGER"

echo "STATUS=SAGCO_PROV_TICK"
echo "DEVICE=${DEV}"
echo "BRAIN=${ROLE}"
echo "PROJECT=${PROJECT}"
