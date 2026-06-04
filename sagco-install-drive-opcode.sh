#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Install Drive Opcode
# Adds drive.rs + drive opcode to sagco-core.
# drive computes each agent's desire to act and emits an auto-generated pipeline.
# Requires: excavate + lineage + weight opcodes already installed.
#
# Run from ~/downloads/sagco_rust_command_compiler:
#   bash ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-install-drive-opcode.sh
set -euo pipefail

REPO="${HOME}/Sovereignty-Architecture-Elevator-Pitch-"
SRC="crates/sagco-core/src"

echo "SAGCO INSTALL DRIVE OPCODE"
echo "WS=$(pwd)"

if [[ ! -f "Cargo.toml" ]] || [[ ! -d "${SRC}" ]]; then
  echo "ERROR: run from ~/downloads/sagco_rust_command_compiler"
  exit 1
fi

echo ""
echo "=== STEP 1: drive.rs module ==="
cp "${REPO}/rust/sagco-core/drive.rs" "${SRC}/drive.rs"
echo "  COPIED: ${SRC}/drive.rs"

echo ""
echo "=== STEP 2: patch lexer / parser / main ==="
python3 - <<'PY'
from pathlib import Path
import sys

SRC = Path("crates/sagco-core/src")

# ── lexer.rs ──────────────────────────────────────────────────────────────────
p = SRC / "lexer.rs"
s = p.read_text()

if "OpDrive" not in s:
    s = s.replace("OpExcavate,", "OpExcavate,\n    OpDrive,")
    print("  lexer.rs: +OpDrive variant")
else:
    print("  lexer.rs: OpDrive already present")

if '"drive"' not in s:
    s = s.replace(
        '"excavate" => Token::OpExcavate,',
        '"excavate" => Token::OpExcavate,\n            "drive" => Token::OpDrive,'
    )
    print('  lexer.rs: +"drive" keyword')
else:
    print("  lexer.rs: drive keyword already present")

p.write_text(s)

# ── parser.rs ─────────────────────────────────────────────────────────────────
p = SRC / "parser.rs"
s = p.read_text()

if "Drive { folder: String }" not in s:
    s = s.replace(
        "Excavate { folder: String },",
        "Excavate { folder: String },\n    Drive { folder: String },"
    )
    print("  parser.rs: +Command::Drive variant")
else:
    print("  parser.rs: variant already present")

if "Token::OpDrive" not in s:
    marker = "Token::OpExcavate"
    idx = s.find(marker)
    if idx == -1:
        print("  ERROR: Token::OpExcavate not found — install excavate opcode first")
        sys.exit(1)
    arm = (
        '\n            Token::OpDrive => {\n'
        '                self.advance();\n'
        '                match &self.current_token {\n'
        '                    Token::Identifier(folder) => {\n'
        '                        let cmd = Command::Drive { folder: folder.clone() };\n'
        '                        self.advance();\n'
        '                        Ok(cmd)\n'
        '                    }\n'
        '                    _ => Err("Expected folder after drive".to_string()),\n'
        '                }\n'
        '            }\n'
        '            '
    )
    s = s[:idx] + arm + s[idx:]
    print("  parser.rs: +Token::OpDrive parse arm")
else:
    print("  parser.rs: arm already present")

p.write_text(s)

# ── main.rs ───────────────────────────────────────────────────────────────────
p = SRC / "main.rs"
s = p.read_text()

if "mod drive;" not in s:
    s = s.replace("mod excavate;", "mod excavate;\nmod drive;")
    print("  main.rs: +mod drive;")
else:
    print("  main.rs: mod drive already declared")

if "Command::Drive" not in s:
    needle = "Command::Excavate { folder } => {"
    idx = s.find(needle)
    if idx == -1:
        print("  ERROR: Command::Excavate arm not found — install excavate opcode first")
        sys.exit(1)
    handler = (
        '\n                Command::Drive { folder } => {\n'
        '                    let result = drive::score(&folder);\n'
        '                    let rpt = drive::report(&result);\n'
        '                    print!("{}", rpt);\n'
        '                    std::fs::create_dir_all("reports").unwrap_or(());\n'
        '                    use std::time::{SystemTime, UNIX_EPOCH};\n'
        '                    let stamp = SystemTime::now()\n'
        '                        .duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();\n'
        '                    let mp = format!("reports/sagco_drive_{}.manifest", stamp);\n'
        '                    let pipeline = drive::generate_pipeline(&result);\n'
        '                    std::fs::write(&mp, &rpt).unwrap_or(());\n'
        '                    std::fs::write("pipeline_autodrive.txt", &pipeline).unwrap_or(());\n'
        '                    println!("MANIFEST={}", mp);\n'
        '                    println!("AUTODRIVE_PIPELINE=pipeline_autodrive.txt");\n'
        '                }\n'
        '                '
    )
    s = s[:idx] + handler + s[idx:]
    print("  main.rs: +Command::Drive handler")
else:
    print("  main.rs: handler already present")

p.write_text(s)
print("")
print("STATUS=DRIVE_OPCODE_PATCHED")
PY

echo ""
echo "=== STEP 3: cargo build --bin sagco-core ==="
cargo build --bin sagco-core 2>&1 | grep -v "^warning" | tail -5

echo ""
echo "=== STEP 4: smoke test ==="
cp "${REPO}/pipeline_drive_l1.txt" .
cargo run --bin sagco-core -- pipeline_drive_l1.txt 2>/dev/null \
  | grep -v "^warning"

echo ""
echo "STATUS=SAGCO_DRIVE_OPCODE_INSTALLED"
