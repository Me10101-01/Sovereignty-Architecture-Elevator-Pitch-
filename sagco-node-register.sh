#!/bin/sh
# sagco-node-register — SAGCO Fleet Node Registration
# Register any node: phone, laptop, Raspberry Pi, cloud VM.
# Every node becomes a measurable fleet member with artifacts + contribution %.
#
# Usage:
#   sagco-node-register                              → register current device
#   sagco-node-register rpi-telemetry-01             → register an RPi
#   sagco-node-register rpi-camera-01 rpi vision     → name + type + role
#   sagco-node-register seed                         → pre-seed all 11 known nodes
#   sagco-node-register case-study <node>            → generate per-node case study

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
REGISTRY="$HOME/sagco_fleet/node_registry.yaml"
CASE_DIR="$HOME/sagco_fleet/case_studies"
LEDGER="$HOME/sagco_ledger.csv"
RACE_LOG="$HOME/sagco_race/race_log.csv"

mkdir -p "$HOME/sagco_fleet" "$CASE_DIR"

# ── node type defaults ────────────────────────────────────────────────────────
node_defaults() {
    NODE="$1"
    case "$NODE" in
        ipad)               echo "apple_tablet   ideation      corpus_christi WorkingCopy@iPad-04062025" ;;
        zfold)              echo "android_phone  execution     corpus_christi SAGCO-OS-PIPELINE" ;;
        termux)             echo "android_phone  compilation   corpus_christi SAGCO-OS-PIPELINE" ;;
        ish)                echo "ios_emulator   integration   corpus_christi WorkingCopy@iPad-04062025" ;;
        hp|hp-sagco-os)     echo "laptop_x86     mansion       corpus_christi GitKraken-DESKTOP" ;;
        linux)              echo "linux_vm       build         cloud          git-key" ;;
        rpi-telemetry-01)   echo "raspberry_pi   telemetry     corpus_christi SAGCO-OS-PIPELINE" ;;
        rpi-camera-01)      echo "raspberry_pi   vision        corpus_christi SAGCO-OS-PIPELINE" ;;
        rpi-weather-01)     echo "raspberry_pi   weather       corpus_christi SAGCO-OS-PIPELINE" ;;
        rpi-qr-01)          echo "raspberry_pi   qr_scanner    corpus_christi SAGCO-OS-PIPELINE" ;;
        rpi-inventory-01)   echo "raspberry_pi   inventory     corpus_christi SAGCO-OS-PIPELINE" ;;
        rpi-inference-01)   echo "raspberry_pi   ai_inference  corpus_christi SAGCO-OS-PIPELINE" ;;
        *)                  echo "unknown        node          unknown        git-key" ;;
    esac
}

node_commands() {
    case "$1" in
        ipad)             echo "sagco-brain sagco-master-report sagco-sheet" ;;
        zfold)            echo "sagco-race sagco-brain sagco-eru sagco-360 sagco-nems nina-trader" ;;
        termux)           echo "sagco-classify sagco-antibody cargo-build sagco-verify" ;;
        ish)              echo "sagco-ish-heartbeat sagco-classify sagco-refinery sagco-mri" ;;
        hp|hp-sagco-os)   echo "sagco-daemon sagco-state sagco-mansion sagco-gcp sagco-sync-brain" ;;
        rpi-telemetry-01) echo "sagco-360 sagco-cloud-ping sagco-race" ;;
        rpi-camera-01)    echo "sagco-360 sagco-race sagco-brain" ;;
        rpi-weather-01)   echo "sagco-360 sagco-cloud-ping sagco-race" ;;
        rpi-qr-01)        echo "sagco-race sagco-cloud-ping" ;;
        rpi-inventory-01) echo "sagco-race sagco-cloud-ping sagco-brain" ;;
        rpi-inference-01) echo "sagco-race sagco-brain sagco-eru" ;;
        *)                echo "sagco-race sagco-cloud-ping" ;;
    esac
}

# ── init registry if missing ──────────────────────────────────────────────────
init_registry() {
    [ -f "$REGISTRY" ] && return
    cat > "$REGISTRY" << INIT
# SAGCO Fleet Node Registry
# Generated: $STAMP
# Format: see sagco-node-register
---
fleet:
  meta:
    created: $STAMP
    owner: Domenic Garza
    org: Strategickhaos DAO LLC
    location: Corpus Christi TX
  nodes:
INIT
}

# ── write one node entry ──────────────────────────────────────────────────────
write_node() {
    NODE="$1"
    TYPE="${2:-$(node_defaults "$NODE" | awk '{print $1}')}"
    ROLE="${3:-$(node_defaults "$NODE" | awk '{print $2}')}"
    LOCATION="${4:-$(node_defaults "$NODE" | awk '{print $3}')}"
    SSH_KEY="${5:-$(node_defaults "$NODE" | awk '{print $4}')}"
    CMDS=$(node_commands "$NODE")

    # Count artifacts from ledger
    ART_COUNT=0
    [ -f "$LEDGER" ] && ART_COUNT=$(grep -c ",${NODE}," "$LEDGER" 2>/dev/null || echo 0)
    RACE_COUNT=0
    [ -f "$RACE_LOG" ] && RACE_COUNT=$(grep -c ",${NODE}," "$RACE_LOG" 2>/dev/null || echo 0)

    # Remove old entry for this node
    TMP="${REGISTRY}.tmp"
    awk -v node="    ${NODE}:" '
        $0 ~ node { skip=1; next }
        skip && /^    [a-z]/ { skip=0 }
        !skip { print }
    ' "$REGISTRY" > "$TMP" 2>/dev/null && mv "$TMP" "$REGISTRY"

    cat >> "$REGISTRY" << ENTRY
    ${NODE}:
      name:       ${NODE}
      type:       ${TYPE}
      role:       ${ROLE}
      location:   ${LOCATION}
      owner:      sagco
      ssh_key:    ${SSH_KEY}
      commands:   "${CMDS}"
      artifacts:  ${ART_COUNT}
      race_ticks: ${RACE_COUNT}
      registered: ${STAMP}
      status:     active
ENTRY

    printf "  ✅ %-22s type=%-15s role=%-15s artifacts=%d\n" \
        "$NODE" "$TYPE" "$ROLE" "$ART_COUNT"
}

