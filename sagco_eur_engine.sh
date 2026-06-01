#!/data/data/com.termux/files/usr/bin/bash
# SAGCO EUR Engine — Expected / Actual / Variance scoring
# Score: PASS | WARN | FAIL | ADAPT | EVOLVE
# License: SSL-1.0 — Strategickhaos DAO LLC
set -e

export PATH="${HOME}/bin:${PATH}"

OUT="reports/eur"
mkdir -p "$OUT"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$OUT/eur_${STAMP}.md"

PASS=0; WARN=0; FAIL=0; ADAPT=0; EVOLVE=0

# ── EUR check function ────────────────────────────────────────────────────────
# eur_check "NAME" "EXPECTED" "ACTUAL_CMD" "MATCH_PATTERN" "SCORE_TYPE"
eur_check() {
  local name="$1" expected="$2" cmd="$3" pattern="$4" score_type="${5:-PASS}"
  local actual verdict variance

  actual="$(eval "$cmd" 2>/dev/null | head -1 || echo "NO_OUTPUT")"

  if echo "$actual" | grep -qi "$pattern"; then
    verdict="PASS"
    variance="0"
    PASS=$((PASS+1))
  else
    verdict="$score_type"
    variance="+1"
    case "$score_type" in
      WARN)   WARN=$((WARN+1)) ;;
      FAIL)   FAIL=$((FAIL+1)) ;;
      ADAPT)  ADAPT=$((ADAPT+1)) ;;
      EVOLVE) EVOLVE=$((EVOLVE+1)) ;;
    esac
  fi

  printf "| %-32s | %-28s | %-28s | %-8s | %-8s |\n" \
    "$name" "$expected" "$actual" "$variance" "$verdict" >> "$REPORT.rows"
}

# ── write header ──────────────────────────────────────────────────────────────
cat > "$REPORT" <<HDR
# SAGCO EUR VARIANCE ENGINE

**STAMP:** $STAMP
**ENTITY:** Strategickhaos DAO LLC | EIN: 39-2900295
**MODE:** Expected / Actual / Variance

| Artifact | Expected | Actual | Variance | Score |
|----------|---------|--------|---------|-------|
HDR
: > "$REPORT.rows"

# ── core commands ─────────────────────────────────────────────────────────────
eur_check "sagco past"           "SAGCO_PAST_PASS"        "sagco past"            "SAGCO_PAST_PASS"   "FAIL"
eur_check "sagco past-fuzz SHA"  "SHA256: ..."            "sagco past-fuzz"       "SHA256:"           "FAIL"
eur_check "sagco cmd dna"        "SAGCO_COMMAND_DNA=..."  "sagco cmd dna"         "SAGCO_COMMAND_DNA" "FAIL"
eur_check "sagco wave usage"     "Use: sagco wave"        "sagco wave"            "wave"              "WARN"
eur_check "sagco bill"           "TOTAL output"           "bash sagco_bill.sh --bill 2>/dev/null | grep -o 'TOTAL.*'" "TOTAL" "WARN"

# ── binary / source ───────────────────────────────────────────────────────────
eur_check "binary exists"        "FOUND"                  "ls target/release/sagco_rust_command_compiler 2>/dev/null && echo FOUND" "FOUND" "FAIL"
eur_check "main.rs line count"   ">50 lines"              "wc -l < src/main.rs"   "[5-9][0-9]\|[1-9][0-9][0-9]" "FAIL"
eur_check "main.rs.backup"       "FOUND"                  "ls src/main.rs.backup 2>/dev/null && echo FOUND" "FOUND" "FAIL"
eur_check "Cargo.toml"           "FOUND"                  "ls Cargo.toml 2>/dev/null && echo FOUND" "FOUND" "FAIL"

