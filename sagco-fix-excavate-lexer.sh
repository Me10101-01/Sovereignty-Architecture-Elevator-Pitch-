#!/data/data/com.termux/files/usr/bin/bash
# sagco-fix-excavate-lexer.sh
#
# WHAT IT FIXES:
#   The original patcher used s.replace("OpSeal,", ...) which replaced
#   EVERY occurrence of "OpSeal," — including inside match arms.
#   This left "OpExcavate," as a bare identifier inside a match expression,
#   causing the compile error on line 64.
#
# HOW IT FIXES IT:
#   Uses a scope-aware Python patcher that ONLY touches the enum Token { } block.
#   All other occurrences of "OpSeal," are left alone.
#
# Run from ~/downloads/sagco_rust_command_compiler:
#   bash ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-fix-excavate-lexer.sh
set -euo pipefail

SRC="crates/sagco-core/src"

echo "SAGCO FIX — EXCAVATE LEXER PATCH"
echo "WS=$(pwd)"

if [[ ! -f "Cargo.toml" ]] || [[ ! -d "${SRC}" ]]; then
  echo "ERROR: run from ~/downloads/sagco_rust_command_compiler"
  exit 1
fi

echo ""
echo "=== DIAGNOSE: current state of lexer.rs ==="
python3 - <<'PY'
from pathlib import Path

p = Path("crates/sagco-core/src/lexer.rs")
s = p.read_text()
lines = s.splitlines()

print(f"  Total lines: {len(lines)}")

for i, line in enumerate(lines, 1):
    if "OpExcavate" in line or "OpSeal" in line:
        flag = "  <<< " if "OpExcavate" in line else "      "
        print(f"  {flag}line {i:3d}: {line}")

# Check for the bad pattern: OpExcavate inside a match/expression context
bad = [i+1 for i, l in enumerate(lines)
       if "OpExcavate," in l and "=>" in lines[max(0,i-3):i+1].__str__()]
if bad:
    print(f"\n  PROBLEM DETECTED: OpExcavate in expression context near lines: {bad}")
else:
    print("\n  No expression-context OpExcavate found.")

enum_ok = any("OpExcavate" in l and "=>" not in l for l in lines)
print(f"  OpExcavate in enum block: {enum_ok}")
PY

echo ""
echo "=== FIX: scope-aware patch ==="
python3 - <<'PY'
import re
from pathlib import Path
import sys

p = Path("crates/sagco-core/src/lexer.rs")
s = p.read_text()

# ─────────────────────────────────────────────────────────────────────────────
# STEP A: Remove ALL existing "OpExcavate" insertions so we start clean.
# The bad patcher may have inserted it in multiple places.
# ─────────────────────────────────────────────────────────────────────────────
original_count = s.count("OpExcavate")
if original_count > 0:
    print(f"  Found {original_count} existing OpExcavate occurrence(s) — removing all.")
    # Remove the variant line wherever it appears (handles both correct and misplaced)
    s = re.sub(r'\n[ \t]*OpExcavate,', '', s)
    # Remove it if it was inserted inline after OpSeal on same line
    s = re.sub(r'(OpSeal,)\s*OpExcavate,', r'\1', s)
    print(f"  After removal: {s.count('OpExcavate')} occurrence(s) remain.")
else:
    print("  No existing OpExcavate found — inserting fresh.")

# ─────────────────────────────────────────────────────────────────────────────
# STEP B: Find the enum Token block and insert OpExcavate ONLY there.
# Strategy: find "enum Token {", scan forward to "}", insert before "}"
# but after OpSeal.
# ─────────────────────────────────────────────────────────────────────────────

# Find the Token enum block using line scanning
lines = s.splitlines(keepends=True)
in_enum  = False
depth    = 0
enum_start = None
enum_end   = None
opseal_line = None

for i, line in enumerate(lines):
    stripped = line.strip()
    if not in_enum:
        if re.search(r'\benum\s+Token\b', line) and '{' in line:
            in_enum = True
            depth = line.count('{') - line.count('}')
            enum_start = i
            continue
    else:
        depth += line.count('{') - line.count('}')
        if 'OpSeal' in line and '=>' not in line:
            opseal_line = i
        if depth <= 0:
            enum_end = i
            break

if opseal_line is None:
    print("  ERROR: Could not find OpSeal in enum Token block — verify lexer.rs structure")
    sys.exit(1)

# Insert OpExcavate immediately after the OpSeal line in the enum
indent = re.match(r'^(\s*)', lines[opseal_line]).group(1)
insert_line = f"{indent}OpExcavate,\n"
lines.insert(opseal_line + 1, insert_line)
print(f"  Inserted OpExcavate in enum Token at line {opseal_line + 2}")

s = ''.join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# STEP C: Add "excavate" keyword → Token::OpExcavate in the keyword match.
# Only if not already there.
# ─────────────────────────────────────────────────────────────────────────────
if '"excavate"' not in s:
    # Find the "seal" arm in the keyword/tokenize function
    pattern = r'("seal"\s*=>\s*Token::OpSeal,)'
    match = re.search(pattern, s)
    if match:
        replacement = match.group(1) + '\n            "excavate" => Token::OpExcavate,'
        s = s[:match.start()] + replacement + s[match.end():]
        print('  Added "excavate" => Token::OpExcavate in keyword match')
    else:
        print('  WARNING: "seal" arm not found — add manually:')
        print('    "excavate" => Token::OpExcavate,')
else:
    print('  "excavate" keyword mapping already present')

p.write_text(s)
print("")
print("STATUS=LEXER_FIX_APPLIED")
PY

echo ""
echo "=== VERIFY: lines around OpExcavate after fix ==="
python3 - <<'PY'
from pathlib import Path
p = Path("crates/sagco-core/src/lexer.rs")
lines = p.read_text().splitlines()
for i, line in enumerate(lines, 1):
    if "OpExcavate" in line or "OpSeal" in line:
        print(f"  line {i:3d}: {line}")
PY

echo ""
echo "=== BUILD: cargo build --bin sagco-core ==="
cargo build --bin sagco-core 2>&1 | grep -E "(^error|^warning.*unused|PASS|FAIL|Compiling sagco)" | head -20

echo ""
echo "STATUS=SAGCO_LEXER_FIX_COMPLETE"
