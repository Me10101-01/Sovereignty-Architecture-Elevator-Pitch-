#!/bin/sh
# sagco-daemon — Polyglot Cross-Device Synchronization Daemon
# Reads sagco-compose.yaml, syncs SAGCO state across iSH / iPad / Termux / Z Fold
# "Quantum entanglement": work done on one device propagates to all others
#
# Usage:
#   sagco-daemon              → start sync loop (foreground on iSH/ash)
#   sagco-daemon once         → single sync pass, exit
#   sagco-daemon status       → show last tick and health
#   sagco-daemon stop         → kill running daemon
#   sagco-daemon compose      → print device role and active compose targets
#   sagco-daemon pipeline     → run full SAGCO pipeline for this device
#   sagco-daemon entangle     → show what this device produces + who consumes it
#   sagco-daemon install      → add sagco-daemon to startup (profile)

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
REPO_ROOT="$(cd "$(dirname "$0")" 2>/dev/null && pwd || echo "$HOME")"
COMPOSE_FILE="$REPO_ROOT/sagco-compose.yaml"
DAEMON_LOG="$HOME/sagco_race/daemon_log.csv"
PID_FILE="$HOME/.sagco_daemon.pid"
LEDGER="$HOME/sagco_ledger.csv"
RACE_OUT="$HOME/sagco_race/race_log.csv"
TICK_INTERVAL=30

mkdir -p "$HOME/sagco_race" "$HOME/sagco_sync"

# ── helpers ───────────────────────────────────────────────────────────────────
log_tick() {
    EVENT="$1"; STATUS="$2"
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$DAEMON_LOG" ] || echo "timestamp,device,event,status,battery" > "$DAEMON_LOG"
    echo "${STAMP},${DEV},${EVENT},${STATUS},${BAT}" >> "$DAEMON_LOG"
}

print_header() {
    echo "SAGCO DAEMON — Cross-Device Sync"
    echo "================================="
    echo "Stamp:   $STAMP"
    echo "Device:  $DEV"
    echo "Compose: $COMPOSE_FILE"
    echo ""
}

# ── read compose targets ──────────────────────────────────────────────────────
# Parse sagco-compose.yaml for sync target paths (simple grep approach for sh)
get_sync_targets() {
    grep "^    - path:" "$COMPOSE_FILE" 2>/dev/null | awk '{print $3}' | sed "s|sagco_|$HOME/sagco_|g" | sed "s|sagco_ledger.csv|$HOME/sagco_ledger.csv|"
}

get_device_role() {
    DEV_KEY="$1"
    grep -A1 "^  ${DEV_KEY}:" "$COMPOSE_FILE" 2>/dev/null | grep "role:" | awk '{print $2}'
}

get_pipeline_stages() {
    grep "command:" "$COMPOSE_FILE" 2>/dev/null | awk '{print $2}' | head -10
}

# ── symlink latest artifacts ──────────────────────────────────────────────────
# After each tool run, link timestamped outputs to _latest for stable sync
link_latest() {
    DIR="$1"
    PATTERN="$2"
    SUFFIX="$3"    # e.g. .yaml or .md
    LATEST_NAME="$4"
    [ -d "$DIR" ] || return
    NEWEST=$(ls -1t "${DIR}/${PATTERN}" 2>/dev/null | head -1)
    if [ -n "$NEWEST" ] && [ -f "$NEWEST" ]; then
        cp "$NEWEST" "${DIR}/${LATEST_NAME}" 2>/dev/null
    fi
}

refresh_latest_links() {
    link_latest "$HOME/sagco_refinery" "refinery_score_*.yaml" ".yaml" "refinery_score_latest.yaml"
    link_latest "$HOME/sagco_refinery" "refinery_report_*.md"  ".md"   "refinery_report_latest.md"
    link_latest "$HOME/sagco_mri"      "mri_score_*.yaml"      ".yaml" "mri_score_latest.yaml"
    link_latest "$HOME/sagco_mri"      "mri_report_*.md"       ".md"   "mri_report_latest.md"
    link_latest "$HOME/sagco_antibody" "antibody_*.md"         ".md"   "antibody_report_latest.md"
    link_latest "$HOME/sagco_eru_device" "eru_device_*.yaml"   ".yaml" "eru_device_latest.yaml"
    link_latest "$HOME/sagco_verify"   "verify_*.txt"          ".txt"  "verify_genesis_latest.txt"
    link_latest "$HOME/sagco_nina/reports" "strategy_score.yaml" ".yaml" "strategy_score_latest.yaml"
    link_latest "$HOME/sagco_classify" "classified_inventory_*.csv" ".csv" "classified_inventory_latest.csv"
}

