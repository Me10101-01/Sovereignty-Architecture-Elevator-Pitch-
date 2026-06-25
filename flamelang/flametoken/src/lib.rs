// FlameToken — canonical token definitions + lexicon weights
// Layer L1 vocabulary for the FlameLang v2.0 compiler pipeline.
// Each FlameToken carries a gematria weight and a 432–741 Hz wave resonance
// used by the downstream Hebrew and Wave transform layers.

use serde::{Deserialize, Serialize};

// ── Token kinds ──────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum TokenKind {
    // Structural
    Namespace,    // {namespace⟐modifier} glyph routing
    Modifier,
    BindingCode,  // [999] [777] [137]
    GlyphRoute,   // →  absolute script path

    // Biological pipeline triggers
    HebChar,      // Hebrew codepoint (gematria source)
    WaveFreq,     // Hz literal  432 | 528 | 639 | 741
    Codon,        // DNA triplet  ATG | GAT | CGA | TAC …

    // SAGCO dispatch
    Dispatch,     // DISPATCH keyword → sagco_k8s_job
    Email,        // EMAIL keyword    → sagco_email
    Audit,        // AUDIT keyword    → sagco_audit_log
    Genesis,      // GENESIS keyword  → sagco_genesis_proof

    // Arithmetic / comparison (shared with omni_calc)
    Number,
    Plus, Minus, Star, Slash, Percent,
    EqEq, BangEq, Lt, Gt, LtEq, GtEq,

    // Delimiters
    LBrace, RBrace, LParen, RParen, LBracket, RBracket,
    Comma, Semicolon, Arrow,

    // Identifiers / literals
    Ident,
    StringLit,

    Eof,
}

// ── Token span ───────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Span {
    pub line:  u32,
    pub col:   u32,
    pub start: usize,
    pub end:   usize,
}

// ── Full token ───────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlameToken {
    pub kind:     TokenKind,
    pub lexeme:   String,
    pub span:     Span,
    pub weight:   LexiconWeight,
}

// ── Lexicon weight ────────────────────────────────────────────────────────────
// Every token carries gematria + wave data even if zero — downstream
// transforms use these to seed the Hebrew and Wave pipeline layers.

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct LexiconWeight {
    pub gematria:  u32,   // Hebrew numeric value (0 if not applicable)
    pub wave_hz:   f64,   // Resonance frequency (0.0 if not applicable)
    pub dna_seed:  u8,    // First codon bias byte (0 = unconstrained)
}

impl LexiconWeight {
    pub const ZERO: Self = Self { gematria: 0, wave_hz: 0.0, dna_seed: 0 };

    // Standard sacred-geometry frequencies
    pub const FREQ_432:  f64 = 432.0;
    pub const FREQ_528:  f64 = 528.0;
    pub const FREQ_639:  f64 = 639.0;
    pub const FREQ_741:  f64 = 741.0;
    pub const FREQ_852:  f64 = 852.0;
    pub const FREQ_963:  f64 = 963.0;
}

// ── Gematria table (standard Hebrew, English-to-value) ───────────────────────
// Maps ASCII uppercase letters to their standard gematria weight.
// Source: aleph=1 … tav=400 mapped via English equivalents.
pub fn gematria_weight(ch: char) -> u32 {
    match ch.to_ascii_uppercase() {
        'A' => 1,   'B' => 2,   'C' => 3,   'D' => 4,   'E' => 5,
        'F' => 6,   'G' => 7,   'H' => 8,   'I' => 9,   'J' => 10,
        'K' => 20,  'L' => 30,  'M' => 40,  'N' => 50,  'O' => 60,
        'P' => 70,  'Q' => 80,  'R' => 90,  'S' => 100, 'T' => 200,
        'U' => 300, 'V' => 400, 'W' => 500, 'X' => 600, 'Y' => 700,
        'Z' => 800,
        _   => 0,
    }
}

/// Sum gematria for an entire word / identifier.
pub fn word_gematria(s: &str) -> u32 {
    s.chars().map(gematria_weight).sum()
}

// ── DNA codon table ───────────────────────────────────────────────────────────
// Maps the 4 AGTC bases to their encoding byte for the DNA transform layer.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum DnaBase { A = 0, G = 1, T = 2, C = 3 }

impl DnaBase {
    pub fn from_char(c: char) -> Option<Self> {
        match c { 'A' => Some(Self::A), 'G' => Some(Self::G),
                  'T' => Some(Self::T), 'C' => Some(Self::C), _ => None }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Codon(pub DnaBase, pub DnaBase, pub DnaBase);

impl Codon {
    /// Encode a codon as a 6-bit integer (2 bits per base).
    pub fn encode(&self) -> u8 {
        ((self.0 as u8) << 4) | ((self.1 as u8) << 2) | (self.2 as u8)
    }
}
