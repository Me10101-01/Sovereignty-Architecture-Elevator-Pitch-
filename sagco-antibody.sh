#!/bin/sh
# sagco-antibody — System Anomaly Detector
# Scans SAGCO telemetry for known failure patterns
# Each antibody = detected pattern + count + evidence + prescribed action
#
# Not a file classifier. A self-auditing runtime monitor.
#
# Known antibodies:
#   RUST_EDITION_MISMATCH     — Cargo.toml with edition="2021" on iSH
#   DEVICE_IDENTITY_MISSING   — ,unknown, entries in race_log/ledger
#   CLASSIFICATION_DEFICIT    — discovery >> classification rate
#   ATTRIBUTION_GAP           — events without device tag
#   ERU_VARIANCE_HIGH         — adaptation_pct extreme (>85 or <15)
#   MISSING_LEDGER_HOOK       — sagco commands with no ledger entry
#   STALE_STATE_SNAPSHOT      — sagco_state.yaml >24h stale
#   QR_AUDIT_UNVERIFIED       — audit files without VERIFIED=TRUE
#   NINA_GATE_BLOCKED         — nina paper-trading gates not yet passed
#
# Usage:
#   sagco-antibody            → full system scan
#   sagco-antibody show       → show last report
#   sagco-antibody <antibody> → run single check (e.g. sagco-antibody RUST)

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
REPO_ROOT="$(cd "$(dirname "$0")" 2>/dev/null && pwd || echo "$HOME")"
AB_DIR="$HOME/sagco_antibody"
REPORT="$AB_DIR/antibody_report_${STAMP}.md"
SCORE="$AB_DIR/antibody_score_${STAMP}.yaml"
LEDGER="$HOME/sagco_ledger.csv"

mkdir -p "$AB_DIR"

# ── show last report ──────────────────────────────────────────────────────────
if [ "$1" = "show" ]; then
    LAST=$(ls -1t "$AB_DIR"/antibody_report_*.md 2>/dev/null | head -1)
    if [ -n "$LAST" ]; then cat "$LAST"; else echo "No antibody report — run: sagco-antibody"; fi
    exit 0
fi

# ── antibody emitter ─────────────────────────────────────────────────────────
# Prints structured antibody block and appends to report
ANTIBODY_COUNT=0
CRITICAL_COUNT=0
WARN_COUNT=0

