#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Advanced Tree Scaffold
# Adds antibody/identity/reverse_engineering/fuzz/trajectory Rust modules
# and data_engineering SQLite ledger — WITHOUT touching src/spl/
# Run from: ~/downloads/sagco_rust_command_compiler
# License: SSL-1.0 — Strategickhaos DAO LLC
set -e

REPO="${HOME}/sagco_pr_lab/repo"
RUST_PROJECT="$(pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"

echo "===== SAGCO ADVANCED TREE SCAFFOLD ====="
echo "Rust project : $RUST_PROJECT"
echo "Repo source  : $REPO"
echo "Stamp        : $STAMP"
echo ""

# ── safety check: verify we're in the right project ──────────────────────────
if [ ! -f "Cargo.toml" ]; then
  echo "ERROR: run from ~/downloads/sagco_rust_command_compiler"
  exit 1
fi

if ! grep -q "sagco_rust_command_compiler" Cargo.toml 2>/dev/null; then
  echo "ERROR: wrong Cargo.toml — expected sagco_rust_command_compiler"
  exit 1
fi

echo "[1/6] Rust project verified: $(grep ^name Cargo.toml)"

# ── create Rust module directories ───────────────────────────────────────────
echo "[2/6] Creating src/ module directories..."
mkdir -p src/antibody
mkdir -p src/identity
mkdir -p src/reverse_engineering
mkdir -p src/fuzz
mkdir -p src/trajectory
mkdir -p tests/common
echo "      src/antibody/, src/identity/, src/reverse_engineering/, src/fuzz/, src/trajectory/"
echo "      tests/common/"

# ── copy Rust module files from repo ─────────────────────────────────────────
echo "[3/6] Copying Rust module files from repo..."

for MODULE in antibody/types.rs antibody/classifier.rs antibody/mod.rs \
              identity/dna_crypto.rs \
              reverse_engineering/ghidra_import.rs; do
  SRC="$REPO/sagco_rust_modules/$MODULE"
  DST="src/$MODULE"
  if [ -f "$SRC" ]; then
    cp "$SRC" "$DST"
    echo "      copied: $MODULE"
  else
    echo "      WARN: $SRC not found — skipping"
  fi
done

# create mod.rs files for modules not yet having them
for MOD in identity reverse_engineering fuzz trajectory; do
  if [ ! -f "src/$MOD/mod.rs" ]; then
    echo "// SAGCO $MOD module — stub" > "src/$MOD/mod.rs"
    echo "      created stub: src/$MOD/mod.rs"
  fi
done

# ── patch main.rs to add mod antibody ────────────────────────────────────────
echo "[4/6] Patching src/main.rs to add mod antibody..."

MAINRS="src/main.rs"
BAK="src/main.rs.pre_antibody_${STAMP}"

# verify main.rs is real (antibody check)
LINES="$(wc -l < "$MAINRS")"
if [ "$LINES" -lt 50 ]; then
  echo "      WARN: main.rs only $LINES lines — possible stub"
  echo "      Running antibody..."
  bash "$REPO/sagco_mainrs_antibody.sh" --restore 2>/dev/null || true
fi

# backup before patching
cp "$MAINRS" "$BAK"
echo "      backup: $BAK"

# add mod declarations if not already present
if ! grep -q "^mod antibody" "$MAINRS"; then
  # insert after the last existing 'mod ' line, or at top if none
  if grep -q "^mod " "$MAINRS"; then
    # insert after last mod line
    sed -i "/^mod /{h;d};/^[^m]/{G;s/\n//}" "$MAINRS" 2>/dev/null || true
    # simpler approach: append after last mod line
    python3 - "$MAINRS" <<'PY'
import sys
path = sys.argv[1]
lines = open(path).readlines()
last_mod = max((i for i, l in enumerate(lines) if l.startswith('mod ')), default=-1)
insert = last_mod + 1 if last_mod >= 0 else 0
new_lines = [
    'mod antibody;\n',
    'mod identity;\n',
    'mod reverse_engineering;\n',
]
for m in new_lines:
    if m not in lines:
        lines.insert(insert, m)
        insert += 1
open(path, 'w').writelines(lines)
print(f"patched {path} — added mod declarations after line {last_mod+1}")
PY
  else
    # no existing mod lines — prepend
    { printf 'mod antibody;\nmod identity;\nmod reverse_engineering;\n\n'; cat "$MAINRS"; } > "${MAINRS}.tmp"
    mv "${MAINRS}.tmp" "$MAINRS"
    echo "      prepended mod declarations to main.rs"
  fi
else
  echo "      mod antibody already present — skipping"
fi

# ── create data_engineering workspace ────────────────────────────────────────
echo "[5/6] Creating data_engineering/ workspace..."
mkdir -p data_engineering/{sql,schemas,etl,warehouse,marts,reports,circuits,audits}

DB="data_engineering/sagco_circuit.db"
SQL_INIT="$REPO/data_engineering/sql/001_sagco_circuit_ledger.sql"

if command -v sqlite3 >/dev/null 2>&1; then
  if [ ! -f "$DB" ]; then
    sqlite3 "$DB" < "$SQL_INIT"
    echo "      sagco_circuit.db initialized"
  else
    echo "      sagco_circuit.db already exists — skipping init"
  fi
  # copy ETL script
  cp "$REPO/data_engineering/etl/sagco_circuit_etl.sh" data_engineering/etl/
  chmod +x data_engineering/etl/sagco_circuit_etl.sh
  echo "      ETL script installed"
else
  echo "      sqlite3 not found — run: pkg install sqlite"
  echo "      SQL schema copied for later init:"
  cp "$SQL_INIT" data_engineering/sql/001_sagco_circuit_ledger.sql
fi

# ── smoke test build ──────────────────────────────────────────────────────────
echo "[6/6] Smoke test: cargo build --release..."
if cargo build --release 2>&1; then
  echo ""
  echo "===== SCAFFOLD COMPLETE — BUILD PASS ====="
  echo ""
  sagco past
  sagco past-fuzz
  sagco cmd dna
  echo ""
  echo "STATUS=SAGCO_ADVANCED_TREE_SCAFFOLD_PASS"
  if command -v sqlite3 >/dev/null 2>&1 && [ -f "data_engineering/sagco_circuit.db" ]; then
    echo ""
    echo "Running ETL..."
    bash data_engineering/etl/sagco_circuit_etl.sh
  fi
else
  echo ""
  echo "BUILD FAILED — rolling back main.rs patch"
  cp "$BAK" "$MAINRS"
  echo "main.rs restored from $BAK"
  echo "STATUS=SAGCO_ADVANCED_TREE_SCAFFOLD_ROLLBACK"
  exit 1
fi
