// Mood state management with whale delta frequencies
use std::collections::HashMap;

pub struct MoodState {
    current_band: String,
    frequency_hz: f64,
}

impl MoodState {
    pub fn new() -> Self {
        MoodState {
            current_band: "alpha".to_string(),
            frequency_hz: 10.0,
        }
    }
    
    pub fn set_frequency(&mut self, hz: f64) {
        self.frequency_hz = hz;
        self.current_band = Self::hz_to_band(hz);
    }
    
    fn hz_to_band(hz: f64) -> String {
        match hz {
            h if (0.5..=4.0).contains(&h) => "delta",
            h if (4.0..=8.0).contains(&h) => "theta",
            h if (8.0..=12.0).contains(&h) => "alpha",
            h if (12.0..=30.0).contains(&h) => "beta",
            _ => "gamma",
        }.to_string()
    }
}
