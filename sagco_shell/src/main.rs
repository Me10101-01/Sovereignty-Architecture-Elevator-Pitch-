// SAGCO-OS Terminal Embedded Engine
// Quote-preserving REPL shell with antibody error classifier
// License: SSL-1.0 — Strategickhaos DAO LLC
mod parser;
mod antibody;

use std::io::{self, Write};
use std::process::Command;

const BANNER: &str = r#"
===== SAGCO-OS TERMINAL EMBEDDED ENGINE =====
Parser   : quote-preserving (SHELL_TOKENIZATION_ANTIBODY immune)
Antibody : 8 classifiers × 4 trajectories
Type 'exit' to quit | 'sagco help' for commands
"#;

fn main() {
    println!("{}", BANNER);

    loop {
        print!("sagco-os $ ");
        io::stdout().flush().unwrap();

        let mut input = String::new();
        match io::stdin().read_line(&mut input) {
            Ok(0) | Err(_) => break, // EOF or error — clean exit
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

        let parts = parser::parse_line(input);
        if parts.is_empty() {
            continue;
        }

        let command = &parts[0];
        let args = &parts[1..];

        match Command::new(command).args(args).output() {
            Ok(output) => {
                // write stdout
                io::stdout().write_all(&output.stdout).ok();

                // classify stderr if non-empty
                let stderr_text = String::from_utf8_lossy(&output.stderr);
                if !stderr_text.trim().is_empty() {
                    eprint!("{}", stderr_text);
                    let ab = antibody::classify_error(&stderr_text);
                    eprintln!("ANTIBODY={}  TRAJECTORY={}",
                              ab.name, ab.trajectory_str());
                    eprintln!("RECOVERY: {}", ab.recovery);
                }

                if !output.status.success() {
                    let code = output.status.code().unwrap_or(-1);
                    println!("EXIT_CODE={}", code);
                }
            }
            Err(e) => {
                let msg = e.to_string();
                let ab = antibody::classify_error(&msg);
                println!("SAGCO_SHELL_ERROR={}", msg);
                println!("ANTIBODY={}  TRAJECTORY={}",
                         ab.name, ab.trajectory_str());
                println!("RECOVERY: {}", ab.recovery);
            }
        }
    }
}
