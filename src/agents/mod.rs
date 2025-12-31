// Agents Module
// Logical AI agent scaffolding
// GPT assistant, neural tick clocks, swarm bots

pub mod gpt_assistant;
pub mod neural_tick_clock;
pub mod swarm_bots;

use std::collections::HashMap;

/// Agent system coordinator
pub struct AgentSystem {
    /// Registered agents
    agents: HashMap<String, Agent>,
    /// System tick rate (Hz)
    tick_rate: f64,
}

/// Generic agent
#[derive(Debug, Clone)]
pub struct Agent {
    pub id: String,
    pub agent_type: AgentType,
    pub state: AgentState,
    pub capabilities: Vec<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum AgentType {
    GPTAssistant,
    NeuralTickClock,
    SwarmBot,
    Custom(String),
}

#[derive(Debug, Clone, PartialEq)]
pub enum AgentState {
    Idle,
    Active,
    Processing,
    Suspended,
}

impl AgentSystem {
    /// Create a new agent system
    pub fn new(tick_rate: f64) -> Self {
        AgentSystem {
            agents: HashMap::new(),
            tick_rate,
        }
    }

    /// Register an agent
    pub fn register_agent(&mut self, agent: Agent) {
        self.agents.insert(agent.id.clone(), agent);
    }

    /// Get agent by ID
    pub fn get_agent(&self, id: &str) -> Option<&Agent> {
        self.agents.get(id)
    }

    /// Get all agents of a specific type
    pub fn agents_by_type(&self, agent_type: &AgentType) -> Vec<&Agent> {
        self.agents
            .values()
            .filter(|a| &a.agent_type == agent_type)
            .collect()
    }

    /// Activate an agent
    pub fn activate_agent(&mut self, id: &str) -> Result<(), String> {
        let agent = self.agents
            .get_mut(id)
            .ok_or_else(|| format!("Agent not found: {}", id))?;

        agent.state = AgentState::Active;
        Ok(())
    }

    /// Suspend an agent
    pub fn suspend_agent(&mut self, id: &str) -> Result<(), String> {
        let agent = self.agents
            .get_mut(id)
            .ok_or_else(|| format!("Agent not found: {}", id))?;

        agent.state = AgentState::Suspended;
        Ok(())
    }

    /// Get active agents
    pub fn active_agents(&self) -> Vec<&Agent> {
        self.agents
            .values()
            .filter(|a| a.state == AgentState::Active)
            .collect()
    }

    /// Set system tick rate
    pub fn set_tick_rate(&mut self, hz: f64) {
        self.tick_rate = hz;
    }

    /// Get current tick rate
    pub fn tick_rate(&self) -> f64 {
        self.tick_rate
    }

    /// Execute a system tick
    pub fn tick(&mut self) -> Vec<String> {
        let mut tick_results = Vec::new();

        for agent in self.agents.values() {
            if agent.state == AgentState::Active {
                tick_results.push(format!("Agent {} ticked", agent.id));
            }
        }

        tick_results
    }
}

impl Default for AgentSystem {
    fn default() -> Self {
        Self::new(10.0) // Default 10Hz tick rate (alpha waves)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_register_agent() {
        let mut system = AgentSystem::new(10.0);
        
        let agent = Agent {
            id: "gpt1".to_string(),
            agent_type: AgentType::GPTAssistant,
            state: AgentState::Idle,
            capabilities: vec!["reasoning".to_string(), "code_gen".to_string()],
        };
        
        system.register_agent(agent);
        assert!(system.agents.contains_key("gpt1"));
    }

    #[test]
    fn test_activate_agent() {
        let mut system = AgentSystem::new(10.0);
        
        let agent = Agent {
            id: "agent1".to_string(),
            agent_type: AgentType::SwarmBot,
            state: AgentState::Idle,
            capabilities: vec![],
        };
        
        system.register_agent(agent);
        system.activate_agent("agent1").unwrap();
        
        let agent = system.get_agent("agent1").unwrap();
        assert_eq!(agent.state, AgentState::Active);
    }

    #[test]
    fn test_agents_by_type() {
        let mut system = AgentSystem::new(10.0);
        
        system.register_agent(Agent {
            id: "gpt1".to_string(),
            agent_type: AgentType::GPTAssistant,
            state: AgentState::Idle,
            capabilities: vec![],
        });
        
        system.register_agent(Agent {
            id: "clock1".to_string(),
            agent_type: AgentType::NeuralTickClock,
            state: AgentState::Idle,
            capabilities: vec![],
        });
        
        let gpt_agents = system.agents_by_type(&AgentType::GPTAssistant);
        assert_eq!(gpt_agents.len(), 1);
    }

    #[test]
    fn test_active_agents() {
        let mut system = AgentSystem::new(10.0);
        
        system.register_agent(Agent {
            id: "agent1".to_string(),
            agent_type: AgentType::SwarmBot,
            state: AgentState::Active,
            capabilities: vec![],
        });
        
        system.register_agent(Agent {
            id: "agent2".to_string(),
            agent_type: AgentType::SwarmBot,
            state: AgentState::Idle,
            capabilities: vec![],
        });
        
        let active = system.active_agents();
        assert_eq!(active.len(), 1);
    }

    #[test]
    fn test_tick() {
        let mut system = AgentSystem::new(10.0);
        
        system.register_agent(Agent {
            id: "agent1".to_string(),
            agent_type: AgentType::NeuralTickClock,
            state: AgentState::Active,
            capabilities: vec![],
        });
        
        let results = system.tick();
        assert_eq!(results.len(), 1);
    }

    #[test]
    fn test_tick_rate() {
        let mut system = AgentSystem::new(10.0);
        assert_eq!(system.tick_rate(), 10.0);
        
        system.set_tick_rate(18.0);
        assert_eq!(system.tick_rate(), 18.0);
    }
}
