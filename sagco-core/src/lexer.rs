/// lexer.rs
/// SAGCO-Core Lexer — transforms raw field input into typed tokens.
///
/// Input:  "RB-001 4 27 1 0 N E UP"
/// Output: [Ident("RB-001"), Number(4), Number(27), Number(1),
///          Number(0), Direction(N), Direction(E), Direction(UP)]

#[derive(Debug, Clone, PartialEq)]
pub enum Direction {
    N, S, E, W,
    NE, NW, SE, SW,
    Up, Down,
    Unknown(String),
}

impl Direction {
    fn parse(s: &str) -> Self {
        match s.to_uppercase().as_str() {
            "N"  => Direction::N,
            "S"  => Direction::S,
            "E"  => Direction::E,
            "W"  => Direction::W,
            "NE" => Direction::NE,
            "NW" => Direction::NW,
            "SE" => Direction::SE,
            "SW" => Direction::SW,
            "UP" => Direction::Up,
            "DOWN" | "DN" => Direction::Down,
            other => Direction::Unknown(other.to_string()),
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    Ident(String),      // RB-001, P1, sagco
    Number(i64),        // 4, 27, 3200
    Float(f64),         // 0.0025, 3.14
    Direction(Direction),
    Domain(String),     // geo, tri, bubble, units, pmi
    Keyword(String),    // dist2unit, rpmvolt, score
    Eof,
}

#[derive(Debug)]
pub struct LexError {
    pub token: String,
    pub pos:   usize,
}

pub fn lex(input: &str) -> Result<Vec<Token>, LexError> {
    let mut tokens = Vec::new();

    for (pos, word) in input.split_whitespace().enumerate() {
        let tok = classify(word, pos)?;
        tokens.push(tok);
    }

    tokens.push(Token::Eof);
    Ok(tokens)
}

fn classify(word: &str, pos: usize) -> Result<Token, LexError> {
    // Direction keywords first (pure alpha, compass-like)
    let up = word.to_uppercase();
    if matches!(up.as_str(), "N"|"S"|"E"|"W"|"NE"|"NW"|"SE"|"SW"|"UP"|"DOWN"|"DN") {
        return Ok(Token::Direction(Direction::parse(word)));
    }

    // Domain keywords
    if matches!(word, "geo"|"tri"|"bubble"|"units"|"pmi"|"search"|"omni"|
                       "transistor"|"freq"|"math"|"proof") {
        return Ok(Token::Domain(word.to_string()));
    }

    // Sub-commands / keywords
    if matches!(word, "dist2unit"|"rpmvolt"|"score"|"state"|"verify"|"status") {
        return Ok(Token::Keyword(word.to_string()));
    }

    // Integer
    if let Ok(n) = word.parse::<i64>() {
        return Ok(Token::Number(n));
    }

    // Float
    if let Ok(f) = word.parse::<f64>() {
        if word.contains('.') {
            return Ok(Token::Float(f));
        }
    }

    // Identifier: starts with alpha/underscore, may contain '-', '_', digits
    let first = word.chars().next().unwrap_or(' ');
    if first.is_alphabetic() || first == '_' {
        return Ok(Token::Ident(word.to_string()));
    }

    Err(LexError { token: word.to_string(), pos })
}

// ─── TESTS ─────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bubble_input() {
        let tokens = lex("RB-001 4 27 1 0 N E UP").unwrap();
        assert_eq!(tokens[0], Token::Ident("RB-001".to_string()));
        assert_eq!(tokens[1], Token::Number(4));
        assert_eq!(tokens[2], Token::Number(27));
        assert_eq!(tokens[3], Token::Number(1));
        assert_eq!(tokens[4], Token::Number(0));
        assert_eq!(tokens[5], Token::Direction(Direction::N));
        assert_eq!(tokens[6], Token::Direction(Direction::E));
        assert_eq!(tokens[7], Token::Direction(Direction::Up));
        assert_eq!(tokens[8], Token::Eof);
    }

    #[test]
    fn test_rpmvolt_input() {
        let tokens = lex("units rpmvolt P1 3200 0.0025").unwrap();
        assert_eq!(tokens[0], Token::Domain("units".to_string()));
        assert_eq!(tokens[1], Token::Keyword("rpmvolt".to_string()));
        assert_eq!(tokens[2], Token::Ident("P1".to_string()));
        assert_eq!(tokens[3], Token::Number(3200));
        assert_eq!(tokens[4], Token::Float(0.0025));
    }

    #[test]
    fn test_geo_input() {
        let tokens = lex("geo dist2unit").unwrap();
        assert_eq!(tokens[0], Token::Domain("geo".to_string()));
        assert_eq!(tokens[1], Token::Keyword("dist2unit".to_string()));
    }

    #[test]
    fn test_tri_input() {
        let tokens = lex("tri 0 0 5 10 0 5 5 10 5").unwrap();
        assert_eq!(tokens[0], Token::Domain("tri".to_string()));
        // 9 numbers follow
        let nums: Vec<_> = tokens[1..10].iter().collect();
        assert_eq!(nums.len(), 9);
    }
}
