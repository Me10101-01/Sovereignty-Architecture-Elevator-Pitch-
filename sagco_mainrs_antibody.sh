#!/data/data/com.termux/files/usr/bin/bash
# SAGCO main.rs Antibody — detects stub overwrites and auto-restores
# Run before every cargo build, or wire into a git pre-commit hook
# Install hook: bash sagco_mainrs_antibody.sh --install-hook
set -e

MAINRS="src/main.rs"
BACKUP="src/main.rs.backup"
BYPASS="src/main.rs.bypass"
MIN_LINES=50        # real main.rs is hundreds of lines; stub is ~5
IMMUNE_MARKER="spl" # real main.rs uses mod spl / use spl::

antibody_check() {
  local status="OK"
  local reason=""

  if [ ! -f "$MAINRS" ]; then
    status="MISSING"
    reason="src/main.rs does not exist"
  else
    LINE_COUNT=$(wc -l < "$MAINRS")
    if [ "$LINE_COUNT" -lt "$MIN_LINES" ]; then
      status="STUB_DETECTED"
      reason="main.rs is only $LINE_COUNT lines (min: $MIN_LINES)"
    elif ! grep -q "$IMMUNE_MARKER" "$MAINRS" 2>/dev/null; then
      status="STUB_DETECTED"
      reason="main.rs missing '$IMMUNE_MARKER' — not the real SAGCO entrypoint"
    fi
  fi

  echo "ANTIBODY: $status"
  [ -n "$reason" ] && echo "  REASON: $reason"
  echo "$status"
}

antibody_restore() {
  if [ -f "$BACKUP" ]; then
    echo "ANTIBODY: restoring from $BACKUP"
    cp "$BACKUP" "$MAINRS"
    echo "ANTIBODY: restored ($(wc -l < "$MAINRS") lines)"
    return 0
  elif [ -f "$BYPASS" ]; then
    echo "ANTIBODY: backup missing, trying bypass"
    cp "$BYPASS" "$MAINRS"
    return 0
  else
    echo "ANTIBODY: ERROR — no backup found at $BACKUP"
    echo "ANTIBODY: run from ~/downloads/sagco_rust_command_compiler"
    return 1
  fi
}

antibody_seal() {
  # make backup read-only so it can't be accidentally clobbered
  if [ -f "$BACKUP" ]; then
    chmod 444 "$BACKUP"
    echo "ANTIBODY: $BACKUP sealed (read-only)"
  fi
  if [ -f "$BYPASS" ]; then
    chmod 444 "$BYPASS"
    echo "ANTIBODY: $BYPASS sealed (read-only)"
  fi
  echo "ANTIBODY: seals applied"
}

install_hook() {
  HOOK_DIR=".git/hooks"
  if [ ! -d "$HOOK_DIR" ]; then
    echo "ANTIBODY: no .git directory — not a git repo, skipping hook"
    return
  fi
  cat > "$HOOK_DIR/pre-commit" <<'HOOK'
#!/bin/sh
# SAGCO main.rs antibody pre-commit hook
if [ -f sagco_mainrs_antibody.sh ]; then
  STATUS=$(bash sagco_mainrs_antibody.sh --check-only 2>/dev/null | tail -1)
  if [ "$STATUS" = "STUB_DETECTED" ]; then
    echo "ANTIBODY PRE-COMMIT: main.rs stub detected — run: bash sagco_mainrs_antibody.sh"
    exit 1
  fi
fi
exit 0
HOOK
  chmod +x "$HOOK_DIR/pre-commit"
  echo "ANTIBODY: pre-commit hook installed at $HOOK_DIR/pre-commit"
}

# ── main dispatch ────────────────────────────────────────────────────────────
case "${1:-}" in
  --install-hook)
    install_hook
    antibody_seal
    ;;
  --seal)
    antibody_seal
    ;;
  --check-only)
    antibody_check
    ;;
  --restore)
    antibody_restore
    ;;
  *)
    # default: check and auto-restore if needed, then seal backups
    STATUS=$(antibody_check)
    if [ "$STATUS" = "STUB_DETECTED" ] || [ "$STATUS" = "MISSING" ]; then
      echo "ANTIBODY: IMMUNE RESPONSE TRIGGERED"
      antibody_restore
      echo "ANTIBODY: re-checking..."
      antibody_check
    fi
    antibody_seal
    echo ""
    echo "ANTIBODY: main.rs is healthy ($(wc -l < "$MAINRS") lines)"
    echo "ANTIBODY: to rebuild: cargo build --release"
    ;;
esac
