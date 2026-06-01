// SAGCO Shell Parser — quote-preserving tokenizer
// Fixes SHELL_TOKENIZATION_ANTIBODY: "file with spaces" stays as one token
// License: SSL-1.0 — Strategickhaos DAO LLC

pub fn parse_line(input: &str) -> Vec<String> {
    let mut tokens = Vec::new();
    let mut current = String::new();
    let mut in_double = false;
    let mut in_single = false;

    let mut chars = input.chars().peekable();
    while let Some(c) = chars.next() {
        match c {
            '"' if !in_single => in_double = !in_double,
            '\'' if !in_double => in_single = !in_single,
            '\\' if in_double => {
                // escape inside double-quotes: consume next char literally
                if let Some(next) = chars.next() {
                    current.push(next);
                }
            }
            ' ' | '\t' if !in_double && !in_single => {
                if !current.is_empty() {
                    tokens.push(current.clone());
                    current.clear();
                }
            }
            _ => current.push(c),
        }
    }
    if !current.is_empty() {
        tokens.push(current);
    }
    tokens
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn spaced_filename_stays_one_token() {
        // "sagco wave <quoted>" → 3 tokens: [sagco, wave, full-filename]
        let t = parse_line(r#"sagco wave "SAGCO Computable Reality Engineering Blueprint- v1.pdf""#);
        assert_eq!(t.len(), 3);
        assert_eq!(t[0], "sagco");
        assert_eq!(t[1], "wave");
        assert_eq!(t[2], "SAGCO Computable Reality Engineering Blueprint- v1.pdf");
    }

    #[test]
    fn single_quotes_preserved() {
        let t = parse_line("exiftool 'file with spaces.pdf'");
        assert_eq!(t.len(), 2);
        assert_eq!(t[1], "file with spaces.pdf");
    }

    #[test]
    fn normal_args_split() {
        let t = parse_line("cargo build --release");
        assert_eq!(t, vec!["cargo", "build", "--release"]);
    }

    #[test]
    fn empty_input() {
        assert!(parse_line("").is_empty());
        assert!(parse_line("   ").is_empty());
    }
}
