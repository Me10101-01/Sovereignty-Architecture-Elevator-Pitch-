// ALU Module - Trigonometric wave calculations for whale Hz
use std::f64::consts::PI;

pub fn sine_wave(hz: f64, time: f64) -> f64 {
    (2.0 * PI * hz * time).sin()
}

pub fn cosine_wave(hz: f64, time: f64) -> f64 {
    (2.0 * PI * hz * time).cos()
}

pub fn oscillate(hz: f64, duration: f64, samples: usize) -> Vec<f64> {
    (0..samples)
        .map(|i| {
            let time = (i as f64 / samples as f64) * duration;
            sine_wave(hz, time)
        })
        .collect()
}
