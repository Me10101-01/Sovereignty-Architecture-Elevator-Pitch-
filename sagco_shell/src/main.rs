// SAGCO-OS Terminal Embedded Engine
// Quote-preserving REPL with builtins + shell-fallback + antibody classifier
// License: SSL-1.0 — Strategickhaos DAO LLC
mod parser;
mod antibody;

use std::io::{self, Write};
use std::path::PathBuf;
use std::process::Command;

const BANNER: &str = r#"
===== SAGCO-OS TERMINAL EMBEDDED ENGINE =====
Parser   : quote-preserving (SHELL_TOKENIZATION_ANTIBODY immune)
Builtins : cd, pwd, exit
Fallback : pipes/redirects → sh -c
Antibody : 9 classifiers × 4 trajectories
Type 'exit' to quit
"#;

// Detect shell syntax that needs sh -c fallback
fn has_shell_syntax(input: &str) -> bool {
    input.contains('|')
        || input.contains('>')
        || input.contains("2>")
        || input.contains("&&")
        || input.contains("||")
        || input.contains(';')
}

// Handle shell builtins — returns Some(exit_ok) if handled, None if not a builtin
fn run_builtin(parts: &[String]) -> Option<bool> {
    match parts[0].as_str() {
        "cd" => {
            let target: PathBuf = if parts.len() > 1 {
                let raw = &parts[1];
                // expand leading ~ manually
                if raw == "~" || raw.starts_with("~/") {
                    let home = std::env::var("HOME").unwrap_or_else(|_| ".".into());
                    PathBuf::from(raw.replacen('~', &home, 1))
                } else {
                    PathBuf::from(raw)
                }
            } else {
                // cd with no arg → $HOME
                std::env::var("HOME")
                    .map(PathBuf::from)
                    .unwrap_or_else(|_| std::env::current_dir().unwrap_or_default())
            };

            match std::env::set_current_dir(&target) {
                Ok(_) => {}
                Err(e) => {
                    let msg = format!("{}: {}", target.display(), e);
                    let ab = antibody::classify_error(&msg);
                    eprintln!("cd: {}", msg);
                    eprintln!("ANTIBODY=SHELL_BUILTIN_ANTIBODY  TRAJECTORY=adaptation");
                    eprintln!("RECOVERY: {}", ab.recovery);
                }
            }
            Some(true)
        }
        "pwd" => {
            match std::env::current_dir() {
                Ok(cwd) => println!("{}", cwd.display()),
                Err(e) => eprintln!("pwd: {}", e),
            }
            Some(true)
        }
        _ => None,
    }
}

fn main() {
    println!("{}", BANNER);

    loop {
        // show cwd in prompt
        let cwd = std::env::current_dir()
            .map(|p| p.display().to_string())
            .unwrap_or_else(|_| "?".into());
        print!("sagco-os [{}] $ ", cwd);
        io::stdout().flush().unwrap();

        let mut input = String::new();
        match io::stdin().read_line(&mut input) {
            Ok(0) | Err(_) => break,
            Ok(_) => {}
        }

        let input = input.trim();
        if input.is_empty() {
            continue;
        }
        if input == "exit" || input == "quit" {
            println!("STATUS=SAGCO_SHELL_CLEAN_EXIT");
            break;
        }

        // ── pipe/redirect → sh -c fallback ───────────────────────────────────
        if has_shell_syntax(input) {
            match Command::new("sh").arg("-c").arg(input).output() {
                Ok(output) => {
                    io::stdout().write_all(&output.stdout).ok();
                    let stderr_text = String::from_utf8_lossy(&output.stderr);
                    if !stderr_text.trim().is_empty() {
                        eprint!("{}", stderr_text);
                    }
                    if !output.status.success() {
                        let code = output.status.code().unwrap_or(-1);
                        println!("EXIT_CODE={}", code);
                    }
                }
                Err(e) => eprintln!("sh -c error: {}", e),
            }
            continue;
        }

        // ── tokenize ─────────────────────────────────────────────────────────
        let parts = parser::parse_line(input);
        if parts.is_empty() {
            continue;
        }

        // ── builtins ─────────────────────────────────────────────────────────
        if run_builtin(&parts).is_some() {
            continue;
        }

        // ── external command ──────────────────────────────────────────────────
        match Command::new(&parts[0]).args(&parts[1..]).output() {
            Ok(output) => {
                io::stdout().write_all(&output.stdout).ok();
                let stderr_text = String::from_utf8_lossy(&output.stderr);
                if !stderr_text.trim().is_empty() {
                    eprint!("{}", stderr_text);
                    let ab = antibody::classify_error(&stderr_text);
                    eprintln!("ANTIBODY={}  TRAJECTORY={}", ab.name, ab.trajectory_str());
                    eprintln!("RECOVERY: {}", ab.recovery);
                }
                if !output.status.success() {
                    let code = output.status.code().unwrap_or(-1);
                    println!("EXIT_CODE={}", code);
                }
            }
            Err(e) => {
                let msg = e.to_string();
                // check if this was a builtin attempted externally
                let ab_name = if ["cd", "pwd", "export", "source", "alias", "unset",
                                   "set", "eval", "exec", "read", "trap", "umask"]
                    .contains(&parts[0].as_str())
                {
                    "SHELL_BUILTIN_ANTIBODY"
                } else {
                    antibody::classify_error(&msg).name
                };
                let ab = antibody::classify_error(&msg);
                println!("SAGCO_SHELL_ERROR={}", msg);
                println!("ANTIBODY={}  TRAJECTORY={}", ab_name, ab.trajectory_str());
                println!("RECOVERY: {}", ab.recovery);
            }
        }
    }
}