# ── git sync engine ───────────────────────────────────────────────────────────
sync_via_git() {
    MODE="$1"   # push | pull | both

    if ! git -C "$REPO_ROOT" rev-parse HEAD >/dev/null 2>&1; then
        echo "  [daemon] not a git repo: $REPO_ROOT"
        return 1
    fi

    BRANCH=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || echo "unknown")
    echo "  [daemon] git branch: $BRANCH"

    if [ "$MODE" = "pull" ] || [ "$MODE" = "both" ]; then
        echo "  [daemon] pulling latest from origin/$BRANCH ..."
        git -C "$REPO_ROOT" fetch origin "$BRANCH" 2>&1 | tail -3
        git -C "$REPO_ROOT" merge --ff-only "origin/$BRANCH" 2>/dev/null \
            && echo "  [daemon] pull: OK" \
            || echo "  [daemon] pull: nothing new or conflict (OK to continue)"
    fi

    if [ "$MODE" = "push" ] || [ "$MODE" = "both" ]; then
        refresh_latest_links

        # Stage latest artifacts
        CHANGED=0
        for LATF in \
            "$HOME/sagco_refinery/refinery_score_latest.yaml" \
            "$HOME/sagco_mri/mri_score_latest.yaml" \
            "$HOME/sagco_antibody/antibody_report_latest.md" \
            "$HOME/sagco_classify/classified_inventory_latest.csv" \
            "$HOME/sagco_eru_device/eru_device_latest.yaml" \
            "$HOME/sagco_nina/reports/strategy_score_latest.yaml" \
            "$HOME/sagco_ledger.csv" \
            "$HOME/sagco_race/race_log.csv"
        do
            [ -f "$LATF" ] || continue
            # Copy to repo if different from what's tracked
            DEST="$REPO_ROOT/sagco_sync/$(basename "$LATF")"
            mkdir -p "$REPO_ROOT/sagco_sync"
            cp "$LATF" "$DEST" 2>/dev/null && CHANGED=$((CHANGED + 1))
        done

        if [ "$CHANGED" -gt 0 ]; then
            git -C "$REPO_ROOT" add sagco_sync/ 2>/dev/null
            git -C "$REPO_ROOT" diff --cached --quiet 2>/dev/null || {
                git -C "$REPO_ROOT" commit -m "sagco-daemon sync tick ${STAMP} device=${DEV}" 2>/dev/null \
                    && echo "  [daemon] committed $CHANGED artifacts"
                git -C "$REPO_ROOT" push -u origin "$BRANCH" 2>/dev/null \
                    && echo "  [daemon] push: OK" \
                    || echo "  [daemon] push: network unavailable (will retry next tick)"
            }
        else
            echo "  [daemon] no artifact changes to push"
        fi
    fi
}

# ── copy sync engine (for offline / no-git devices) ──────────────────────────
sync_via_copy() {
    SYNC_DIR="$HOME/sagco_sync"
    mkdir -p "$SYNC_DIR"
    refresh_latest_links

    COPIED=0
    for LATF in \
        "$HOME/sagco_refinery/refinery_score_latest.yaml" \
        "$HOME/sagco_mri/mri_score_latest.yaml" \
        "$HOME/sagco_antibody/antibody_report_latest.md" \
        "$HOME/sagco_classify/classified_inventory_latest.csv" \
        "$HOME/sagco_ledger.csv"
    do
        [ -f "$LATF" ] || continue
        cp "$LATF" "$SYNC_DIR/$(basename "$LATF")" 2>/dev/null && COPIED=$((COPIED + 1))
    done
    echo "  [daemon] copy sync: $COPIED files → $SYNC_DIR"
}

