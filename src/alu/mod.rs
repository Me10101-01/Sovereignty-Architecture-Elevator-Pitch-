// ALU (Arithmetic Logic Unit) Module
// Handles arithmetic transforms: pipe offsets, neural weights, trigonometric wave cores
//
// Maps pipefitting domains to computational transforms using UDAP addressing:
// skhaos://quantum/alu/pipe_offset?angle=45
// skhaos://quantum/alu/neural_weight?layer=3&neuron=5

pub mod pipe_transform;
pub mod neural_weight;

use std::f64::consts::PI;

/// Core ALU structure for quantum-inspired arithmetic operations
pub struct ALU {
    /// Wave function cache for trigonometric transforms
    wave_cache: Vec<WaveTransform>,
    /// Precision for floating point operations
    precision: f64,
}

/// Represents a trigonometric wave transformation
#[derive(Debug, Clone)]
pub struct WaveTransform {
    pub frequency: f64,
    pub amplitude: f64,
    pub phase: f64,
    pub domain: String,
}

impl ALU {
    /// Create a new ALU instance with default precision
    pub fn new() -> Self {
        ALU {
            wave_cache: Vec::new(),
            precision: 1e-10,
        }
    }

    /// Create ALU with custom precision
    pub fn with_precision(precision: f64) -> Self {
        ALU {
            wave_cache: Vec::new(),
            precision,
        }
    }

    /// Execute a trig-formula wave core transform
    /// Converts angles to wave superpositions using sin/cos
    pub fn wave_transform(&mut self, angle: f64, amplitude: f64) -> (f64, f64) {
        let radians = angle * PI / 180.0;
        let x_component = amplitude * radians.cos();
        let y_component = amplitude * radians.sin();
        
        // Cache the transformation
        self.wave_cache.push(WaveTransform {
            frequency: 1.0,
            amplitude,
            phase: angle,
            domain: "pipe".to_string(),
        });
        
        (x_component, y_component)
    }

    /// Calculate offset using Run, Offset, and Travel (pipefitting)
    /// Returns the offset distance
    pub fn calculate_offset(&self, run: f64, offset: f64) -> f64 {
        // Using Pythagorean theorem for offset calculation
        (run.powi(2) + offset.powi(2)).sqrt()
    }

    /// Calculate travel distance for a given angle and offset
    pub fn calculate_travel(&self, offset: f64, angle: f64) -> f64 {
        let radians = angle * PI / 180.0;
        if radians.sin().abs() > self.precision {
            offset / radians.sin()
        } else {
            f64::MAX // Undefined for angle approaching 0
        }
    }

    /// Superposition of multiple wave functions
    /// Quantum-inspired: combine multiple domain transforms
    pub fn superpose_waves(&self, waves: &[(f64, f64, f64)]) -> f64 {
        waves.iter()
            .map(|(freq, amp, phase)| {
                amp * (2.0 * PI * freq + phase).sin()
            })
            .sum()
    }

    /// Clear wave cache
    pub fn clear_cache(&mut self) {
        self.wave_cache.clear();
    }

    /// Get cached wave transforms
    pub fn get_cache(&self) -> &[WaveTransform] {
        &self.wave_cache
    }
}

impl Default for ALU {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_wave_transform() {
        let mut alu = ALU::new();
        let (x, y) = alu.wave_transform(45.0, 1.0);
        
        // 45 degrees should give approximately equal x and y components
        assert!((x - 0.707).abs() < 0.01);
        assert!((y - 0.707).abs() < 0.01);
    }

    #[test]
    fn test_offset_calculation() {
        let alu = ALU::new();
        let offset = alu.calculate_offset(3.0, 4.0);
        
        // 3-4-5 triangle
        assert!((offset - 5.0).abs() < 0.01);
    }

    #[test]
    fn test_travel_calculation() {
        let alu = ALU::new();
        let travel = alu.calculate_travel(10.0, 30.0);
        
        // Travel = offset / sin(angle)
        assert!((travel - 20.0).abs() < 0.1);
    }

    #[test]
    fn test_superposition() {
        let alu = ALU::new();
        let waves = vec![
            (1.0, 1.0, 0.0),
            (2.0, 0.5, PI / 4.0),
        ];
        
        let result = alu.superpose_waves(&waves);
        assert!(result.abs() <= 1.5); // Sum of amplitudes
    }
}
