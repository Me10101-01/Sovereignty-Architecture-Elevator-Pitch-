// Swarm Orchestrator - Mutates MIDI-to-Hz mappings

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SwarmBot {
    pub id: u32,
    pub state: String,
    pub target_hz: f64,
}

pub struct SwarmOrchestrator {
    bots: Vec<SwarmBot>,
}

impl SwarmOrchestrator {
    pub fn new(bot_count: u32) -> Self {
        let bots = (0..bot_count)
            .map(|id| SwarmBot {
                id,
                state: "idle".to_string(),
                target_hz: 440.0,
            })
            .collect();
        
        SwarmOrchestrator { bots }
    }
    
    /// Evolve MIDI-to-Hz mappings through mutation
    pub fn evolve_mapping(&mut self, base_hz: f64) -> Vec<f64> {
        self.bots.iter().enumerate().map(|(i, _bot)| {
            // Mutate frequency with slight variations
            let mutation = (i as f64 * 0.1) - 0.5;
            base_hz * (1.0 + mutation)
        }).collect()
    }
    
    /// Parallel reconnaissance across bots
    pub fn parallel_recon(&mut self, uri: &str) -> Vec<String> {
        self.bots.iter_mut().map(|bot| {
            bot.state = "active".to_string();
            format!("Bot {} probing {}", bot.id, uri)
        }).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_swarm_creation() {
        let swarm = SwarmOrchestrator::new(5);
        assert_eq!(swarm.bots.len(), 5);
    }
    
    #[test]
    fn test_evolve_mapping() {
        let mut swarm = SwarmOrchestrator::new(3);
        let evolved = swarm.evolve_mapping(440.0);
        assert_eq!(evolved.len(), 3);
    }
}
