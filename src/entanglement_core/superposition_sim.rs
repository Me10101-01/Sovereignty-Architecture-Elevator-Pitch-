// Superposition Simulation Module
// Quantum-inspired state simulation using wave functions
// Treats domain addresses as symbolic qubits in superposition

use std::f64::consts::PI;

/// Represents a quantum-inspired superposition state
#[derive(Debug, Clone)]
pub struct SuperpositionState {
    /// Amplitude for each basis state
    pub amplitudes: Vec<ComplexAmplitude>,
    /// Basis states (UDAP addresses)
    pub basis_states: Vec<String>,
}

/// Complex amplitude (simplified representation)
#[derive(Debug, Clone)]
pub struct ComplexAmplitude {
    pub real: f64,
    pub imag: f64,
}

impl ComplexAmplitude {
    pub fn new(real: f64, imag: f64) -> Self {
        ComplexAmplitude { real, imag }
    }

    /// Magnitude squared (probability)
    pub fn probability(&self) -> f64 {
        self.real * self.real + self.imag * self.imag
    }

    /// Phase angle
    pub fn phase(&self) -> f64 {
        self.imag.atan2(self.real)
    }
}

impl SuperpositionState {
    /// Create a new superposition state
    pub fn new(basis_states: Vec<String>) -> Self {
        let n = basis_states.len();
        let amplitude = 1.0 / (n as f64).sqrt();
        
        let amplitudes = (0..n)
            .map(|_| ComplexAmplitude::new(amplitude, 0.0))
            .collect();

        SuperpositionState {
            amplitudes,
            basis_states,
        }
    }

    /// Create with custom amplitudes
    pub fn with_amplitudes(basis_states: Vec<String>, amplitudes: Vec<ComplexAmplitude>) -> Result<Self, String> {
        if basis_states.len() != amplitudes.len() {
            return Err("Basis states and amplitudes must have same length".to_string());
        }

        // Verify normalization
        let total_prob: f64 = amplitudes.iter().map(|a| a.probability()).sum();
        if (total_prob - 1.0).abs() > 1e-6 {
            return Err(format!("Amplitudes not normalized: {}", total_prob));
        }

        Ok(SuperpositionState {
            amplitudes,
            basis_states,
        })
    }

    /// Measure the superposition (collapse to one state)
    /// Returns the index of the collapsed state
    pub fn measure(&self, random_value: f64) -> usize {
        let mut cumulative = 0.0;
        
        for (i, amplitude) in self.amplitudes.iter().enumerate() {
            cumulative += amplitude.probability();
            if random_value <= cumulative {
                return i;
            }
        }

        self.amplitudes.len() - 1
    }

    /// Get probability distribution
    pub fn probabilities(&self) -> Vec<f64> {
        self.amplitudes.iter().map(|a| a.probability()).collect()
    }

    /// Apply a phase shift to a specific basis state
    pub fn apply_phase(&mut self, index: usize, phase: f64) {
        if index < self.amplitudes.len() {
            let amp = &self.amplitudes[index];
            let magnitude = (amp.probability()).sqrt();
            let current_phase = amp.phase();
            let new_phase = current_phase + phase;
            
            self.amplitudes[index] = ComplexAmplitude::new(
                magnitude * new_phase.cos(),
                magnitude * new_phase.sin(),
            );
        }
    }

    /// Entangle with another superposition state
    /// Creates a combined state space
    pub fn entangle(&self, other: &SuperpositionState) -> SuperpositionState {
        let mut combined_basis = Vec::new();
        let mut combined_amplitudes = Vec::new();

        for (i, state1) in self.basis_states.iter().enumerate() {
            for (j, state2) in other.basis_states.iter().enumerate() {
                combined_basis.push(format!("{}|{}", state1, state2));
                
                let amp1 = &self.amplitudes[i];
                let amp2 = &other.amplitudes[j];
                
                // Tensor product of amplitudes
                let real = amp1.real * amp2.real - amp1.imag * amp2.imag;
                let imag = amp1.real * amp2.imag + amp1.imag * amp2.real;
                
                combined_amplitudes.push(ComplexAmplitude::new(real, imag));
            }
        }

        SuperpositionState {
            basis_states: combined_basis,
            amplitudes: combined_amplitudes,
        }
    }

