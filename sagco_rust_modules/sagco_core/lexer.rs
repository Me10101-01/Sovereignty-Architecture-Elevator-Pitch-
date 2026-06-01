// SAGCO-Core Lexer — tokenizes the SAGCO instruction stream
// Bytecode format: wave <source> | pulse <node_id> | seal <target>
//                  spawn <plugin> | fork <count> | connect <endpoint>
// License: SSL-1.0 — Strategickhaos DAO LLC

#[derive(Debug, PartialEq, Clone)]
pub enum Token {
    // ── opcodes ──────────────────────────────────────────────────
    OpRead,      // read <file>       → open file, report BYTES (file I/O gate)
    OpWave,      // wave <source>     → Extract + Tokenize + Fingerprint
    OpPulse,     // pulse <node_id>   → Verify + Validate (EUR probe)
    OpSeal,      // seal <target>     → SHA256 evidence artifact
    OpSpawn,     // spawn <plugin>    → PluginRegistry::run()
    OpFork,      // fork <count>      → parallel antibody branches
    OpConnect,   // connect <endpoint>→ SagcoInput source binding

    // ── operands ─────────────────────────────────────────────────
    Identifier(String),  // file paths, plugin names, endpoints
    LiteralInt(u64),     // node IDs, port numbers, byte counts
    Hash(String),        // hex fingerprints (16-char like a364ca9f90356c85)

    EOF,
}

pub struct Lexer {
    input: Vec<char>,
    position: usize,
}

impl Lexer {
    pub fn new(input: &str) -> Self {
        Self {
            input: input.chars().collect(),
            position: 0,
        }
    }

    fn peek(&self) -> Option<char> {
        self.input.get(self.position).cloned()
    }

    fn advance(&mut self) -> Option<char> {
        let ch = self.peek();
        if ch.is_some() {
            self.position += 1;
        }
        ch
    }

    fn skip_whitespace(&mut self) {
        while let Some(ch) = self.peek() {
            if ch.is_whitespace() || ch == '#' {
                // skip comments to end of line
                if ch == '#' {
                    while let Some(c) = self.peek() {
                        self.advance();
                        if c == '\n' { break; }
                    }
                } else {
                    self.advance();
                }
            } else {
                break;
            }
        }
    }

    pub fn next_token(&mut self) -> Token {
        self.skip_whitespace();

        let ch = match self.advance() {
            Some(c) => c,
            None => return Token::EOF,
        };

        // ── identifier or opcode ──────────────────────────────────
        if ch.is_alphabetic() || ch == '_' || ch == '/' || ch == '.' || ch == '-' {
            let mut s = String::new();
            s.push(ch);
            while let Some(next) = self.peek() {
                if next.is_alphanumeric()
                    || next == '_' || next == '/' || next == '.'
                    || next == '-' || next == '@'
                {
                    s.push(self.advance().unwrap());
                } else {
                    break;
                }
            }
            return match s.as_str() {
                "read"    => Token::OpRead,
                "wave"    => Token::OpWave,
                "pulse"   => Token::OpPulse,
                "seal"    => Token::OpSeal,
                "spawn"   => Token::OpSpawn,
                "fork"    => Token::OpFork,
                "connect" => Token::OpConnect,
                _ => {
                    // 16-char hex = fingerprint hash
                    if s.len() == 16 && s.chars().all(|c| c.is_ascii_hexdigit()) {
                        Token::Hash(s)
                    } else {
                        Token::Identifier(s)
                    }
                }
            };
        }

        // ── integer literal ───────────────────────────────────────
        if ch.is_numeric() {
            let mut num = String::new();
            num.push(ch);
            while let Some(next) = self.peek() {
                if next.is_numeric() {
                    num.push(self.advance().unwrap());
                } else {
                    break;
                }
            }
            return Token::LiteralInt(num.parse::<u64>().unwrap_or(0));
        }

        Token::EOF
    }

    pub fn tokenize_all(&mut self) -> Vec<Token> {
        let mut tokens = Vec::new();
        loop {
            let t = self.next_token();
            if t == Token::EOF {
                tokens.push(Token::EOF);
                break;
            }
            tokens.push(t);
        }
        tokens
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lex_wave_opcode() {
        let mut l = Lexer::new("wave gcp_services.txt");
        assert_eq!(l.next_token(), Token::OpWave);
        assert_eq!(l.next_token(), Token::Identifier("gcp_services.txt".into()));
        assert_eq!(l.next_token(), Token::EOF);
    }

    #[test]
    fn lex_pulse_with_project_number() {
        let mut l = Lexer::new("pulse 793398609444");
        assert_eq!(l.next_token(), Token::OpPulse);
        assert_eq!(l.next_token(), Token::LiteralInt(793398609444));
    }

    #[test]
    fn lex_full_pipeline() {
        let src = "wave gcp_services.txt pulse 793398609444 seal evidence.bin";
        let mut l = Lexer::new(src);
        let tokens = l.tokenize_all();
        assert_eq!(tokens[0], Token::OpWave);
        assert_eq!(tokens[1], Token::Identifier("gcp_services.txt".into()));
        assert_eq!(tokens[2], Token::OpPulse);
        assert_eq!(tokens[3], Token::LiteralInt(793398609444));
        assert_eq!(tokens[4], Token::OpSeal);
        assert_eq!(tokens[5], Token::Identifier("evidence.bin".into()));
    }

    #[test]
    fn lex_extended_opcodes() {
        let mut l = Lexer::new("spawn gcloud_plugin fork 4 connect gcp");
        assert_eq!(l.next_token(), Token::OpSpawn);
        assert_eq!(l.next_token(), Token::Identifier("gcloud_plugin".into()));
        assert_eq!(l.next_token(), Token::OpFork);
        assert_eq!(l.next_token(), Token::LiteralInt(4));
        assert_eq!(l.next_token(), Token::OpConnect);
        assert_eq!(l.next_token(), Token::Identifier("gcp".into()));
    }

    #[test]
    fn lex_skips_comments() {
        let mut l = Lexer::new("wave src.txt # ingest artifact\npulse 123");
        assert_eq!(l.next_token(), Token::OpWave);
        assert_eq!(l.next_token(), Token::Identifier("src.txt".into()));
        assert_eq!(l.next_token(), Token::OpPulse);
        assert_eq!(l.next_token(), Token::LiteralInt(123));
    }
}