# ── seed all 11 known nodes ───────────────────────────────────────────────────
seed_fleet() {
    echo "SEEDING FLEET — 11 nodes"
    echo "=========================="
    init_registry

    for NODE in ipad zfold termux ish hp \
                rpi-telemetry-01 rpi-camera-01 rpi-weather-01 \
                rpi-qr-01 rpi-inventory-01 rpi-inference-01; do
        write_node "$NODE"
    done
    echo ""
    echo "  Registry: $REGISTRY"
    echo "  Run: sagco-node-list"
}

# ── generate per-node case study ──────────────────────────────────────────────
generate_case_study() {
    NODE="$1"
    [ -z "$NODE" ] && { echo "Usage: sagco-node-register case-study <node>"; return 1; }

    DEFAULTS=$(node_defaults "$NODE")
    TYPE=$(echo "$DEFAULTS" | awk '{print $1}')
    ROLE=$(echo "$DEFAULTS" | awk '{print $2}')
    LOCATION=$(echo "$DEFAULTS" | awk '{print $3}')
    CMDS=$(node_commands "$NODE")

    ART_COUNT=0
    [ -f "$LEDGER" ] && ART_COUNT=$(grep -c ",${NODE}," "$LEDGER" 2>/dev/null || echo 0)
    RACE_COUNT=0
    [ -f "$RACE_LOG" ] && RACE_COUNT=$(grep -c ",${NODE}," "$RACE_LOG" 2>/dev/null || echo 0)

    # Contribution %
    TOTAL_ART=0
    [ -f "$LEDGER" ] && TOTAL_ART=$(($(wc -l < "$LEDGER" 2>/dev/null || echo 1) - 1))
    CONTRIB=0
    [ "$TOTAL_ART" -gt 0 ] && \
        CONTRIB=$(echo "scale=1; $ART_COUNT * 100 / $TOTAL_ART" | bc 2>/dev/null || echo 0)

    CASE_FILE="$CASE_DIR/case_study_${NODE}_${STAMP}.md"

    cat > "$CASE_FILE" << CASE
# Case Study — ${NODE}

## Node Profile

| Field | Value |
|-------|-------|
| Name | ${NODE} |
| Type | ${TYPE} |
| Role | ${ROLE} |
| Location | ${LOCATION} |
| Owner | Domenic Garza / Strategickhaos DAO LLC |
| SSH Key | $(node_defaults "$NODE" | awk '{print $4}') |
| Registered | ${STAMP} |

## Performance Metrics

| Metric | Value |
|--------|-------|
| Artifacts Generated | ${ART_COUNT} |
| Race Ticks | ${RACE_COUNT} |
| Fleet Contribution | ${CONTRIB}% |
| Status | active |

## Command Set

\`\`\`
${CMDS}
\`\`\`

## Role in SAGCO Pipeline

\`\`\`
$(case "$ROLE" in
    ideation)     echo "iPad → doctrine/case studies → corpus callosum → portfolio" ;;
    execution)    echo "zfold → race ticks/trading → ledger → ERU → refinery" ;;
    compilation)  echo "termux → cargo build → Rust artifacts → classify → antibody" ;;
    integration)  echo "iSH → heartbeat → classify → refinery → state" ;;
    mansion)      echo "hp → daemon → sync brain → master report → GCP" ;;
    telemetry)    echo "rpi → sagco-360 → cloud-ping → GCP Logs → fleet dashboard" ;;
    vision)       echo "rpi → camera → classify → brain node → portfolio" ;;
    weather)      echo "rpi → sensor → sagco-360 → cloud-ping → telemetry stream" ;;
    qr_scanner)   echo "rpi → scan event → race tick → cloud → analytics" ;;
    inventory)    echo "rpi → count → sagco-brain → ledger → ERU" ;;
    ai_inference) echo "rpi → model → classify → brain → refinery → portfolio" ;;
    *)            echo "${NODE} → sagco-race → ledger → fleet" ;;
esac)
\`\`\`

STATUS=SAGCO_CASE_STUDY_PASS
CASE

    echo "  Case study: $CASE_FILE"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-register}"

echo "SAGCO NODE REGISTER"
echo "===================="
echo "Stamp:  $STAMP"
echo "Device: $DEV"
echo ""

case "$CMD" in
    seed)
        seed_fleet
        ;;
    case-study)
        init_registry
        generate_case_study "${2:-$DEV}"
        ;;
    register|"")
        init_registry
        write_node "$DEV"
        echo ""
        echo "  Run: sagco-node-list"
        ;;
    *)
        # Treat as node name with optional type/role args
        init_registry
        write_node "$CMD" "${2:-}" "${3:-}" "${4:-}" "${5:-}"
        echo ""
        echo "  Run: sagco-node-list"
        ;;
esac

# ── ledger ────────────────────────────────────────────────────────────────────
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
[ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
echo "${STAMP},${DEV},sagco_node_register,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
HASH=$(echo "${STAMP}sagco-node-register${DEV}" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${DEV},sagco-node-register,${REGISTRY},${HASH},SAGCO_NODE_REGISTERED" >> "$LEDGER"
