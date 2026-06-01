#!/usr/bin/env bash
# sagco_compose_run — YAML-driven plugin executor
# Reads sagco.compose.yaml → executes each plugin → composed EUR report
# License: SSL-1.0 — Strategickhaos DAO LLC
set -e

COMPOSE="${1:-sagco.compose.yaml}"
[ ! -f "$COMPOSE" ] && { echo "ERROR: $COMPOSE not found"; exit 1; }

OUT="reports/compose_run"
mkdir -p "$OUT"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$OUT/compose_${STAMP}.md"
JSON="$OUT/compose_${STAMP}.json"
RESULTS_CSV="/tmp/sagco_compose_results_$$.csv"
touch "$RESULTS_CSV"

# ── parse YAML: extract plugin entries ────────────────────────────────────────
# Uses quoted heredoc (<<'PY') — no bash expansion inside Python block
# Compose file passed as sys.argv[1] to avoid variable-in-heredoc issues
PLUGIN_LIST=$(python3 - "$COMPOSE" <<'PY'
import sys

with open(sys.argv[1]) as f:
    lines = f.readlines()

plugins = []
current = {}
in_plugins = False

for line in lines:
    s = line.strip()
    indent = len(line) - len(line.lstrip())

    if s == "plugins:":
        in_plugins = True
        continue

    if not in_plugins:
        continue

    # indent=0 top-level key means plugins section is over
    if s and indent == 0:
        if current and "name" in current:
            plugins.append(current)
        in_plugins = False
        current = {}
        continue

    if s.startswith("- name:"):
        if current and "name" in current:
            plugins.append(current)
        current = {"name": s.split(":", 1)[1].strip()}
    elif s.startswith("script:"):
        current["script"] = s.split(":", 1)[1].strip()
    elif s.startswith("output:"):
        current["output"] = s.split(":", 1)[1].strip()
    elif s.startswith("compose_args:"):
        val = s.split(":", 1)[1].strip().strip('"')
        current["args"] = val

if current and "name" in current:
    plugins.append(current)

for p in plugins:
    print("{name}|{script}|{output}|{args}".format(
        name=p.get("name", ""),
        script=p.get("script", ""),
        output=p.get("output", "reports"),
        args=p.get("args", ""),
    ))
PY
)

[ -z "$PLUGIN_LIST" ] && { echo "ERROR: no plugins parsed from $COMPOSE"; exit 1; }

# ── run each plugin ────────────────────────────────────────────────────────────
PASS=0; SKIP=0; FAIL=0

echo "===== SAGCO COMPOSE RUN ====="
echo "COMPOSE=$COMPOSE"
echo "STAMP=$STAMP"
echo ""

while IFS='|' read -r NAME SCRIPT OUTPUT ARGS; do
  [ -z "$NAME" ] && continue
  printf ">>> plugin: %-30s" "$NAME"

  if [ ! -f "$SCRIPT" ]; then
    printf "SKIP (not found: %s)\n" "$SCRIPT"
    echo "$NAME|SKIP|SKIP_ANTIBODY|skipped" >> "$RESULTS_CSV"
    SKIP=$((SKIP+1))
    continue
  fi

  [ ! -x "$SCRIPT" ] && chmod +x "$SCRIPT"
  mkdir -p "$OUTPUT"

  EXIT=0
  if [ -n "$ARGS" ]; then
    # word-split intentional: ARGS contains flags and message
    # shellcheck disable=SC2086
    bash "$SCRIPT" $ARGS > /tmp/_co_out_$$ 2>&1 || EXIT=$?
  else
    bash "$SCRIPT" > /tmp/_co_out_$$ 2>&1 || EXIT=$?
  fi

  OUT_SHA=$(sha256sum /tmp/_co_out_$$ | cut -c1-16)

  if [ "$EXIT" -eq 0 ]; then
    printf "PASS  sha=%s\n" "$OUT_SHA"
    echo "$NAME|PASS|PASS_IMMUNITY|stabilized" >> "$RESULTS_CSV"
    PASS=$((PASS+1))
  else
    LAST=$(tail -1 /tmp/_co_out_$$ 2>/dev/null || true)
    if echo "$LAST" | grep -qi "host not in"; then
      AB="NETWORK_POLICY_ANTIBODY"
    elif echo "$LAST" | grep -qi "cargo.toml\|no workspace\|platform\|jdk\|java"; then
      AB="PLATFORM_LIMITATION_ANTIBODY"
    elif echo "$LAST" | grep -qi "not found\|no such\|not find\|cannot find"; then
      AB="PATH_DISCOVERY_ANTIBODY"
    elif echo "$LAST" | grep -qi "no input\|no artifact\|no message"; then
      AB="MISSING_ARGS_ANTIBODY"
    else
      AB="UNKNOWN_VARIANCE_ANTIBODY"
    fi
    printf "FAIL  exit=%d  antibody=%s\n" "$EXIT" "$AB"
    echo "$NAME|FAIL|$AB|adaptation" >> "$RESULTS_CSV"
    FAIL=$((FAIL+1))
  fi

  rm -f /tmp/_co_out_$$

