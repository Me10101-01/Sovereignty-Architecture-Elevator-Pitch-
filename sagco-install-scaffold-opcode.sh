#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Install Scaffold Opcode
# Adds scaffold.rs + scaffold opcode to sagco-core.
# scaffold <name> generates a full deployable agent repository in sagco_fleet/agents/.
# Requires: excavate + lineage + weight opcodes already installed.
#
# Run from ~/downloads/sagco_rust_command_compiler:
#   bash ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-install-scaffold-opcode.sh
set -euo pipefail

REPO="${HOME}/Sovereignty-Architecture-Elevator-Pitch-"
SRC="crates/sagco-core/src"

echo "SAGCO INSTALL SCAFFOLD OPCODE"
echo "WS=$(pwd)"

if [[ ! -f "Cargo.toml" ]] || [[ ! -d "${SRC}" ]]; then
  echo "ERROR: run from ~/downloads/sagco_rust_command_compiler"
  exit 1
fi

echo ""
echo "=== STEP 1: scaffold.rs module ==="
cp "${REPO}/rust/sagco-core/scaffold.rs" "${SRC}/scaffold.rs"
echo "  COPIED: ${SRC}/scaffold.rs"

echo ""
echo "=== STEP 2: patch lexer / parser / main ==="
python3 - <<'PY'
from pathlib import Path
import sys, re

SRC = Path("crates/sagco-core/src")

# ── lexer.rs ──────────────────────────────────────────────────────────────────
p = SRC / "lexer.rs"
s = p.read_text()

if "OpScaffold" not in s:
    lines = s.splitlines(keepends=True)
    in_enum, depth, anchor_line = False, 0, None
    for i, line in enumerate(lines):
        if not in_enum:
            if re.search(r'\benum\s+Token\b', line) and '{' in line:
                in_enum, depth = True, line.count('{') - line.count('}')
        else:
            depth += line.count('{') - line.count('}')
            # anchor after the last known opcode in the enum
            for known in ['OpDrive', 'OpWeight', 'OpLineage', 'OpExcavate']:
                if known in line and '=>' not in line:
                    anchor_line = i
            if depth <= 0:
                break
    if anchor_line is None:
        print("  ERROR: no known anchor opcode found in enum — install earlier opcodes first"); sys.exit(1)
    indent = re.match(r'^(\s*)', lines[anchor_line]).group(1)
    lines.insert(anchor_line + 1, f"{indent}OpScaffold,\n")
    s = ''.join(lines)
    print("  lexer.rs: +OpScaffold variant (enum-scoped insert)")
else:
    print("  lexer.rs: OpScaffold already present")

if '"scaffold"' not in s:
    # Insert after the last known keyword mapping
    for kw in ['"drive"', '"weight"', '"lineage"', '"excavate"']:
        if kw in s:
            old = f'{kw} => Token::Op{kw[1:-1].capitalize()},'
            # find the actual line
            break
    # Simple append near excavate
    s = s.replace(
        '"excavate" => Token::OpExcavate,',
        '"excavate" => Token::OpExcavate,\n            "scaffold" => Token::OpScaffold,'
    )
    print('  lexer.rs: +"scaffold" keyword')
else:
    print("  lexer.rs: scaffold keyword already present")

p.write_text(s)

# ── parser.rs ─────────────────────────────────────────────────────────────────
p = SRC / "parser.rs"
s = p.read_text()

if "Scaffold { name: String }" not in s:
    s = s.replace(
        "Excavate { folder: String },",
        "Excavate { folder: String },\n    Scaffold { name: String },"
    )
    print("  parser.rs: +Command::Scaffold variant")
else:
    print("  parser.rs: variant already present")

if "Token::OpScaffold" not in s:
    marker = "Token::OpExcavate"
    idx = s.find(marker)
    if idx == -1:
        print("  ERROR: Token::OpExcavate not found — install excavate opcode first")
        sys.exit(1)
    arm = (
        '\n            Token::OpScaffold => {\n'
        '                self.advance();\n'
        '                match &self.current_token {\n'
        '                    Token::Identifier(name) => {\n'
        '                        let cmd = Command::Scaffold { name: name.clone() };\n'
        '                        self.advance();\n'
        '                        Ok(cmd)\n'
        '                    }\n'
        '                    _ => Err("Expected agent name after scaffold".to_string()),\n'
        '                }\n'
        '            }\n'
        '            '
    )
    s = s[:idx] + arm + s[idx:]
    print("  parser.rs: +Token::OpScaffold parse arm")
else:
    print("  parser.rs: arm already present")

p.write_text(s)

# ── main.rs ───────────────────────────────────────────────────────────────────
p = SRC / "main.rs"
s = p.read_text()

if "mod scaffold;" not in s:
    s = s.replace("mod excavate;", "mod excavate;\nmod scaffold;")
    print("  main.rs: +mod scaffold;")
else:
    print("  main.rs: mod scaffold already declared")

if "Command::Scaffold" not in s:
    needle = "Command::Excavate { folder } => {"
    idx = s.find(needle)
    if idx == -1:
        print("  ERROR: Command::Excavate arm not found — install excavate opcode first")
        sys.exit(1)
    handler = (
        '\n                Command::Scaffold { name } => {\n'
        '                    let result = scaffold::scaffold(&name);\n'
        '                    print!("{}", scaffold::report(&result));\n'
        '                    if let Ok(ref r) = result {\n'
        '                        std::fs::create_dir_all("reports").unwrap_or(());\n'
        '                        use std::time::{SystemTime, UNIX_EPOCH};\n'
        '                        let stamp = SystemTime::now()\n'
        '                            .duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();\n'
        '                        let mp = format!("reports/sagco_scaffold_{}.manifest", stamp);\n'
        '                        std::fs::write(&mp, &r.manifest).unwrap_or(());\n'
        '                        println!("MANIFEST={}", mp);\n'
        '                        // ERU fleet report\n'
        '                        let eru = scaffold::eru_report("sagco_fleet");\n'
        '                        print!("{}", eru);\n'
        '                    }\n'
        '                }\n'
        '                '
    )
    s = s[:idx] + handler + s[idx:]
    print("  main.rs: +Command::Scaffold handler")
else:
    print("  main.rs: handler already present")

p.write_text(s)
print("")
print("STATUS=SCAFFOLD_OPCODE_PATCHED")
PY

echo ""
echo "=== STEP 3: cargo build --bin sagco-core ==="
cargo build --bin sagco-core 2>&1 | grep -v "^warning" | tail -5

echo ""
echo "=== STEP 4: smoke test — scaffold excavate-agent ==="
cp "${REPO}/pipeline_scaffold_l1.txt" . 2>/dev/null || cat > pipeline_scaffold_l1.txt <<'EOF'
scaffold excavate-agent
scaffold deploy-agent
scaffold antibody-agent
seal evidence_scaffold_l1.bin
EOF

cargo run --bin sagco-core -- pipeline_scaffold_l1.txt 2>/dev/null \
  | grep -v "^warning"

echo ""
echo "=== STEP 5: show scaffolded tree ==="
if command -v tree >/dev/null 2>&1; then
  tree sagco_fleet/agents/ 2>/dev/null | head -40 || true
else
  find sagco_fleet/agents/ -type f 2>/dev/null | head -30 || true
fi

echo ""
echo "STATUS=SAGCO_SCAFFOLD_OPCODE_INSTALLED"
