// Control Unit - UDAP Parser
// Parses and routes UDAP addresses across domains

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UdapAddress {
    pub uri: String,
    pub domain: String,
    pub x: String,
    pub y: String,
    pub z: String,
    pub properties: HashMap<String, String>,
}

impl UdapAddress {
    /// Parse a UDAP URI: skhaos://domain/x/y/z?key=value&key2=value2
    pub fn parse(uri: &str) -> Result<Self, String> {
        if !uri.starts_with("skhaos://") {
            return Err("URI must start with 'skhaos://'".to_string());
        }
        
        let without_scheme = uri.trim_start_matches("skhaos://");
        let parts: Vec<&str> = without_scheme.split('?').collect();
        
        if parts.is_empty() {
            return Err("Invalid URI format".to_string());
        }
        
        let path_parts: Vec<&str> = parts[0].split('/').collect();
        
        if path_parts.len() < 4 {
            return Err("URI must have format: skhaos://domain/x/y/z".to_string());
        }
        
        let domain = path_parts[0].to_string();
        let x = path_parts[1].to_string();
        let y = path_parts[2].to_string();
        let z = path_parts[3].to_string();
        
        let mut properties = HashMap::new();
        if parts.len() > 1 {
            for pair in parts[1].split('&') {
                let kv: Vec<&str> = pair.split('=').collect();
                if kv.len() == 2 {
                    properties.insert(kv[0].to_string(), kv[1].to_string());
                }
            }
        }
        
        Ok(UdapAddress {
            uri: uri.to_string(),
            domain,
            x,
            y,
            z,
            properties,
        })
    }
    
    /// Check if this address is for browser/proxy domain
    pub fn is_proxy(&self) -> bool {
        matches!(self.domain.as_str(), "browser" | "proxy")
    }
    
    /// Check if this address is for audio/music domain
    pub fn is_audio(&self) -> bool {
        self.domain == "audio"
    }
    
    /// Check if this address is for recon domain
    pub fn is_recon(&self) -> bool {
        self.domain == "recon"
    }
    
    /// Get property value
    pub fn get_property(&self, key: &str) -> Option<&String> {
        self.properties.get(key)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_parse_basic_uri() {
        let addr = UdapAddress::parse("skhaos://net/192.168.1.1/80/tcp").unwrap();
        assert_eq!(addr.domain, "net");
        assert_eq!(addr.x, "192.168.1.1");
        assert_eq!(addr.y, "80");
        assert_eq!(addr.z, "tcp");
    }
    
    #[test]
    fn test_parse_uri_with_properties() {
        let addr = UdapAddress::parse("skhaos://browser/127.0.0.1/8080/proxy?sovereign=true&sim=wave").unwrap();
        assert_eq!(addr.domain, "browser");
        assert_eq!(addr.get_property("sovereign"), Some(&"true".to_string()));
        assert_eq!(addr.get_property("sim"), Some(&"wave".to_string()));
    }
    
    #[test]
    fn test_is_proxy() {
        let addr = UdapAddress::parse("skhaos://proxy/127.0.0.1/8080/http").unwrap();
        assert!(addr.is_proxy());
    }
    
    #[test]
    fn test_is_audio() {
        let addr = UdapAddress::parse("skhaos://audio/440/A4/piece1").unwrap();
        assert!(addr.is_audio());
    }
}
