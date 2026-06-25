// flame-lexer — FlameLang v2.0 L1 tokeniser
// Converts raw UTF-8 source text into a Vec<FlameToken>.
// Each token is tagged with a LexiconWeight carrying gematria + wave Hz values.

use anyhow::{bail, Result};
use flametoken::{
    gematria_weight, word_gematria, DnaBase, FlameToken, LexiconWeight, Span, TokenKind,
};

pub struct Lexer<'src> {
    src:    &'src str,
    chars:  Vec<char>,
    pos:    usize,
    line:   u32,
    col:    u32,
}

impl<'src> Lexer<'src> {
    pub fn new(src: &'src str) -> Self {
        Self {
            src,
            chars: src.chars().collect(),
            pos: 0,
            line: 1,
            col: 1,
        }
    }

    pub fn tokenise(&mut self) -> Result<Vec<FlameToken>> {
        let mut tokens = Vec::new();
        loop {
            self.skip_whitespace_and_comments();
            if self.pos >= self.chars.len() {
                tokens.push(self.make(TokenKind::Eof, ""));
                break;
            }
            let tok = self.next_token()?;
            tokens.push(tok);
        }
        Ok(tokens)
    }

    fn next_token(&mut self) -> Result<FlameToken> {
        let ch = self.chars[self.pos];
        match ch {
            // ── Glyph namespace  {namespace⟐modifier} ──────────────────
            '{' => self.lex_glyph_route(),

            // ── Binding codes  [999] [777] [137] ───────────────────────
            '[' => self.lex_binding_code(),

            // ── String literal ──────────────────────────────────────────
            '"' => self.lex_string(),

            // ── Hebrew Unicode block  U+05D0–U+05EA ────────────────────
            '\u{05D0}'..='\u{05EA}' => self.lex_heb_char(),

            // ── Numbers (may include Hz literals) ──────────────────────
            '0'..='9' => self.lex_number(),

            // ── DNA codon  (3-char run of AGTC) ────────────────────────
            'A' | 'G' | 'T' | 'C' => self.lex_codon_or_ident(),

            // ── Identifiers / keywords ──────────────────────────────────
            'a'..='z' | '_' | 'D'..='Z' | 'B' | 'E'..='S' | 'U'..='W' | 'X'..='Z'
                => self.lex_ident_or_keyword(),

            // ── Punctuation ─────────────────────────────────────────────
            '+' => { self.advance(); Ok(self.make(TokenKind::Plus,    "+")) }
            '-' => {
                if self.peek_next() == Some('>') {
                    self.advance(); self.advance();
                    Ok(self.make(TokenKind::Arrow, "->"))
                } else {
                    self.advance(); Ok(self.make(TokenKind::Minus, "-"))
                }
            }
            '*' => { self.advance(); Ok(self.make(TokenKind::Star,    "*")) }
            '/' => { self.advance(); Ok(self.make(TokenKind::Slash,   "/")) }
            '%' => { self.advance(); Ok(self.make(TokenKind::Percent, "%")) }
            '(' => { self.advance(); Ok(self.make(TokenKind::LParen,  "(")) }
            ')' => { self.advance(); Ok(self.make(TokenKind::RParen,  ")")) }
            '}' => { self.advance(); Ok(self.make(TokenKind::RBrace,  "}")) }
            ']' => { self.advance(); Ok(self.make(TokenKind::RBracket,"]")) }
            ',' => { self.advance(); Ok(self.make(TokenKind::Comma,   ",")) }
            ';' => { self.advance(); Ok(self.make(TokenKind::Semicolon,";" )) }
            '=' => {
                if self.peek_next() == Some('=') {
                    self.advance(); self.advance();
                    Ok(self.make(TokenKind::EqEq, "=="))
                } else {
                    bail!("unexpected '=' at {}:{} (use '==')", self.line, self.col)
                }
            }
            '!' => {
                if self.peek_next() == Some('=') {
                    self.advance(); self.advance();
                    Ok(self.make(TokenKind::BangEq, "!="))
                } else {
                    bail!("unexpected '!' at {}:{}", self.line, self.col)
                }
            }
            '<' => {
                if self.peek_next() == Some('=') {
                    self.advance(); self.advance(); Ok(self.make(TokenKind::LtEq, "<="))
                } else { self.advance(); Ok(self.make(TokenKind::Lt, "<")) }
            }
            '>' => {
                if self.peek_next() == Some('=') {
                    self.advance(); self.advance(); Ok(self.make(TokenKind::GtEq, ">="))
                } else { self.advance(); Ok(self.make(TokenKind::Gt, ">")) }
            }

            other => bail!("unexpected character {:?} at {}:{}", other, self.line, self.col),
        }
    }