# ── single sync pass ──────────────────────────────────────────────────────────
do_sync_pass() {
    PASS_STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000")
    echo "[${PASS_STAMP}] SAGCO DAEMON TICK — device=${DEV}"

    refresh_latest_links
    echo "  [daemon] latest links refreshed"

    if git -C "$REPO_ROOT" rev-parse HEAD >/dev/null 2>&1; then
        sync_via_git both
    else
        sync_via_copy
    fi

    log_tick "sync_tick" "PASS"

    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    HASH=$(echo "${PASS_STAMP}sagco-daemon-tick" | cksum | awk '{printf "%012d", $1}')
    echo "${PASS_STAMP},${DEV},sagco-daemon,sync_tick,${HASH},SAGCO_DAEMON_TICK" >> "$LEDGER"

    [ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    echo "${PASS_STAMP},${DEV},sagco_daemon_tick,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

    echo ""
}

# ── pipeline runner ───────────────────────────────────────────────────────────
run_pipeline() {
    ROLE=$(get_device_role "$DEV")
    echo "SAGCO PIPELINE RUN — device=${DEV} role=${ROLE}"
    echo ""

    BIN="$HOME/bin"

    run_stage() {
        CMD="$1"
        FULL="$BIN/$CMD"
        if [ -x "$FULL" ]; then
            echo "  → $CMD"
            sh "$FULL" 2>&1 | tail -3
            echo ""
        elif command -v "$CMD" >/dev/null 2>&1; then
            echo "  → $CMD (system path)"
            "$CMD" 2>&1 | tail -3
            echo ""
        else
            echo "  SKIP $CMD — not installed (copy $CMD to ~/bin/)"
        fi
    }

    run_stage sagco-mri
    run_stage sagco-classify
    run_stage sagco-antibody
    run_stage sagco-refinery
    run_stage sagco-eru-device
    run_stage sagco-verify

    if [ "$ROLE" = "compilation" ] || [ "$ROLE" = "execution" ]; then
        NINA="$REPO_ROOT/nina-trader/target/release/nina-trader"
        if [ -x "$NINA" ]; then
            echo "  → nina-trader dry-run all"
            "$NINA" dry-run all 2>&1 | tail -5
            echo ""
        else
            echo "  SKIP nina-trader — not compiled (cd nina-trader && cargo build --release)"
        fi
    fi

    refresh_latest_links
    do_sync_pass

    echo "PIPELINE COMPLETE — device=${DEV}"
}

# ── entanglement report ───────────────────────────────────────────────────────
show_entanglement() {
    ROLE=$(get_device_role "$DEV")
    echo "ENTANGLEMENT MAP — device=${DEV} role=${ROLE}"
    echo ""
    echo "This device PRODUCES:"
    case "$ROLE" in
        integration)
            echo "  classify → sagco_classify/classified_inventory_latest.csv"
            echo "  antibody → sagco_antibody/antibody_report_latest.md"
            echo "  refinery → sagco_refinery/refinery_score_latest.yaml"
            ;;
        compilation)
            echo "  nina backtest → sagco_nina/reports/strategy_score.yaml"
            echo "  rust binary   → nina-trader/target/release/nina-trader"
            ;;
        execution)
            echo "  nina live trades → sagco_nina/trade_log.csv"
            ;;
        ideation)
            echo "  doctrine YAML → EMPIRE_GENOME_v1.7.yaml"
            echo "  case studies  → Bell_Aroma_*.md"
            ;;
    esac
    echo ""
    echo "All devices CONSUME:"
    echo "  sagco_ledger.csv           (append)"
    echo "  sagco_race/race_log.csv    (append)"
    echo "  sagco_state.yaml           (last_write_wins)"
    echo ""
    echo "Quantum entanglement via: sagco_sync/ → git push → git pull (all devices)"
}