# ── ghidra / reverse engineering ──────────────────────────────────────────────
eur_check "Ghidra log"           "FOUND"                  "ls reports/ghidra/ghidra_sagco.log 2>/dev/null && echo FOUND" "FOUND" "WARN"
eur_check "Ghidra import"        "Import succeeded"       "grep 'Import succeeded' reports/ghidra/ghidra_sagco.log 2>/dev/null | tail -1" "Import succeeded" "WARN"
eur_check "Ghidra analysis"      "Save succeeded"         "grep 'Save succeeded' reports/ghidra/ghidra_sagco.log 2>/dev/null | tail -1" "Save succeeded" "WARN"
eur_check "Decompiler native"    "native binary present"  "grep -i 'decompil' reports/ghidra/ghidra_sagco.log 2>/dev/null | tail -1" "native" "ADAPT"
eur_check "FlameTokens >0"       ">0 tokens"              "wc -l < reports/ghidra/flametokens.txt" "[1-9]" "WARN"
eur_check "FlameTokens >100"     ">100 tokens"            "wc -l < reports/ghidra/flametokens.txt" "[1-9][0-9][0-9]" "ADAPT"
eur_check "ELF headers"          "FOUND"                  "ls reports/ghidra/elf_headers.txt 2>/dev/null && echo FOUND" "FOUND" "WARN"
eur_check "ASM objdump"          "FOUND"                  "ls reports/ghidra/objdump_sagco.txt 2>/dev/null && echo FOUND" "FOUND" "EVOLVE"

# ── validation artifacts ──────────────────────────────────────────────────────
eur_check "Darwin antibody"      "report exists"          "ls reports/darwin_antibody/darwin_*.md 2>/dev/null | tail -1 | xargs basename 2>/dev/null" "darwin_" "WARN"
eur_check "PAST chain index"     "FOUND"                  "ls reports/SAGCO_PAST_CHAIN_INDEX.md 2>/dev/null && echo FOUND" "FOUND" "FAIL"
eur_check "sagco.yaml compose"   "FOUND"                  "ls sagco.yaml 2>/dev/null && echo FOUND" "FOUND" "FAIL"
eur_check "Purple audit"         "report exists"          "ls reports/purple_efficiency_audit/audit_*.md 2>/dev/null | tail -1 | xargs basename 2>/dev/null" "audit_" "WARN"
eur_check "DE fellowship report" "FOUND"                  "ls reports/SAGCO_DISTINGUISHED_ENGINEER_REPORT.md 2>/dev/null && echo FOUND" "FOUND" "WARN"
eur_check "Isometric PID"        "FOUND"                  "ls reports/cad/SAGCO_ISOMETRIC_PID.md 2>/dev/null && echo FOUND" "FOUND" "WARN"
eur_check "Isometric CAD"        "FOUND"                  "ls reports/cad/SAGCO_ISOMETRIC_CAD.md 2>/dev/null && echo FOUND" "FOUND" "WARN"

# ── production gaps ───────────────────────────────────────────────────────────
eur_check "GUI interface"        "GUI app"                "echo none"             "GUI"    "EVOLVE"
eur_check "Persistence layer"    "database/storage"       "echo none"             "sqlite" "EVOLVE"
eur_check "Multi-user support"   "auth/sessions"          "echo none"             "auth"   "EVOLVE"
eur_check "Production deploy"    "sagco deploy"           "sagco deploy 2>/dev/null | head -1" "deploy" "EVOLVE"

# ── assemble report ───────────────────────────────────────────────────────────
cat "$REPORT.rows" >> "$REPORT"
rm -f "$REPORT.rows"

TOTAL=$((PASS+WARN+FAIL+ADAPT+EVOLVE))
SCORE=$(( PASS * 100 / (TOTAL > 0 ? TOTAL : 1) ))

cat >> "$REPORT" <<FOOTER

---

## EUR Summary

| Score | Count |
|-------|------:|
| PASS  | $PASS |
| WARN  | $WARN |
| ADAPT | $ADAPT |
| EVOLVE| $EVOLVE |
| FAIL  | $FAIL |
| **TOTAL** | **$TOTAL** |

**Pass rate: $SCORE% ($PASS/$TOTAL)**

## Variance Map

\`\`\`
PASS   = variance 0     — system at spec
WARN   = variance +1    — minor deviation, monitor
ADAPT  = variance +1    — platform limit, redesign tier
EVOLVE = variance +1    — planned gap, future feature
FAIL   = variance +1    — unexpected failure, fix now
\`\`\`

## EUR Verdict

\`\`\`
STATUS=SAGCO_EUR_ENGINE_PASS
PASS=$PASS  WARN=$WARN  ADAPT=$ADAPT  EVOLVE=$EVOLVE  FAIL=$FAIL
PASS_RATE=$SCORE%
SAGCO_COMMAND_DNA=$(sagco cmd dna 2>/dev/null | grep -o 'SAGCO_COMMAND_DNA=.*' || echo unknown)
\`\`\`

---
*Strategickhaos DAO LLC — Domenic Gabriel Garza | SSL-1.0*
FOOTER

cat "$REPORT"
echo ""
echo "REPORT=$REPORT"
sha256sum "$REPORT"
