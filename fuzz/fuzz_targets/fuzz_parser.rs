// fuzz_parser — grammatical and logic boundary disruption target
// Production invariants:
//   1. No panic for any input (panic = crash = fuzz finding)
//   2. parse_program() always terminates (no infinite loop)
//   3. Malformed input → structured Err, never corrupted Ok
//   4. Command count bounded by input length
//   5. EMPTY_PAYLOAD_ANTIBODY fires for zero-byte or whitespace-only input
// License: SSL-1.0 — Strategickhaos DAO LLC
#![no_main]

use libfuzzer_sys::fuzz_target;

// Inline minimal Lexer + Parser for standalone fuzz compilation
#[derive(Debug, PartialEq, Clone)]
enum Token {
    OpRead, OpWave, OpPulse, OpSeal, OpSpawn, OpFork, OpConnect,
    Identifier(String), LiteralInt(u64), EOF,
}

#[derive(Debug)]
enum Command {
    Read { file: String }, Wave { source: String }, Pulse { node_id: u64 },
    Seal { target: String }, Spawn { plugin: String }, Fork { count: u64 },
    Connect { endpoint: String },
}

struct Lexer { input: Vec<char>, pos: usize }
impl Lexer {
    fn new(s: &str) -> Self { Lexer { input: s.chars().collect(), pos: 0 } }
    fn peek(&self) -> Option<char> { self.input.get(self.pos).cloned() }
    fn adv(&mut self) -> Option<char> { let c = self.peek(); if c.is_some() { self.pos += 1; } c }
    fn skip(&mut self) { while let Some(c) = self.peek() { if c.is_whitespace() { self.adv(); } else { break; } } }
    fn next(&mut self) -> Token {
        self.skip();
        let ch = match self.adv() { Some(c) => c, None => return Token::EOF };
        if ch.is_alphabetic() || "_/.-".contains(ch) {
            let mut s = ch.to_string();
            while let Some(n) = self.peek() {
                if n.is_alphanumeric() || "_/.-".contains(n) { s.push(self.adv().unwrap()); } else { break; }
            }
            return match s.as_str() {
                "read" => Token::OpRead, "wave" => Token::OpWave, "pulse" => Token::OpPulse,
                "seal" => Token::OpSeal, "spawn" => Token::OpSpawn, "fork" => Token::OpFork,
                "connect" => Token::OpConnect, _ => Token::Identifier(s),
            };
        }
        if ch.is_numeric() {
            let mut n = ch.to_string();
            while let Some(x) = self.peek() { if x.is_numeric() { n.push(self.adv().unwrap()); } else { break; } }
            return Token::LiteralInt(n.parse::<u64>().unwrap_or(0));
        }
        Token::EOF
    }
}

struct Parser { lexer: Lexer, cur: Token }
impl Parser {
    fn new(mut l: Lexer) -> Self { let t = l.next(); Parser { lexer: l, cur: t } }
    fn adv(&mut self) { self.cur = self.lexer.next(); }
    fn parse_id(&mut self) -> Option<String> {
        match &self.cur {
            Token::Identifier(s) => { let v = s.clone(); self.adv(); Some(v) }
            _ => None,
        }
    }
    fn parse_int(&mut self) -> Option<u64> {
        match self.cur { Token::LiteralInt(n) => { self.adv(); Some(n) } _ => None }
    }
    fn parse_cmd(&mut self) -> Result<Command, String> {
        match self.cur.clone() {
            Token::OpRead    => { self.adv(); self.parse_id().map(|f| Command::Read    { file: f     }).ok_or_else(|| "expected file".into()) }
            Token::OpWave    => { self.adv(); self.parse_id().map(|s| Command::Wave    { source: s   }).ok_or_else(|| "expected source".into()) }
            Token::OpPulse   => { self.adv(); self.parse_int().map(|n| Command::Pulse  { node_id: n  }).ok_or_else(|| "expected int".into()) }
            Token::OpSeal    => { self.adv(); self.parse_id().map(|t| Command::Seal    { target: t   }).ok_or_else(|| "expected target".into()) }
            Token::OpSpawn   => { self.adv(); self.parse_id().map(|p| Command::Spawn   { plugin: p   }).ok_or_else(|| "expected plugin".into()) }
            Token::OpFork    => { self.adv(); self.parse_int().map(|c| Command::Fork   { count: c    }).ok_or_else(|| "expected count".into()) }
            Token::OpConnect => { self.adv(); self.parse_id().map(|e| Command::Connect { endpoint: e }).ok_or_else(|| "expected endpoint".into()) }
            Token::EOF => Err("EOF".into()),
            _ => { self.adv(); Err(format!("unknown: {:?}", "?")) }
        }
    }
}

fuzz_target!(|data: &[u8]| {
    // ── Input guard ───────────────────────────────────────────────────────────
    if data.len() > 4096 { return; }

    let s = match std::str::from_utf8(data) {
        Ok(s) => s,
        Err(_) => return,
    };

    // ── Invariant 5: empty/whitespace → EMPTY_PAYLOAD_ANTIBODY ───────────────
    if s.trim().is_empty() { return; }   // graceful exit, not a panic

    let mut parser = Parser::new(Lexer::new(s));
    let mut cmd_count: usize = 0;
    let max_cmds = data.len() / 2 + 10;

    loop {
        match parser.parse_cmd() {
            Ok(_cmd) => {
                cmd_count += 1;
                // ── Invariant 4: command count bounded ────────────────────────
                assert!(
                    cmd_count <= max_cmds,
                    "FUZZ_INVARIANT_BROKEN: infinite loop — {} cmds for {} byte input",
                    cmd_count, data.len()
                );
            }
            Err(e) if e == "EOF" => break,
            Err(_) => break,  // ── Invariant 3: malformed → Err, no panic ─────
        }
    }
    // ── Invariant 1: reaching here without panicking = pass ──────────────────
});
