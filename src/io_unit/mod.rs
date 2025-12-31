// IO Unit Module
// Input/Output: Handles external domains (network, GPS, etc.)

pub mod api_bridge;

use std::collections::HashMap;

/// IO Unit for external system communication
pub struct IOUnit {
    /// Connected external systems
    connections: HashMap<String, Connection>,
    /// Request history
    request_log: Vec<Request>,
}

/// External connection
#[derive(Debug, Clone)]
pub struct Connection {
    pub name: String,
    pub endpoint: String,
    pub status: ConnectionStatus,
    pub last_activity: std::time::Instant,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ConnectionStatus {
    Connected,
    Disconnected,
    Error,
}

/// Request record
#[derive(Debug, Clone)]
pub struct Request {
    pub id: String,
    pub connection_name: String,
    pub request_type: RequestType,
    pub timestamp: std::time::Instant,
    pub response: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum RequestType {
    NetworkPing,
    GPSQuery,
    APICall,
    DataFetch,
}

impl IOUnit {
    /// Create a new IO Unit
    pub fn new() -> Self {
        IOUnit {
            connections: HashMap::new(),
            request_log: Vec::new(),
        }
    }

    /// Register a new external connection
    pub fn register_connection(&mut self, name: String, endpoint: String) {
        let connection = Connection {
            name: name.clone(),
            endpoint,
            status: ConnectionStatus::Disconnected,
            last_activity: std::time::Instant::now(),
        };

        self.connections.insert(name, connection);
    }

    /// Connect to an external system
    pub fn connect(&mut self, name: &str) -> Result<(), String> {
        let connection = self.connections
            .get_mut(name)
            .ok_or_else(|| format!("Connection not found: {}", name))?;

        connection.status = ConnectionStatus::Connected;
        connection.last_activity = std::time::Instant::now();

        Ok(())
    }

    /// Disconnect from external system
    pub fn disconnect(&mut self, name: &str) -> Result<(), String> {
        let connection = self.connections
            .get_mut(name)
            .ok_or_else(|| format!("Connection not found: {}", name))?;

        connection.status = ConnectionStatus::Disconnected;

        Ok(())
    }

    /// Send a request to external system
    pub fn send_request(&mut self, connection_name: &str, request_type: RequestType) -> Result<String, String> {
        let connection = self.connections
            .get(connection_name)
            .ok_or_else(|| format!("Connection not found: {}", connection_name))?;

        if connection.status != ConnectionStatus::Connected {
            return Err("Connection not active".to_string());
        }

        let request_id = format!("req_{}", self.request_log.len());

        // Simulate request (in real implementation, this would make actual API calls)
        let response = self.simulate_request(&request_type, &connection.endpoint);

        let request = Request {
            id: request_id.clone(),
            connection_name: connection_name.to_string(),
            request_type,
            timestamp: std::time::Instant::now(),
            response: Some(response.clone()),
        };

        self.request_log.push(request);

        Ok(response)
    }

    /// Simulate external request (placeholder)
    fn simulate_request(&self, request_type: &RequestType, endpoint: &str) -> String {
        match request_type {
            RequestType::NetworkPing => {
                format!("PONG from {}", endpoint)
            },
            RequestType::GPSQuery => {
                format!("GPS: 42.3601, -71.0589 (simulated)")
            },
            RequestType::APICall => {
                format!("API response from {}", endpoint)
            },
            RequestType::DataFetch => {
                format!("Data from {}", endpoint)
            },
        }
    }

    /// Get connection status
    pub fn connection_status(&self, name: &str) -> Option<ConnectionStatus> {
        self.connections.get(name).map(|c| c.status.clone())
    }

    /// Get all active connections
    pub fn active_connections(&self) -> Vec<&Connection> {
        self.connections
            .values()
            .filter(|c| c.status == ConnectionStatus::Connected)
            .collect()
    }

    /// Get request history
    pub fn request_history(&self) -> &[Request] {
        &self.request_log
    }

    /// Clear request log
    pub fn clear_log(&mut self) {
        self.request_log.clear();
    }
}

impl Default for IOUnit {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_register_connection() {
        let mut io = IOUnit::new();
        io.register_connection("test_api".to_string(), "http://api.example.com".to_string());
        
        assert!(io.connections.contains_key("test_api"));
    }

    #[test]
    fn test_connect_disconnect() {
        let mut io = IOUnit::new();
        io.register_connection("test".to_string(), "http://test.com".to_string());
        
        io.connect("test").unwrap();
        assert_eq!(io.connection_status("test"), Some(ConnectionStatus::Connected));
        
        io.disconnect("test").unwrap();
        assert_eq!(io.connection_status("test"), Some(ConnectionStatus::Disconnected));
    }

    #[test]
    fn test_send_request() {
        let mut io = IOUnit::new();
        io.register_connection("api".to_string(), "http://api.test".to_string());
        io.connect("api").unwrap();
        
        let response = io.send_request("api", RequestType::NetworkPing).unwrap();
        assert!(response.contains("PONG"));
        
        assert_eq!(io.request_log.len(), 1);
    }

    #[test]
    fn test_request_without_connection() {
        let mut io = IOUnit::new();
        io.register_connection("api".to_string(), "http://api.test".to_string());
        
        let result = io.send_request("api", RequestType::APICall);
        assert!(result.is_err());
    }

    #[test]
    fn test_active_connections() {
        let mut io = IOUnit::new();
        io.register_connection("api1".to_string(), "http://api1.test".to_string());
        io.register_connection("api2".to_string(), "http://api2.test".to_string());
        
        io.connect("api1").unwrap();
        
        let active = io.active_connections();
        assert_eq!(active.len(), 1);
        assert_eq!(active[0].name, "api1");
    }
}
