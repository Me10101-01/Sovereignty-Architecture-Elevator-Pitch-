#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Storage Antibody
# Detects and eliminates storage-critical conditions blocking cargo builds.
# Targets: Termux on ZFold — safe to run from any directory.
#
# Usage:
#   bash sagco-storage-antibody.sh          → full clean (scan + purge)
#   bash sagco-storage-antibody.sh scan     → scan only, no deletions
#   bash sagco-storage-antibody.sh purge    → purge only (skip scan output)
set -euo pipefail

MODE="${1:-full}"
WS="${HOME}/downloads/sagco_rust_command_compiler"
STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
FREED_KB=0

echo "SAGCO STORAGE ANTIBODY"
echo "======================"
echo "Stamp:  $STAMP"
echo "Mode:   $MODE"
echo "WS:     $WS"
echo ""

# ── helper: available KB on / ─────────────────────────────────────────────────
avail_kb() {
    df /data 2>/dev/null | awk 'NR==2{print $4}' || \
    df /     2>/dev/null | awk 'NR==2{print $4}' || echo 0
}

avail_pct() {
    df /data 2>/dev/null | awk 'NR==2{gsub(/%/,"",$5); print 100-$5}' || \
    df /     2>/dev/null | awk 'NR==2{gsub(/%/,"",$5); print 100-$5}' || echo 0
}

before_kb=$(avail_kb)

# ── SCAN ──────────────────────────────────────────────────────────────────────
echo "=== DISK SNAPSHOT ==="
df -h /data 2>/dev/null || df -h / 2>/dev/null || df -h . 2>/dev/null
echo ""

