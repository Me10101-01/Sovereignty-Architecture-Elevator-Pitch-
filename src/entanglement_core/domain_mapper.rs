// Domain Mapper Module
// Universal schema applicator for cross-domain transformations
// Maps between: Chess ↔ GPS ↔ Pipe ↔ Neural ↔ Mood ↔ Network

use std::collections::HashMap;

/// Universal coordinate that can represent any domain
#[derive(Debug, Clone)]
pub struct UniversalCoordinate {
    pub x: f64,
    pub y: f64,
    pub z: f64,
    pub domain: String,
    pub metadata: HashMap<String, String>,
}

impl UniversalCoordinate {
    /// Create a new universal coordinate
    pub fn new(x: f64, y: f64, z: f64, domain: &str) -> Self {
        UniversalCoordinate {
            x,
            y,
            z,
            domain: domain.to_string(),
            metadata: HashMap::new(),
        }
    }

    /// Add metadata
    pub fn with_metadata(mut self, key: &str, value: &str) -> Self {
        self.metadata.insert(key.to_string(), value.to_string());
        self
    }
}

/// Domain mapper handles transformations between domains
pub struct DomainMapper {
    /// Normalization ranges for each domain
    ranges: HashMap<String, (f64, f64, f64)>,
}

impl DomainMapper {
    /// Create a new domain mapper with default ranges
    pub fn new() -> Self {
        let mut ranges = HashMap::new();
        
        // Define normalization ranges (min, max, default_z)
        ranges.insert("chess".to_string(), (0.0, 8.0, 0.0));      // 8x8 board
        ranges.insert("gps".to_string(), (-180.0, 180.0, 0.0));   // Longitude range
        ranges.insert("pipe".to_string(), (0.0, 100.0, 0.0));     // Arbitrary pipe range
        ranges.insert("neural".to_string(), (0.0, 1.0, 0.0));     // Normalized weights
        ranges.insert("mood".to_string(), (0.0, 40.0, 0.0));      // Hz range (Delta to Gamma)
        ranges.insert("network".to_string(), (0.0, 255.0, 0.0));  // IP octet range
        
        DomainMapper { ranges }
    }

    /// Map chess position to universal coordinate
    /// e4 -> (4, 3, 0) in 0-based indexing
    pub fn chess_to_universal(&self, file: char, rank: u8) -> Result<UniversalCoordinate, String> {
        let file_index = match file.to_ascii_lowercase() {
            'a' => 0, 'b' => 1, 'c' => 2, 'd' => 3,
            'e' => 4, 'f' => 5, 'g' => 6, 'h' => 7,
            _ => return Err("Invalid chess file".to_string()),
        };

        if !(1..=8).contains(&rank) {
            return Err("Invalid chess rank".to_string());
        }

        Ok(UniversalCoordinate::new(
            file_index as f64,
            (rank - 1) as f64,
            0.0,
            "chess"
        ))
    }

    /// Map GPS to universal coordinate
    pub fn gps_to_universal(&self, lat: f64, lon: f64, alt: f64) -> Result<UniversalCoordinate, String> {
        if !(-90.0..=90.0).contains(&lat) {
            return Err("Invalid latitude".to_string());
        }
        if !(-180.0..=180.0).contains(&lon) {
            return Err("Invalid longitude".to_string());
        }

        Ok(UniversalCoordinate::new(lat, lon, alt, "gps"))
    }

    /// Map pipe coordinate to universal
    pub fn pipe_to_universal(&self, run: f64, offset: f64, travel: f64) -> UniversalCoordinate {
        UniversalCoordinate::new(run, offset, travel, "pipe")
    }

    /// Map neural coordinate to universal
    pub fn neural_to_universal(&self, layer: usize, neuron: usize, weight: f64) -> UniversalCoordinate {
        UniversalCoordinate::new(layer as f64, neuron as f64, weight, "neural")
    }

    /// Map mood/frequency to universal
    pub fn mood_to_universal(&self, hz: f64, intensity: f64, duration: f64) -> UniversalCoordinate {
        UniversalCoordinate::new(hz, intensity, duration, "mood")
            .with_metadata("wave_type", &Self::hz_to_wave_type(hz))
    }

    /// Map network address to universal
    pub fn network_to_universal(&self, ip: &str, port: u16) -> Result<UniversalCoordinate, String> {
        let octets: Vec<&str> = ip.split('.').collect();
        if octets.len() != 4 {
            return Err("Invalid IP address".to_string());
        }

        // Use first two octets for x, last two for y
        let x = format!("{}.{}", octets[0], octets[1]).parse::<f64>()
            .map_err(|_| "Invalid IP format")?;
        let y = format!("{}.{}", octets[2], octets[3]).parse::<f64>()
            .map_err(|_| "Invalid IP format")?;

        Ok(UniversalCoordinate::new(x, y, port as f64, "network"))
    }

