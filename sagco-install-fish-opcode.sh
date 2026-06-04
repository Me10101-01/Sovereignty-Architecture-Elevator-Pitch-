#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Install Fish Opcode
# Adds fish.rs + fish opcode to sagco-core.
# fish performs a recursive filesystem search (deeper than excavate).
# Requires: excavate opcode already installed.
#
# Run from ~/downloads/sagco_rust_command_compiler:
#   bash ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-install-fish-opcode.sh
set -euo pipefail

REPO="${HOME}/Sovereignty-Architecture-Elevator-Pitch-"
SRC="crates/sagco-core/src"

echo "SAGCO INSTALL FISH OPCODE"
echo "WS=$(pwd)"

if [[ ! -f "Cargo.toml" ]] || [[ ! -d "${SRC}" ]]; then
  echo "ERROR: run from ~/downloads/sagco_rust_command_compiler"
  exit 1
fi

echo ""
echo "=== STEP 1: fish.rs module ==="
cp "${REPO}/rust/sagco-core/fish.rs" "${SRC}/fish.rs"
echo "  COPIED: ${SRC}/fish.rs"

echo ""
echo "=== STEP 2: patch lexer / parser / main ==="
python3 - <<'PY'
from pathlib import Path
import sys, re

SRC = Path("crates/sagco-core/src")

# ── lexer.rs ──────────────────────────────────────────────────────────────────
p = SRC / "lexer.rs"
s = p.read_text()

if "OpFish" not in s:
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
    lines.insert(anchor_line + 1, f"{indent}OpFish,\n")
    s = ''.join(lines)
    print("  lexer.rs: +OpFish variant (enum-scoped insert)")
else:
    print("  lexer.rs: OpFish already present")

if '"fish"' not in s:
    s = s.replace(
        '"excavate" => Token::OpExcavate,',
        '"excavate" => Token::OpExcavate,\n            "fish" => Token::OpFish,'
    )
    print('  lexer.rs: +"fish" keyword')
else:
    print("  lexer.rs: fish keyword already present")

p.write_text(s)

# ── parser.rs ─────────────────────────────────────────────────────────────────
p = SRC / "parser.rs"
s = p.read_text()

if "Fish { folder: String }" not in s:
    s = s.replace(
        "Excavate { folder: String },",
        "Excavate { folder: String },\n    Fish { folder: String },"
    )
    print("  parser.rs: +Command::Fish variant")
else:
    print("  parser.rs: variant already present")

if "Token::OpFish" not in s:
    marker = "Token::OpExcavate"
    idx = s.find(marker)
    if idx == -1:
        print("  ERROR: Token::OpExcavate not found — install excavate opcode first")
        sys.exit(1)
    arm = (
        '\n            Token::OpFish => {\n'
        '                self.advance();\n'
        '                match &self.current_token {\n'
        '                    Token::Identifier(folder) => {\n'
        '                        let cmd = Command::Fish { folder: folder.clone() };\n'
        '                        self.advance();\n'
        '                        Ok(cmd)\n'
        '                    }\n'
        '                    _ => Err("Expected folder after fish".to_string()),\n'
        '                }\n'
        '            }\n'
        '            '
    )
    s = s[:idx] + arm + s[idx:]
    print("  parser.rs: +Token::OpFish parse arm")
else:
    print("  parser.rs: arm already present")

p.write_text(s)

# ── main.rs ───────────────────────────────────────────────────────────────────
p = SRC / "main.rs"
s = p.read_text()

if "mod fish;" not in s:
    s = s.replace("mod excavate;", "mod excavate;\nmod fish;")
    print("  main.rs: +mod fish;")
else:
    print("  main.rs: mod fish already declared")

if "Command::Fish" not in s:
    needle = "Command::Excavate { folder } => {"
    idx = s.find(needle)
    if idx == -1:
        print("  ERROR: Command::Excavate arm not found — install excavate opcode first")
        sys.exit(1)
    handler = (
        '\n                Command::Fish { folder } => {\n'
        '                    let result = fish::search(&folder);\n'
        '                    print!("{}", fish::report(&result));\n'
        '                    if let Ok(ref r) = result {\n'
        '                        std::fs::create_dir_all("reports").unwrap_or(());\n'
        '                        use std::time::{SystemTime, UNIX_EPOCH};\n'
        '                        let stamp = SystemTime::now()\n'
        '                            .duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();\n'
        '                        let mp = format!("reports/sagco_fish_{}.manifest", stamp);\n'
        '                        std::fs::write(&mp, &r.manifest).unwrap_or(());\n'
        '                        println!("MANIFEST={}", mp);\n'
        '                    }\n'
        '                }\n'
        '                '
    )
    s = s[:idx] + handler + s[idx:]
    print("  main.rs: +Command::Fish handler")
else:
    print("  main.rs: handler already present")

p.write_text(s)
print("")
print("STATUS=FISH_OPCODE_PATCHED")
PY

echo ""
echo "=== STEP 3: cargo build --bin sagco-core ==="
cargo build --bin sagco-core 2>&1 | grep -v "^warning" | tail -5

echo ""
echo "=== STEP 4: smoke test ==="
# Use the workspace root as the search target
cargo run --bin sagco-core -- pipeline_fish_l2.txt 2>/dev/null \
  | grep -v "^warning" || true

echo ""
echo "STATUS=SAGCO_FISH_OPCODE_INSTALLED"