if [ -d "$WS" ]; then
    echo "=== WORKSPACE BREAKDOWN (${WS}) ==="
    du -sh "${WS}"/* 2>/dev/null | sort -h | tail -30
    echo ""
fi

if [ "$MODE" = "scan" ]; then
    echo "STATUS=STORAGE_ANTIBODY_SCAN_ONLY"
    exit 0
fi

# ── PURGE TARGET: cargo clean (biggest quick win) ─────────────────────────────
echo "=== STEP 1: cargo clean ==="
if [ -d "${WS}/target" ]; then
    SIZE_KB=$(du -sk "${WS}/target" 2>/dev/null | awk '{print $1}' || echo 0)
    if command -v cargo >/dev/null 2>&1; then
        cargo clean --manifest-path "${WS}/Cargo.toml" 2>/dev/null \
            || rm -rf "${WS}/target"
    else
        rm -rf "${WS}/target"
    fi
    FREED_KB=$((FREED_KB + SIZE_KB))
    echo "  FREED: ~$((SIZE_KB / 1024)) MB (target/)"
else
    echo "  SKIP: target/ not found"
fi

# ── PURGE TARGET: old reports (2.1G potential) ───────────────────────────────
echo ""
echo "=== STEP 2: prune old reports ==="
REPORTS_DIR="${WS}/reports"
if [ -d "$REPORTS_DIR" ]; then
    TOTAL_REPORTS=$(find "$REPORTS_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "  Found: $TOTAL_REPORTS report files"

    # Keep the 20 most recently modified — delete everything else
    KEEP=20
    if [ "$TOTAL_REPORTS" -gt "$KEEP" ]; then
        SIZE_BEFORE=$(du -sk "$REPORTS_DIR" 2>/dev/null | awk '{print $1}' || echo 0)

        # Sort by modification time newest-first; skip first $KEEP; delete the rest
        find "$REPORTS_DIR" -type f -printf "%T@ %p\n" 2>/dev/null \
            | sort -rn \
            | awk -v k="$KEEP" 'NR>k {print $2}' \
            | xargs rm -f 2>/dev/null || true

        # Remove empty subdirs
        find "$REPORTS_DIR" -type d -empty -delete 2>/dev/null || true

        SIZE_AFTER=$(du -sk "$REPORTS_DIR" 2>/dev/null | awk '{print $1}' || echo 0)
        DELTA=$((SIZE_BEFORE - SIZE_AFTER))
        FREED_KB=$((FREED_KB + DELTA))
        echo "  FREED: ~$((DELTA / 1024)) MB (kept $KEEP most recent reports)"
    else
        echo "  SKIP: only $TOTAL_REPORTS reports, below keep threshold ($KEEP)"
    fi
else
    echo "  SKIP: reports/ not found"
fi

# ── PURGE TARGET: known large fuzz case study tarballs ───────────────────────
echo ""
echo "=== STEP 3: remove large fuzz tarballs ==="
REMOVED_COUNT=0
for pattern in \
    "SAGCO_HEADLESS_VM_FUZZ_CASE_STUDY.tar.gz" \
    "SAGCO_HEADLESS_VM_FUZZ_CASE_STUDY_v2.tar.gz"; do
    F="${WS}/${pattern}"
    if [ -f "$F" ]; then
        SIZE_KB=$(du -sk "$F" 2>/dev/null | awk '{print $1}' || echo 0)
        rm -f "$F"
        FREED_KB=$((FREED_KB + SIZE_KB))
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
        echo "  FREED: ~$((SIZE_KB / 1024)) MB ($pattern)"
    fi
done
[ "$REMOVED_COUNT" -eq 0 ] && echo "  SKIP: fuzz tarballs already removed"

# ── PURGE TARGET: rust_binary_compiler cache (19M) ───────────────────────────
echo ""
echo "=== STEP 4: rust binary compiler cache ==="
RBC="${WS}/rust_binary_compiler"
if [ -d "$RBC" ]; then
    SIZE_KB=$(du -sk "$RBC" 2>/dev/null | awk '{print $1}' || echo 0)
    # Only remove if >10MB — it's a cached compiler binary, reproducible
    if [ "$SIZE_KB" -gt 10240 ]; then
        rm -rf "$RBC"
        FREED_KB=$((FREED_KB + SIZE_KB))
        echo "  FREED: ~$((SIZE_KB / 1024)) MB (rust_binary_compiler/)"
    else
        echo "  SKIP: only $((SIZE_KB / 1024))MB, not worth it"
    fi
else
    echo "  SKIP: rust_binary_compiler/ not found"
fi

# ── PURGE TARGET: node_modules (if present in WS) ────────────────────────────
echo ""
echo "=== STEP 5: node_modules ==="
NM="${WS}/node_modules"
if [ -d "$NM" ]; then
    SIZE_KB=$(du -sk "$NM" 2>/dev/null | awk '{print $1}' || echo 0)
    rm -rf "$NM"
    FREED_KB=$((FREED_KB + SIZE_KB))
    echo "  FREED: ~$((SIZE_KB / 1024)) MB (node_modules/)"
else
    echo "  SKIP: node_modules/ not found"
fi

# ── PURGE TARGET: dropbox_inbox (user-controlled, only if >100M and old) ─────
echo ""
echo "=== STEP 6: dropbox_inbox ==="
INBOX="${WS}/dropbox_inbox"
if [ -d "$INBOX" ]; then
    SIZE_KB=$(du -sk "$INBOX" 2>/dev/null | awk '{print $1}' || echo 0)
    echo "  INFO: dropbox_inbox is $((SIZE_KB / 1024))MB — NOT auto-deleted (manual review)"
    echo "  To clear: rm -rf ${INBOX}"
else
    echo "  SKIP: dropbox_inbox/ not found"
fi

# ── RESULT ────────────────────────────────────────────────────────────────────
after_kb=$(avail_kb)
gained_kb=$((after_kb - before_kb))

echo ""
echo "=================================================="
echo "STORAGE ANTIBODY COMPLETE"
printf "  Freed (estimated):  ~%d MB\n" "$((FREED_KB / 1024))"
printf "  Free before:        ~%d MB\n" "$((before_kb / 1024))"
printf "  Free after:         ~%d MB\n" "$((after_kb / 1024))"
printf "  Gained (actual):    ~%d MB\n" "$((gained_kb / 1024))"
echo "=================================================="
echo ""

# ── verify cargo can now build ────────────────────────────────────────────────
FREE_PCT=$(avail_pct)
echo "=== DISK STATUS AFTER PURGE ==="
df -h /data 2>/dev/null || df -h / 2>/dev/null
echo ""

if [ "${FREE_PCT:-0}" -gt 5 ] 2>/dev/null; then
    echo "STATUS=STORAGE_ANTIBODY_PASS"
    echo "DISK_FREE_PCT=${FREE_PCT}%"
    echo ""
    echo "Next: cargo build --bin sagco-core"
else
    echo "STATUS=STORAGE_ANTIBODY_WARN — still low on disk"
    echo "DISK_FREE_PCT=${FREE_PCT}%"
    echo ""
    echo "Additional options:"
    echo "  rm -rf ${WS}/dropbox_inbox    # ~131MB"
    echo "  rm -rf ${WS}/portfolio_case_study  # ~83MB"
    echo "  rm -rf ${WS}/sagco_shell       # ~15MB"
fi
