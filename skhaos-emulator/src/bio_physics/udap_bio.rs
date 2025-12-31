// UDAP Bio-Physics URI Extensions
//
// Extends UDAP (Universal Domain Addressing Protocol) with bio-physics parameters:
// - skhaos://bio/zipf/unit/rank?law=entropy&hz=20
// - skhaos://bio/dolphin/whistle?signature=true&hz=10
// - skhaos://physics/rondo/law=conservation&hz=10

use std::collections::HashMap;

/// UDAP URI parser and builder for bio-physics domains
pub struct UdapBio {
    scheme: String,
    domain: String,
    path_segments: Vec<String>,
    query_params: HashMap<String, String>,
}

impl UdapBio {
    /// Create new UDAP bio URI builder
    pub fn new() -> Self {
        UdapBio {
            scheme: "skhaos".to_string(),
            domain: String::new(),
            path_segments: Vec::new(),
            query_params: HashMap::new(),
        }
    }

    /// Parse existing UDAP URI
    pub fn parse(uri: &str) -> Result<Self, UdapError> {
        // Format: skhaos://domain/path1/path2?param1=value1&param2=value2
        
        if !uri.starts_with("skhaos://") {
            return Err(UdapError::InvalidScheme(uri.to_string()));
        }

        let without_scheme = &uri[9..]; // Skip "skhaos://"
        let parts: Vec<&str> = without_scheme.splitn(2, '?').collect();
        
        let path_part = parts[0];
        let query_part = if parts.len() > 1 { parts[1] } else { "" };

        // Parse path
        let path_components: Vec<&str> = path_part.split('/').collect();
        if path_components.is_empty() {
            return Err(UdapError::InvalidPath(uri.to_string()));
        }

        let domain = path_components[0].to_string();
        let path_segments: Vec<String> = path_components[1..].iter().map(|s| s.to_string()).collect();

        // Parse query parameters
        let mut query_params = HashMap::new();
        if !query_part.is_empty() {
            for param in query_part.split('&') {
                let kv: Vec<&str> = param.splitn(2, '=').collect();
                if kv.len() == 2 {
                    query_params.insert(kv[0].to_string(), kv[1].to_string());
                }
            }
        }

        Ok(UdapBio {
            scheme: "skhaos".to_string(),
            domain,
            path_segments,
            query_params,
        })
    }

    /// Build bio domain URI (whale/dolphin)
    pub fn bio(resource_type: BioResourceType) -> Self {
        let mut udap = Self::new();
        udap.domain = "bio".to_string();
        
        match resource_type {
            BioResourceType::ZipfUnit(rank) => {
                udap.path_segments = vec!["zipf".to_string(), "unit".to_string(), rank.to_string()];
            }
            BioResourceType::ZipfPhrase => {
                udap.path_segments = vec!["zipf".to_string(), "phrase".to_string()];
            }
            BioResourceType::DolphinWhistle(signature) => {
                udap.path_segments = vec!["dolphin".to_string(), "whistle".to_string()];
                if signature {
                    udap.query_params.insert("signature".to_string(), "true".to_string());
                }
            }
            BioResourceType::DolphinClick(burst_count) => {
                udap.path_segments = vec!["dolphin".to_string(), "click".to_string()];
                udap.query_params.insert("burst".to_string(), burst_count.to_string());
            }
            BioResourceType::DolphinDialect(pod) => {
                udap.path_segments = vec!["dolphin".to_string(), "dialect".to_string()];
                udap.query_params.insert("pod".to_string(), pod);
            }
        }
        
        udap
    }

