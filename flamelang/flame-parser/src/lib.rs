// flame-parser — FlameLang v2.0 L2 AST builder
// Consumes a token stream from flame-lexer and produces an AST.

use anyhow::{bail, Result};
use flametoken::{FlameToken, TokenKind};

// ── AST nodes ─────────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub enum Expr {
    Number(f64),
    StringLit(String),
    Ident(String),
    GlyphRoute { namespace: String, modifier: Option<String> },
    BindingCode(u32),
    HebChar { codepoint: char, gematria: u32 },
    WaveFreq(f64),
    Codon(String),
    BinOp { op: BinOpKind, lhs: Box<Expr>, rhs: Box<Expr> },
    Dispatch { command: String, payload: Box<Expr> },
    Email     { to: Box<Expr>, subject: Box<Expr>, body: Box<Expr> },
    Audit     { component: String, event: String, data: Box<Expr> },
    Genesis,
}

#[derive(Debug, Clone, Copy)]
pub enum BinOpKind { Add, Sub, Mul, Div, Mod, EqEq, BangEq, Lt, Gt, LtEq, GtEq }

#[derive(Debug, Clone)]
pub struct Statement {
    pub expr: Expr,
}

#[derive(Debug, Clone)]
pub struct Program {
    pub stmts: Vec<Statement>,
}

// ── Parser ────────────────────────────────────────────────────────────────────

pub struct Parser {
    tokens: Vec<FlameToken>,
    pos:    usize,
}

impl Parser {
    pub fn new(tokens: Vec<FlameToken>) -> Self {
        Self { tokens, pos: 0 }
    }

    pub fn parse(&mut self) -> Result<Program> {
        let mut stmts = Vec::new();
        while !self.is_eof() {
            stmts.push(Statement { expr: self.parse_expr()? });
            if self.peek_kind() == TokenKind::Semicolon { self.advance(); }
        }
        Ok(Program { stmts })
    }

    fn parse_expr(&mut self) -> Result<Expr> {
        self.parse_comparison()
    }

    fn parse_comparison(&mut self) -> Result<Expr> {
        let mut lhs = self.parse_additive()?;
        loop {
            let op = match self.peek_kind() {
                TokenKind::EqEq  => BinOpKind::EqEq,
                TokenKind::BangEq=> BinOpKind::BangEq,
                TokenKind::Lt    => BinOpKind::Lt,
                TokenKind::Gt    => BinOpKind::Gt,
                TokenKind::LtEq  => BinOpKind::LtEq,
                TokenKind::GtEq  => BinOpKind::GtEq,
                _ => break,
            };
            self.advance();
            let rhs = self.parse_additive()?;
            lhs = Expr::BinOp { op, lhs: Box::new(lhs), rhs: Box::new(rhs) };
        }
        Ok(lhs)
    }

    fn parse_additive(&mut self) -> Result<Expr> {
        let mut lhs = self.parse_multiplicative()?;
        loop {
            let op = match self.peek_kind() {
                TokenKind::Plus  => BinOpKind::Add,
                TokenKind::Minus => BinOpKind::Sub,
                _ => break,
            };
            self.advance();
            let rhs = self.parse_multiplicative()?;
            lhs = Expr::BinOp { op, lhs: Box::new(lhs), rhs: Box::new(rhs) };
        }
        Ok(lhs)
    }

    fn parse_multiplicative(&mut self) -> Result<Expr> {
        let mut lhs = self.parse_primary()?;
        loop {
            let op = match self.peek_kind() {
                TokenKind::Star    => BinOpKind::Mul,
                TokenKind::Slash   => BinOpKind::Div,
                TokenKind::Percent => BinOpKind::Mod,
                _ => break,
            };
            self.advance();
            let rhs = self.parse_primary()?;
            lhs = Expr::BinOp { op, lhs: Box::new(lhs), rhs: Box::new(rhs) };
        }
        Ok(lhs)
    }

