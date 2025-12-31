// UDAP Parser Module
// Parses skhaos:// URIs and dispatches to appropriate modules
// Format: skhaos://domain/subdomain/resource?parameters

use std::collections::HashMap;

/// Parsed UDAP address structure
#[derive(Debug, Clone, PartialEq)]
pub struct UDAPAddress {
    pub domain: String,
    pub path: Vec<String>,
    pub parameters: HashMap<String, String>,
}

impl UDAPAddress {
    /// Parse a UDAP URI string
    pub fn parse(uri: &str) -> Result<Self, String> {
        if !uri.starts_with("skhaos://") {
            return Err("Invalid UDAP scheme. Must start with 'skhaos://'".to_string());
        }

        // Remove the scheme
        let without_scheme = &uri[9..];

        // Split on query separator
        let parts: Vec<&str> = without_scheme.split('?').collect();
        let path_part = parts[0];
        let query_part = parts.get(1);

        // Parse path
        let path_components: Vec<String> = path_part
            .split('/')
            .filter(|s| !s.is_empty())
            .map(|s| s.to_string())
            .collect();

        if path_components.is_empty() {
            return Err("Empty path in UDAP address".to_string());
        }

        let domain = path_components[0].clone();
        let path = path_components[1..].to_vec();

        // Parse query parameters
        let mut parameters = HashMap::new();
        if let Some(query) = query_part {
            for param in query.split('&') {
                let kv: Vec<&str> = param.split('=').collect();
                if kv.len() == 2 {
                    parameters.insert(kv[0].to_string(), kv[1].to_string());
                }
            }
        }

        Ok(UDAPAddress {
            domain,
            path,
            parameters,
        })
    }

    /// Build a UDAP URI from components
    pub fn build(domain: &str, path: &[&str], parameters: &HashMap<String, String>) -> String {
        let mut uri = format!("skhaos://{}", domain);
        
        for component in path {
            uri.push('/');
            uri.push_str(component);
        }

        if !parameters.is_empty() {
            uri.push('?');
            let param_strings: Vec<String> = parameters
                .iter()
                .map(|(k, v)| format!("{}={}", k, v))
                .collect();
            uri.push_str(&param_strings.join("&"));
        }

        uri
    }

    /// Get a specific parameter value
    pub fn get_param(&self, key: &str) -> Option<&String> {
        self.parameters.get(key)
    }

    /// Get parameter as f64
    pub fn get_param_f64(&self, key: &str) -> Option<f64> {
        self.parameters.get(key)?.parse().ok()
    }

    /// Get parameter as usize
    pub fn get_param_usize(&self, key: &str) -> Option<usize> {
        self.parameters.get(key)?.parse().ok()
    }

    /// Check if path matches a pattern
    pub fn matches_path(&self, pattern: &[&str]) -> bool {
        if self.path.len() != pattern.len() {
            return false;
        }

        self.path.iter()
            .zip(pattern.iter())
            .all(|(p, pat)| p == pat || *pat == "*")
    }

    /// Convert to string representation
    pub fn to_string(&self) -> String {
        Self::build(&self.domain, &self.path.iter().map(|s| s.as_str()).collect::<Vec<_>>(), &self.parameters)
    }
}

/// UDAP dispatcher routes addresses to handlers
pub struct UDAPDispatcher {
    handlers: HashMap<String, Box<dyn Fn(&UDAPAddress) -> Result<String, String>>>,
}

impl UDAPDispatcher {
    pub fn new() -> Self {
        UDAPDispatcher {
            handlers: HashMap::new(),
        }
    }

    /// Register a handler for a specific domain
    pub fn register_handler<F>(&mut self, domain: &str, handler: F)
    where
        F: Fn(&UDAPAddress) -> Result<String, String> + 'static,
    {
        self.handlers.insert(domain.to_string(), Box::new(handler));
    }

    /// Dispatch a UDAP address to the appropriate handler
    pub fn dispatch(&self, uri: &str) -> Result<String, String> {
        let address = UDAPAddress::parse(uri)?;
        
        let handler = self.handlers
            .get(&address.domain)
            .ok_or_else(|| format!("No handler registered for domain: {}", address.domain))?;

        handler(&address)
    }
}

impl Default for UDAPDispatcher {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple_udap() {
        let uri = "skhaos://pipe/run/5";
        let addr = UDAPAddress::parse(uri).unwrap();
        
        assert_eq!(addr.domain, "pipe");
        assert_eq!(addr.path, vec!["run", "5"]);
        assert!(addr.parameters.is_empty());
    }

    #[test]
    fn test_parse_with_parameters() {
        let uri = "skhaos://neural/layer/2/neuron/5?value=0.75&activated=true";
        let addr = UDAPAddress::parse(uri).unwrap();
        
        assert_eq!(addr.domain, "neural");
        assert_eq!(addr.path, vec!["layer", "2", "neuron", "5"]);
        assert_eq!(addr.get_param("value"), Some(&"0.75".to_string()));
        assert_eq!(addr.get_param("activated"), Some(&"true".to_string()));
    }

    #[test]
    fn test_parse_invalid_scheme() {
        let uri = "http://invalid/address";
        let result = UDAPAddress::parse(uri);
        
        assert!(result.is_err());
    }

    #[test]
    fn test_build_udap() {
        let mut params = HashMap::new();
        params.insert("angle".to_string(), "45".to_string());
        params.insert("offset".to_string(), "10".to_string());
        
        let uri = UDAPAddress::build("pipe", &["run", "5", "offset", "3"], &params);
        
        assert!(uri.starts_with("skhaos://pipe/run/5/offset/3?"));
        assert!(uri.contains("angle=45"));
        assert!(uri.contains("offset=10"));
    }

    #[test]
    fn test_get_param_typed() {
        let uri = "skhaos://mood/beta?hz=18&intensity=0.75";
        let addr = UDAPAddress::parse(uri).unwrap();
        
        assert_eq!(addr.get_param_f64("hz"), Some(18.0));
        assert_eq!(addr.get_param_f64("intensity"), Some(0.75));
    }

    #[test]
    fn test_matches_path() {
        let uri = "skhaos://pipe/run/5/offset/3";
        let addr = UDAPAddress::parse(uri).unwrap();
        
        assert!(addr.matches_path(&["run", "5", "offset", "3"]));
        assert!(addr.matches_path(&["run", "*", "offset", "*"]));
        assert!(!addr.matches_path(&["run", "5"]));
    }

    #[test]
    fn test_dispatcher() {
        let mut dispatcher = UDAPDispatcher::new();
        
        dispatcher.register_handler("test", |addr| {
            Ok(format!("Handled: {}", addr.domain))
        });
        
        let result = dispatcher.dispatch("skhaos://test/resource").unwrap();
        assert_eq!(result, "Handled: test");
    }

    #[test]
    fn test_dispatcher_no_handler() {
        let dispatcher = UDAPDispatcher::new();
        let result = dispatcher.dispatch("skhaos://unknown/resource");
        
        assert!(result.is_err());
    }

    #[test]
    fn test_roundtrip() {
        let original = "skhaos://pipe/run/5/offset/3?angle=45";
        let addr = UDAPAddress::parse(original).unwrap();
        let rebuilt = addr.to_string();
        
        // Parse again to ensure consistency
        let addr2 = UDAPAddress::parse(&rebuilt).unwrap();
        
        assert_eq!(addr.domain, addr2.domain);
        assert_eq!(addr.path, addr2.path);
        assert_eq!(addr.parameters, addr2.parameters);
    }
}