    // ── Glyph route lexer: {namespace⟐modifier} → path/to/script ──────────
    fn lex_glyph_route(&mut self) -> Result<FlameToken> {
        let start = self.pos;
        let mut raw = String::from('{');
        self.advance(); // consume '{'
        while self.pos < self.chars.len() && self.chars[self.pos] != '}' {
            raw.push(self.chars[self.pos]);
            self.advance();
        }
        if self.pos < self.chars.len() { raw.push('}'); self.advance(); }
        let weight = LexiconWeight {
            gematria: word_gematria(&raw),
            wave_hz:  LexiconWeight::FREQ_432,
            dna_seed: 0,
        };
        Ok(FlameToken { kind: TokenKind::Namespace, lexeme: raw,
                        span: self.span_from(start), weight })
    }

    // ── Binding code: [999] ─────────────────────────────────────────────────
    fn lex_binding_code(&mut self) -> Result<FlameToken> {
        let start = self.pos;
        let mut raw = String::new();
        self.advance(); // consume '['
        while self.pos < self.chars.len() && self.chars[self.pos] != ']' {
            raw.push(self.chars[self.pos]);
            self.advance();
        }
        if self.pos < self.chars.len() { self.advance(); } // consume ']'
        let weight = LexiconWeight {
            gematria: raw.parse::<u32>().unwrap_or(0),
            wave_hz:  LexiconWeight::FREQ_741,
            dna_seed: 0,
        };
        Ok(FlameToken { kind: TokenKind::BindingCode,
                        lexeme: format!("[{}]", raw),
                        span: self.span_from(start), weight })
    }

    // ── String literal ──────────────────────────────────────────────────────
    fn lex_string(&mut self) -> Result<FlameToken> {
        let start = self.pos;
        self.advance(); // opening "
        let mut s = String::new();
        while self.pos < self.chars.len() && self.chars[self.pos] != '"' {
            if self.chars[self.pos] == '\\' { self.advance(); }
            s.push(self.chars[self.pos]);
            self.advance();
        }
        if self.pos < self.chars.len() { self.advance(); } // closing "
        Ok(FlameToken { kind: TokenKind::StringLit, lexeme: s.clone(),
                        span: self.span_from(start),
                        weight: LexiconWeight { gematria: word_gematria(&s),
                                                wave_hz: 0.0, dna_seed: 0 } })
    }

    // ── Hebrew character ────────────────────────────────────────────────────
    fn lex_heb_char(&mut self) -> Result<FlameToken> {
        let start = self.pos;
        let ch = self.chars[self.pos];
        self.advance();
        let g = ch as u32 - 0x05D0 + 1; // aleph=1 … tav=22
        let weight = LexiconWeight { gematria: g, wave_hz: LexiconWeight::FREQ_528, dna_seed: 0 };
        Ok(FlameToken { kind: TokenKind::HebChar, lexeme: ch.to_string(),
                        span: self.span_from(start), weight })
    }