    /// Get the most probable state
    pub fn most_probable(&self) -> (usize, f64) {
        let mut max_prob = 0.0;
        let mut max_index = 0;

        for (i, amp) in self.amplitudes.iter().enumerate() {
            let prob = amp.probability();
            if prob > max_prob {
                max_prob = prob;
                max_index = i;
            }
        }

        (max_index, max_prob)
    }
}

/// Wave function for domain transformations
pub struct WaveFunction {
    pub frequency: f64,
    pub amplitude: f64,
    pub phase: f64,
}

impl WaveFunction {
    pub fn new(frequency: f64, amplitude: f64, phase: f64) -> Self {
        WaveFunction {
            frequency,
            amplitude,
            phase,
        }
    }

    /// Evaluate wave function at time t
    pub fn eval(&self, t: f64) -> f64 {
        self.amplitude * (2.0 * PI * self.frequency * t + self.phase).sin()
    }

    /// Superpose multiple wave functions
    pub fn superpose(waves: &[WaveFunction], t: f64) -> f64 {
        waves.iter().map(|w| w.eval(t)).sum()
    }

    /// Interference between two waves
    pub fn interfere(&self, other: &WaveFunction, t: f64) -> f64 {
        self.eval(t) + other.eval(t)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_complex_amplitude_probability() {
        let amp = ComplexAmplitude::new(0.6, 0.8);
        assert!((amp.probability() - 1.0).abs() < 0.01);
    }

    #[test]
    fn test_superposition_creation() {
        let states = vec![
            "skhaos://pipe/run/5".to_string(),
            "skhaos://neural/layer/2".to_string(),
        ];
        
        let superpos = SuperpositionState::new(states);
        
        assert_eq!(superpos.basis_states.len(), 2);
        assert_eq!(superpos.amplitudes.len(), 2);
        
        // Each state should have equal probability
        let probs = superpos.probabilities();
        assert!((probs[0] - 0.5).abs() < 0.01);
        assert!((probs[1] - 0.5).abs() < 0.01);
    }

    #[test]
    fn test_measure() {
        let states = vec![
            "state1".to_string(),
            "state2".to_string(),
        ];
        
        let superpos = SuperpositionState::new(states);
        
        // Measure with specific random value
        let result = superpos.measure(0.3);
        assert!(result < 2);
    }

    #[test]
    fn test_most_probable() {
        let states = vec!["s1".to_string(), "s2".to_string()];
        let amplitudes = vec![
            ComplexAmplitude::new(0.9, 0.0),
            ComplexAmplitude::new(0.1, 0.0),
        ];
        
        // Note: These aren't normalized, but for testing purposes
        let superpos = SuperpositionState {
            basis_states: states,
            amplitudes,
        };
        
        let (index, _prob) = superpos.most_probable();
        assert_eq!(index, 0);
    }

    #[test]
    fn test_entangle() {
        let states1 = vec!["a".to_string(), "b".to_string()];
        let states2 = vec!["x".to_string(), "y".to_string()];
        
        let s1 = SuperpositionState::new(states1);
        let s2 = SuperpositionState::new(states2);
        
        let entangled = s1.entangle(&s2);
        
        // Should have 2 * 2 = 4 combined states
        assert_eq!(entangled.basis_states.len(), 4);
    }

    #[test]
    fn test_wave_function_eval() {
        let wave = WaveFunction::new(1.0, 1.0, 0.0);
        let val = wave.eval(0.0);
        
        assert!((val - 0.0).abs() < 0.01);
    }

    #[test]
    fn test_wave_superposition() {
        let w1 = WaveFunction::new(1.0, 1.0, 0.0);
        let w2 = WaveFunction::new(2.0, 0.5, 0.0);
        
        let combined = WaveFunction::superpose(&[w1, w2], 0.0);
        assert!((combined - 0.0).abs() < 0.01);
    }

    #[test]
    fn test_wave_interference() {
        let w1 = WaveFunction::new(1.0, 1.0, 0.0);
        let w2 = WaveFunction::new(1.0, 1.0, 0.0);
        
        // Constructive interference at t=0
        let interference = w1.interfere(&w2, 0.0);
        assert!((interference - 0.0).abs() < 0.01);
    }

    #[test]
    fn test_apply_phase() {
        let states = vec!["s1".to_string(), "s2".to_string()];
        let mut superpos = SuperpositionState::new(states);
        
        superpos.apply_phase(0, PI / 2.0);
        
        // After phase shift, state should still be valid
        assert!(superpos.amplitudes[0].probability() > 0.0);
    }
}