    /// Build physics domain URI
    pub fn physics(form: MusicalForm, law: PhysicsLaw) -> Self {
        let mut udap = Self::new();
        udap.domain = "physics".to_string();
        
        let form_str = match form {
            MusicalForm::Rondo => "rondo",
            MusicalForm::Sonata => "sonata",
            MusicalForm::Fugue => "fugue",
            MusicalForm::Canon => "canon",
            MusicalForm::Variation => "variation",
            MusicalForm::Coda => "coda",
        };
        
        let law_str = match law {
            PhysicsLaw::Entropy => "entropy",
            PhysicsLaw::Uncertainty => "uncertainty",
            PhysicsLaw::Conservation => "conservation",
            PhysicsLaw::Relativity => "relativity",
        };
        
        udap.path_segments = vec![form_str.to_string()];
        udap.query_params.insert("law".to_string(), law_str.to_string());
        
        udap
    }

    /// Add frequency parameter
    pub fn with_hz(mut self, hz: f64) -> Self {
        self.query_params.insert("hz".to_string(), hz.to_string());
        self
    }

    /// Add law parameter
    pub fn with_law(mut self, law: &str) -> Self {
        self.query_params.insert("law".to_string(), law.to_string());
        self
    }

    /// Add custom query parameter
    pub fn with_param(mut self, key: &str, value: &str) -> Self {
        self.query_params.insert(key.to_string(), value.to_string());
        self
    }

    /// Build URI string
    pub fn build(&self) -> String {
        let mut uri = format!("{}://{}", self.scheme, self.domain);
        
        for segment in &self.path_segments {
            uri.push('/');
            uri.push_str(segment);
        }

        if !self.query_params.is_empty() {
            uri.push('?');
            let params: Vec<String> = self.query_params
                .iter()
                .map(|(k, v)| format!("{}={}", k, v))
                .collect();
            uri.push_str(&params.join("&"));
        }

        uri
    }

    /// Get domain
    pub fn domain(&self) -> &str {
        &self.domain
    }

    /// Get path segments
    pub fn path(&self) -> &[String] {
        &self.path_segments
    }

    /// Get query parameter
    pub fn param(&self, key: &str) -> Option<&String> {
        self.query_params.get(key)
    }

    /// Check if this is a bio domain URI
    pub fn is_bio(&self) -> bool {
        self.domain == "bio"
    }

    /// Check if this is a physics domain URI
    pub fn is_physics(&self) -> bool {
        self.domain == "physics"
    }
}

#[derive(Debug, Clone)]
pub enum BioResourceType {
    ZipfUnit(usize),
    ZipfPhrase,
    DolphinWhistle(bool), // signature flag
    DolphinClick(usize),  // burst count
    DolphinDialect(String), // pod ID
}

#[derive(Debug, Clone)]
pub enum MusicalForm {
    Rondo,
    Sonata,
    Fugue,
    Canon,
    Variation,
    Coda,
}

#[derive(Debug, Clone)]
pub enum PhysicsLaw {
    Entropy,
    Uncertainty,
    Conservation,
    Relativity,
}

#[derive(Debug)]
pub enum UdapError {
    InvalidScheme(String),
    InvalidPath(String),
    MissingParameter(String),
}

impl std::fmt::Display for UdapError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            UdapError::InvalidScheme(s) => write!(f, "Invalid scheme: {}", s),
            UdapError::InvalidPath(s) => write!(f, "Invalid path: {}", s),
            UdapError::MissingParameter(s) => write!(f, "Missing parameter: {}", s),
        }
    }
}

impl std::error::Error for UdapError {}

/// CLI Command mapping for 42 recon commands
pub struct CliCommandTable {
    commands: Vec<ReconCommand>,
}

impl CliCommandTable {
    pub fn new() -> Self {
        CliCommandTable {
            commands: Self::build_42_commands(),
        }
    }

