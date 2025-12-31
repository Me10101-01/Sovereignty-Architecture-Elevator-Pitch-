// Mood State Module
// Hz/Color/State storage with neural tick clocks
// Maps brain wave frequencies to system states

use std::time::{Duration, Instant};

/// Brain wave type based on frequency
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum WaveType {
    Delta,  // 0.5-4 Hz (deep sleep)
    Theta,  // 4-8 Hz (meditation, creativity)
    Alpha,  // 8-13 Hz (relaxed, calm)
    Beta,   // 13-30 Hz (alert, focused)
    Gamma,  // 30-100 Hz (high-level processing)
}

impl WaveType {
    /// Get wave type from frequency
    pub fn from_hz(hz: f64) -> Self {
        match hz {
            h if h < 4.0 => WaveType::Delta,
            h if h < 8.0 => WaveType::Theta,
            h if h < 13.0 => WaveType::Alpha,
            h if h < 30.0 => WaveType::Beta,
            _ => WaveType::Gamma,
        }
    }

    /// Get frequency range for wave type
    pub fn frequency_range(&self) -> (f64, f64) {
        match self {
            WaveType::Delta => (0.5, 4.0),
            WaveType::Theta => (4.0, 8.0),
            WaveType::Alpha => (8.0, 13.0),
            WaveType::Beta => (13.0, 30.0),
            WaveType::Gamma => (30.0, 100.0),
        }
    }

    /// Get typical color associated with wave type
    pub fn typical_color(&self) -> &str {
        match self {
            WaveType::Delta => "deep_blue",
            WaveType::Theta => "purple",
            WaveType::Alpha => "green",
            WaveType::Beta => "yellow",
            WaveType::Gamma => "orange",
        }
    }
}

/// Mood state with frequency, color, and duration
#[derive(Debug, Clone)]
pub struct MoodState {
    pub id: String,
    pub wave_type: WaveType,
    pub frequency_hz: f64,
    pub color: String,
    pub intensity: f64,
    pub duration: Duration,
    pub created_at: Instant,
    pub metadata: Vec<String>,
}

impl MoodState {
    /// Create a new mood state from frequency
    pub fn from_frequency(id: String, frequency_hz: f64, intensity: f64, duration: Duration) -> Self {
        let wave_type = WaveType::from_hz(frequency_hz);
        let color = wave_type.typical_color().to_string();

        MoodState {
            id,
            wave_type,
            frequency_hz,
            color,
            intensity,
            duration,
            created_at: Instant::now(),
            metadata: Vec::new(),
        }
    }

    /// Create from wave type
    pub fn from_wave_type(id: String, wave_type: WaveType, intensity: f64, duration: Duration) -> Self {
        let (min_hz, max_hz) = wave_type.frequency_range();
        let frequency_hz = (min_hz + max_hz) / 2.0; // Use midpoint
        let color = wave_type.typical_color().to_string();

        MoodState {
            id,
            wave_type,
            frequency_hz,
            color,
            intensity,
            duration,
            created_at: Instant::now(),
            metadata: Vec::new(),
        }
    }

    /// Check if mood state is still active
    pub fn is_active(&self) -> bool {
        self.created_at.elapsed() < self.duration
    }

    /// Get remaining duration
    pub fn remaining_duration(&self) -> Duration {
        self.duration.saturating_sub(self.created_at.elapsed())
    }

    /// Add metadata tag
    pub fn add_metadata(&mut self, tag: String) {
        self.metadata.push(tag);
    }

    /// Convert to UDAP address
    pub fn to_udap(&self) -> String {
        format!(
            "skhaos://mood/{:?}/{}?hz={}&intensity={}&color={}",
            self.wave_type,
            self.id,
            self.frequency_hz,
            self.intensity,
            self.color
        )
    }

    /// Parse from UDAP address
    pub fn from_udap(uri: &str) -> Result<Self, String> {
        if !uri.starts_with("skhaos://mood/") {
            return Err("Invalid UDAP prefix for mood".to_string());
        }

        // Simple parsing for demonstration
        // In production, use a proper parser
        let parts: Vec<&str> = uri.split('?').collect();
        if parts.len() != 2 {
            return Err("Missing query parameters".to_string());
        }

        let path_parts: Vec<&str> = parts[0].split('/').collect();
        if path_parts.len() < 5 {
            return Err("Invalid path format".to_string());
        }

        let _wave_str = path_parts[3];
        let id = path_parts[4].to_string();

        // Parse query parameters
        let query = parts[1];
        let mut hz = 10.0;
        let mut intensity = 0.5;
        let mut color = String::new();

        for param in query.split('&') {
            let kv: Vec<&str> = param.split('=').collect();
            if kv.len() == 2 {
                match kv[0] {
                    "hz" => hz = kv[1].parse().unwrap_or(10.0),
                    "intensity" => intensity = kv[1].parse().unwrap_or(0.5),
                    "color" => color = kv[1].to_string(),
                    _ => {}
                }
            }
        }

        let wave_type = WaveType::from_hz(hz);

        Ok(MoodState {
            id,
            wave_type,
            frequency_hz: hz,
            color,
            intensity,
            duration: Duration::from_secs(60),
            created_at: Instant::now(),
            metadata: Vec::new(),
        })
    }
}

