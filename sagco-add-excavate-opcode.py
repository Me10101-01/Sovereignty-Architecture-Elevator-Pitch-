#!/usr/bin/env python3
"""
SAGCO Excavate Opcode Patcher — correct token names from live source.
Token::OpSeal, Token::OpExcavate, Token::Identifier, self.advance()

Run from ~/downloads/sagco_rust_command_compiler:
  python3 ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-add-excavate-opcode.py

Or paste the heredoc block directly in Termux.
"""
from pathlib import Path
import sys
import os

WS = Path(os.environ.get("SAGCO_WS",
    os.path.expanduser("~/downloads/sagco_rust_command_compiler")))
SRC = WS / "crates" / "sagco-core" / "src"

def patch_parser():
    p = SRC / "parser.rs"
    if not p.exists():
        print(f"  ERROR: not found: {p}"); return False
    s = p.read_text()

    if "Excavate { folder: String }" not in s:
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
            print("  ERROR: Token::OpSeal not found in parser.rs"); return False
        arm = '''
            Token::OpExcavate => {
                self.advance();
                match &self.current_token {
                    Token::Identifier(folder) => {
                        let cmd = Command::Excavate { folder: folder.clone() };
                        self.advance();
                        Ok(cmd)
                    }
                    _ => Err("Expected folder after excavate".to_string()),
                }
            }
'''
        s = s[:idx] + arm + "            " + s[idx:]
        print("  parser.rs: +Token::OpExcavate parse arm")
    else:
        print("  parser.rs: parse arm already present")

    p.write_text(s)
    return True

def patch_lexer():
    p = SRC / "lexer.rs"
    if not p.exists():
        print(f"  ERROR: not found: {p}"); return False
    s = p.read_text()

    if "OpExcavate" not in s:
        s = s.replace("OpSeal,", "OpSeal,\n    OpExcavate,")
        print("  lexer.rs: +OpExcavate token variant")
    else:
        print("  lexer.rs: OpExcavate already present")

    if '"excavate"' not in s:
        s = s.replace(
            '"seal" => Token::OpSeal,',
            '"seal" => Token::OpSeal,\n            "excavate" => Token::OpExcavate,'
        )
        print('  lexer.rs: +"excavate" keyword mapping')
    else:
        print("  lexer.rs: excavate keyword already present")

    p.write_text(s)
    return True

def patch_main():
    p = SRC / "main.rs"
    if not p.exists():
        print(f"  ERROR: not found: {p}"); return False
    s = p.read_text()

    if "Command::Excavate" not in s:
        needle = "Command::Seal { target } => {"
        idx = s.find(needle)
        if idx == -1:
            print("  ERROR: Command::Seal arm not found in main.rs"); return False
        arm = '''
                Command::Excavate { folder } => {
                    let mut artifacts = 0usize;
                    let mut reports   = 0usize;
                    match std::fs::read_dir(&folder) {
                        Ok(entries) => {
                            for entry in entries.flatten() {
                                artifacts += 1;
                                let name = entry.file_name().to_string_lossy().to_string();
                                if name.contains("report") || name.ends_with(".md") || name.ends_with(".txt") {
                                    reports += 1;
                                }
                            }
                            println!("[EXCAVATE]: {}", folder);
                            println!("ARTIFACTS={}", artifacts);
                            println!("REPORTS={}", reports);
                        }
                        Err(e) => {
                            println!("STATUS=SAGCO_EXCAVATE_IO_FAIL");
                            println!("ERROR={}", e);
                        }
                    }
                }
'''
        s = s[:idx] + arm + s[idx:]
        print("  main.rs: +Command::Excavate handler")
    else:
        print("  main.rs: handler already present")

    p.write_text(s)
    return True

def main():
    print("SAGCO ADD EXCAVATE OPCODE")
    print(f"WS={WS}")
    if not SRC.exists():
        print(f"ERROR: {SRC} not found"); sys.exit(1)

    ok = patch_lexer() and patch_parser() and patch_main()
    print()
    if ok:
        print("PATCHES APPLIED")
        print("STATUS=EXCAVATE_OPCODE_PATCHED")
    else:
        print("PARTIAL — check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()
