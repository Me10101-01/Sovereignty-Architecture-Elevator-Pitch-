// Entanglement Core Module
// Links domains through isomorphisms (Chess/GPS/Frequency/Pipe/Neural)
// Implements quantum-inspired superposition states

pub mod domain_mapper;
pub mod superposition_sim;

use std::collections::HashMap;

/// Entanglement Core - manages domain relationships
pub struct EntanglementCore {
    /// Domain mappings: (domain1, domain2) -> mapping_function
    mappings: HashMap<(String, String), Box<dyn Fn(&str) -> Result<String, String>>>,
    /// Entangled pairs tracking
    entangled_pairs: Vec<EntangledPair>,
}

/// Represents an entangled pair of domain elements
#[derive(Debug, Clone)]
pub struct EntangledPair {
    pub domain1: String,
    pub address1: String,
    pub domain2: String,
    pub address2: String,
    pub correlation: f64,
}

impl EntanglementCore {
    /// Create a new Entanglement Core
    pub fn new() -> Self {
        EntanglementCore {
            mappings: HashMap::new(),
            entangled_pairs: Vec::new(),
        }
    }

    /// Create entanglement between two domain addresses
    pub fn entangle(&mut self, addr1: &str, addr2: &str, correlation: f64) -> Result<(), String> {
        // Parse domains from addresses
        let domain1 = self.extract_domain(addr1)?;
        let domain2 = self.extract_domain(addr2)?;

        let pair = EntangledPair {
            domain1: domain1.clone(),
            address1: addr1.to_string(),
            domain2: domain2.clone(),
            address2: addr2.to_string(),
            correlation,
        };

        self.entangled_pairs.push(pair);
        Ok(())
    }

    /// Find entangled addresses for a given address
    pub fn find_entangled(&self, address: &str) -> Vec<&EntangledPair> {
        self.entangled_pairs
            .iter()
            .filter(|p| p.address1 == address || p.address2 == address)
            .collect()
    }

    /// Measure correlation between two addresses
    pub fn measure_correlation(&self, addr1: &str, addr2: &str) -> Option<f64> {
        self.entangled_pairs
            .iter()
            .find(|p| {
                (p.address1 == addr1 && p.address2 == addr2) ||
                (p.address1 == addr2 && p.address2 == addr1)
            })
            .map(|p| p.correlation)
    }

    /// Register a bidirectional mapping between domains
    pub fn register_mapping<F>(&mut self, domain1: &str, domain2: &str, mapper: F)
    where
        F: Fn(&str) -> Result<String, String> + 'static + Clone,
    {
        let key1 = (domain1.to_string(), domain2.to_string());
        let key2 = (domain2.to_string(), domain1.to_string());
        
        self.mappings.insert(key1, Box::new(mapper.clone()));
        self.mappings.insert(key2, Box::new(mapper));
    }

    /// Transform address from one domain to another
    pub fn transform(&self, from_address: &str, to_domain: &str) -> Result<String, String> {
        let from_domain = self.extract_domain(from_address)?;
        let key = (from_domain.clone(), to_domain.to_string());

        let mapper = self.mappings
            .get(&key)
            .ok_or_else(|| format!("No mapping from {} to {}", from_domain, to_domain))?;

        mapper(from_address)
    }

    /// Extract domain from UDAP address
    fn extract_domain(&self, address: &str) -> Result<String, String> {
        if !address.starts_with("skhaos://") {
            return Err("Invalid UDAP address".to_string());
        }

        let without_prefix = &address[9..];
        let domain = without_prefix.split('/')
            .next()
            .ok_or("Missing domain")?;

        Ok(domain.to_string())
    }

    /// Get all entangled pairs for a specific domain
    pub fn domain_entanglements(&self, domain: &str) -> Vec<&EntangledPair> {
        self.entangled_pairs
            .iter()
            .filter(|p| p.domain1 == domain || p.domain2 == domain)
            .collect()
    }

    /// Calculate average correlation for a domain
    pub fn average_correlation(&self, domain: &str) -> f64 {
        let pairs = self.domain_entanglements(domain);
        if pairs.is_empty() {
            return 0.0;
        }

        let sum: f64 = pairs.iter().map(|p| p.correlation).sum();
        sum / pairs.len() as f64
    }
}

impl Default for EntanglementCore {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_entangle() {
        let mut core = EntanglementCore::new();
        
        let result = core.entangle(
            "skhaos://chess/file/e/rank/4",
            "skhaos://gps/lat/42.3601/long/-71.0589",
            0.95
        );
        
        assert!(result.is_ok());
        assert_eq!(core.entangled_pairs.len(), 1);
    }

    #[test]
    fn test_find_entangled() {
        let mut core = EntanglementCore::new();
        
        core.entangle(
            "skhaos://chess/file/e/rank/4",
            "skhaos://gps/lat/42.3601/long/-71.0589",
            0.95
        ).unwrap();
        
        let entangled = core.find_entangled("skhaos://chess/file/e/rank/4");
        assert_eq!(entangled.len(), 1);
    }

    #[test]
    fn test_measure_correlation() {
        let mut core = EntanglementCore::new();
        
        let addr1 = "skhaos://pipe/run/5";
        let addr2 = "skhaos://neural/layer/3";
        
        core.entangle(addr1, addr2, 0.85).unwrap();
        
        let correlation = core.measure_correlation(addr1, addr2);
        assert_eq!(correlation, Some(0.85));
    }

    #[test]
    fn test_domain_entanglements() {
        let mut core = EntanglementCore::new();
        
        core.entangle(
            "skhaos://chess/file/e/rank/4",
            "skhaos://gps/lat/42.3601/long/-71.0589",
            0.95
        ).unwrap();
        
        core.entangle(
            "skhaos://chess/file/d/rank/4",
            "skhaos://pipe/run/5/offset/3",
            0.80
        ).unwrap();
        
        let chess_entanglements = core.domain_entanglements("chess");
        assert_eq!(chess_entanglements.len(), 2);
    }

    #[test]
    fn test_average_correlation() {
        let mut core = EntanglementCore::new();
        
        core.entangle("skhaos://pipe/run/5", "skhaos://neural/layer/3", 0.8).unwrap();
        core.entangle("skhaos://pipe/run/10", "skhaos://chess/file/e/rank/4", 0.6).unwrap();
        
        let avg = core.average_correlation("pipe");
        assert!((avg - 0.7).abs() < 0.01);
    }
}
