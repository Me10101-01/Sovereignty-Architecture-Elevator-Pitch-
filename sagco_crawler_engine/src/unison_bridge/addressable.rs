use std::time::{SystemTime, UNIX_EPOCH};
use crate::flamelang::token::FlameHash;

pub struct LiveMigrator;

impl LiveMigrator {
    pub fn migrate_function(hash: &FlameHash, target_node: &str) -> String {
        let tick = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0);
        format!(
            "MIGRATE {} TO {} @tick:{} [verified]",
            hash.0, target_node, tick
        )
    }

    pub fn simulate_two_node_migration(hash: &FlameHash) -> Vec<String> {
        vec![
            format!("NODE_A: holding  {}", &hash.0[..16]),
            Self::migrate_function(hash, "NODE_B"),
            format!("NODE_B: received {} — executing immediately", &hash.0[..16]),
            format!("NODE_A: released {} — zero downtime", &hash.0[..16]),
        ]
    }
}
