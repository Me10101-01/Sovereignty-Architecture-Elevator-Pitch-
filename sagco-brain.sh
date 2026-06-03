#!/bin/sh
# sagco-brain — SAGCO Context Node Writer
# Writes a context checkpoint to the Obsidian brain corpus callosum.
# Each call = one neuron firing. SAGCO_OBSIDIAN_BRAIN/nodes/ = memory.
#
# Usage:
#   sagco-brain                                → write context for current device
#   sagco-brain zfold "context_verified"       → write for zfold with label
#   sagco-brain ipad "qr_audit" ~/context.csv  → write + append to context log
#   sagco-brain show                           → show brain nodes for this device
#   sagco-brain show zfold                     → show zfold brain nodes
#   sagco-brain corpus                         → show full corpus callosum (all nodes)
#   sagco-brain replay zfold                   → replay zfold's node sequence

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
BRAIN_DIR="$HOME/SAGCO_OBSIDIAN_BRAIN/nodes"
CORPUS_LOG="$HOME/SAGCO_OBSIDIAN_BRAIN/corpus_callosum.csv"
CONTEXT_LOG="${SAGCO_CONTEXT_LOG:-$HOME/sagco_context_log.csv}"
RACE_OUT="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"

mkdir -p "$BRAIN_DIR" "$(dirname "$CORPUS_LOG")"

# ── subcommands ───────────────────────────────────────────────────────────────
CMD="${1:-write}"

case "$CMD" in

    show)
        TARGET="${2:-$DEV}"
        echo "BRAIN NODES — device=${TARGET}"
        echo "================================"
        NODES=$(ls -1t "$BRAIN_DIR/${TARGET}_"*.md 2>/dev/null | head -10)
        if [ -n "$NODES" ]; then
            echo "$NODES" | while read -r N; do
                LABEL=$(head -1 "$N" 2>/dev/null | sed 's/# //')
                printf "  %-50s\n" "$N"
                printf "    → %s\n" "$LABEL"
            done
        else
            echo "  (no brain nodes for device: $TARGET)"
        fi
        exit 0
        ;;

    corpus)
        echo "CORPUS CALLOSUM — full brain timeline"
        echo "======================================"
        [ -f "$CORPUS_LOG" ] || { echo "  (no corpus log yet)"; exit 0; }
        tail -30 "$CORPUS_LOG" | awk -F',' \
            '{printf "  [%s] %-10s %-30s %s\n", $1,$2,$3,$4}'
        TOTAL=$(($(wc -l < "$CORPUS_LOG" 2>/dev/null || echo 1) - 1))
        echo ""
        echo "  Total nodes: $TOTAL"
        exit 0
        ;;

    replay)
        TARGET="${2:-$DEV}"
        echo "BRAIN REPLAY — device=${TARGET}"
        echo "================================"
        NODES=$(ls -1t "$BRAIN_DIR/${TARGET}_"*.md 2>/dev/null)
        COUNT=0
        if [ -n "$NODES" ]; then
            echo "$NODES" | sort | while read -r N; do
                COUNT=$((COUNT + 1))
                echo "  [node $COUNT] $N"
                grep -E "^(context|event|pwd|status):" "$N" 2>/dev/null | sed 's/^/    /'
                echo ""
            done
        else
            echo "  (no nodes to replay for: $TARGET)"
        fi
        exit 0
        ;;

    write|*)
        # parse positional: sagco-brain [device] [label] [logfile]
        BRAIN_DEV="$DEV"
        BRAIN_LABEL="context_checkpoint"
        BRAIN_LOG="$CONTEXT_LOG"

        if [ "$CMD" != "write" ]; then
            case "$CMD" in
                ish|ipad|termux|zfold|linux|android) BRAIN_DEV="$CMD" ;;
                *) BRAIN_LABEL="$CMD" ;;
            esac
        fi
        [ -n "$2" ] && {
            case "$2" in
                ish|ipad|termux|zfold|linux|android) BRAIN_DEV="$2"; [ -n "$3" ] && BRAIN_LABEL="$3" ;;
                *) BRAIN_LABEL="$2" ;;
            esac
        }
        [ -n "$3" ] && case "$3" in
            ish|ipad|termux|zfold) ;;
            *) BRAIN_LOG="$3" ;;
        esac
        [ -n "$4" ] && BRAIN_LOG="$4"
        ;;
