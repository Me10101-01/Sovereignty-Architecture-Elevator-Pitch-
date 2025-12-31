// SkhaOS Emulator Library
// Main library entry point for quantum-symbolic processor modules

pub mod alu;
pub mod control_unit;
pub mod entanglement_core;
pub mod register_memory;
pub mod io_unit;
pub mod agents;

/// SkhaOS version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// UDAP scheme
pub const UDAP_SCHEME: &str = "skhaos://";

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert!(!VERSION.is_empty());
    }

    #[test]
    fn test_udap_scheme() {
        assert_eq!(UDAP_SCHEME, "skhaos://");
    }
}
