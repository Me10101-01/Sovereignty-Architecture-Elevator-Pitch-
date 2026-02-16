// Control Unit Module
// Orchestrates system flows and UDAP routing
// Maps Network (IP:Port) to Mood (Hz/Color/State)

pub mod udap_parser;
pub mod swarm_orchestrator;

use std::collections::HashMap;

/// Control Unit for system orchestration
pub struct ControlUnit {
    /// Routing table: UDAP domain -> Handler
    routing_table: HashMap<String, RouteHandler>,
    /// Active connections/sessions
    sessions: Vec<Session>,
}

/// Route handler types
#[derive(Debug, Clone)]
pub enum RouteHandler {
    ALU,
    EntanglementCore,
    RegisterMemory,
    IOUnit,
    SwarmBot,
}

/// Session tracking
#[derive(Debug, Clone)]
pub struct Session {
    pub id: String,
    pub domain: String,
    pub state: SessionState,
}

#[derive(Debug, Clone)]
pub enum SessionState {
    Active,
    Idle,
    Processing,
    Complete,
}

impl ControlUnit {
    /// Create a new Control Unit
    pub fn new() -> Self {
        let mut routing_table = HashMap::new();
        
        // Initialize default routes
        routing_table.insert("pipe".to_string(), RouteHandler::ALU);
        routing_table.insert("neural".to_string(), RouteHandler::ALU);
        routing_table.insert("mood".to_string(), RouteHandler::RegisterMemory);
        routing_table.insert("chess".to_string(), RouteHandler::EntanglementCore);
        routing_table.insert("gps".to_string(), RouteHandler::EntanglementCore);
        routing_table.insert("network".to_string(), RouteHandler::IOUnit);
        routing_table.insert("quantum".to_string(), RouteHandler::ALU);
        
        ControlUnit {
            routing_table,
            sessions: Vec::new(),
        }
    }

    /// Route a UDAP address to appropriate handler
    pub fn route(&self, udap_address: &str) -> Result<RouteHandler, String> {
        // Parse domain from UDAP address
        let domain = self.extract_domain(udap_address)?;
        
        self.routing_table
            .get(&domain)
            .cloned()
            .ok_or_else(|| format!("No handler for domain: {}", domain))
    }

    /// Extract domain from UDAP address
    fn extract_domain(&self, udap_address: &str) -> Result<String, String> {
        if !udap_address.starts_with("skhaos://") {
            return Err("Invalid UDAP prefix".to_string());
        }
        
        let without_prefix = &udap_address[9..]; // Remove "skhaos://"
        let domain = without_prefix.split('/')
            .next()
            .ok_or("Missing domain")?;
        
        Ok(domain.to_string())
    }

    /// Create a new session
    pub fn create_session(&mut self, domain: String) -> String {
        let id = format!("session_{}", self.sessions.len());
        let session = Session {
            id: id.clone(),
            domain,
            state: SessionState::Active,
        };
        
        self.sessions.push(session);
        id
    }

    /// Update session state
    pub fn update_session(&mut self, session_id: &str, state: SessionState) -> Result<(), String> {
        self.sessions
            .iter_mut()
            .find(|s| s.id == session_id)
            .map(|s| s.state = state)
            .ok_or_else(|| format!("Session not found: {}", session_id))
    }

    /// Get active sessions
    pub fn active_sessions(&self) -> Vec<&Session> {
        self.sessions
            .iter()
            .filter(|s| matches!(s.state, SessionState::Active))
            .collect()
    }

    /// Register a custom route
    pub fn register_route(&mut self, domain: String, handler: RouteHandler) {
        self.routing_table.insert(domain, handler);
    }
}

impl Default for ControlUnit {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_route_pipe_domain() {
        let cu = ControlUnit::new();
        let result = cu.route("skhaos://pipe/run/5/offset/3");
        
        assert!(result.is_ok());
        assert!(matches!(result.unwrap(), RouteHandler::ALU));
    }

    #[test]
    fn test_route_neural_domain() {
        let cu = ControlUnit::new();
        let result = cu.route("skhaos://neural/layer/2/neuron/5");
        
        assert!(result.is_ok());
        assert!(matches!(result.unwrap(), RouteHandler::ALU));
    }

    #[test]
    fn test_route_mood_domain() {
        let cu = ControlUnit::new();
        let result = cu.route("skhaos://mood/beta/high?hz=18");
        
        assert!(result.is_ok());
        assert!(matches!(result.unwrap(), RouteHandler::RegisterMemory));
    }

    #[test]
    fn test_invalid_udap() {
        let cu = ControlUnit::new();
        let result = cu.route("http://invalid/address");
        
        assert!(result.is_err());
    }

    #[test]
    fn test_session_management() {
        let mut cu = ControlUnit::new();
        let session_id = cu.create_session("pipe".to_string());
        
        assert_eq!(cu.sessions.len(), 1);
        
        let update_result = cu.update_session(&session_id, SessionState::Complete);
        assert!(update_result.is_ok());
        
        let active = cu.active_sessions();
        assert_eq!(active.len(), 0);
    }

    #[test]
    fn test_custom_route() {
        let mut cu = ControlUnit::new();
        cu.register_route("custom".to_string(), RouteHandler::SwarmBot);
        
        let result = cu.route("skhaos://custom/test");
        assert!(result.is_ok());
        assert!(matches!(result.unwrap(), RouteHandler::SwarmBot));
    }
}