    fn build_42_commands() -> Vec<ReconCommand> {
        vec![
            // Zipf Whale Group (1-18)
            ReconCommand::new(1, "wave_probe", 20.0, "Humpback Zipf", "skhaos://bio/zipf/unit/1?law=entropy&hz=20"),
            ReconCommand::new(2, "entangle_scan", 500.0, "Humpback Zipf", "skhaos://bio/zipf/phrase/rank?hz=500"),
            ReconCommand::new(3, "packet_oscillate", 1000.0, "Humpback Zipf", "skhaos://bio/zipf/moan?brevity=true&hz=1000"),
            
            // Dolphin Group (19-21)
            ReconCommand::new(19, "dolphin_whistle", 10.0, "Dolphin", "skhaos://bio/dolphin/whistle?signature=true&hz=10"),
            ReconCommand::new(20, "echo_burst", 120.0, "Dolphin", "skhaos://bio/dolphin/click?burst=200&hz=120"),
            ReconCommand::new(21, "dialect_dialogue", 200.0, "Dolphin", "skhaos://bio/dolphin/dialect?pod=alpha&hz=200"),
            
            // Physics DOM Group (37-42)
            ReconCommand::new(37, "rondo_cycle", 10.0, "Physics", "skhaos://physics/rondo?law=conservation&hz=10"),
            ReconCommand::new(38, "sonata_transform", 22.0, "Physics", "skhaos://physics/sonata?law=uncertainty&hz=22"),
            ReconCommand::new(39, "fugue_parallel", 28.0, "Physics", "skhaos://physics/fugue?law=relativity&hz=28"),
            ReconCommand::new(40, "canon_delay", 33.0, "Physics", "skhaos://physics/canon?law=entropy&hz=33"),
            ReconCommand::new(41, "variation_mutate", 37.0, "Physics", "skhaos://physics/variation?law=conservation&hz=37"),
            ReconCommand::new(42, "coda_terminate", 40.0, "Physics", "skhaos://physics/coda?law=uncertainty&hz=40"),
        ]
    }

    pub fn get_command(&self, id: usize) -> Option<&ReconCommand> {
        self.commands.iter().find(|c| c.id == id)
    }

    pub fn all_commands(&self) -> &[ReconCommand] {
        &self.commands
    }
}

#[derive(Debug, Clone)]
pub struct ReconCommand {
    pub id: usize,
    pub name: String,
    pub freq_hz: f64,
    pub bio_type: String,
    pub udap_uri: String,
}

impl ReconCommand {
    fn new(id: usize, name: &str, freq_hz: f64, bio_type: &str, udap_uri: &str) -> Self {
        ReconCommand {
            id,
            name: name.to_string(),
            freq_hz,
            bio_type: bio_type.to_string(),
            udap_uri: udap_uri.to_string(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_build_bio_zipf_uri() {
        let uri = UdapBio::bio(BioResourceType::ZipfUnit(1))
            .with_law("entropy")
            .with_hz(20.0)
            .build();
        
        assert_eq!(uri, "skhaos://bio/zipf/unit/1?hz=20&law=entropy");
    }

    #[test]
    fn test_build_dolphin_whistle_uri() {
        let uri = UdapBio::bio(BioResourceType::DolphinWhistle(true))
            .with_hz(10.0)
            .build();
        
        assert!(uri.contains("skhaos://bio/dolphin/whistle"));
        assert!(uri.contains("signature=true"));
    }

    #[test]
    fn test_build_physics_rondo_uri() {
        let uri = UdapBio::physics(MusicalForm::Rondo, PhysicsLaw::Conservation)
            .with_hz(10.0)
            .build();
        
        assert_eq!(uri, "skhaos://physics/rondo?hz=10&law=conservation");
    }

    #[test]
    fn test_parse_uri() {
        let uri = "skhaos://bio/zipf/unit/1?law=entropy&hz=20";
        let parsed = UdapBio::parse(uri).unwrap();
        
        assert_eq!(parsed.domain(), "bio");
        assert_eq!(parsed.path()[0], "zipf");
        assert_eq!(parsed.param("law").unwrap(), "entropy");
        assert_eq!(parsed.param("hz").unwrap(), "20");
    }

    #[test]
    fn test_cli_command_table() {
        let table = CliCommandTable::new();
        let cmd = table.get_command(1).unwrap();
        
        assert_eq!(cmd.name, "wave_probe");
        assert_eq!(cmd.freq_hz, 20.0);
    }
}
