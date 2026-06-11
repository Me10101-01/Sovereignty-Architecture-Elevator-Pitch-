use crate::lang::token::Token;

static KEYWORDS: &[(&str, fn() -> Token)] = &[
    ("project",      || Token::KwProject),
    ("circuit",      || Token::KwCircuit),
    ("cut",          || Token::KwCut),
    ("estimate_hrs", || Token::KwEstHrs),
    ("used_hrs",     || Token::KwUsedHrs),
    ("lnf_total",    || Token::KwLnfTotal),
    ("lnf_done",     || Token::KwLnfDone),
    ("elevation",    || Token::KwElevation),
    ("bands",        || Token::KwBands),
    ("metal",        || Token::KwMetal),
    ("access",       || Token::KwAccess),
    ("description",  || Token::KwDescription),
    ("cost_code",    || Token::KwCostCode),
    ("yes",          || Token::KwYes),
    ("no",           || Token::KwNo),
    ("true",         || Token::KwYes),
    ("false",        || Token::KwNo),
    ("ground",       || Token::KwGround),
    ("ladder",       || Token::KwLadder),
    ("rope",         || Token::KwRope),
    ("manlift",      || Token::KwManlift),
];

pub fn lookup(s: &str) -> Option<Token> {
    for (kw, ctor) in KEYWORDS {
        if *kw == s {
            return Some(ctor());
        }
    }
    None
}
