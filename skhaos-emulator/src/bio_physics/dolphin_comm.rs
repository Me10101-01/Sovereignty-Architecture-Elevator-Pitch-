// Dolphin Communication Pattern Simulator
//
// Models dolphin communication including:
// - Signature whistles (1-20kHz, unique ID per individual)
// - Echolocation clicks (120-200kHz burst-pulse clicks)
// - Dialects (pod-specific, matrilineal like orcas)
//
// References DolphinGemma-style AI generation for bio-patterns

use std::collections::HashMap;

/// Frequency ranges for dolphin communication
pub const WHISTLE_FREQ_MIN_HZ: f64 = 1000.0;
pub const WHISTLE_FREQ_MAX_HZ: f64 = 20000.0;
pub const CLICK_FREQ_MIN_HZ: f64 = 120000.0;
pub const CLICK_FREQ_MAX_HZ: f64 = 200000.0;

/// Dolphin communication simulator
pub struct DolphinComm {
    /// Known signature whistles mapped to dolphin IDs
    signatures: HashMap<String, SignatureWhistle>,
    /// Dialect patterns per pod
    dialects: HashMap<String, Dialect>,
    /// Echolocation burst patterns
    burst_patterns: Vec<EcholocationBurst>,
}

impl DolphinComm {
    pub fn new() -> Self {
        DolphinComm {
            signatures: HashMap::new(),
            dialects: HashMap::new(),
            burst_patterns: Vec::new(),
        }
    }

    /// Register a signature whistle for a dolphin
    pub fn register_signature(&mut self, dolphin_id: &str, freq_hz: f64, pattern: Vec<f64>) -> Result<(), CommError> {
        if freq_hz < WHISTLE_FREQ_MIN_HZ || freq_hz > WHISTLE_FREQ_MAX_HZ {
            return Err(CommError::InvalidFrequency(format!(
                "Whistle frequency {} Hz outside range {}-{} Hz",
                freq_hz, WHISTLE_FREQ_MIN_HZ, WHISTLE_FREQ_MAX_HZ
            )));
        }

        let signature = SignatureWhistle {
            dolphin_id: dolphin_id.to_string(),
            base_freq_hz: freq_hz,
            contour_pattern: pattern,
            call_count: 0,
        };

        self.signatures.insert(dolphin_id.to_string(), signature);
        Ok(())
    }

    /// Generate a signature whistle call
    pub fn call_signature(&mut self, dolphin_id: &str) -> Result<WhistleCall, CommError> {
        let signature = self.signatures.get_mut(dolphin_id)
            .ok_or_else(|| CommError::UnknownSignature(dolphin_id.to_string()))?;

        signature.call_count += 1;

        Ok(WhistleCall {
            dolphin_id: dolphin_id.to_string(),
            freq_hz: signature.base_freq_hz,
            duration_ms: 1000.0, // Typical ~1 second
            contour: signature.contour_pattern.clone(),
            timestamp: signature.call_count,
        })
    }

    /// Add echolocation burst pattern (for prey detection, navigation)
    pub fn add_echolocation_burst(&mut self, center_freq_hz: f64, click_count: usize) -> Result<(), CommError> {
        if center_freq_hz < CLICK_FREQ_MIN_HZ || center_freq_hz > CLICK_FREQ_MAX_HZ {
            return Err(CommError::InvalidFrequency(format!(
                "Click frequency {} Hz outside range {}-{} Hz",
                center_freq_hz, CLICK_FREQ_MIN_HZ, CLICK_FREQ_MAX_HZ
            )));
        }

        let burst = EcholocationBurst {
            center_freq_hz,
            click_count,
            inter_click_interval_us: 50.0, // Typical 50 microseconds
            purpose: EchoPurpose::Navigation,
        };

        self.burst_patterns.push(burst);
        Ok(())
    }

    /// Register a pod dialect
    pub fn register_dialect(&mut self, pod_id: &str, chirp_patterns: Vec<String>, matriline: String) {
        let dialect = Dialect {
            pod_id: pod_id.to_string(),
            chirp_patterns,
            scream_variants: Vec::new(),
            matriline,
            learned: true, // Culturally transmitted
        };

        self.dialects.insert(pod_id.to_string(), dialect);
    }

    /// Simulate dialect dialogue between pod members
    pub fn dialect_dialogue(&self, pod_id: &str, exchange_count: usize) -> Result<Vec<String>, CommError> {
        let dialect = self.dialects.get(pod_id)
            .ok_or_else(|| CommError::UnknownDialect(pod_id.to_string()))?;

        let mut dialogue = Vec::new();
        for i in 0..exchange_count {
            let pattern_idx = i % dialect.chirp_patterns.len();
            dialogue.push(dialect.chirp_patterns[pattern_idx].clone());
        }

        Ok(dialogue)
    }

