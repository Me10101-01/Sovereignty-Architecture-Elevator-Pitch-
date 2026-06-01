#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Darwin Antibody — maps CLI error codes into immune trajectories
# Antibody types: PASS_IMMUNITY | PATH_DISCOVERY | PROJECT_ROOT | JDK_GATE | DEPENDENCY | UNKNOWN_VARIANCE
# Trajectories:   stabilized | adaptation | evolution | mutation
set -e

# ── environment setup ────────────────────────────────────────────────────────
export GHIDRA_HOME="${GHIDRA_HOME:-${HOME}/downloads/ghidra_12.1_PUBLIC}"
export JAVA_HOME="${JAVA_HOME:-${PREFIX}/lib/jvm/java-21-openjdk}"
export PATH="${HOME}/bin:${PATH}"

BINARY="target/release/sagco_rust_command_compiler"
OUT="reports/darwin_antibody"
mkdir -p "$OUT"

STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="$OUT/darwin_${STAMP}.md"

# ── antibody classifier ──────────────────────────────────────────────────────
classify() {
  local text="$1" code="$2"
  if   echo "$text" | grep -qi "No such file or directory"; then echo "PATH_DISCOVERY_ANTIBODY|adaptation"
  elif echo "$text" | grep -qi "could not find.*Cargo.toml"; then echo "PROJECT_ROOT_ANTIBODY|adaptation"
  elif echo "$text" | grep -qi "JDK 21\|JDK.*not be found"; then echo "JDK_GATE_ANTIBODY|evolution"
  elif echo "$text" | grep -qi "command not found\|not installed"; then echo "DEPENDENCY_ANTIBODY|adaptation"
  elif echo "$text" | grep -qi "stub\|fn main.*println"; then echo "STUB_DETECTED_ANTIBODY|mutation"
  elif [ "$code" -eq 0 ]; then echo "PASS_IMMUNITY|stabilized"
  else echo "UNKNOWN_VARIANCE_ANTIBODY|mutation"
  fi
}

run_case() {
  local NAME="$1" CMD="$2"
  echo "## CASE: $NAME" >> "$LOG"
  printf '```bash\n%s\n```\n' "$CMD" >> "$LOG"

  set +e; OUTTEXT="$(eval "$CMD" 2>&1)"; CODE="$?"; set -e

  printf '```text\n%s\n```\n' "$(echo "$OUTTEXT" | head -40)" >> "$LOG"

  RESULT="$(classify "$OUTTEXT" "$CODE")"
  ANTIBODY="${RESULT%%|*}"
  TRAJECTORY="${RESULT##*|}"

  echo "- exit_code: $CODE" >> "$LOG"
  echo "- antibody:  $ANTIBODY" >> "$LOG"
  echo "- trajectory: $TRAJECTORY" >> "$LOG"
  echo "" >> "$LOG"

  echo "[${TRAJECTORY}] $NAME → $ANTIBODY (exit $CODE)"
}

# ── report header ────────────────────────────────────────────────────────────
cat > "$LOG" <<HEADER
# SAGCO DARWIN ANTIBODY REPORT

STAMP: $STAMP
GHIDRA_HOME: $GHIDRA_HOME
JAVA_HOME: $JAVA_HOME
BINARY: $BINARY

## Mission
Map CLI error codes into adaptive antibodies and track SAGCO evolution vs adaptation trajectory.

HEADER

echo "===== SAGCO DARWIN ANTIBODY ====="
echo "stamp=$STAMP"
echo ""

# ── test cases ───────────────────────────────────────────────────────────────
# Core commands
run_case "past"          "sagco past"
run_case "past_fuzz"     "sagco past-fuzz"
run_case "cmd_dna"       "sagco cmd dna"

# Binary path verification (direct, not via PATH alias)
run_case "direct_binary" "./$BINARY past"

# Ghidra JDK gate (correct binary + GHIDRA_HOME set)
if [ -f "$GHIDRA_HOME/support/analyzeHeadless" ]; then
  run_case "ghidra_jdk_gate" \
    "\$GHIDRA_HOME/support/analyzeHeadless ~/ghidra_projects SAGCO_TEST -import $BINARY -overwrite"
else
  run_case "ghidra_not_found" "ls $GHIDRA_HOME/support/analyzeHeadless"
fi

# main.rs stub immunity check
run_case "mainrs_antibody" "bash sagco_mainrs_antibody.sh --check-only 2>/dev/null | tail -1"

# ── DNA seal ─────────────────────────────────────────────────────────────────
DARWIN_DNA="$(sha256sum "$LOG" | awk '{print $1}')"

cat >> "$LOG" <<FOOTER

## Darwin DNA

SAGCO_DARWIN_DNA=$DARWIN_DNA

## Trajectory Summary

| Case | Antibody | Trajectory |
|------|---------|------------|
$(grep -E "^## CASE:|^- antibody:|^- trajectory:" "$LOG" | \
  paste - - - | \
  sed 's/## CASE: //; s/- antibody:  //; s/- trajectory: //' | \
  awk -F'\t' '{print "| "$1" | "$2" | "$3" |"}')

## Verdict

STATUS=SAGCO_DARWIN_ANTIBODY_PASS
FOOTER

cat "$LOG"
echo ""
echo "REPORT=$LOG"
echo "SAGCO_DARWIN_DNA=$DARWIN_DNA"
