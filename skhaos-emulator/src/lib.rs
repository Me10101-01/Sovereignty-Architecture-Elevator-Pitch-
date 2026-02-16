// SkhaOS Emulator - Main Library
// Quantum-addressed sovereign architecture with UDAP

pub mod alu;
pub mod control_unit;
pub mod entanglement_core;
pub mod register_memory;
pub mod io_unit;
pub mod agents;

// Re-export commonly used types
pub use control_unit::udap_parser::UdapAddress;

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_udap_parse() {
        let addr = UdapAddress::parse("skhaos://net/192.168.1.1/80/tcp").unwrap();
        assert_eq!(addr.domain, "net");
    }
}