# ── status ────────────────────────────────────────────────────────────────────
show_status() {
    echo "SAGCO DAEMON STATUS"
    echo "==================="
    echo "Device:    $DEV"
    echo "Compose:   $COMPOSE_FILE"
    echo "PID file:  $PID_FILE"

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Running:   YES (PID=$PID)"
        else
            echo "Running:   NO (stale PID=$PID)"
        fi
    else
        echo "Running:   NO"
    fi

    echo ""
    if [ -f "$DAEMON_LOG" ]; then
        LAST=$(tail -1 "$DAEMON_LOG" 2>/dev/null)
        echo "Last tick: $LAST"
        TOTAL=$(wc -l < "$DAEMON_LOG" 2>/dev/null || echo 0)
        echo "Tick count: $((TOTAL - 1))"
    else
        echo "Last tick: never"
    fi

    echo ""
    echo "Sync dir:"
    ls -1 "$HOME/sagco_sync/" 2>/dev/null | head -10 | sed 's/^/  /'
    [ ! -d "$HOME/sagco_sync" ] && echo "  (empty)"
}

# ── compose info ──────────────────────────────────────────────────────────────
show_compose() {
    echo "SAGCO COMPOSE — device=${DEV}"
    echo "=============================="
    ROLE=$(get_device_role "$DEV")
    echo "Role: $ROLE"
    echo ""
    echo "Active sync targets:"
    if [ -f "$COMPOSE_FILE" ]; then
        grep "^    - path:" "$COMPOSE_FILE" | awk '{print "  " $3}'
    else
        echo "  (compose file not found: $COMPOSE_FILE)"
    fi
    echo ""
    echo "Pipeline stages:"
    get_pipeline_stages | sed 's/^/  /'
}

# ── install ───────────────────────────────────────────────────────────────────
do_install() {
    SELF="$(cd "$(dirname "$0")" && pwd)/sagco-daemon.sh"
    LINK="$HOME/bin/sagco-daemon"
    mkdir -p "$HOME/bin"
    cp "$SELF" "$LINK" 2>/dev/null && chmod +x "$LINK" && echo "Installed: $LINK"

    # Add to profile if not already there
    PROFILE="$HOME/.profile"
    if ! grep -q "sagco-daemon" "$PROFILE" 2>/dev/null; then
        cat >> "$PROFILE" << 'PROF'

# SAGCO daemon auto-start (added by sagco-daemon install)
# Uncomment to auto-sync on shell open:
# sagco-daemon once 2>/dev/null &
PROF
        echo "Profile:  $PROFILE (auto-start commented — edit to enable)"
    fi
}

# ── stop ──────────────────────────────────────────────────────────────────────
do_stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill "$PID" 2>/dev/null; then
            echo "Stopped daemon (PID=$PID)"
            rm -f "$PID_FILE"
        else
            echo "No daemon at PID=$PID (removing stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        echo "No daemon running (no PID file)"
    fi
}

# ── main loop ─────────────────────────────────────────────────────────────────
start_loop() {
    echo $$ > "$PID_FILE"
    echo "[daemon] started — device=${DEV} interval=${TICK_INTERVAL}s"
    echo "[daemon] PID=$$ written to $PID_FILE"
    echo "[daemon] Press Ctrl+C to stop, or: sagco-daemon stop"
    echo ""

    while true; do
        do_sync_pass
        sleep "$TICK_INTERVAL"
    done
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-loop}"
print_header

case "$CMD" in
    loop|start|"")
        start_loop
        ;;
    once)
        do_sync_pass
        ;;
    status)
        show_status
        ;;
    stop)
        do_stop
        ;;
    compose)
        show_compose
        ;;
    pipeline)
        run_pipeline
        ;;
    entangle)
        show_entanglement
        ;;
    install)
        do_install
        ;;
    help|--help|-h)
        cat << HELP
sagco-daemon — Polyglot Cross-Device Sync

Commands:
  (none) / loop    Start sync loop (30s interval)
  once             Single sync pass, then exit
  status           Show daemon state and last tick
  stop             Kill running daemon
  compose          Show device role + sync targets
  pipeline         Run full SAGCO pipeline for this device
  entangle         Show what this device produces/consumes
  install          Install to ~/bin, add profile entry

Environment:
  SAGCO_DEVICE     Override device key (ish/termux/zfold/ipad)
  ~/.sagco_device  Persistent device identity

Compose file: $COMPOSE_FILE
HELP
        ;;
    *)
        echo "Unknown command: $CMD"
        echo "Usage: sagco-daemon [loop|once|status|stop|compose|pipeline|entangle|install|help]"
        exit 1
        ;;
esac