    // ── Number (integer or float, optionally suffixed with Hz) ─────────────
    fn lex_number(&mut self) -> Result<FlameToken> {
        let start = self.pos;
        let mut raw = String::new();
        while self.pos < self.chars.len()
              && (self.chars[self.pos].is_ascii_digit() || self.chars[self.pos] == '.') {
            raw.push(self.chars[self.pos]);
            self.advance();
        }
        // Check for Hz suffix
        let is_wave = if self.pos + 1 < self.chars.len()
              && self.chars[self.pos] == 'H' && self.chars[self.pos+1] == 'z' {
            self.advance(); self.advance(); true
        } else { false };

        let hz_val: f64 = raw.parse().unwrap_or(0.0);
        let (kind, wave_hz) = if is_wave {
            (TokenKind::WaveFreq, hz_val)
        } else {
            (TokenKind::Number, 0.0)
        };
        let weight = LexiconWeight { gematria: hz_val as u32, wave_hz, dna_seed: 0 };
        let lexeme = if is_wave { format!("{}Hz", raw) } else { raw };
        Ok(FlameToken { kind, lexeme, span: self.span_from(start), weight })
    }

    // ── Codon (3-char AGTC run) or identifier ──────────────────────────────
    fn lex_codon_or_ident(&mut self) -> Result<FlameToken> {
        let start = self.pos;
        // Peek ahead: is this exactly 3 AGTC chars followed by non-alnum?
        let maybe_codon = (0..3).all(|i| {
            self.pos + i < self.chars.len()
                && DnaBase::from_char(self.chars[self.pos + i]).is_some()
        }) && self.pos + 3 < self.chars.len()
             && !self.chars[self.pos + 3].is_alphanumeric();

        if maybe_codon {
            let s: String = self.chars[self.pos..self.pos+3].iter().collect();
            self.pos += 3; self.col += 3;
            let weight = LexiconWeight { gematria: word_gematria(&s),
                                         wave_hz: LexiconWeight::FREQ_528, dna_seed: s.as_bytes()[0] };
            return Ok(FlameToken { kind: TokenKind::Codon, lexeme: s,
                                   span: self.span_from(start), weight });
        }
        self.lex_ident_or_keyword()
    }

    // ── Identifier / keyword ────────────────────────────────────────────────
    fn lex_ident_or_keyword(&mut self) -> Result<FlameToken> {
        let start = self.pos;
        let mut raw = String::new();
        while self.pos < self.chars.len()
              && (self.chars[self.pos].is_alphanumeric() || self.chars[self.pos] == '_') {
            raw.push(self.chars[self.pos]);
            self.advance();
        }
        let kind = match raw.as_str() {
            "DISPATCH" => TokenKind::Dispatch,
            "EMAIL"    => TokenKind::Email,
            "AUDIT"    => TokenKind::Audit,
            "GENESIS"  => TokenKind::Genesis,
            _          => TokenKind::Ident,
        };
        let weight = LexiconWeight { gematria: word_gematria(&raw),
                                     wave_hz: 0.0, dna_seed: 0 };
        Ok(FlameToken { kind, lexeme: raw, span: self.span_from(start), weight })
    }

    // ── Helpers ─────────────────────────────────────────────────────────────
    fn advance(&mut self) {
        if self.pos < self.chars.len() {
            if self.chars[self.pos] == '\n' { self.line += 1; self.col = 1; }
            else { self.col += 1; }
            self.pos += 1;
        }
    }

    fn peek_next(&self) -> Option<char> {
        self.chars.get(self.pos + 1).copied()
    }

    fn skip_whitespace_and_comments(&mut self) {
        while self.pos < self.chars.len() {
            match self.chars[self.pos] {
                ' ' | '\t' | '\r' | '\n' => { self.advance(); }
                '#' => { while self.pos < self.chars.len() && self.chars[self.pos] != '\n' { self.advance(); } }
                '/' if self.peek_next() == Some('/') => {
                    while self.pos < self.chars.len() && self.chars[self.pos] != '\n' { self.advance(); }
                }
                _ => break,
            }
        }
    }

    fn span_from(&self, start: usize) -> Span {
        Span { line: self.line, col: self.col, start, end: self.pos }
    }

    fn make(&self, kind: TokenKind, lexeme: &str) -> FlameToken {
        FlameToken {
            kind,
            lexeme: lexeme.to_string(),
            span: Span { line: self.line, col: self.col, start: self.pos, end: self.pos },
            weight: LexiconWeight::ZERO,
        }
    }
}