    fn parse_primary(&mut self) -> Result<Expr> {
        let tok = self.current().clone();
        match tok.kind {
            TokenKind::Number => {
                self.advance();
                let n: f64 = tok.lexeme.parse().unwrap_or(0.0);
                Ok(Expr::Number(n))
            }
            TokenKind::WaveFreq => {
                self.advance();
                let hz: f64 = tok.lexeme.trim_end_matches("Hz").parse().unwrap_or(0.0);
                Ok(Expr::WaveFreq(hz))
            }
            TokenKind::StringLit => {
                self.advance();
                Ok(Expr::StringLit(tok.lexeme.clone()))
            }
            TokenKind::Codon => {
                self.advance();
                Ok(Expr::Codon(tok.lexeme.clone()))
            }
            TokenKind::HebChar => {
                self.advance();
                let cp = tok.lexeme.chars().next().unwrap_or('\0');
                Ok(Expr::HebChar { codepoint: cp, gematria: tok.weight.gematria })
            }
            TokenKind::Namespace => {
                self.advance();
                let inner = tok.lexeme.trim_matches(|c| c == '{' || c == '}');
                let parts: Vec<&str> = inner.splitn(2, '⟐').collect();
                Ok(Expr::GlyphRoute {
                    namespace: parts.get(0).unwrap_or(&"").to_string(),
                    modifier:  parts.get(1).map(|s| s.to_string()),
                })
            }
            TokenKind::BindingCode => {
                self.advance();
                let n: u32 = tok.lexeme.trim_matches(|c| c == '[' || c == ']')
                                       .parse().unwrap_or(0);
                Ok(Expr::BindingCode(n))
            }
            TokenKind::Dispatch => {
                self.advance();
                self.expect(TokenKind::LParen)?;
                let cmd = self.expect_string_or_ident()?;
                self.expect(TokenKind::Comma)?;
                let payload = self.parse_expr()?;
                self.expect(TokenKind::RParen)?;
                Ok(Expr::Dispatch { command: cmd, payload: Box::new(payload) })
            }
            TokenKind::Email => {
                self.advance();
                self.expect(TokenKind::LParen)?;
                let to      = self.parse_expr()?;
                self.expect(TokenKind::Comma)?;
                let subject = self.parse_expr()?;
                self.expect(TokenKind::Comma)?;
                let body    = self.parse_expr()?;
                self.expect(TokenKind::RParen)?;
                Ok(Expr::Email { to: Box::new(to), subject: Box::new(subject),
                                  body: Box::new(body) })
            }
            TokenKind::Audit => {
                self.advance();
                self.expect(TokenKind::LParen)?;
                let component = self.expect_string_or_ident()?;
                self.expect(TokenKind::Comma)?;
                let event     = self.expect_string_or_ident()?;
                self.expect(TokenKind::Comma)?;
                let data      = self.parse_expr()?;
                self.expect(TokenKind::RParen)?;
                Ok(Expr::Audit { component, event, data: Box::new(data) })
            }
            TokenKind::Genesis => { self.advance(); Ok(Expr::Genesis) }
            TokenKind::Ident => {
                self.advance();
                Ok(Expr::Ident(tok.lexeme.clone()))
            }
            TokenKind::LParen => {
                self.advance();
                let e = self.parse_expr()?;
                self.expect(TokenKind::RParen)?;
                Ok(e)
            }
            other => bail!("unexpected token {:?} '{}'", other, tok.lexeme),
        }
    }

    // ── Helpers ─────────────────────────────────────────────────────────────
    fn current(&self) -> &FlameToken { &self.tokens[self.pos] }
    fn peek_kind(&self) -> TokenKind { self.tokens[self.pos].kind.clone() }
    fn is_eof(&self) -> bool { self.peek_kind() == TokenKind::Eof }
    fn advance(&mut self) { if !self.is_eof() { self.pos += 1; } }

    fn expect(&mut self, kind: TokenKind) -> Result<()> {
        if self.peek_kind() == kind { self.advance(); Ok(()) }
        else { bail!("expected {:?} but got {:?}", kind, self.peek_kind()) }
    }

    fn expect_string_or_ident(&mut self) -> Result<String> {
        let tok = self.current().clone();
        match tok.kind {
            TokenKind::StringLit | TokenKind::Ident => { self.advance(); Ok(tok.lexeme) }
            other => bail!("expected string or ident, got {:?}", other),
        }
    }
}