/// Mood state manager
pub struct MoodStateManager {
    states: Vec<MoodState>,
}

impl MoodStateManager {
    pub fn new() -> Self {
        MoodStateManager {
            states: Vec::new(),
        }
    }

    /// Add a mood state
    pub fn add_state(&mut self, state: MoodState) {
        self.states.push(state);
    }

    /// Get active mood states
    pub fn active_states(&self) -> Vec<&MoodState> {
        self.states.iter().filter(|s| s.is_active()).collect()
    }

    /// Remove expired states
    pub fn cleanup_expired(&mut self) {
        self.states.retain(|s| s.is_active());
    }

    /// Get state by ID
    pub fn get_state(&self, id: &str) -> Option<&MoodState> {
        self.states.iter().find(|s| s.id == id)
    }

    /// Get average frequency of active states
    pub fn average_frequency(&self) -> f64 {
        let active = self.active_states();
        if active.is_empty() {
            return 0.0;
        }

        let sum: f64 = active.iter().map(|s| s.frequency_hz).sum();
        sum / active.len() as f64
    }

    /// Get dominant wave type
    pub fn dominant_wave_type(&self) -> Option<WaveType> {
        let active = self.active_states();
        if active.is_empty() {
            return None;
        }

        // Count occurrences of each wave type
        let mut counts = std::collections::HashMap::new();
        for state in active {
            *counts.entry(state.wave_type.clone()).or_insert(0) += 1;
        }

        counts.into_iter()
            .max_by_key(|(_, count)| *count)
            .map(|(wave_type, _)| wave_type)
    }
}

impl Default for MoodStateManager {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_wave_type_from_hz() {
        assert_eq!(WaveType::from_hz(2.0), WaveType::Delta);
        assert_eq!(WaveType::from_hz(6.0), WaveType::Theta);
        assert_eq!(WaveType::from_hz(10.0), WaveType::Alpha);
        assert_eq!(WaveType::from_hz(18.0), WaveType::Beta);
        assert_eq!(WaveType::from_hz(40.0), WaveType::Gamma);
    }

    #[test]
    fn test_mood_state_from_frequency() {
        let mood = MoodState::from_frequency(
            "test_mood".to_string(),
            10.0,
            0.75,
            Duration::from_secs(60)
        );

        assert_eq!(mood.wave_type, WaveType::Alpha);
        assert_eq!(mood.frequency_hz, 10.0);
        assert_eq!(mood.intensity, 0.75);
    }

    #[test]
    fn test_mood_state_active() {
        let mood = MoodState::from_frequency(
            "test".to_string(),
            10.0,
            0.5,
            Duration::from_secs(60)
        );

        assert!(mood.is_active());
    }

    #[test]
    fn test_mood_to_udap() {
        let mood = MoodState::from_frequency(
            "test".to_string(),
            10.0,
            0.75,
            Duration::from_secs(60)
        );

        let udap = mood.to_udap();
        assert!(udap.contains("skhaos://mood/"));
        assert!(udap.contains("hz=10"));
        assert!(udap.contains("intensity=0.75"));
    }

    #[test]
    fn test_mood_state_manager() {
        let mut manager = MoodStateManager::new();

        let mood1 = MoodState::from_frequency(
            "alpha1".to_string(),
            10.0,
            0.5,
            Duration::from_secs(60)
        );

        let mood2 = MoodState::from_frequency(
            "beta1".to_string(),
            18.0,
            0.7,
            Duration::from_secs(60)
        );

        manager.add_state(mood1);
        manager.add_state(mood2);

        assert_eq!(manager.active_states().len(), 2);
        assert!(manager.average_frequency() > 0.0);
    }

    #[test]
    fn test_dominant_wave_type() {
        let mut manager = MoodStateManager::new();

        manager.add_state(MoodState::from_wave_type(
            "alpha1".to_string(),
            WaveType::Alpha,
            0.5,
            Duration::from_secs(60)
        ));

        manager.add_state(MoodState::from_wave_type(
            "alpha2".to_string(),
            WaveType::Alpha,
            0.6,
            Duration::from_secs(60)
        ));

        manager.add_state(MoodState::from_wave_type(
            "beta1".to_string(),
            WaveType::Beta,
            0.7,
            Duration::from_secs(60)
        ));

        let dominant = manager.dominant_wave_type();
        assert_eq!(dominant, Some(WaveType::Alpha));
    }
}
