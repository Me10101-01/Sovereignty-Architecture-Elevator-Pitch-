#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Install Lineage Opcode
# Adds lineage.rs module + lineage opcode to sagco-core.
# Requires: excavate opcode already installed (uses OpExcavate as anchor).
#
# Run from ~/downloads/sagco_rust_command_compiler:
#   bash ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-install-lineage-opcode.sh
set -euo pipefail

REPO="${HOME}/Sovereignty-Architecture-Elevator-Pitch-"
SRC="crates/sagco-core/src"

echo "SAGCO INSTALL LINEAGE OPCODE"
echo "WS=$(pwd)"

if [[ ! -f "Cargo.toml" ]] || [[ ! -d "${SRC}" ]]; then
  echo "ERROR: run from ~/downloads/sagco_rust_command_compiler"
  exit 1
fi

echo ""
echo "=== STEP 1: lineage.rs module ==="
cp "${REPO}/rust/sagco-core/lineage.rs" "${SRC}/lineage.rs"
echo "  COPIED: ${SRC}/lineage.rs"

echo ""
echo "=== STEP 2: patch lexer / parser / main ==="
python3 - <<'PY'
from pathlib import Path
import sys

SRC = Path("crates/sagco-core/src")

# ── lexer.rs ──────────────────────────────────────────────────────────────────
p = SRC / "lexer.rs"
s = p.read_text()

if "OpLineage" not in s:
    import re
    lines = s.splitlines(keepends=True)
    in_enum, depth, anchor_line = False, 0, None
    for i, line in enumerate(lines):
        if not in_enum:
            if re.search(r'\benum\s+Token\b', line) and '{' in line:
                in_enum, depth = True, line.count('{') - line.count('}')
        else:
            depth += line.count('{') - line.count('}')
            if 'OpExcavate' in line and '=>' not in line:
                anchor_line = i
            if depth <= 0:
                break
    if anchor_line is None:
        print("  ERROR: OpExcavate not found in enum — install excavate opcode first"); sys.exit(1)
    indent = re.match(r'^(\s*)', lines[anchor_line]).group(1)
    lines.insert(anchor_line + 1, f"{indent}OpLineage,\n")
    s = ''.join(lines)
    print("  lexer.rs: +OpLineage variant (enum-scoped insert)")
else:
    print("  lexer.rs: OpLineage already present")

if '"lineage"' not in s:
    s = s.replace(
        '"excavate" => Token::OpExcavate,',
        '"excavate" => Token::OpExcavate,\n            "lineage" => Token::OpLineage,'
    )
    print('  lexer.rs: +"lineage" keyword')
else:
    print("  lexer.rs: lineage keyword already present")

p.write_text(s)

# ── parser.rs ─────────────────────────────────────────────────────────────────
p = SRC / "parser.rs"
s = p.read_text()

if "Lineage { folder: String }" not in s:
    s = s.replace(
        "Excavate { folder: String },",
        "Excavate { folder: String },\n    Lineage { folder: String },"
    )
    print("  parser.rs: +Command::Lineage variant")
else:
    print("  parser.rs: variant already present")

if "Token::OpLineage" not in s:
    marker = "Token::OpExcavate"
    idx = s.find(marker)
    if idx == -1:
        print("  ERROR: Token::OpExcavate not found — install excavate opcode first")
        sys.exit(1)
    arm = (
        '\n            Token::OpLineage => {\n'
        '                self.advance();\n'
        '                match &self.current_token {\n'
        '                    Token::Identifier(folder) => {\n'
        '                        let cmd = Command::Lineage { folder: folder.clone() };\n'
        '                        self.advance();\n'
        '                        Ok(cmd)\n'
        '                    }\n'
        '                    _ => Err("Expected folder after lineage".to_string()),\n'
        '                }\n'
        '            }\n'
        '            '
    )
    s = s[:idx] + arm + s[idx:]
    print("  parser.rs: +Token::OpLineage parse arm")
else:
    print("  parser.rs: arm already present")

p.write_text(s)

# ── main.rs ───────────────────────────────────────────────────────────────────
p = SRC / "main.rs"
s = p.read_text()

if "mod lineage;" not in s:
    s = s.replace("mod excavate;", "mod excavate;\nmod lineage;")
    print("  main.rs: +mod lineage;")
else:
    print("  main.rs: mod lineage already declared")

if "Command::Lineage" not in s:
    needle = "Command::Excavate { folder } => {"
    idx = s.find(needle)
    if idx == -1:
        print("  ERROR: Command::Excavate arm not found — install excavate opcode first")
        sys.exit(1)
    handler = (
        '\n                Command::Lineage { folder } => {\n'
        '                    match lineage::trace(&folder) {\n'
        '                        Ok(result) => {\n'
        '                            let rpt = lineage::report(&result);\n'
        '                            print!("{}", rpt);\n'
        '                            std::fs::create_dir_all("reports").unwrap_or(());\n'
        '                            use std::time::{SystemTime, UNIX_EPOCH};\n'
        '                            let stamp = SystemTime::now()\n'
        '                                .duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();\n'
        '                            let mp = format!("reports/sagco_lineage_{}.manifest", stamp);\n'
        '                            std::fs::write(&mp, &rpt).unwrap_or(());\n'
        '                            println!("MANIFEST={}", mp);\n'
        '                        }\n'
        '                        Err(e) => eprintln!("lineage error: {}", e),\n'
        '                    }\n'
        '                }\n'
        '                '
    )
    s = s[:idx] + handler + s[idx:]
    print("  main.rs: +Command::Lineage handler")
else:
    print("  main.rs: handler already present")

p.write_text(s)
print("")
print("STATUS=LINEAGE_OPCODE_PATCHED")
PY

echo ""
echo "=== STEP 3: cargo build --bin sagco-core ==="
cargo build --bin sagco-core 2>&1 | grep -v "^warning" | tail -5

echo ""
echo "=== STEP 4: smoke test ==="
cp "${REPO}/pipeline_lineage_l1.txt" .
cargo run --bin sagco-core -- pipeline_lineage_l1.txt 2>/dev/null \
  | grep -v "^warning"

echo ""
echo "STATUS=SAGCO_LINEAGE_OPCODE_INSTALLED"
