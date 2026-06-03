/// ingestion_bus.rs
/// SAGCO-Core Ingestion Bus — domain router for all input types.
///
/// Every command enters here. The bus identifies the domain,
/// validates the token stream, and dispatches to the right engine.
///
/// Domains:
///   bubble      → BubbleEngine (rope access state machine)
///   geo         → GeometryEngine (distance, coordinates)
///   tri         → TriangulationEngine (3-anchor position)
///   units       → UnitsEngine (conversion, RPM→voltage)
///   pmi         → PMIEngine (concept association scoring)
///   transistor  → TransistorEngine (signal switching)
///   freq        → FreqEngine (frequency / waveform)
///   math        → MathEngine (proof, calculation)
///   proof       → ProofEngine (deterministic verification)
///   search      → SearchEngine (corpus query)
///   omni        → OmniEngine (cross-domain synthesis)

use crate::lexer::{Token, lex};

#[derive(Debug, Clone, PartialEq)]
pub enum Domain {
    Bubble,
    Geo,
    Tri,
    Units,
    Pmi,
    Transistor,
    Freq,
    Math,
    Proof,
    Search,
    Omni,
    Unknown(String),
}

impl Domain {
    pub fn from_str(s: &str) -> Self {
        match s {
            "bubble"     => Domain::Bubble,
            "geo"        => Domain::Geo,
            "tri"        => Domain::Tri,
            "units"      => Domain::Units,
            "pmi"        => Domain::Pmi,
            "transistor" => Domain::Transistor,
            "freq"       => Domain::Freq,
            "math"       => Domain::Math,
            "proof"      => Domain::Proof,
            "search"     => Domain::Search,
            "omni"       => Domain::Omni,
            other        => Domain::Unknown(other.to_string()),
        }
    }
}

#[derive(Debug)]
pub struct RoutedInput {
    pub domain:   Domain,
    pub tokens:   Vec<Token>,
    pub raw:      String,
}

pub struct IngestionBus;

impl IngestionBus {
    pub fn ingest(raw: &str) -> Result<RoutedInput, String> {
        let tokens = lex(raw).map_err(|e| {
            format!("Lex error at position {}: unknown token '{}'", e.pos, e.token)
        })?;

        // First token determines the domain.
        // If it's an Ident that looks like a bubble ID (RB-xxx), route to Bubble.
        let domain = match tokens.first() {
            Some(Token::Domain(d)) => Domain::from_str(d),
            Some(Token::Ident(id)) if id.starts_with("RB-") => Domain::Bubble,
            Some(Token::Ident(id)) if id.starts_with("P")   => Domain::Units,
            Some(other) => return Err(format!("Expected domain keyword, got {:?}", other)),
            None => return Err("Empty input".to_string()),
        };

        Ok(RoutedInput { domain, tokens, raw: raw.to_string() })
    }
}

// ─── TESTS ─────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bubble_routing() {
        let r = IngestionBus::ingest("RB-001 4 27 1 0 N E UP").unwrap();
        assert_eq!(r.domain, Domain::Bubble);
    }

    #[test]
    fn test_geo_routing() {
        let r = IngestionBus::ingest("geo dist2unit").unwrap();
        assert_eq!(r.domain, Domain::Geo);
    }

    #[test]
    fn test_tri_routing() {
        let r = IngestionBus::ingest("tri 0 0 5 10 0 5 5 10 5").unwrap();
        assert_eq!(r.domain, Domain::Tri);
    }

    #[test]
    fn test_units_routing() {
        let r = IngestionBus::ingest("units rpmvolt P1 3200 0.0025").unwrap();
        assert_eq!(r.domain, Domain::Units);
    }

    #[test]
    fn test_unknown_domain() {
        // A non-domain word that isn't an RB identifier
        let result = IngestionBus::ingest("42 bad input");
        assert!(result.is_err());
    }
}
