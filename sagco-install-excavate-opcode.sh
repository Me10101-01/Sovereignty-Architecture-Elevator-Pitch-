#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Install Excavate Opcode
# Drops excavate.rs module into crates/sagco-core/src/
# Patches lexer.rs, parser.rs, main.rs
# Compiles and smoke-tests.
#
# Run from ~/downloads/sagco_rust_command_compiler:
#   bash ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-install-excavate-opcode.sh
set -euo pipefail

REPO="${HOME}/Sovereignty-Architecture-Elevator-Pitch-"
SRC="crates/sagco-core/src"

echo "SAGCO INSTALL EXCAVATE OPCODE"
echo "WS=$(pwd)"
echo ""

# ── Verify we're in the right place ──────────────────────────────────────────
if [[ ! -f "Cargo.toml" ]] || [[ ! -d "${SRC}" ]]; then
  echo "ERROR: run from ~/downloads/sagco_rust_command_compiler"
  exit 1
fi

# ── Step 1: Drop excavate.rs module ──────────────────────────────────────────
echo "=== STEP 1: excavate.rs module ==="
cp "${REPO}/rust/sagco-core/excavate.rs" "${SRC}/excavate.rs"
echo "  COPIED: ${SRC}/excavate.rs"

# ── Step 2: Python patcher for lexer / parser / main ─────────────────────────
echo ""
echo "=== STEP 2: patch lexer.rs, parser.rs, main.rs ==="

python3 - <<'PY'
from pathlib import Path
import sys

SRC = Path("crates/sagco-core/src")

# ── lexer.rs ──────────────────────────────────────────────────────────────────
p = SRC / "lexer.rs"
s = p.read_text()

if "OpExcavate" not in s:
    if "OpSeal," not in s:
        print("  ERROR: OpSeal not found in lexer.rs"); sys.exit(1)
    s = s.replace("OpSeal,", "OpSeal,\n    OpExcavate,")
    print("  lexer.rs: +OpExcavate variant")
else:
    print("  lexer.rs: OpExcavate already present")

if '"excavate"' not in s:
    if '"seal" => Token::OpSeal,' not in s:
        print("  ERROR: seal keyword not found in lexer.rs"); sys.exit(1)
    s = s.replace(
        '"seal" => Token::OpSeal,',
        '"seal" => Token::OpSeal,\n            "excavate" => Token::OpExcavate,'
    )
    print('  lexer.rs: +"excavate" => Token::OpExcavate')
else:
    print("  lexer.rs: excavate keyword already present")

p.write_text(s)

# ── parser.rs ─────────────────────────────────────────────────────────────────
p = SRC / "parser.rs"
s = p.read_text()

if "Excavate { folder: String }" not in s:
    if "Seal { target: String }," not in s:
        print("  ERROR: Seal variant not found in parser.rs"); sys.exit(1)
    s = s.replace(
        "Seal { target: String },",
        "Seal { target: String },\n    Excavate { folder: String },"
    )
    print("  parser.rs: +Command::Excavate variant")
else:
    print("  parser.rs: variant already present")

if "Token::OpExcavate" not in s:
    marker = "Token::OpSeal"
    idx = s.find(marker)
    if idx == -1:
        print("  ERROR: Token::OpSeal arm not found in parser.rs"); sys.exit(1)
    arm = (
        '\n            Token::OpExcavate => {\n'
        '                self.advance();\n'
        '                match &self.current_token {\n'
        '                    Token::Identifier(folder) => {\n'
        '                        let cmd = Command::Excavate { folder: folder.clone() };\n'
        '                        self.advance();\n'
        '                        Ok(cmd)\n'
        '                    }\n'
        '                    _ => Err("Expected folder after excavate".to_string()),\n'
        '                }\n'
        '            }\n'
        '            '
    )
    s = s[:idx] + arm + s[idx:]
    print("  parser.rs: +Token::OpExcavate parse arm")
else:
    print("  parser.rs: parse arm already present")

p.write_text(s)

# ── main.rs ───────────────────────────────────────────────────────────────────
p = SRC / "main.rs"
s = p.read_text()

# Add mod excavate; if not present
if "mod excavate;" not in s:
    if "mod antibody;" not in s:
        print("  WARNING: mod antibody not found — prepending mod excavate")
        s = "mod excavate;\n" + s
    else:
        s = s.replace("mod antibody;", "mod excavate;\nmod antibody;")
    print("  main.rs: +mod excavate;")
else:
    print("  main.rs: mod excavate already declared")

# Add Command::Excavate handler
if "Command::Excavate" not in s:
    needle = "Command::Seal { target } => {"
    idx = s.find(needle)
    if idx == -1:
        print("  ERROR: Command::Seal arm not found in main.rs"); sys.exit(1)
    handler = (
        '\n                Command::Excavate { folder } => {\n'
        '                    match excavate::excavate(&folder) {\n'
        '                        Ok(r) => {\n'
        '                            println!("[EXCAVATE]: {}", r.folder);\n'
        '                            println!("ARTIFACTS={}", r.total);\n'
        '                            println!("REPORTS={}",   r.reports);\n'
        '                            println!("WAVES={}",     r.waves);\n'
        '                            println!("CONFIGS={}",   r.configs);\n'
        '                            println!("SOURCES={}",   r.sources);\n'
        '                            println!("OTHER={}",     r.other);\n'
        '                            std::fs::create_dir_all("reports").unwrap_or(());\n'
        '                            let slug = r.folder.replace(\'/\', "_").replace(\'.\', "_");\n'
        '                            let mp = format!("reports/sagco_excavate_{}.manifest", slug);\n'
        '                            std::fs::write(&mp, &r.manifest).unwrap_or(());\n'
        '                            println!("MANIFEST={}", mp);\n'
        '                        }\n'
        '                        Err(e) => {\n'
        '                            println!("STATUS=SAGCO_EXCAVATE_IO_FAIL");\n'
        '                            println!("ERROR={}", e);\n'
        '                        }\n'
        '                    }\n'
        '                }\n'
        '                '
    )
    s = s[:idx] + handler + s[idx:]
    print("  main.rs: +Command::Excavate handler (calls excavate::excavate)")
else:
    print("  main.rs: handler already present")

p.write_text(s)
print("")
print("STATUS=EXCAVATE_OPCODE_PATCHED")
PY

# ── Step 3: Build ─────────────────────────────────────────────────────────────
echo ""
echo "=== STEP 3: cargo build --bin sagco-core ==="
cargo build --bin sagco-core 2>&1 | grep -v "^warning" | tail -5
echo ""

# ── Step 4: Smoke test ────────────────────────────────────────────────────────
echo "=== STEP 4: smoke test ==="
cp "${REPO}/pipeline_excavate_l2.txt" .
cargo run --bin sagco-core -- pipeline_excavate_l2.txt 2>/dev/null \
  | grep -v "^warning"

echo ""
echo "evidence_excavate_l2.bin:"
cat evidence_excavate_l2.bin 2>/dev/null || echo "(not yet sealed — check pipeline output)"

echo ""
echo "STATUS=SAGCO_EXCAVATE_OPCODE_INSTALLED"
