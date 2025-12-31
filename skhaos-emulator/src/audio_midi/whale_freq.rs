// Whale song frequencies (10-40 Hz) for deep grounding
// Entanglement with delta/theta mood bands

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WhaleFrequency {
    pub species: String,
    pub frequency_range_hz: (f64, f64),
    pub mood_band: String,
    pub description: String,
}

pub const WHALE_FREQUENCIES: [WhaleFrequency; 5] = [
    WhaleFrequency {
        species: "Blue Whale".to_string(),
        frequency_range_hz: (10.0, 40.0),
        mood_band: "delta".to_string(),
        description: "Deep grounding, sleep, meditation".to_string(),
    },
    WhaleFrequency {
        species: "Humpback Whale".to_string(),
        frequency_range_hz: (20.0, 30.0),
        mood_band: "delta".to_string(),
        description: "Deep calm, restorative".to_string(),
    },
    WhaleFrequency {
        species: "Fin Whale".to_string(),
        frequency_range_hz: (15.0, 25.0),
        mood_band: "delta".to_string(),
        description: "Ultra-low resonance".to_string(),
    },
    WhaleFrequency {
        species: "Bowhead Whale".to_string(),
        frequency_range_hz: (18.0, 35.0),
        mood_band: "delta".to_string(),
        description: "Arctic deep tones".to_string(),
    },
    WhaleFrequency {
        species: "Gray Whale".to_string(),
        frequency_range_hz: (25.0, 40.0),
        mood_band: "theta".to_string(),
        description: "Transitional frequencies".to_string(),
    },
];

/// Check if a frequency falls within whale song range
pub fn is_whale_frequency(hz: f64) -> bool {
    (10.0..=40.0).contains(&hz)
}

/// Get the mood band for a given frequency
pub fn frequency_to_mood_band(hz: f64) -> &'static str {
    match hz {
        h if (0.5..=4.0).contains(&h) => "delta",      // Deep sleep
        h if (4.0..=8.0).contains(&h) => "theta",      // Meditation, creativity
        h if (8.0..=12.0).contains(&h) => "alpha",     // Relaxed focus
        h if (12.0..=30.0).contains(&h) => "beta",     // Active thinking
        h if h >= 30.0 => "gamma",                     // Peak cognition
        _ => "sub-delta",
    }
}

/// Entangle classical piece frequency with whale frequency
pub fn entangle_frequencies(classical_hz: f64, whale_hz: f64) -> String {
    let ratio = classical_hz / whale_hz;
    let mood = frequency_to_mood_band(whale_hz);
    
    format!(
        "Entangled: {}Hz classical + {}Hz whale = {}:1 ratio (mood: {})",
        classical_hz, whale_hz, ratio, mood
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_whale_frequency_detection() {
        assert!(is_whale_frequency(20.0));
        assert!(!is_whale_frequency(100.0));
    }
    
    #[test]
    fn test_frequency_to_mood_band() {
        assert_eq!(frequency_to_mood_band(2.0), "delta");
        assert_eq!(frequency_to_mood_band(6.0), "theta");
        assert_eq!(frequency_to_mood_band(10.0), "alpha");
        assert_eq!(frequency_to_mood_band(20.0), "beta");
        assert_eq!(frequency_to_mood_band(40.0), "gamma");
    }
    
    #[test]
    fn test_entangle_frequencies() {
        let result = entangle_frequencies(440.0, 20.0);
        assert!(result.contains("440Hz"));
        assert!(result.contains("20Hz"));
    }
}
