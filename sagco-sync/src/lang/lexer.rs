use crate::lang::token::Token;
use crate::lang::lexicon::lookup;

pub struct Lexer {
    input: Vec<char>,
    pos: usize,
    line: usize,
}

impl Lexer {
    pub fn new(input: &str) -> Lexer {
        Lexer {
            input: input.chars().collect(),
            pos: 0,
            line: 1,
        }
    }

    fn peek(&self) -> Option<char> {
        self.input.get(self.pos).copied()
    }

    fn advance(&mut self) -> Option<char> {
        let c = self.input.get(self.pos).copied();
        self.pos += 1;
        c
    }

    fn skip_whitespace(&mut self) {
        while let Some(c) = self.peek() {
            if c == ' ' || c == '\t' || c == '\r' {
                self.advance();
            } else {
                break;
            }
        }
    }

    fn read_string(&mut self) -> Token {
        // consume opening quote
        self.advance();
        let mut s = String::new();
        loop {
            match self.advance() {
                Some('"') => break,
                Some('\\') => {
                    match self.advance() {
                        Some('n') => s.push('\n'),
                        Some('t') => s.push('\t'),
                        Some(c)   => s.push(c),
                        None      => break,
                    }
                }
                Some(c) => s.push(c),
                None => break,
            }
        }
        Token::Str(s)
    }

    fn read_number(&mut self) -> Token {
        let mut s = String::new();
        // possible leading minus
        if self.peek() == Some('-') {
            s.push('-');
            self.advance();
        }
        while let Some(c) = self.peek() {
            if c.is_ascii_digit() || c == '.' {
                s.push(c);
                self.advance();
            } else {
                break;
            }
        }
        let val: f64 = s.parse().unwrap_or(0.0);
        Token::Number(val)
    }

    fn read_ident(&mut self) -> Token {
        let mut s = String::new();
        while let Some(c) = self.peek() {
            if c.is_alphanumeric() || c == '_' {
                s.push(c);
                self.advance();
            } else {
                break;
            }
        }
        lookup(&s).unwrap_or(Token::Ident(s))
    }

    pub fn tokenize(&mut self) -> Vec<Token> {
        let mut tokens = Vec::new();
        loop {
            self.skip_whitespace();
            match self.peek() {
                None => {
                    tokens.push(Token::Eof);
                    break;
                }
                Some('#') => {
                    // line comment
                    while let Some(c) = self.advance() {
                        if c == '\n' {
                            self.line += 1;
                            tokens.push(Token::Newline);
                            break;
                        }
                    }
                }
                Some('\n') => {
                    self.advance();
                    self.line += 1;
                    tokens.push(Token::Newline);
                }
                Some('{') => { self.advance(); tokens.push(Token::LBrace); }
                Some('}') => { self.advance(); tokens.push(Token::RBrace); }
                Some(':') => { self.advance(); tokens.push(Token::Colon); }
                Some(',') => { self.advance(); tokens.push(Token::Comma); }
                Some('"') => {
                    let t = self.read_string();
                    tokens.push(t);
                }
                Some(c) if c.is_ascii_digit() => {
                    let t = self.read_number();
                    tokens.push(t);
                }
                Some('-') => {
                    // peek ahead: if next is digit, it's a number
                    let next = self.input.get(self.pos + 1).copied();
                    if next.map(|x| x.is_ascii_digit()).unwrap_or(false) {
                        let t = self.read_number();
                        tokens.push(t);
                    } else {
                        self.advance();
                        tokens.push(Token::Ident("-".to_string()));
                    }
                }
                Some(c) if c.is_alphabetic() || c == '_' => {
                    let t = self.read_ident();
                    tokens.push(t);
                }
                Some(_) => {
                    self.advance();
                    tokens.push(Token::Ident("?".to_string()));
                }
            }
        }
        tokens
    }
}
