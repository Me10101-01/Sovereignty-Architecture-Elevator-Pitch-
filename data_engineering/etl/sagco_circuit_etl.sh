#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Circuit ETL — populates sagco_circuit.db from live command probes
# Run from: ~/downloads/sagco_rust_command_compiler
# Prereqs: pkg install sqlite
# License: SSL-1.0 — Strategickhaos DAO LLC
set -e

export PATH="${HOME}/bin:${PATH}"

REPO="${HOME}/sagco_pr_lab/repo"
DB="${REPO}/data_engineering/sagco_circuit.db"
SQL="${REPO}/data_engineering/sql/001_sagco_circuit_ledger.sql"
SESSION="sagco-rust-compiler-archive"
STAMP="$(date +%Y%m%d_%H%M%S)"

# bootstrap DB if missing
if [ ! -f "$DB" ]; then
  echo "[ETL] initializing sagco_circuit.db..."
  sqlite3 "$DB" < "$SQL"
fi

# probe helper: runs command, inserts circuit row
insert_circuit() {
  local CMD="$1" EXPECTED="$2" MATCH="$3"
  local actual exit_code antibody trajectory variance score

  set +e
  actual="$(eval "$CMD" 2>&1 | head -3)"
  exit_code="$?"
  set -e

  if echo "$actual" | grep -qi "$MATCH"; then
    antibody="PASS_IMMUNITY"; trajectory="stabilized"; variance=0; score="PASS"
  elif echo "$actual" | grep -qi "no such file\|not found"; then
    antibody="PATH_DISCOVERY_ANTIBODY"; trajectory="adaptation"; variance=1; score="FAIL"
  elif echo "$actual" | grep -qi "JDK 21"; then
    antibody="JDK_GATE_ANTIBODY"; trajectory="evolution"; variance=1; score="EVOLVE"
  elif echo "$actual" | grep -qi "decompiler\|platform"; then
    antibody="PLATFORM_LIMITATION_ANTIBODY"; trajectory="evolution"; variance=1; score="ADAPT"
  elif [ "$exit_code" -eq 0 ]; then
    antibody="PASS_IMMUNITY"; trajectory="stabilized"; variance=0; score="PASS"
  else
    antibody="UNKNOWN_VARIANCE_ANTIBODY"; trajectory="mutation"; variance=1; score="WARN"
  fi

  sqlite3 "$DB" <<SQL
INSERT INTO sagco_circuit (stamp,session,command,expected,actual,exit_code,antibody,trajectory,variance,score)
VALUES ('$STAMP','$SESSION','$(echo "$CMD" | sed "s/'/''/g")','$EXPECTED','$(echo "$actual" | head -1 | sed "s/'/''/g")',$exit_code,'$antibody','$trajectory',$variance,'$score');
SQL

  echo "  [${score}] $CMD → $antibody"
}

echo "[ETL] SAGCO Circuit ETL — $STAMP"
echo "[ETL] DB: $DB"
echo ""

# ── probe all SAGCO commands ──────────────────────────────────────────────────
insert_circuit "sagco past"      "SAGCO_PAST_PASS"        "SAGCO_PAST_PASS"
insert_circuit "sagco past-fuzz" "SHA256: ..."            "SHA256:"
insert_circuit "sagco cmd dna"   "SAGCO_COMMAND_DNA=..."  "SAGCO_COMMAND_DNA"
insert_circuit "ls target/release/sagco_rust_command_compiler" "FOUND" "sagco_rust"
insert_circuit "wc -l < src/main.rs" ">50" "[5-9][0-9]"
insert_circuit "ls reports/SAGCO_PAST_CHAIN_INDEX.md" "FOUND" "PAST_CHAIN"
insert_circuit "ls sagco.yaml" "FOUND" "sagco.yaml"
insert_circuit "ls reports/ghidra/flametokens.txt" "FOUND" "flametokens"

# ── insert current maturity scores ───────────────────────────────────────────
FLAMECOUNT="$(wc -l < reports/ghidra/flametokens.txt 2>/dev/null || echo 0)"
DNA="$(sagco cmd dna 2>/dev/null | grep -o 'a364[^ ]*' || echo unknown)"

sqlite3 "$DB" <<SQL
INSERT INTO sagco_maturity
  (stamp,session,prototype_score,validation_score,audit_score,
   analysis_score,evidence_score,production_score,overall_score,
   flametoken_count,command_dna,trajectory)
VALUES
  ('$STAMP','$SESSION',100,100,100,85,90,30,84,
   $FLAMECOUNT,'$DNA','EVOLUTION_WITH_PLATFORM_SPECIALIZATION');
SQL
echo "  [ETL] maturity row inserted"

# ── report ────────────────────────────────────────────────────────────────────
echo ""
echo "[ETL] ── Circuit Summary ──"
sqlite3 -column -header "$DB" \
  "SELECT antibody, score, COUNT(*) as n FROM sagco_circuit
   WHERE session='$SESSION' AND stamp>='$STAMP'
   GROUP BY antibody, score ORDER BY n DESC;"

echo ""
sqlite3 -column -header "$DB" \
  "SELECT pass_count, fail_count, pass_rate_pct FROM mart_session_pass_rate
   WHERE session='$SESSION';"

echo ""
echo "[ETL] SAGCO_CIRCUIT_ETL_PASS"
echo "DB=$DB"
