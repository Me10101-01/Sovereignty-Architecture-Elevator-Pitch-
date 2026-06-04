#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Install Weight Opcode
# Adds weight.rs module + weight opcode to sagco-core.
# Assumes excavate opcode is already installed (uses same patch pattern).
#
# Run from ~/downloads/sagco_rust_command_compiler:
#   bash ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-install-weight-opcode.sh
set -euo pipefail

REPO="${HOME}/Sovereignty-Architecture-Elevator-Pitch-"
SRC="crates/sagco-core/src"

echo "SAGCO INSTALL WEIGHT OPCODE"
echo "WS=$(pwd)"

if [[ ! -f "Cargo.toml" ]] || [[ ! -d "${SRC}" ]]; then
  echo "ERROR: run from ~/downloads/sagco_rust_command_compiler"
  exit 1
fi

echo ""
echo "=== STEP 1: weight.rs module ==="
cp "${REPO}/rust/sagco-core/weight.rs" "${SRC}/weight.rs"
echo "  COPIED: ${SRC}/weight.rs"

echo ""
echo "=== STEP 2: patch lexer / parser / main ==="
python3 - <<'PY'
from pathlib import Path
import sys

SRC = Path("crates/sagco-core/src")

# ── lexer.rs ──────────────────────────────────────────────────────────────────
p = SRC / "lexer.rs"
s = p.read_text()

if "OpWeight" not in s:
    s = s.replace("OpExcavate,", "OpExcavate,\n    OpWeight,")
    print("  lexer.rs: +OpWeight variant")
else:
    print("  lexer.rs: OpWeight already present")

if '"weight"' not in s:
    s = s.replace(
        '"excavate" => Token::OpExcavate,',
        '"excavate" => Token::OpExcavate,\n            "weight" => Token::OpWeight,'
    )
    print('  lexer.rs: +"weight" keyword')
else:
    print("  lexer.rs: weight keyword already present")

p.write_text(s)

# ── parser.rs ─────────────────────────────────────────────────────────────────
p = SRC / "parser.rs"
s = p.read_text()

if "Weight { folder: String }" not in s:
    s = s.replace(
        "Excavate { folder: String },",
        "Excavate { folder: String },\n    Weight { folder: String },"
    )
    print("  parser.rs: +Command::Weight variant")
else:
    print("  parser.rs: variant already present")

if "Token::OpWeight" not in s:
    marker = "Token::OpExcavate"
    idx = s.find(marker)
    if idx == -1:
        print("  ERROR: Token::OpExcavate not found — install excavate opcode first")
        sys.exit(1)
    arm = (
        '\n            Token::OpWeight => {\n'
        '                self.advance();\n'
        '                match &self.current_token {\n'
        '                    Token::Identifier(folder) => {\n'
        '                        let cmd = Command::Weight { folder: folder.clone() };\n'
        '                        self.advance();\n'
        '                        Ok(cmd)\n'
        '                    }\n'
        '                    _ => Err("Expected folder after weight".to_string()),\n'
        '                }\n'
        '            }\n'
        '            '
    )
    s = s[:idx] + arm + s[idx:]
    print("  parser.rs: +Token::OpWeight parse arm")
else:
    print("  parser.rs: arm already present")

p.write_text(s)

# ── main.rs ───────────────────────────────────────────────────────────────────
p = SRC / "main.rs"
s = p.read_text()

if "mod weight;" not in s:
    s = s.replace("mod excavate;", "mod excavate;\nmod weight;")
    print("  main.rs: +mod weight;")
else:
    print("  main.rs: mod weight already declared")

if "Command::Weight" not in s:
    needle = "Command::Excavate { folder } => {"
    idx = s.find(needle)
    if idx == -1:
        print("  ERROR: Command::Excavate arm not found — install excavate opcode first")
        sys.exit(1)
    handler = (
        '\n                Command::Weight { folder } => {\n'
        '                    let mut bricks = weight::registry();\n'
        '                    weight::rank(&mut bricks);\n'
        '                    let rpt = weight::report(&bricks);\n'
        '                    print!("{}", rpt);\n'
        '                    std::fs::create_dir_all("reports").unwrap_or(());\n'
        '                    use std::time::{SystemTime, UNIX_EPOCH};\n'
        '                    let stamp = SystemTime::now()\n'
        '                        .duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();\n'
        '                    let mp = format!("reports/sagco_weight_{}.manifest", stamp);\n'
        '                    std::fs::write(&mp, &rpt).unwrap_or(());\n'
        '                    println!("MANIFEST={}", mp);\n'
        '                    let gate = weight::gate(&bricks, 0.90);\n'
        '                    println!("GATE_90={}", gate.len());\n'
        '                    let _ = folder;\n'
        '                }\n'
        '                '
    )
    s = s[:idx] + handler + s[idx:]
    print("  main.rs: +Command::Weight handler")
else:
    print("  main.rs: handler already present")

p.write_text(s)
print("")
print("STATUS=WEIGHT_OPCODE_PATCHED")
PY

echo ""
echo "=== STEP 3: cargo build --bin sagco-core ==="
cargo build --bin sagco-core 2>&1 | grep -v "^warning" | tail -5

echo ""
echo "=== STEP 4: smoke test ==="
cp "${REPO}/pipeline_weight.txt" .
cp "${REPO}/CORTEX.md" .
cargo run --bin sagco-core -- pipeline_weight.txt 2>/dev/null \
  | grep -v "^warning"

echo ""
echo "STATUS=SAGCO_WEIGHT_OPCODE_INSTALLED"