esac

# ── gather context snapshot ───────────────────────────────────────────────────
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)

LAST_RACE=""
[ -f "$RACE_OUT" ] && LAST_RACE=$(grep ",${BRAIN_DEV}," "$RACE_OUT" 2>/dev/null | tail -1 | cut -d',' -f3)

LAST_CMD=""
[ -f "$LEDGER" ] && LAST_CMD=$(grep ",${BRAIN_DEV}," "$LEDGER" 2>/dev/null | tail -1 | cut -d',' -f3)

CLASSIFY_COUNT=0
[ -f "$HOME/sagco_classify.csv" ] && CLASSIFY_COUNT=$(wc -l < "$HOME/sagco_classify.csv" 2>/dev/null || echo 0)

ANTIBODY_STATUS="unknown"
AB_LATEST=$(ls -1t "$HOME/sagco_antibody/"*.md 2>/dev/null | head -1)
[ -n "$AB_LATEST" ] && ANTIBODY_STATUS=$(grep "^SYSTEM_HEALTH=" "$AB_LATEST" 2>/dev/null | cut -d'=' -f2 || echo unknown)

STATE_RANK="unknown"
[ -f "$HOME/sagco_state.yaml" ] && STATE_RANK=$(grep "^portfolio_rank:" "$HOME/sagco_state.yaml" 2>/dev/null | awk '{print $2}')

# ── write brain node ─────────────────────────────────────────────────────────
NODE_FILE="$BRAIN_DIR/${BRAIN_DEV}_${STAMP}.md"
cat > "$NODE_FILE" << NODE
# Brain Node — ${BRAIN_DEV} — ${BRAIN_LABEL}
timestamp: ${STAMP}
device: ${BRAIN_DEV}
event: ${BRAIN_LABEL}
pwd: ${PWD}
battery: ${BAT}
last_race_event: ${LAST_RACE:-none}
last_command: ${LAST_CMD:-none}
classify_artifact_count: ${CLASSIFY_COUNT}
antibody_health: ${ANTIBODY_STATUS}
portfolio_rank: ${STATE_RANK:-unknown}
status: SAGCO_BRAIN_NODE
NODE

# ── write context log ─────────────────────────────────────────────────────────
[ -f "$BRAIN_LOG" ] || echo "timestamp,device,event,pwd,battery,last_cmd,antibody,rank,status" > "$BRAIN_LOG"
echo "${STAMP},${BRAIN_DEV},${BRAIN_LABEL},${PWD},${BAT},${LAST_CMD:-none},${ANTIBODY_STATUS},${STATE_RANK:-unknown},SAGCO_BRAIN_NODE" >> "$BRAIN_LOG"

# ── write corpus callosum entry ───────────────────────────────────────────────
[ -f "$CORPUS_LOG" ] || echo "timestamp,device,event,pwd,battery,node_file,status" > "$CORPUS_LOG"
echo "${STAMP},${BRAIN_DEV},${BRAIN_LABEL},${PWD},${BAT},${NODE_FILE},SAGCO_CORPUS_TICK" >> "$CORPUS_LOG"

# ── race tick ─────────────────────────────────────────────────────────────────
[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${BRAIN_DEV},sagco_brain_${BRAIN_LABEL},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

HASH=$(echo "${STAMP}sagco-brain${BRAIN_DEV}${BRAIN_LABEL}" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${BRAIN_DEV},sagco-brain,${NODE_FILE},${HASH},SAGCO_BRAIN_NODE" >> "$LEDGER"

# ── print ─────────────────────────────────────────────────────────────────────
echo "SAGCO BRAIN NODE"
echo "================"
printf "  %-14s %s\n" "Stamp:"    "$STAMP"
printf "  %-14s %s\n" "Device:"   "$BRAIN_DEV"
printf "  %-14s %s\n" "Event:"    "$BRAIN_LABEL"
printf "  %-14s %s\n" "PWD:"      "$PWD"
printf "  %-14s %s%%\n" "Battery:" "$BAT"
printf "  %-14s %s\n" "Antibody:" "$ANTIBODY_STATUS"
printf "  %-14s %s\n" "Rank:"     "${STATE_RANK:-unknown}"
echo ""
echo "  Node:  $NODE_FILE"
echo "  Log:   $BRAIN_LOG"
echo ""
echo "STATUS=SAGCO_BRAIN_NODE"
