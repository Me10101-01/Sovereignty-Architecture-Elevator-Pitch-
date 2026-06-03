#!/bin/sh
# sagco-dept — SAGCO Corporate Department Agent Registry
# Each department is a named SAGCO agent with its own:
#   - device role, artifact category, refinery weight, ERU tracking
# Departments feed the refinery → portfolio pipeline.
#
# Usage:
#   sagco-dept                        → show active department for this device
#   sagco-dept list                   → show all departments + roles
#   sagco-dept register <dept>        → register this device under a department
#   sagco-dept report                 → per-department artifact + ERU summary
#   sagco-dept refinery               → run refinery scoped to active department
#
# Departments:
#   it-dept       → infrastructure, network, sagco-360, fleet ops
#   finance-dept  → nina-trader, ERU, invoice tracking, burn rate
#   engineering   → Rust kernel, compilation, sagco-classify, pipeline
#   ops-dept      → sagco-daemon, deployment, state, fleet orchestration
#   research      → doctrine YAML, case studies, architecture, ideation

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
DEPT_REGISTRY="$HOME/sagco_fleet/dept_registry.yaml"
DEPT_LEDGER="$HOME/sagco_fleet/dept_ledger.csv"
RACE_OUT="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"

mkdir -p "$HOME/sagco_fleet"

# ── department definitions ────────────────────────────────────────────────────
dept_for_device() {
    case "${1:-$DEV}" in
        zfold|termux) echo "it-dept" ;;
        ish)          echo "engineering" ;;
        ipad)         echo "research" ;;
        hp|sagco-os)  echo "ops-dept" ;;
        *)            echo "unassigned" ;;
    esac
}

dept_artifact_class() {
    case "$1" in
        it-dept)     echo "YAML_SYSTEM,CSV_DATA,SAGCO_COMMAND" ;;
        finance-dept) echo "PDF_FINANCE,XLSX_PORTFOLIO,CSV_DATA" ;;
        engineering) echo "RUST_KERNEL,RUST_MODULE,PYTHON_MODULE,SAGCO_COMMAND" ;;
        ops-dept)    echo "YAML_SYSTEM,MD_LEDGER,YAML_CONFIG" ;;
        research)    echo "YAML_DOCTRINE,MD_CASE_STUDY,MD_SAGCO" ;;
        *)           echo "UNKNOWN" ;;
    esac
}

dept_refinery_weight() {
    case "$1" in
        it-dept)     echo "3" ;;   # runtime points
        finance-dept) echo "5" ;;  # client evidence points
        engineering) echo "4" ;;   # portfolio points
        ops-dept)    echo "3" ;;   # intelligence points
        research)    echo "5" ;;   # case study points
        *)           echo "1" ;;
    esac
}

dept_primary_commands() {
    case "$1" in
        it-dept)     echo "sagco-360 sagco-cloud-ping sagco-nems sagco-node-id" ;;
        finance-dept) echo "nina-trader sagco-eru sagco-refinery sagco-wafer" ;;
        engineering) echo "sagco-classify sagco-antibody sagco-verify sagco-mri" ;;
        ops-dept)    echo "sagco-daemon sagco-state sagco-mansion sagco-sync-brain" ;;
        research)    echo "sagco-brain sagco-master-report sagco-portfolio sagco-sheet" ;;
        *)           echo "sagco-pwd sagco-race sagco-identity" ;;
    esac
}

# ── list all departments ──────────────────────────────────────────────────────
list_depts() {
    echo "SAGCO DEPARTMENT REGISTRY"
    echo "=========================="
    echo ""
    for DEPT in it-dept finance-dept engineering ops-dept research; do
        WEIGHT=$(dept_refinery_weight "$DEPT")
        CLASSES=$(dept_artifact_class "$DEPT")
        CMDS=$(dept_primary_commands "$DEPT")
        echo "  [$DEPT]"
        printf "    %-20s %s pts\n" "refinery_weight:" "$WEIGHT"
        printf "    %-20s %s\n"     "artifact_classes:" "$CLASSES"
        printf "    %-20s %s\n"     "primary_commands:" "$CMDS"
        echo ""
    done
}

# ── register device under a department ───────────────────────────────────────
register_dept() {
    DEPT="${1:-$(dept_for_device "$DEV")}"
    WEIGHT=$(dept_refinery_weight "$DEPT")
    CMDS=$(dept_primary_commands "$DEPT")

    [ -f "$DEPT_REGISTRY" ] || cat > "$DEPT_REGISTRY" << RINIT
# SAGCO Department Registry
---
departments:
RINIT

    # Remove old entry for this device
    TMP="${DEPT_REGISTRY}.tmp"
    grep -v "^  ${DEV}:" "$DEPT_REGISTRY" > "$TMP" 2>/dev/null && mv "$TMP" "$DEPT_REGISTRY"

    cat >> "$DEPT_REGISTRY" << ENTRY
  ${DEV}:
    device: ${DEV}
    department: ${DEPT}
    registered: ${STAMP}
    refinery_weight: ${WEIGHT}
    primary_commands: "${CMDS}"
ENTRY

    echo "  Registered: $DEV → $DEPT (weight=$WEIGHT)"
    echo "  Registry: $DEPT_REGISTRY"

    # Also write to dept ledger
    [ -f "$DEPT_LEDGER" ] || echo "timestamp,device,department,weight,status" > "$DEPT_LEDGER"
    echo "${STAMP},${DEV},${DEPT},${WEIGHT},SAGCO_DEPT_REGISTERED" >> "$DEPT_LEDGER"

    echo ""
    echo "  Primary commands for $DEPT:"
    echo "  $CMDS" | tr ' ' '\n' | sed 's/^/    /'
}