    /// Transform between domains via universal coordinate
    pub fn transform(&self, from: UniversalCoordinate, to_domain: &str) -> Result<UniversalCoordinate, String> {
        // Normalize from source domain
        let normalized = self.normalize(&from)?;
        
        // Denormalize to target domain
        self.denormalize(&normalized, to_domain)
    }

    /// Normalize coordinate to [0, 1] range
    fn normalize(&self, coord: &UniversalCoordinate) -> Result<UniversalCoordinate, String> {
        let (min, max, _) = self.ranges
            .get(&coord.domain)
            .ok_or_else(|| format!("Unknown domain: {}", coord.domain))?;

        let range = max - min;
        let x_norm = (coord.x - min) / range;
        let y_norm = (coord.y - min) / range;
        let z_norm = if coord.z == 0.0 { 0.0 } else { (coord.z - min) / range };

        Ok(UniversalCoordinate {
            x: x_norm,
            y: y_norm,
            z: z_norm,
            domain: "normalized".to_string(),
            metadata: coord.metadata.clone(),
        })
    }

    /// Denormalize from [0, 1] to target domain range
    fn denormalize(&self, normalized: &UniversalCoordinate, to_domain: &str) -> Result<UniversalCoordinate, String> {
        let (min, max, default_z) = self.ranges
            .get(to_domain)
            .ok_or_else(|| format!("Unknown domain: {}", to_domain))?;

        let range = max - min;
        let x = normalized.x * range + min;
        let y = normalized.y * range + min;
        let z = if normalized.z == 0.0 { *default_z } else { normalized.z * range + min };

        Ok(UniversalCoordinate {
            x,
            y,
            z,
            domain: to_domain.to_string(),
            metadata: normalized.metadata.clone(),
        })
    }

    /// Convert Hz to brain wave type
    fn hz_to_wave_type(hz: f64) -> String {
        match hz {
            h if h < 4.0 => "delta",
            h if h < 8.0 => "theta",
            h if h < 13.0 => "alpha",
            h if h < 30.0 => "beta",
            _ => "gamma",
        }.to_string()
    }
}

impl Default for DomainMapper {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_chess_to_universal() {
        let mapper = DomainMapper::new();
        let coord = mapper.chess_to_universal('e', 4).unwrap();
        
        assert_eq!(coord.x, 4.0);
        assert_eq!(coord.y, 3.0);
        assert_eq!(coord.domain, "chess");
    }

    #[test]
    fn test_gps_to_universal() {
        let mapper = DomainMapper::new();
        let coord = mapper.gps_to_universal(42.3601, -71.0589, 0.0).unwrap();
        
        assert_eq!(coord.x, 42.3601);
        assert_eq!(coord.y, -71.0589);
        assert_eq!(coord.domain, "gps");
    }

    #[test]
    fn test_pipe_to_universal() {
        let mapper = DomainMapper::new();
        let coord = mapper.pipe_to_universal(10.0, 5.0, 15.0);
        
        assert_eq!(coord.x, 10.0);
        assert_eq!(coord.y, 5.0);
        assert_eq!(coord.z, 15.0);
        assert_eq!(coord.domain, "pipe");
    }

    #[test]
    fn test_mood_to_universal() {
        let mapper = DomainMapper::new();
        let coord = mapper.mood_to_universal(10.0, 0.75, 5.0);
        
        assert_eq!(coord.x, 10.0);
        assert_eq!(coord.metadata.get("wave_type"), Some(&"alpha".to_string()));
    }

    #[test]
    fn test_network_to_universal() {
        let mapper = DomainMapper::new();
        let coord = mapper.network_to_universal("192.168.1.1", 8080).unwrap();
        
        assert!(coord.x > 0.0);
        assert!(coord.y > 0.0);
        assert_eq!(coord.z, 8080.0);
    }

    #[test]
    fn test_hz_to_wave_type() {
        assert_eq!(DomainMapper::hz_to_wave_type(3.0), "delta");
        assert_eq!(DomainMapper::hz_to_wave_type(6.0), "theta");
        assert_eq!(DomainMapper::hz_to_wave_type(10.0), "alpha");
        assert_eq!(DomainMapper::hz_to_wave_type(18.0), "beta");
        assert_eq!(DomainMapper::hz_to_wave_type(35.0), "gamma");
    }

    #[test]
    fn test_cross_domain_transform() {
        let mapper = DomainMapper::new();
        
        // Chess to pipe transformation
        let chess_coord = mapper.chess_to_universal('e', 4).unwrap();
        let pipe_coord = mapper.transform(chess_coord, "pipe").unwrap();
        
        assert_eq!(pipe_coord.domain, "pipe");
        assert!(pipe_coord.x >= 0.0 && pipe_coord.x <= 100.0);
    }
}
