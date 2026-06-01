#!/usr/bin/env bash
# sagco_reality_pass — REAL vs PLANNED vs DOCUMENTED audit
# Builds binary, tests compiled commands, verifies shell plugins + compose
# Run from: ~/downloads/sagco_rust_command_compiler (Termux root)
# License: SSL-1.0 — Strategickhaos DAO LLC
set -e

OUT="reports/reality_pass"
mkdir -p "$OUT"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$OUT/reality_${STAMP}.md"

BIN="target/release/sagco_rust_command_compiler"

{
echo "# SAGCO Reality Pass"
echo
echo "STAMP: $STAMP"
echo
echo "## Build Reality"
cargo clean
cargo build --release
echo
echo "## Binary"
ls -lh "$BIN"
file "$BIN" 2>/dev/null || true
sha256sum "$BIN"
echo
echo "## Compiled Command Tests"
echo '```text'
./"$BIN" past      || true
./"$BIN" past-fuzz || true
./"$BIN" cmd dna   || true
echo '```'
echo
echo "## Dependency Graph"
echo '```text'
cargo tree 2>/dev/null | head -120 || echo "cargo tree unavailable"
echo '```'
echo
echo "## FlameToken Census"
echo '```text'
llvm-strings "$BIN" 2>/dev/null \
  | grep -i "sagco\|past\|wave\|agent\|dna" \
  | sort -u | head -200 || true
echo '```'
echo
echo "## Shell Plugin Reality"
echo "| Plugin | Exists | Executable |"
echo "|--------|--------|------------|"
for s in sagco_send.sh sagco_trinity_recon.sh sagco_evo.sh \
          sagco_ghidra_flametoken.sh sagco_purple_efficiency_audit.sh \
          sagco_terminal_antibody.sh sagco_bloodhound.sh sagco_compose_run.sh; do
  echo "| $s | $(test -f "$s" && echo yes || echo no) | $(test -x "$s" && echo yes || echo no) |"
done
echo
echo "## Compose Reality"
echo '```yaml'
cat sagco.compose.yaml 2>/dev/null || echo "NO_COMPOSE_FOUND"
echo '```'
echo
echo "## Reality Ledger"
echo "- compiled_rust: past, past-fuzz, cmd dna"
echo "- shell_plugins: send, trinity_recon, evo, ghidra_flametoken, purple_efficiency_audit,"
echo "                 terminal_antibody, bloodhound, compose_run"
echo "- architecture_specs: compose yaml, plugin protocol reports, send protocol reports"
echo
echo "STATUS=SAGCO_REALITY_PASS_COMPLETE"
} > "$REPORT"

cat "$REPORT"
sha256sum "$REPORT"
echo "REPORT=$REPORT"