    /// Map dolphin patterns to quantum probes (for BPEC integration)
    pub fn map_to_quantum_probe(&self, dolphin_id: &str) -> Result<QuantumProbe, CommError> {
        let signature = self.signatures.get(dolphin_id)
            .ok_or_else(|| CommError::UnknownSignature(dolphin_id.to_string()))?;

        // Map whistle frequency to symbolic quantum state
        let state_id = format!("q_{}", (signature.base_freq_hz / 1000.0) as usize);
        
        Ok(QuantumProbe {
            state_id,
            frequency_hz: signature.base_freq_hz,
            coherence: 0.95, // High coherence for signature whistles
            measurement_type: MeasurementType::ReconWave,
        })
    }

    /// Get statistics about registered signatures
    pub fn get_signature_stats(&self) -> SignatureStats {
        let total_calls: usize = self.signatures.values().map(|s| s.call_count).sum();
        let avg_freq: f64 = if !self.signatures.is_empty() {
            self.signatures.values().map(|s| s.base_freq_hz).sum::<f64>() / self.signatures.len() as f64
        } else {
            0.0
        };

        SignatureStats {
            total_signatures: self.signatures.len(),
            total_calls,
            average_frequency_hz: avg_freq,
            dialect_count: self.dialects.len(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct SignatureWhistle {
    pub dolphin_id: String,
    pub base_freq_hz: f64,
    pub contour_pattern: Vec<f64>, // Frequency modulation over time
    pub call_count: usize,
}

#[derive(Debug, Clone)]
pub struct WhistleCall {
    pub dolphin_id: String,
    pub freq_hz: f64,
    pub duration_ms: f64,
    pub contour: Vec<f64>,
    pub timestamp: usize,
}

#[derive(Debug, Clone)]
pub struct EcholocationBurst {
    pub center_freq_hz: f64,
    pub click_count: usize,
    pub inter_click_interval_us: f64,
    pub purpose: EchoPurpose,
}

#[derive(Debug, Clone)]
pub enum EchoPurpose {
    Navigation,
    PreyDetection,
    Communication,
}

#[derive(Debug, Clone)]
pub struct Dialect {
    pub pod_id: String,
    pub chirp_patterns: Vec<String>,
    pub scream_variants: Vec<String>,
    pub matriline: String, // Matrilineal inheritance
    pub learned: bool,
}

#[derive(Debug)]
pub struct QuantumProbe {
    pub state_id: String,
    pub frequency_hz: f64,
    pub coherence: f64,
    pub measurement_type: MeasurementType,
}

#[derive(Debug)]
pub enum MeasurementType {
    ReconWave,
    StateCollapse,
    Entanglement,
}

#[derive(Debug)]
pub struct SignatureStats {
    pub total_signatures: usize,
    pub total_calls: usize,
    pub average_frequency_hz: f64,
    pub dialect_count: usize,
}

#[derive(Debug)]
pub enum CommError {
    InvalidFrequency(String),
    UnknownSignature(String),
    UnknownDialect(String),
}

impl std::fmt::Display for CommError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CommError::InvalidFrequency(s) => write!(f, "Invalid frequency: {}", s),
            CommError::UnknownSignature(s) => write!(f, "Unknown signature: {}", s),
            CommError::UnknownDialect(s) => write!(f, "Unknown dialect: {}", s),
        }
    }
}

impl std::error::Error for CommError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_register_signature() {
        let mut comm = DolphinComm::new();
        let result = comm.register_signature("dolphin_alpha", 10000.0, vec![10000.0, 12000.0, 8000.0]);
        assert!(result.is_ok());
    }

    #[test]
    fn test_call_signature() {
        let mut comm = DolphinComm::new();
        comm.register_signature("dolphin_beta", 15000.0, vec![15000.0, 16000.0]).unwrap();
        
        let call = comm.call_signature("dolphin_beta");
        assert!(call.is_ok());
        assert_eq!(call.unwrap().freq_hz, 15000.0);
    }

    #[test]
    fn test_echolocation_burst() {
        let mut comm = DolphinComm::new();
        let result = comm.add_echolocation_burst(150000.0, 20);
        assert!(result.is_ok());
    }

    #[test]
    fn test_invalid_whistle_frequency() {
        let mut comm = DolphinComm::new();
        let result = comm.register_signature("dolphin_gamma", 100.0, vec![]);
        assert!(result.is_err());
    }

    #[test]
    fn test_dialect_registration() {
        let mut comm = DolphinComm::new();
        comm.register_dialect("pod_alpha", vec!["chirp1".to_string(), "chirp2".to_string()], "matriline_A".to_string());
        
        let dialogue = comm.dialect_dialogue("pod_alpha", 3);
        assert!(dialogue.is_ok());
        assert_eq!(dialogue.unwrap().len(), 3);
    }

    #[test]
    fn test_quantum_probe_mapping() {
        let mut comm = DolphinComm::new();
        comm.register_signature("dolphin_delta", 12000.0, vec![]).unwrap();
        
        let probe = comm.map_to_quantum_probe("dolphin_delta");
        assert!(probe.is_ok());
        assert_eq!(probe.unwrap().frequency_hz, 12000.0);
    }
}