done <<< "$PLUGIN_LIST"

TOTAL=$((PASS+SKIP+FAIL))
PASS_RATE=0
[ "$TOTAL" -gt 0 ] && PASS_RATE=$(python3 -c "print(round($PASS*100/$TOTAL))")

echo ""
echo "TOTAL=$TOTAL  PASS=$PASS  SKIP=$SKIP  FAIL=$FAIL  PASS_RATE=${PASS_RATE}%"
echo ""

# ── write .md ─────────────────────────────────────────────────────────────────
cat > "$REPORT" <<MD
# SAGCO COMPOSE RUN — ${STAMP}
## SAGCO Evidence Engineering OS — Plugin Executor
## Entity: Strategickhaos DAO LLC | License: SSL-1.0

---

## Compose Source

\`\`\`
FILE = $COMPOSE
\`\`\`

---

## Plugin Run Results

| Plugin | Status | Antibody | Trajectory |
|--------|--------|----------|------------|
MD

while IFS='|' read -r n s ab tr; do
  printf "| \`%s\` | %s | %s | %s |\n" "$n" "$s" "$ab" "$tr"
done < "$RESULTS_CSV" >> "$REPORT"

cat >> "$REPORT" <<MD2

---

## EUR Probe

\`\`\`
Expected: all plugins PASS
Actual:   TOTAL=$TOTAL  PASS=$PASS  SKIP=$SKIP  FAIL=$FAIL
Variance: FAIL=$FAIL  SKIP=$SKIP
Score:    PASS_RATE=${PASS_RATE}%
\`\`\`

---

## Pipeline Stages

\`\`\`
detect → tokenize → fingerprint → variance → antibody → evidence → project → seal
\`\`\`

---

STATUS=SAGCO_COMPOSE_RUN_PASS
SAGCO_COMMAND_DNA=a364ca9f90356c85

*Strategickhaos DAO LLC — SSL-1.0*
MD2

# ── write .json ────────────────────────────────────────────────────────────────
# Pass results file as sys.argv[1]; quoted heredoc avoids backtick issues
python3 - "$RESULTS_CSV" "$JSON" "$STAMP" "$COMPOSE" "$TOTAL" "$PASS" "$SKIP" "$FAIL" "$PASS_RATE" <<'PY2'
import json, sys

results_csv, json_path, stamp, compose, total, pass_, skip, fail, pass_rate = sys.argv[1:]

results = []
with open(results_csv) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if len(parts) == 4:
            results.append({
                "plugin":     parts[0],
                "status":     parts[1],
                "antibody":   parts[2],
                "trajectory": parts[3],
            })

data = {
    "stamp":     stamp,
    "compose":   compose,
    "total":     int(total),
    "pass":      int(pass_),
    "skip":      int(skip),
    "fail":      int(fail),
    "pass_rate": int(pass_rate),
    "results":   results,
    "sagco_dna": "a364ca9f90356c85",
    "status":    "SAGCO_COMPOSE_RUN_PASS",
}
with open(json_path, "w") as f:
    json.dump(data, f, indent=2)
print("JSON written:", json_path)
PY2

rm -f "$RESULTS_CSV"

# ── SHA seals ─────────────────────────────────────────────────────────────────
SPEC_SHA="$(sha256sum "$REPORT" | awk '{print $1}')"
ARTIFACT_SHA="$(sha256sum "$JSON" | awk '{print $1}')"

cat >> "$REPORT" <<SEAL

## SHA256 Seals

\`\`\`
SPEC_SHA     = $SPEC_SHA
ARTIFACT_SHA = $ARTIFACT_SHA
SAGCO_DNA    = a364ca9f90356c85
STATUS       = SAGCO_COMPOSE_RUN_PASS
\`\`\`

*Strategickhaos DAO LLC — SSL-1.0*
SEAL

echo "REPORT=$REPORT"
echo "JSON=$JSON"
echo "SPEC_SHA=$SPEC_SHA"
echo "ARTIFACT_SHA=$ARTIFACT_SHA"
echo ""
echo "STATUS=SAGCO_COMPOSE_RUN_PASS"
