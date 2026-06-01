// SAGCO Darwin Antibody Engine — first-class immune response types
// Each antibody carries its own name, exit code, and fire() method.
// fire() is diverging (!): it prints and exits — no caller can suppress it.
// License: SSL-1.0 — Strategickhaos DAO LLC

use std::process;

#[derive(Debug, Clone, PartialEq)]
pub enum Antibody {
    EmptyPayload,
    ForeignNode,
    ParseVariance,
    PathDiscovery,
    NetworkPolicy,
    EmptyResponse,
}

impl Antibody {
    pub fn name(&self) -> &'static str {
        match self {
            Antibody::EmptyPayload  => "EMPTY_PAYLOAD_ANTIBODY",
            Antibody::ForeignNode   => "FOREIGN_NODE_ANTIBODY",
            Antibody::ParseVariance => "PARSE_VARIANCE_ANTIBODY",
            Antibody::PathDiscovery => "PATH_DISCOVERY_ANTIBODY",
            Antibody::NetworkPolicy => "NETWORK_POLICY_ANTIBODY",
            Antibody::EmptyResponse => "EMPTY_RESPONSE_ANTIBODY",
        }
    }

    pub fn exit_code(&self) -> i32 {
        match self {
            Antibody::EmptyPayload  => 2,
            Antibody::ForeignNode   => 3,
            Antibody::ParseVariance => 4,
            Antibody::PathDiscovery => 1,
            Antibody::NetworkPolicy => 1,
            Antibody::EmptyResponse => 1,
        }
    }

    pub fn fire(&self, status: &str) -> ! {
        println!("ANTIBODY={}", self.name());
        println!("STATUS={}", status);
        process::exit(self.exit_code());
    }
}
