/// sagco_lex — SAGCO-Core Lexer CLI
///
/// Tokenizes any SAGCO-Core input and prints the typed token stream.
///
/// Usage:
///   sagco-lex "RB-001 4 27 1 0 N E UP"
///   sagco-lex "units rpmvolt P1 3200 0.0025"
///   sagco-lex "tri 0 0 5 10 0 5 5 10 5"

use sagco_core::lexer::lex;

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();

    if args.is_empty() {
        eprintln!("Usage: sagco-lex \"<input string>\"");
        std::process::exit(1);
    }

    let input = args.join(" ");

    match lex(&input) {
        Ok(tokens) => {
            println!("SAGCO-LEX TOKEN STREAM");
            println!("Input: {}", input);
            println!("{}", "─".repeat(40));
            for (i, tok) in tokens.iter().enumerate() {
                if format!("{:?}", tok) == "Eof" { break; }
                println!("[{:02}]  {:?}", i, tok);
            }
            println!("{}", "─".repeat(40));
            println!("STATUS=LEX_PASS");
        }
        Err(e) => {
            eprintln!("LEX_ERROR at position {}: unknown token '{}'", e.pos, e.token);
            std::process::exit(1);
        }
    }
}
