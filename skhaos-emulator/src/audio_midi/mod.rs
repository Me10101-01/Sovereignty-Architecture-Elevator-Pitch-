// Audio MIDI Module
// MuseScore-inspired MIDI handling for 36 classical pieces
// Entanglement with whale song frequencies (10-40 Hz)

pub mod classical_pieces;
pub mod whale_freq;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MidiNote {
    pub note: u8,
    pub frequency_hz: f64,
    pub velocity: u8,
}

/// Convert MIDI note number to frequency (A4 = 440 Hz)
pub fn midi_to_hz(note: u8) -> f64 {
    440.0 * 2_f64.powf((note as f64 - 69.0) / 12.0)
}

/// Parse MIDI file and extract fundamental frequency
pub fn parse_midi_file(path: &str) -> Result<Vec<MidiNote>, String> {
    // For now, return a simulated structure
    // In production, would use midly crate to parse actual MIDI files
    Ok(vec![
        MidiNote {
            note: 60, // Middle C
            frequency_hz: midi_to_hz(60),
            velocity: 64,
        }
    ])
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_midi_to_hz_a4() {
        let hz = midi_to_hz(69); // A4
        assert!((hz - 440.0).abs() < 0.01);
    }
    
    #[test]
    fn test_midi_to_hz_c4() {
        let hz = midi_to_hz(60); // Middle C
        assert!((hz - 261.63).abs() < 0.1);
    }
}
