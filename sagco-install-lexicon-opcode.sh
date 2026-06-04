#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Install Lexicon Opcode
# Adds lexicon.rs + lexicon opcode to sagco-core.
# lexicon <folder> = unified artifact record: SAGCO_ID + TOKEN + TYPE +
#   ANCESTOR + DESCENDANTS + RUST_CALL + PATH + WEIGHT + STATUS
#
# This is the bridge between sagco-wing (brick enumeration) and
# lineage (ancestry graph) — the complete SAGCO-LEXICON.
#
# Run from ~/downloads/sagco_rust_command_compiler:
#   bash ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-install-lexicon-opcode.sh
set -euo pipefail

REPO="${HOME}/Sovereignty-Architecture-Elevator-Pitch-"
SRC="crates/sagco-core/src"

echo "SAGCO INSTALL LEXICON OPCODE"
echo "WS=$(pwd)"

if [[ ! -f "Cargo.toml" ]] || [[ ! -d "${SRC}" ]]; then
  echo "ERROR: run from ~/downloads/sagco_rust_command_compiler"
  exit 1
fi

echo ""
echo "=== STEP 1: lexicon.rs module ==="
cp "${REPO}/rust/sagco-core/lexicon.rs" "${SRC}/lexicon.rs"
echo "  COPIED: ${SRC}/lexicon.rs"

echo ""
echo "=== STEP 2: patch lexer / parser / main ==="
python3 - <<'PY'
from pathlib import Path
import sys, re

SRC = Path("crates/sagco-core/src")

# ── lexer.rs ──────────────────────────────────────────────────────────────────
p = SRC / "lexer.rs"
s = p.read_text()

if "OpLexicon" not in s:
    lines = s.splitlines(keepends=True)
    in_enum, depth, anchor_line = False, 0, None
    for i, line in enumerate(lines):
        if not in_enum:
            if re.search(r'\benum\s+Token\b', line) and '{' in line:
                in_enum, depth = True, line.count('{') - line.count('}')
        else:
            depth += line.count('{') - line.count('}')
            for known in ['OpScaffold', 'OpDrive', 'OpWeight', 'OpLineage', 'OpExcavate']:
                if known in line and '=>' not in line:
                    anchor_line = i
            if depth <= 0:
                break
    if anchor_line is None:
        print("  ERROR: no anchor opcode found in Token enum"); sys.exit(1)
    indent = re.match(r'^(\s*)', lines[anchor_line]).group(1)
    lines.insert(anchor_line + 1, f"{indent}OpLexicon,\n")
    s = ''.join(lines)
    print("  lexer.rs: +OpLexicon variant")
else:
    print("  lexer.rs: OpLexicon already present")

if '"lexicon"' not in s:
    s = s.replace(
        '"excavate" => Token::OpExcavate,',
        '"excavate" => Token::OpExcavate,\n            "lexicon" => Token::OpLexicon,'
    )
    print('  lexer.rs: +"lexicon" keyword')
else:
    print("  lexer.rs: lexicon keyword already present")
p.write_text(s)

# ── parser.rs ─────────────────────────────────────────────────────────────────
p = SRC / "parser.rs"
s = p.read_text()

if "Lexicon { folder: String }" not in s:
    s = s.replace(
        "Excavate { folder: String },",
        "Excavate { folder: String },\n    Lexicon { folder: String },"
    )
    print("  parser.rs: +Command::Lexicon variant")
else:
    print("  parser.rs: variant already present")

if "Token::OpLexicon" not in s:
    marker = "Token::OpExcavate"
    idx = s.find(marker)
    if idx == -1:
        print("  ERROR: Token::OpExcavate not found"); sys.exit(1)
    arm = (
        '\n            Token::OpLexicon => {\n'
        '                self.advance();\n'
        '                match &self.current_token {\n'
        '                    Token::Identifier(folder) => {\n'
        '                        let cmd = Command::Lexicon { folder: folder.clone() };\n'
        '                        self.advance();\n'
        '                        Ok(cmd)\n'
        '                    }\n'
        '                    _ => Err("Expected folder after lexicon".to_string()),\n'
        '                }\n'
        '            }\n'
        '            '
    )
    s = s[:idx] + arm + s[idx:]
    print("  parser.rs: +Token::OpLexicon parse arm")
else:
    print("  parser.rs: arm already present")
p.write_text(s)

# ── main.rs ───────────────────────────────────────────────────────────────────
p = SRC / "main.rs"
s = p.read_text()

if "mod lexicon;" not in s:
    s = s.replace("mod excavate;", "mod excavate;\nmod lexicon;")
    print("  main.rs: +mod lexicon;")
else:
    print("  main.rs: mod lexicon already declared")

if "Command::Lexicon" not in s:
    needle = "Command::Excavate { folder } => {"
    idx = s.find(needle)
    if idx == -1:
        print("  ERROR: Command::Excavate arm not found"); sys.exit(1)
    handler = (
        '\n                Command::Lexicon { folder } => {\n'
        '                    let result = lexicon::build(&folder);\n'
        '                    print!("{}", lexicon::report(&result));\n'
        '                    if let Ok(ref r) = result {\n'
        '                        std::fs::create_dir_all("reports").unwrap_or(());\n'
        '                        use std::time::{SystemTime, UNIX_EPOCH};\n'
        '                        let stamp = SystemTime::now()\n'
        '                            .duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();\n'
        '                        let mp = format!("reports/sagco_lexicon_{}.manifest", stamp);\n'
        '                        std::fs::write(&mp, &r.manifest).unwrap_or(());\n'
        '                        println!("MANIFEST={}", mp);\n'
        '                        println!("TOTAL_BRICKS={}", r.total);\n'
        '                    }\n'
        '                }\n'
        '                '
    )
    s = s[:idx] + handler + s[idx:]
    print("  main.rs: +Command::Lexicon handler")
else:
    print("  main.rs: handler already present")
p.write_text(s)
print("")
print("STATUS=LEXICON_OPCODE_PATCHED")
PY

echo ""
echo "=== STEP 3: cargo build ==="
cargo build --bin sagco-core 2>&1 | grep -v "^warning" | tail -5

echo ""
echo "=== STEP 4: smoke test ==="
cat > pipeline_lexicon_l1.txt << 'EOF'
lexicon crates
lexicon inputs
seal evidence_lexicon_l1.bin
EOF

cargo run --bin sagco-core -- pipeline_lexicon_l1.txt 2>/dev/null | grep -v "^warning"

echo ""
echo "=== STEP 5: inspect lexicon manifest ==="
ls -lh reports/sagco_lexicon_*.manifest 2>/dev/null | tail -1
cat reports/sagco_lexicon_*.manifest 2>/dev/null | head -40

echo ""
echo "STATUS=SAGCO_LEXICON_OPCODE_INSTALLED"
