// SAGCO-Core Parser — AST + validation ledger
// Turns token stream into typed Command nodes for the VM
// License: SSL-1.0 — Strategickhaos DAO LLC

use super::lexer::{Lexer, Token};

// ── AST ───────────────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub enum Command {
    Read    { file: String },          // open file → BYTES gate (I/O proof)
    Wave    { source: String },        // ingest artifact → tokens
    Pulse   { node_id: u64 },          // EUR probe a node (GCP project, etc.)
    Seal    { target: String },        // SHA256 evidence artifact
    Spawn   { plugin: String },        // spawn plugin from registry
    Fork    { count: u64 },            // parallel execution branches
    Connect { endpoint: String },      // bind a SagcoInput source
}

pub type ParseResult = Result<Command, String>;

// ── Parser ────────────────────────────────────────────────────────────────────

pub struct Parser {
    lexer: Lexer,
    current: Token,
}

impl Parser {
    pub fn new(mut lexer: Lexer) -> Self {
        let current = lexer.next_token();
        Self { lexer, current }
    }

    fn advance(&mut self) {
        self.current = self.lexer.next_token();
    }

    fn expect_identifier(&mut self, context: &str) -> Result<String, String> {
        match &self.current {
            Token::Identifier(s) => {
                let val = s.clone();
                self.advance();
                Ok(val)
            }
            Token::Hash(h) => {
                let val = h.clone();
                self.advance();
                Ok(val)
            }
            other => Err(format!(
                "[PARSE_ERROR] expected identifier after '{}', got: {:?}",
                context, other
            )),
        }
    }

    fn expect_integer(&mut self, context: &str) -> Result<u64, String> {
        match self.current {
            Token::LiteralInt(n) => {
                let val = n;
                self.advance();
                Ok(val)
            }
            ref other => Err(format!(
                "[PARSE_ERROR] expected integer after '{}', got: {:?}",
                context, other
            )),
        }
    }

    pub fn parse_command(&mut self) -> ParseResult {
        match self.current.clone() {
            Token::OpRead => {
                self.advance();
                let file = self.expect_identifier("read")?;
                Ok(Command::Read { file })
            }
            Token::OpWave => {
                self.advance();
                let source = self.expect_identifier("wave")?;
                Ok(Command::Wave { source })
            }
            Token::OpPulse => {
                self.advance();
                // pulse accepts either integer node_id or identifier (hostname/project)
                let node_id = match &self.current {
                    Token::LiteralInt(n) => { let v = *n; self.advance(); v }
                    Token::Identifier(s) => {
                        // try parsing as number (project IDs can appear as identifiers)
                        let v = s.parse::<u64>().unwrap_or(0);
                        self.advance();
                        v
                    }
                    other => return Err(format!(
                        "[PARSE_ERROR] pulse needs node_id, got: {:?}", other
                    )),
                };
                Ok(Command::Pulse { node_id })
            }
            Token::OpSeal => {
                self.advance();
                let target = self.expect_identifier("seal")?;
                Ok(Command::Seal { target })
            }
            Token::OpSpawn => {
                self.advance();
                let plugin = self.expect_identifier("spawn")?;
                Ok(Command::Spawn { plugin })
            }
            Token::OpFork => {
                self.advance();
                let count = self.expect_integer("fork")?;
                Ok(Command::Fork { count })
            }
            Token::OpConnect => {
                self.advance();
                let endpoint = self.expect_identifier("connect")?;
                Ok(Command::Connect { endpoint })
            }
            Token::EOF => Err("EOF".to_string()),
            other => {
                self.advance();
                Err(format!("[PARSE_ERROR] unknown token: {:?}", other))
            }
        }
    }

    pub fn parse_program(&mut self) -> Vec<ParseResult> {
        let mut cmds = Vec::new();
        loop {
            match self.parse_command() {
                Err(e) if e == "EOF" => break,
                result => cmds.push(result),
            }
        }
        cmds
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn parse_one(src: &str) -> ParseResult {
        let lexer = Lexer::new(src);
        let mut parser = Parser::new(lexer);
        parser.parse_command()
    }

    #[test]
    fn parse_wave() {
        let cmd = parse_one("wave gcp_services.txt").unwrap();
        assert!(matches!(cmd, Command::Wave { source } if source == "gcp_services.txt"));
    }

    #[test]
    fn parse_pulse_int() {
        let cmd = parse_one("pulse 793398609444").unwrap();
        assert!(matches!(cmd, Command::Pulse { node_id } if node_id == 793398609444));
    }

    #[test]
    fn parse_seal() {
        let cmd = parse_one("seal evidence.bin").unwrap();
        assert!(matches!(cmd, Command::Seal { target } if target == "evidence.bin"));
    }

    #[test]
    fn parse_spawn() {
        let cmd = parse_one("spawn gcloud_plugin").unwrap();
        assert!(matches!(cmd, Command::Spawn { plugin } if plugin == "gcloud_plugin"));
    }

    #[test]
    fn parse_fork() {
        let cmd = parse_one("fork 4").unwrap();
        assert!(matches!(cmd, Command::Fork { count } if count == 4));
    }

    #[test]
    fn parse_connect() {
        let cmd = parse_one("connect gcp").unwrap();
        assert!(matches!(cmd, Command::Connect { endpoint } if endpoint == "gcp"));
    }

    #[test]
    fn parse_full_program() {
        let src = "wave gcp_services.txt pulse 793398609444 seal evidence.bin";
        let lexer = Lexer::new(src);
        let mut parser = Parser::new(lexer);
        let results = parser.parse_program();
        assert_eq!(results.len(), 3);
        assert!(results.iter().all(|r| r.is_ok()));
    }
}
