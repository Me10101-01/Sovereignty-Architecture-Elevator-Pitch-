//! GKE Audit Log Parser
//!
//! Parses Google Kubernetes Engine audit logs into structured events
//! for analysis by the Black Ops Lab.

use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

/// Represents a parsed GKE audit event
#[derive(Debug, Clone)]
pub struct AuditEvent {
    pub timestamp: String,
    pub principal_email: String,
    pub method_name: String,
    pub resource_name: String,
    pub request_metadata: HashMap<String, String>,
    pub response_code: Option<i32>,
    pub severity: String,
}

/// Parser for GKE audit logs
pub struct GkeAuditLogParser {
    /// Path to the input log file
    input_path: String,
    /// Filter for specific methods (empty = all)
    method_filter: Vec<String>,
    /// Filter for specific resources (empty = all)
    resource_filter: Vec<String>,
}

impl GkeAuditLogParser {
    /// Create a new parser instance
    pub fn new(input_path: &str) -> Self {
        Self {
            input_path: input_path.to_string(),
            method_filter: Vec::new(),
            resource_filter: Vec::new(),
        }
    }

    /// Add method name filter
    pub fn with_method_filter(mut self, methods: Vec<String>) -> Self {
        self.method_filter = methods;
        self
    }

    /// Add resource name filter
    pub fn with_resource_filter(mut self, resources: Vec<String>) -> Self {
        self.resource_filter = resources;
        self
    }

    /// Parse the log file and return events
    pub fn parse(&self) -> Result<Vec<AuditEvent>, String> {
        let path = Path::new(&self.input_path);
        if !path.exists() {
            return Err(format!("Input file not found: {}", self.input_path));
        }

        let file = File::open(path)
            .map_err(|e| format!("Failed to open file: {}", e))?;
        let reader = BufReader::new(file);

        let mut events = Vec::new();

        for (line_num, line_result) in reader.lines().enumerate() {
            let line = line_result
                .map_err(|e| format!("Failed to read line {}: {}", line_num, e))?;
            
            if line.trim().is_empty() {
                continue;
            }

            match self.parse_line(&line) {
                Ok(Some(event)) => {
                    if self.matches_filters(&event) {
                        events.push(event);
                    }
                }
                Ok(None) => continue,
                Err(e) => {
                    eprintln!("Warning: Failed to parse line {}: {}", line_num, e);
                }
            }
        }

        Ok(events)
    }

    /// Parse a single log line
    /// 
    /// STUB: This method needs to be implemented by an AI agent.
    /// See docs/BLACK_OPS_LAB.md for the SWARM-HS process.
    /// 
    /// Expected implementation:
    /// 1. Parse JSON line using serde_json
    /// 2. Extract AuditEvent fields from GKE audit log schema
    /// 3. Handle parsing errors gracefully
    fn parse_line(&self, _line: &str) -> Result<Option<AuditEvent>, String> {
        // STUB: Returns None until implemented
        // Use SWARM-HS to implement: send logs to an AI agent with clear intent
        Ok(None)
    }

    /// Check if event matches configured filters
    fn matches_filters(&self, event: &AuditEvent) -> bool {
        // Check method filter
        if !self.method_filter.is_empty() 
            && !self.method_filter.contains(&event.method_name) {
            return false;
        }

        // Check resource filter
        if !self.resource_filter.is_empty() {
            let matches_resource = self.resource_filter.iter()
                .any(|r| event.resource_name.contains(r));
            if !matches_resource {
                return false;
            }
        }

        true
    }
}

/// Extract lease-related events from audit logs
pub fn extract_lease_events(events: &[AuditEvent]) -> Vec<&AuditEvent> {
    events.iter()
        .filter(|e| e.resource_name.contains("leases"))
        .collect()
}

/// Extract autoscaler-related events from audit logs
pub fn extract_autoscaler_events(events: &[AuditEvent]) -> Vec<&AuditEvent> {
    events.iter()
        .filter(|e| {
            e.resource_name.contains("nodepools") 
            || e.method_name.contains("autoscal")
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parser_creation() {
        let parser = GkeAuditLogParser::new("test.json");
        assert_eq!(parser.input_path, "test.json");
    }

    #[test]
    fn test_filter_methods() {
        let parser = GkeAuditLogParser::new("test.json")
            .with_method_filter(vec!["create".to_string()]);
        assert_eq!(parser.method_filter.len(), 1);
    }

    #[test]
    fn test_matches_empty_filters() {
        let parser = GkeAuditLogParser::new("test.json");
        let event = AuditEvent {
            timestamp: "2024-01-15T10:00:00Z".to_string(),
            principal_email: "test@example.com".to_string(),
            method_name: "create".to_string(),
            resource_name: "leases/test".to_string(),
            request_metadata: HashMap::new(),
            response_code: Some(200),
            severity: "INFO".to_string(),
        };
        assert!(parser.matches_filters(&event));
    }
}
