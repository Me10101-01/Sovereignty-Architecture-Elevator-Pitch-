#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    // Literals
    Number(f64),
    Str(String),
    Ident(String),
    // Block keywords
    KwProject,
    KwCircuit,
    KwCut,
    // Field keywords
    KwEstHrs,
    KwUsedHrs,
    KwLnfTotal,
    KwLnfDone,
    KwElevation,
    KwBands,
    KwMetal,
    KwAccess,
    KwDescription,
    KwCostCode,
    // Value keywords
    KwYes,
    KwNo,
    KwGround,
    KwLadder,
    KwRope,
    KwManlift,
    // Punctuation
    LBrace,
    RBrace,
    Colon,
    Comma,
    Newline,
    Eof,
}
