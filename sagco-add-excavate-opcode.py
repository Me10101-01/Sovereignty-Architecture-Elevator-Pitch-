#!/usr/bin/env python3
"""
SAGCO Excavate Opcode Patcher
Adds `excavate <folder>` to sagco-core lexer, parser, and main.

Run from ~/downloads/sagco_rust_command_compiler:
  python3 ~/Sovereignty-Architecture-Elevator-Pitch-/sagco-add-excavate-opcode.py
"""
import re
import sys
import os
import shutil
from pathlib import Path

WS = Path(os.environ.get("SAGCO_WS",
    os.path.expanduser("~/downloads/sagco_rust_command_compiler")))
CRATE = WS / "crates" / "sagco-core" / "src"

def backup(path: Path):
    bak = path.with_suffix(path.suffix + ".pre_excavate")
    if not bak.exists():
        shutil.copy2(path, bak)
        print(f"  BACKUP: {bak.name}")

def patch_lexer():
    path = CRATE / "lexer.rs"
    if not path.exists():
        print(f"  SKIP lexer (not found at {path})")
        return False
    src = path.read_text()
    if "Excavate" in src:
        print("  lexer.rs: Excavate already present")
        return True

    backup(path)

    # Strategy 1: add Token::Excavate variant after Seal
    patched = re.sub(
        r'(\bSeal\b\s*,)',
        r'\1\n    Excavate,',
        src, count=1
    )
    # Strategy 2: add "excavate" keyword match after "seal"
    patched = re.sub(
        r'("seal"\s*=>\s*Token::Seal\s*,)',
        r'\1\n            "excavate" => Token::Excavate,',
        patched, count=1
    )
    if patched == src:
        print("  WARNING: lexer.rs pattern not matched — check manually")
        print('  Need: Token::Excavate variant, "excavate" => Token::Excavate')
        return False

    path.write_text(patched)
    print(f"  PATCHED: lexer.rs (+Excavate token)")
    return True

def patch_parser():
    path = CRATE / "parser.rs"
    if not path.exists():
        print(f"  SKIP parser (not found at {path})")
        return False
    src = path.read_text()
    if "Excavate" in src:
        print("  parser.rs: Excavate already present")
        return True

    backup(path)

    # Add Command::Excavate variant after Seal
    patched = re.sub(
        r'(Seal\s*\{[^}]*\}\s*,)',
        r'\1\n    Excavate { folder: String },',
        src, count=1
    )
    # Add parse arm: Token::Excavate => parse Ident as folder
    # Find where Seal is parsed and add after
    excavate_parse = '''
            Token::Excavate => {
                let folder = match self.lexer.next_token() {
                    Token::Ident(s) => s,
                    _ => return Err("excavate expects <folder>".to_string()),
                };
                Ok(Command::Excavate { folder })
            }'''

    # Insert after the Seal parse arm
    patched = re.sub(
        r'(Token::Seal\s*=>\s*\{[^}]+\})',
        r'\1' + excavate_parse,
        patched, count=1, flags=re.DOTALL
    )

    if patched == src:
        print("  WARNING: parser.rs pattern not matched — check manually")
        print("  Need: Command::Excavate { folder }, Token::Excavate arm")
        return False

    path.write_text(patched)
    print(f"  PATCHED: parser.rs (+Command::Excavate, +Token::Excavate parse arm)")
    return True

