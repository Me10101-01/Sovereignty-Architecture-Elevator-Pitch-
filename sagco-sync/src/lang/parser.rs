use crate::lang::token::Token;
use crate::lang::ast::{AccessType, CircuitNode, CutNode, ProjectNode};

pub struct Parser {
    tokens: Vec<Token>,
    pos: usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Parser {
        Parser { tokens, pos: 0 }
    }

    fn peek(&self) -> &Token {
        self.tokens.get(self.pos).unwrap_or(&Token::Eof)
    }

    fn advance(&mut self) -> &Token {
        let t = self.tokens.get(self.pos).unwrap_or(&Token::Eof);
        self.pos += 1;
        t
    }

    fn skip_newlines(&mut self) {
        while *self.peek() == Token::Newline {
            self.advance();
        }
    }

    fn expect_str(&mut self, ctx: &str) -> Result<String, String> {
        self.skip_newlines();
        match self.advance().clone() {
            Token::Str(s) => Ok(s),
            other => Err(format!("{}: expected string, got {:?}", ctx, other)),
        }
    }

    fn expect_lbrace(&mut self, ctx: &str) -> Result<(), String> {
        self.skip_newlines();
        match self.advance() {
            Token::LBrace => Ok(()),
            other => Err(format!("{}: expected '{{', got {:?}", ctx, other)),
        }
    }

    pub fn parse(&mut self) -> Result<ProjectNode, String> {
        self.skip_newlines();
        match self.advance().clone() {
            Token::KwProject => {}
            other => return Err(format!("Expected 'project', got {:?}", other)),
        }
        let name = self.expect_str("project name")?;
        self.expect_lbrace("project block")?;

        let mut circuits = Vec::new();
        loop {
            self.skip_newlines();
            match self.peek().clone() {
                Token::RBrace | Token::Eof => {
                    self.advance();
                    break;
                }
                Token::KwCircuit => {
                    self.advance();
                    let circ = self.parse_circuit()?;
                    circuits.push(circ);
                }
                _ => {
                    self.advance(); // skip unknown token
                }
            }
        }

        Ok(ProjectNode { name, circuits })
    }

    fn parse_circuit(&mut self) -> Result<CircuitNode, String> {
        let id = self.expect_str("circuit id")?;
        self.expect_lbrace("circuit block")?;

        let mut cuts = Vec::new();
        loop {
            self.skip_newlines();
            match self.peek().clone() {
                Token::RBrace | Token::Eof => {
                    self.advance();
                    break;
                }
                Token::KwCut => {
                    self.advance();
                    let cut = self.parse_cut()?;
                    cuts.push(cut);
                }
                _ => {
                    self.advance();
                }
            }
        }

        Ok(CircuitNode { id, cuts })
    }

    fn parse_cut(&mut self) -> Result<CutNode, String> {
        let id = self.expect_str("cut id")?;
        self.expect_lbrace("cut block")?;

        let mut cut = CutNode { id, ..Default::default() };

        loop {
            self.skip_newlines();
            let tok = self.peek().clone();
            match tok {
                Token::RBrace | Token::Eof => {
                    self.advance();
                    break;
                }
                Token::KwEstHrs => {
                    self.advance();
                    self.consume_colon();
                    cut.estimate_hrs = self.consume_number()?;
                }
                Token::KwUsedHrs => {
                    self.advance();
                    self.consume_colon();
                    cut.used_hrs = self.consume_number()?;
                }
                Token::KwLnfTotal => {
                    self.advance();
                    self.consume_colon();
                    cut.lnf_total = self.consume_number()?;
                }
                Token::KwLnfDone => {
                    self.advance();
                    self.consume_colon();
                    cut.lnf_done = self.consume_number()?;
                }
                Token::KwElevation => {
                    self.advance();
                    self.consume_colon();
                    cut.elevation_ft = self.consume_number()?;
                }
                Token::KwBands => {
                    self.advance();
                    self.consume_colon();
                    cut.bands = self.consume_number()? as u32;
                }
                Token::KwMetal => {
                    self.advance();
                    self.consume_colon();
                    cut.metal = self.consume_bool()?;
                }
                Token::KwAccess => {
                    self.advance();
                    self.consume_colon();
                    cut.access = self.consume_access()?;
                }
                Token::KwDescription => {
                    self.advance();
                    self.consume_colon();
                    cut.description = Some(self.consume_str_value()?);
                }
                Token::KwCostCode => {
                    self.advance();
                    self.consume_colon();
                    cut.cost_code = Some(self.consume_str_value()?);
                }
                _ => {
                    // unknown field — skip token + optional colon + value
                    self.advance();
                    if *self.peek() == Token::Colon {
                        self.advance();
                        self.advance(); // skip value
                    }
                }
            }
            // optional comma
            if *self.peek() == Token::Comma {
                self.advance();
            }
        }

        Ok(cut)
    }

    fn consume_colon(&mut self) {
        self.skip_newlines();
        if *self.peek() == Token::Colon {
            self.advance();
        }
    }

    fn consume_number(&mut self) -> Result<f64, String> {
        self.skip_newlines();
        match self.advance().clone() {
            Token::Number(n) => Ok(n),
            other => Err(format!("Expected number, got {:?}", other)),
        }
    }

    fn consume_bool(&mut self) -> Result<bool, String> {
        self.skip_newlines();
        match self.advance().clone() {
            Token::KwYes => Ok(true),
            Token::KwNo  => Ok(false),
            Token::Number(n) => Ok(n != 0.0),
            other => Err(format!("Expected yes/no, got {:?}", other)),
        }
    }

    fn consume_access(&mut self) -> Result<AccessType, String> {
        self.skip_newlines();
        match self.advance().clone() {
            Token::KwGround  => Ok(AccessType::Ground),
            Token::KwLadder  => Ok(AccessType::Ladder),
            Token::KwRope    => Ok(AccessType::Rope),
            Token::KwManlift => Ok(AccessType::Manlift),
            other => Err(format!("Expected access type, got {:?}", other)),
        }
    }

    fn consume_str_value(&mut self) -> Result<String, String> {
        self.skip_newlines();
        match self.advance().clone() {
            Token::Str(s)   => Ok(s),
            Token::Ident(s) => Ok(s),
            other => Err(format!("Expected string value, got {:?}", other)),
        }
    }
}