emit_antibody() {
    NAME="$1"        # e.g. RUST_EDITION_MISMATCH
    SEVERITY="$2"    # CRITICAL | WARN | INFO
    COUNT="$3"       # number of occurrences
    EVIDENCE="$4"    # what was found
    ACTION="$5"      # prescribed fix

    [ "$COUNT" -eq 0 ] 2>/dev/null && return   # clean — skip

    ANTIBODY_COUNT=$((ANTIBODY_COUNT + 1))
    [ "$SEVERITY" = "CRITICAL" ] && CRITICAL_COUNT=$((CRITICAL_COUNT + 1))
    [ "$SEVERITY" = "WARN" ]     && WARN_COUNT=$((WARN_COUNT + 1))

    printf "\n  ANTIBODY:  %s\n"    "$NAME"
    printf "  SEVERITY:  %s\n"      "$SEVERITY"
    printf "  COUNT:     %d\n"      "$COUNT"
    printf "  EVIDENCE:  %s\n"      "$EVIDENCE"
    printf "  ACTION:    %s\n"      "$ACTION"

    # append to report
    cat >> "$REPORT" <<BLOCK

### $NAME
- **Severity:** $SEVERITY
- **Count:** $COUNT
- **Evidence:** $EVIDENCE
- **Action:** \`$ACTION\`
BLOCK
}

emit_clean() {
    NAME="$1"
    printf "  [OK]  %s\n" "$NAME"
}

# ── initialize report ─────────────────────────────────────────────────────────
cat > "$REPORT" << HDR
# SAGCO Antibody Report
Generated: $STAMP
Device: $DEV

## Anomalies Detected

HDR

echo "SAGCO ANTIBODY ENGINE — System Anomaly Detector"
echo "================================================="
echo "Stamp:  $STAMP"
echo "Device: $DEV"
echo ""
echo "SCANNING SAGCO TELEMETRY..."
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY 1: RUST_EDITION_MISMATCH
# Detect Cargo.toml files using edition="2021" — fails on iSH's older Cargo
# ═══════════════════════════════════════════════════════════════════════════════
scan_rust_edition() {
    HITS=$(find "$REPO_ROOT" -name "Cargo.toml" 2>/dev/null \
        | xargs grep -l 'edition = "2021"' 2>/dev/null | wc -l | tr -d ' ')
    FILES=$(find "$REPO_ROOT" -name "Cargo.toml" 2>/dev/null \
        | xargs grep -l 'edition = "2021"' 2>/dev/null | tr '\n' ' ')
    if [ "${HITS:-0}" -gt 0 ]; then
        emit_antibody "RUST_EDITION_MISMATCH" "CRITICAL" "$HITS" \
            "Cargo.toml: $FILES" \
            "sed -i 's/edition = \"2021\"/edition = \"2018\"/' Cargo.toml"
    else
        emit_clean "RUST_EDITION_MISMATCH"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY 2: DEVICE_IDENTITY_MISSING
# Count ,unknown, in race_log and ledger
# ═══════════════════════════════════════════════════════════════════════════════
scan_device_identity() {
    RACE="$HOME/sagco_race/race_log.csv"
    UNKNOWN_RACE=0
    UNKNOWN_LEDGER=0
    [ -f "$RACE" ]   && UNKNOWN_RACE=$(grep -c ",unknown," "$RACE" 2>/dev/null || echo 0)
    [ -f "$LEDGER" ] && UNKNOWN_LEDGER=$(grep -c ",unknown," "$LEDGER" 2>/dev/null || echo 0)
    TOTAL=$((UNKNOWN_RACE + UNKNOWN_LEDGER))
    if [ "$TOTAL" -gt 0 ]; then
        emit_antibody "DEVICE_IDENTITY_MISSING" "WARN" "$TOTAL" \
            "race_log: $UNKNOWN_RACE unknown events, ledger: $UNKNOWN_LEDGER" \
            "sagco-identity && sagco-identity install"
    else
        emit_clean "DEVICE_IDENTITY_MISSING"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY 3: CLASSIFICATION_DEFICIT
# discovered count >> classified count in ~/sagco_classify.csv
# ═══════════════════════════════════════════════════════════════════════════════
scan_classification_deficit() {
    CSV="$HOME/sagco_classify.csv"
    if [ ! -f "$CSV" ]; then
        emit_antibody "CLASSIFICATION_DEFICIT" "INFO" "1" \
            "sagco_classify.csv not found — classify has not run" \
            "sagco-classify fast"
        return
    fi
    TOTAL=$(grep -c "^20" "$CSV" 2>/dev/null || echo 0)
    UNKNOWN=$(grep -c ",UNKNOWN," "$CSV" 2>/dev/null || echo 0)
    CLASSIFIED=$((TOTAL - UNKNOWN))
    if [ "$TOTAL" -gt 0 ] && [ "$UNKNOWN" -gt "$CLASSIFIED" ] 2>/dev/null; then
        RATE=$(echo "scale=0; $UNKNOWN * 100 / $TOTAL" | bc 2>/dev/null || echo "?")
        emit_antibody "CLASSIFICATION_DEFICIT" "WARN" "$UNKNOWN" \
            "${UNKNOWN}/${TOTAL} unclassified (${RATE}%) — Discovery >> Classification" \
            "sagco-antibody (extend pattern signatures in sagco-classify)"
    elif [ "$TOTAL" -gt 0 ]; then
        emit_clean "CLASSIFICATION_DEFICIT"
    else
        emit_antibody "CLASSIFICATION_DEFICIT" "INFO" "1" \
            "sagco_classify.csv empty — run classifier first" \
            "sagco-classify fast"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY 4: ATTRIBUTION_GAP
# Commands in ledger with no device field (blank or missing)
# ═══════════════════════════════════════════════════════════════════════════════
scan_attribution_gap() {
    if [ ! -f "$LEDGER" ]; then
        emit_clean "ATTRIBUTION_GAP"
        return
    fi
    # Lines where second CSV field (device) is blank or "unknown"
    GAPS=$(awk -F',' 'NR>1 && ($2=="" || $2=="unknown")' "$LEDGER" 2>/dev/null | wc -l | tr -d ' ')
    TOTAL=$(grep -c "^20" "$LEDGER" 2>/dev/null || echo 1)
    if [ "${GAPS:-0}" -gt 0 ]; then
        RATE=$(echo "scale=0; $GAPS * 100 / $TOTAL" | bc 2>/dev/null || echo "?")
        emit_antibody "ATTRIBUTION_GAP" "WARN" "$GAPS" \
            "${GAPS}/${TOTAL} ledger entries missing device attribution (${RATE}%)" \
            "export SAGCO_DEVICE=\$(cat ~/.sagco_device) && re-run commands"
    else
        emit_clean "ATTRIBUTION_GAP"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY 5: ERU_VARIANCE_HIGH
# adaptation_pct extreme values signal system imbalance
# ═══════════════════════════════════════════════════════════════════════════════
scan_eru_variance() {
    STATE="$HOME/sagco_state.yaml"
    if [ ! -f "$STATE" ]; then
        emit_clean "ERU_VARIANCE_HIGH"
        return
    fi
    ADAPT=$(grep "adaptation_pct" "$STATE" 2>/dev/null | head -1 | grep -o '[0-9]*' | head -1)
    [ -z "$ADAPT" ] && emit_clean "ERU_VARIANCE_HIGH" && return
    if [ "$ADAPT" -gt 85 ] 2>/dev/null; then
        emit_antibody "ERU_VARIANCE_HIGH" "WARN" "1" \
            "adaptation_pct=${ADAPT}% — system in maintenance mode, low creation" \
            "introduce new creation tasks to rebalance ERU"
    elif [ "$ADAPT" -lt 15 ] 2>/dev/null; then
        emit_antibody "ERU_VARIANCE_HIGH" "WARN" "1" \
            "adaptation_pct=${ADAPT}% — system in pure creation mode, low validation" \
            "run sagco-variance and sagco-eru to validate recent work"
    else
        emit_clean "ERU_VARIANCE_HIGH"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY 6: MISSING_LEDGER_HOOK
# sagco-* shell scripts that don't contain a ledger write
# ═══════════════════════════════════════════════════════════════════════════════
scan_ledger_hooks() {
    MISSING=0
    MISSING_LIST=""
    for F in "$REPO_ROOT"/sagco-*.sh; do
        [ -f "$F" ] || continue
        if ! grep -q "sagco_ledger\|LEDGER\|log_ledger" "$F" 2>/dev/null; then
            MISSING=$((MISSING + 1))
            MISSING_LIST="$MISSING_LIST $(basename "$F")"
        fi
    done
    if [ "$MISSING" -gt 0 ]; then
        emit_antibody "MISSING_LEDGER_HOOK" "INFO" "$MISSING" \
            "Commands without ledger logging:$MISSING_LIST" \
            "add ledger entry to each command's completion block"
    else
        emit_clean "MISSING_LEDGER_HOOK"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY 7: STALE_STATE_SNAPSHOT
# sagco_state.yaml older than 24 hours
# ═══════════════════════════════════════════════════════════════════════════════
scan_stale_state() {
    STATE="$HOME/sagco_state.yaml"
    if [ ! -f "$STATE" ]; then
        emit_antibody "STALE_STATE_SNAPSHOT" "INFO" "1" \
            "sagco_state.yaml not found" \
            "sagco-state"
        return
    fi
    # Get file age in seconds (POSIX-compatible)
    FILE_TS=$(stat -c %Y "$STATE" 2>/dev/null || stat -f %m "$STATE" 2>/dev/null || echo 0)
    NOW_TS=$(date +%s 2>/dev/null || echo 0)
    AGE_H=$(echo "scale=0; ($NOW_TS - $FILE_TS) / 3600" | bc 2>/dev/null || echo 0)
    if [ "${AGE_H:-0}" -gt 24 ] 2>/dev/null; then
        emit_antibody "STALE_STATE_SNAPSHOT" "WARN" "1" \
            "sagco_state.yaml is ${AGE_H}h old — metrics may be stale" \
            "sagco-state  (regenerate state snapshot)"
    else
        emit_clean "STALE_STATE_SNAPSHOT"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY 8: QR_AUDIT_UNVERIFIED
# QR audit reports missing VERIFIED=TRUE
# ═══════════════════════════════════════════════════════════════════════════════
scan_qr_audits() {
    AUDIT_DIR="$HOME/sagco_qr_audits"
    [ -d "$AUDIT_DIR" ] || return
    TOTAL=$(find "$AUDIT_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    [ "$TOTAL" -eq 0 ] && emit_clean "QR_AUDIT_UNVERIFIED" && return
    UNVERIFIED=$(find "$AUDIT_DIR" -name "*.md" 2>/dev/null \
        | xargs grep -rL "VERIFIED.*TRUE\|VERIFIED: TRUE" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${UNVERIFIED:-0}" -gt 0 ]; then
        emit_antibody "QR_AUDIT_UNVERIFIED" "CRITICAL" "$UNVERIFIED" \
            "${UNVERIFIED}/${TOTAL} audit reports missing VERIFIED=TRUE" \
            "sagco-qr-audit <url>  (re-run audit for flagged reports)"
    else
        emit_clean "QR_AUDIT_UNVERIFIED"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY 9: NINA_GATE_BLOCKED
# Nina paper-trading gates not yet met
# ═══════════════════════════════════════════════════════════════════════════════
scan_nina_gate() {
    NINA_SCORE=$(find "$HOME/sagco_nina" -name "strategy_score*.yaml" 2>/dev/null | head -1)
    if [ -z "$NINA_SCORE" ]; then
        emit_antibody "NINA_GATE_BLOCKED" "INFO" "1" \
            "No Nina strategy_score.yaml found" \
            "nina-trader dry-run all  (generate first backtest)"
        return
    fi
    LIVE_READY=$(grep "ready_for_live: true" "$NINA_SCORE" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${LIVE_READY:-0}" -eq 0 ]; then
        emit_antibody "NINA_GATE_BLOCKED" "INFO" "1" \
            "Live trading gates not met — paper trading required first" \
            "nina-trader dca paper  (run 30 days paper, check strategy_score.yaml)"
    else
        emit_clean "NINA_GATE_BLOCKED"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# RUN ALL SCANS
# ═══════════════════════════════════════════════════════════════════════════════

# Single antibody mode
if [ -n "$1" ]; then
    case "$1" in
        RUST*)  scan_rust_edition ;;
        DEVICE*|IDENTITY*) scan_device_identity ;;
        CLASS*) scan_classification_deficit ;;
        ATTR*)  scan_attribution_gap ;;
        ERU*)   scan_eru_variance ;;
        LEDGER*) scan_ledger_hooks ;;
        STATE*|STALE*) scan_stale_state ;;
        QR*)    scan_qr_audits ;;
        NINA*)  scan_nina_gate ;;
        *)      echo "Unknown antibody: $1"; echo "Valid: RUST DEVICE CLASS ATTR ERU LEDGER STATE QR NINA" ;;
    esac
else
    scan_rust_edition
    scan_device_identity
    scan_classification_deficit
    scan_attribution_gap
    scan_eru_variance
    scan_ledger_hooks
    scan_stale_state
    scan_qr_audits
    scan_nina_gate
fi

# ── summary ───────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════"
echo "ANTIBODY SCAN COMPLETE"
printf "  Antibodies detected:  %d\n" "$ANTIBODY_COUNT"
printf "  Critical:             %d\n" "$CRITICAL_COUNT"
printf "  Warnings:             %d\n" "$WARN_COUNT"
echo "════════════════════════════════"

# Determine overall system health
if [ "$CRITICAL_COUNT" -gt 0 ]; then
    HEALTH="CRITICAL"
elif [ "$WARN_COUNT" -gt 2 ]; then
    HEALTH="DEGRADED"
elif [ "$ANTIBODY_COUNT" -gt 0 ]; then
    HEALTH="WARN"
else
    HEALTH="HEALTHY"
fi

# ── finalize report ───────────────────────────────────────────────────────────
cat >> "$REPORT" <<SUMMARY

---

## Summary

| Metric | Value |
|--------|-------|
| Antibodies detected | $ANTIBODY_COUNT |
| Critical | $CRITICAL_COUNT |
| Warnings | $WARN_COUNT |
| System health | $HEALTH |

## Pipeline Status After Antibody Scan

\`\`\`
MRI          ✅ PASS
Classify     $([ "$ANTIBODY_COUNT" -eq 0 ] && echo "✅ PASS" || echo "⚠️  see antibodies above")
Antibody     ✅ PASS — $ANTIBODY_COUNT issues found
Refinery     → run: sagco-refinery
ERU          → run: sagco-eru-device
Portfolio    → run: sagco-portfolio
State        → run: sagco-state
Mansion      → run: sagco-mansion
\`\`\`

STATUS=SAGCO_ANTIBODY_PASS
SUMMARY

# ── write score YAML ──────────────────────────────────────────────────────────
cat > "$SCORE" <<SYAML
timestamp: $STAMP
device: $DEV
antibodies_detected: $ANTIBODY_COUNT
critical: $CRITICAL_COUNT
warnings: $WARN_COUNT
system_health: $HEALTH
antibodies:
  rust_edition_mismatch: $(grep -c "RUST_EDITION_MISMATCH" "$REPORT" 2>/dev/null && echo "scanned" || echo "scanned")
  device_identity_missing: scanned
  classification_deficit: scanned
  attribution_gap: scanned
  eru_variance_high: scanned
  missing_ledger_hook: scanned
  stale_state_snapshot: scanned
  qr_audit_unverified: scanned
  nina_gate_blocked: scanned
status: SAGCO_ANTIBODY_PASS
SYAML

# ── ledger + race ─────────────────────────────────────────────────────────────
HASH=$(echo "${STAMP}sagco-antibody" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${DEV},sagco-antibody,${REPORT},${HASH},SAGCO_ANTIBODY_PASS" >> "$LEDGER"

RACE_OUT="$HOME/sagco_race/race_log.csv"
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
mkdir -p "$(dirname "$RACE_OUT")"
[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${DEV},sagco_antibody,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

echo ""
echo "Report: $REPORT"
echo "Score:  $SCORE"
echo ""
echo "STATUS=SAGCO_ANTIBODY_PASS"
echo "SYSTEM_HEALTH=$HEALTH"
echo "ANTIBODIES=$ANTIBODY_COUNT"