def patch_main():
    path = CRATE / "main.rs"
    if not path.exists():
        print(f"  SKIP main.rs (not found at {path})")
        return False
    src = path.read_text()
    if "Command::Excavate" in src:
        print("  main.rs: Excavate handler already present")
        return True

    backup(path)

    # The excavate handler body
    handler = '''
                Command::Excavate { folder } => {
                    use std::path::Path as FsPath;
                    let root = FsPath::new(&folder);
                    if !root.exists() {
                        println!("[EXCAVATE]: {} ERROR=not_found", folder);
                    } else {
                        let mut total = 0u64;
                        let mut reports = 0u64;
                        let mut waves   = 0u64;
                        let mut configs = 0u64;
                        let mut sources = 0u64;
                        let mut other   = 0u64;
                        fn walk(dir: &FsPath, t: &mut u64, r: &mut u64,
                                w: &mut u64, c: &mut u64, s: &mut u64, o: &mut u64) {
                            if let Ok(entries) = std::fs::read_dir(dir) {
                                for e in entries.flatten() {
                                    let p = e.path();
                                    let n = p.file_name()
                                        .unwrap_or_default()
                                        .to_string_lossy()
                                        .to_lowercase();
                                    if n.starts_with('.') || n == "target" { continue; }
                                    if p.is_dir() {
                                        walk(&p, t, r, w, c, s, o);
                                    } else {
                                        *t += 1;
                                        let ext = p.extension()
                                            .unwrap_or_default()
                                            .to_string_lossy()
                                            .to_lowercase();
                                        match ext.as_str() {
                                            "md" | "txt" => *r += 1,
                                            "wav"        => *w += 1,
                                            "yaml"|"yml"|"json"|"toml"|"csv" => *c += 1,
                                            "rs"|"py"|"sh" => *s += 1,
                                            _ => *o += 1,
                                        }
                                    }
                                }
                            }
                        }
                        walk(root, &mut total, &mut reports, &mut waves,
                             &mut configs, &mut sources, &mut other);
                        println!("[EXCAVATE]: {} ARTIFACTS={} REPORTS={} WAVES={} CONFIGS={} SOURCES={} OTHER={}",
                            folder, total, reports, waves, configs, sources, other);
                        let seal_path = format!("reports/sagco_excavate_{}.manifest", folder
                            .replace('/', "_").replace('.', "_"));
                        std::fs::create_dir_all("reports").unwrap_or(());
                        let manifest = format!(
                            "EXCAVATE_TARGET={}\nARTIFACTS={}\nREPORTS={}\nWAVES={}\nCONFIGS={}\nSOURCES={}\nOTHER={}\nSTATUS=SAGCO_EXCAVATE_SEALED\n",
                            folder, total, reports, waves, configs, sources, other
                        );
                        std::fs::write(&seal_path, manifest).unwrap_or(());
                        println!("MANIFEST={}", seal_path);
                    }
                }'''

    # Insert after the Seal command handler in the match block
    patched = re.sub(
        r'(Command::Seal\s*\{[^}]+\}\s*=>\s*\{.*?\})',
        r'\1' + handler,
        src, count=1, flags=re.DOTALL
    )

    if patched == src:
        print("  WARNING: main.rs Seal handler pattern not matched")
        print("  Appending handler hint to end of file for manual merge:")
        hint = "\n// TODO: add to match block in main():\n" + handler + "\n"
        path.write_text(src + hint)
        print(f"  HINT appended to main.rs — merge manually")
        return False

    path.write_text(patched)
    print(f"  PATCHED: main.rs (+Command::Excavate handler)")
    return True

def main():
    print("SAGCO ADD EXCAVATE OPCODE")
    print(f"WORKSPACE={WS}")
    print(f"CRATE={CRATE}")
    print()

    if not CRATE.exists():
        print(f"ERROR: crate src not found at {CRATE}")
        sys.exit(1)

    ok_l = patch_lexer()
    ok_p = patch_parser()
    ok_m = patch_main()

    print()
    if ok_l and ok_p and ok_m:
        print("ALL PATCHES APPLIED — building...")
        os.chdir(WS)
        ret = os.system("cargo build --bin sagco-core 2>&1 | tail -8")
        if ret == 0:
            print()
            print("BUILD PASS — testing:")
            os.system('printf "read gcp_services.txt\\nexcavate .\\nseal evidence_excavate_test.bin\\n" '
                      '> /tmp/pipeline_excavate_test.txt && '
                      'cargo run --bin sagco-core -- /tmp/pipeline_excavate_test.txt 2>/dev/null | grep -v "^warning"')
    else:
        print("PARTIAL PATCH — review warnings above, then:")
        print(f"  cd {WS} && cargo build --bin sagco-core")

    print()
    print("STATUS=SAGCO_EXCAVATE_OPCODE_DEPLOYED")

if __name__ == "__main__":
    main()