# ── per-department artifact summary ──────────────────────────────────────────
dept_report() {
    echo "DEPARTMENT REPORT"
    echo "=================="
    echo ""

    [ -f "$LEDGER" ] || { echo "  (no ledger found)"; return; }

    for DEPT in it-dept finance-dept engineering ops-dept research unassigned; do
        # Find devices in this dept
        DEPT_DEVS=""
        if [ -f "$DEPT_REGISTRY" ]; then
            DEPT_DEVS=$(grep -B1 "department: ${DEPT}" "$DEPT_REGISTRY" 2>/dev/null | \
                grep "device:" | awk '{print $2}' | tr '\n' ' ')
        fi
        [ -z "$DEPT_DEVS" ] && continue

        TOTAL_ARTIFACTS=0
        LAST_ACTIVITY=""
        for DDEV in $DEPT_DEVS; do
            CNT=$(grep -c ",${DDEV}," "$LEDGER" 2>/dev/null || echo 0)
            TOTAL_ARTIFACTS=$((TOTAL_ARTIFACTS + CNT))
            LAST=$(grep ",${DDEV}," "$LEDGER" 2>/dev/null | tail -1 | cut -d',' -f1)
            [ -n "$LAST" ] && LAST_ACTIVITY="$LAST"
        done

        WEIGHT=$(dept_refinery_weight "$DEPT")
        REFINERY_SCORE=$((TOTAL_ARTIFACTS * WEIGHT))

        printf "  [%-15s]  devices=%-15s artifacts=%-6d weight=%s pts=%-6d last=%s\n" \
            "$DEPT" "${DEPT_DEVS:-none}" "$TOTAL_ARTIFACTS" "$WEIGHT" \
            "$REFINERY_SCORE" "${LAST_ACTIVITY:-never}"
    done
    echo ""
}

# ── run refinery scoped to active department ──────────────────────────────────
dept_refinery() {
    ACTIVE_DEPT=$(dept_for_device "$DEV")
    [ -f "$DEPT_REGISTRY" ] && {
        REGISTERED=$(grep -A3 "^  ${DEV}:" "$DEPT_REGISTRY" 2>/dev/null | \
            grep "department:" | awk '{print $2}')
        [ -n "$REGISTERED" ] && ACTIVE_DEPT="$REGISTERED"
    }

    echo "DEPARTMENT REFINERY — $ACTIVE_DEPT"
    echo "====================================="
    echo "Device: $DEV"
    echo "Dept:   $ACTIVE_DEPT"
    echo "Weight: $(dept_refinery_weight "$ACTIVE_DEPT")"
    echo ""

    # Run sagco-refinery if available
    REFINERY_CMD="$HOME/bin/sagco-refinery"
    [ -x "$REFINERY_CMD" ] || REFINERY_CMD="$(dirname "$0")/sagco-refinery.sh"

    if [ -x "$REFINERY_CMD" ]; then
        sh "$REFINERY_CMD"
    else
        echo "  sagco-refinery not installed — run sagco-vim-install sagco-refinery.sh"
    fi
}

# ── write ledger ──────────────────────────────────────────────────────────────
write_ledger() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
    echo "${STAMP},${DEV},sagco_dept_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"
    HASH=$(echo "${STAMP}sagco-dept${DEV}${CMD}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-dept,${DEPT_REGISTRY},${HASH},SAGCO_DEPT_PASS" >> "$LEDGER"
}

# ── show active dept ──────────────────────────────────────────────────────────
show_active() {
    ACTIVE=$(dept_for_device "$DEV")
    [ -f "$DEPT_REGISTRY" ] && {
        REGISTERED=$(grep -A3 "^  ${DEV}:" "$DEPT_REGISTRY" 2>/dev/null | \
            grep "department:" | awk '{print $2}')
        [ -n "$REGISTERED" ] && ACTIVE="$REGISTERED"
    }

    echo "ACTIVE DEPARTMENT"
    echo "=================="
    printf "  %-16s %s\n" "Device:"     "$DEV"
    printf "  %-16s %s\n" "Department:" "$ACTIVE"
    printf "  %-16s %s\n" "Weight:"     "$(dept_refinery_weight "$ACTIVE")"
    printf "  %-16s %s\n" "Commands:"   "$(dept_primary_commands "$ACTIVE")"
    printf "  %-16s %s\n" "Artifacts:"  "$(dept_artifact_class "$ACTIVE")"
    echo ""
    echo "  To register: sagco-dept register $ACTIVE"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-show}"

case "$CMD" in
    list)             list_depts ;;
    register)         register_dept "${2:-}" ; write_ledger ;;
    report)           dept_report ; write_ledger ;;
    refinery)         dept_refinery ; write_ledger ;;
    show|"")          show_active ;;
    it-dept|finance-dept|engineering|ops-dept|research)
                      register_dept "$CMD" ; write_ledger ;;
    *)
        echo "Usage: sagco-dept [show|list|register <dept>|report|refinery]"
        echo "Depts: it-dept  finance-dept  engineering  ops-dept  research"
        exit 1
        ;;
esac
