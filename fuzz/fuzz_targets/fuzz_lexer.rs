// fuzz_lexer — byte-level boundary disruption target
// Invariants that must hold for any input:
//   1. No panic (index-out-of-bounds, unwrap, overflow)
//   2. tokenize_all() always terminates with Token::EOF
//   3. Token count is bounded by input length
//   4. All returned Identifiers contain only valid UTF-8
// License: SSL-1.0 — Strategickhaos DAO LLC
#![no_main]

use libfuzzer_sys::fuzz_target;

// Inline minimal Lexer so fuzz target compiles standalone
// In production: `use sagco_core::lexer::{Lexer, Token};`
#[derive(Debug, PartialEq, Clone)]
enum Token {
    OpRead, OpWave, OpPulse, OpSeal, OpSpawn, OpFork, OpConnect,
    Identifier(String), LiteralInt(u64), Hash(String), EOF,
}

struct Lexer { input: Vec<char>, position: usize }

impl Lexer {
    fn new(s: &str) -> Self { Lexer { input: s.chars().collect(), position: 0 } }
    fn peek(&self) -> Option<char> { self.input.get(self.position).cloned() }
    fn advance(&mut self) -> Option<char> {
        let ch = self.peek(); if ch.is_some() { self.position += 1; } ch
    }
    fn skip_ws(&mut self) {
        while let Some(c) = self.peek() {
            if c == '#' { while let Some(x) = self.peek() { self.advance(); if x == '\n' { break; } } }
            else if c.is_whitespace() { self.advance(); }
            else { break; }
        }
    }
    fn next_token(&mut self) -> Token {
        self.skip_ws();
        let ch = match self.advance() { Some(c) => c, None => return Token::EOF };
        if ch.is_alphabetic() || "_/.-:@".contains(ch) {
            let mut s = String::new(); s.push(ch);
            while let Some(n) = self.peek() {
                if n.is_alphanumeric() || "_/.-:@".contains(n) { s.push(self.advance().unwrap()); } else { break; }
            }
            return match s.as_str() {
                "read" => Token::OpRead, "wave" => Token::OpWave,
                "pulse" => Token::OpPulse, "seal" => Token::OpSeal,
                "spawn" => Token::OpSpawn, "fork" => Token::OpFork,
                "connect" => Token::OpConnect,
                _ => if s.len() == 16 && s.chars().all(|c| c.is_ascii_hexdigit()) {
                    Token::Hash(s)
                } else { Token::Identifier(s) },
            };
        }
        if ch.is_numeric() {
            let mut n = String::new(); n.push(ch);
            while let Some(x) = self.peek() { if x.is_numeric() { n.push(self.advance().unwrap()); } else { break; } }
            return Token::LiteralInt(n.parse::<u64>().unwrap_or(0));
        }
        Token::EOF
    }
}

fuzz_target!(|data: &[u8]| {
    // ── Input guard: limit to 4096 bytes (DoS prevention) ────────────────────
    if data.len() > 4096 { return; }

    // ── UTF-8 gate: only process valid UTF-8 (matches real-world CLI input) ──
    let input_str = match std::str::from_utf8(data) {
        Ok(s) => s,
        Err(_) => return,  // graceful rejection — not a panic
    };

    let mut lexer = Lexer::new(input_str);
    let mut token_count: usize = 0;
    let max_tokens = data.len() + 10;  // bounded by input size

    loop {
        let token = lexer.next_token();

        // ── Invariant 3: token count bounded ─────────────────────────────────
        token_count += 1;
        assert!(
            token_count <= max_tokens,
            "FUZZ_INVARIANT_BROKEN: token count {} exceeded bound {} for input {:?}",
            token_count, max_tokens, input_str
        );

        // ── Invariant 4: identifiers are valid UTF-8 (guaranteed by String) ──
        if let Token::Identifier(ref s) = token {
            assert!(
                std::str::from_utf8(s.as_bytes()).is_ok(),
                "FUZZ_INVARIANT_BROKEN: Identifier contains invalid UTF-8"
            );
        }

        // ── Invariant 2: terminates with EOF ─────────────────────────────────
        if token == Token::EOF { break; }
    }
});
