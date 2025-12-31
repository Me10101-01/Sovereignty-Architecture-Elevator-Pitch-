// Neural Tick Clock Module
// Oscillators: Syncs system ticks to brain wave frequencies
// Maps Hz ranges (Delta to Gamma) to system tick rates

use std::f64::consts::PI;
use std::time::{Duration, Instant};

/// Neural tick clock synchronized to brain wave frequencies
pub struct NeuralTickClock {
    /// Current frequency in Hz
    frequency_hz: f64,
    /// Wave type based on frequency
    wave_type: WaveType,
    /// Start time for oscillation
    start_time: Instant,
    /// Tick counter
    tick_count: u64,
}

#[derive(Debug, Clone, PartialEq)]
pub enum WaveType {
    Delta,  // 0.5-4 Hz (deep sleep, unconscious)
    Theta,  // 4-8 Hz (meditation, creativity, REM)
    Alpha,  // 8-13 Hz (relaxed, calm, reflective)
    Beta,   // 13-30 Hz (alert, focused, active thinking)
    Gamma,  // 30-100 Hz (high-level processing, insight)
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

    /// Get typical frequency for wave type
    pub fn typical_frequency(&self) -> f64 {
        match self {
            WaveType::Delta => 2.0,
            WaveType::Theta => 6.0,
            WaveType::Alpha => 10.0,
            WaveType::Beta => 18.0,
            WaveType::Gamma => 40.0,
        }
    }

    /// Get description of mental state
    pub fn mental_state(&self) -> &str {
        match self {
            WaveType::Delta => "Deep sleep, unconscious",
            WaveType::Theta => "Deep meditation, creativity, REM sleep",
            WaveType::Alpha => "Relaxed, calm, reflective",
            WaveType::Beta => "Alert, focused, active thinking",
            WaveType::Gamma => "High-level processing, insight, peak awareness",
        }
    }
}

impl NeuralTickClock {
    /// Create a new neural tick clock at specified frequency
    pub fn new(frequency_hz: f64) -> Self {
        NeuralTickClock {
            frequency_hz,
            wave_type: WaveType::from_hz(frequency_hz),
            start_time: Instant::now(),
            tick_count: 0,
        }
    }

    /// Create clock from wave type
    pub fn from_wave_type(wave_type: WaveType) -> Self {
        let frequency_hz = wave_type.typical_frequency();
        NeuralTickClock {
            frequency_hz,
            wave_type,
            start_time: Instant::now(),
            tick_count: 0,
        }
    }

    /// Set frequency and update wave type
    pub fn set_frequency(&mut self, hz: f64) {
        self.frequency_hz = hz;
        self.wave_type = WaveType::from_hz(hz);
    }

    /// Get current frequency
    pub fn frequency(&self) -> f64 {
        self.frequency_hz
    }

    /// Get wave type
    pub fn wave_type(&self) -> &WaveType {
        &self.wave_type
    }

    /// Calculate tick period in milliseconds
    pub fn tick_period_ms(&self) -> u64 {
        (1000.0 / self.frequency_hz) as u64
    }

    /// Execute a tick (increment counter)
    pub fn tick(&mut self) {
        self.tick_count += 1;
    }

    /// Get tick count
    pub fn tick_count(&self) -> u64 {
        self.tick_count
    }

    /// Calculate wave amplitude at current time
    pub fn wave_amplitude(&self) -> f64 {
        let elapsed = self.start_time.elapsed().as_secs_f64();
        (2.0 * PI * self.frequency_hz * elapsed).sin()
    }

    /// Reset clock
    pub fn reset(&mut self) {
        self.start_time = Instant::now();
        self.tick_count = 0;
    }

    /// Check if it's time for next tick
    pub fn should_tick(&self) -> bool {
        let elapsed_ms = self.start_time.elapsed().as_millis() as u64;
        let expected_ticks = elapsed_ms / self.tick_period_ms();
        expected_ticks > self.tick_count
    }

    /// Get time until next tick
    pub fn time_until_next_tick(&self) -> Duration {
        let elapsed_ms = self.start_time.elapsed().as_millis() as u64;
        let next_tick_time = (self.tick_count + 1) * self.tick_period_ms();
        
        if next_tick_time > elapsed_ms {
            Duration::from_millis(next_tick_time - elapsed_ms)
        } else {
            Duration::from_millis(0)
        }
    }

    /// Convert to UDAP address
    pub fn to_udap(&self) -> String {
        format!(
            "skhaos://agent/neural_clock?hz={}&wave_type={:?}&ticks={}",
            self.frequency_hz,
            self.wave_type,
            self.tick_count
        )
    }
}

/// Clock synchronizer for multiple neural clocks
pub struct ClockSynchronizer {
    clocks: Vec<NeuralTickClock>,
}

impl ClockSynchronizer {
    pub fn new() -> Self {
        ClockSynchronizer {
            clocks: Vec::new(),
        }
    }

    /// Add a clock to synchronize
    pub fn add_clock(&mut self, clock: NeuralTickClock) {
        self.clocks.push(clock);
    }

    /// Tick all clocks that are ready
    pub fn sync_tick(&mut self) -> usize {
        let mut ticked = 0;
        for clock in &mut self.clocks {
            if clock.should_tick() {
                clock.tick();
                ticked += 1;
            }
        }
        ticked
    }

    /// Get all clocks
    pub fn clocks(&self) -> &[NeuralTickClock] {
        &self.clocks
    }

    /// Get average frequency across all clocks
    pub fn average_frequency(&self) -> f64 {
        if self.clocks.is_empty() {
            return 0.0;
        }

        let sum: f64 = self.clocks.iter().map(|c| c.frequency()).sum();
        sum / self.clocks.len() as f64
    }
}

impl Default for ClockSynchronizer {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;

    #[test]
    fn test_wave_type_from_hz() {
        assert_eq!(WaveType::from_hz(2.0), WaveType::Delta);
        assert_eq!(WaveType::from_hz(6.0), WaveType::Theta);
        assert_eq!(WaveType::from_hz(10.0), WaveType::Alpha);
        assert_eq!(WaveType::from_hz(18.0), WaveType::Beta);
        assert_eq!(WaveType::from_hz(40.0), WaveType::Gamma);
    }

    #[test]
    fn test_create_clock() {
        let clock = NeuralTickClock::new(10.0);
        assert_eq!(clock.frequency(), 10.0);
        assert_eq!(clock.wave_type(), &WaveType::Alpha);
    }

    #[test]
    fn test_create_from_wave_type() {
        let clock = NeuralTickClock::from_wave_type(WaveType::Beta);
        assert_eq!(clock.frequency(), 18.0);
        assert_eq!(clock.wave_type(), &WaveType::Beta);
    }

    #[test]
    fn test_tick_period() {
        let clock = NeuralTickClock::new(10.0);
        assert_eq!(clock.tick_period_ms(), 100); // 1000ms / 10Hz = 100ms
    }

    #[test]
    fn test_tick() {
        let mut clock = NeuralTickClock::new(10.0);
        assert_eq!(clock.tick_count(), 0);
        
        clock.tick();
        assert_eq!(clock.tick_count(), 1);
        
        clock.tick();
        assert_eq!(clock.tick_count(), 2);
    }

    #[test]
    fn test_wave_amplitude() {
        let clock = NeuralTickClock::new(1.0);
        let amplitude = clock.wave_amplitude();
        
        // Should be a value between -1 and 1
        assert!(amplitude >= -1.0 && amplitude <= 1.0);
    }

    #[test]
    fn test_set_frequency() {
        let mut clock = NeuralTickClock::new(10.0);
        
        clock.set_frequency(18.0);
        assert_eq!(clock.frequency(), 18.0);
        assert_eq!(clock.wave_type(), &WaveType::Beta);
    }

    #[test]
    fn test_reset() {
        let mut clock = NeuralTickClock::new(10.0);
        
        clock.tick();
        clock.tick();
        assert_eq!(clock.tick_count(), 2);
        
        clock.reset();
        assert_eq!(clock.tick_count(), 0);
    }

    #[test]
    fn test_to_udap() {
        let clock = NeuralTickClock::new(10.0);
        let udap = clock.to_udap();
        
        assert!(udap.contains("skhaos://agent/neural_clock"));
        assert!(udap.contains("hz=10"));
        assert!(udap.contains("Alpha"));
    }

    #[test]
    fn test_clock_synchronizer() {
        let mut sync = ClockSynchronizer::new();
        
        sync.add_clock(NeuralTickClock::new(10.0));
        sync.add_clock(NeuralTickClock::new(18.0));
        
        assert_eq!(sync.clocks().len(), 2);
        
        let avg = sync.average_frequency();
        assert!((avg - 14.0).abs() < 0.1);
    }

    #[test]
    fn test_should_tick() {
        let mut clock = NeuralTickClock::new(1000.0); // High frequency for quick test
        
        thread::sleep(Duration::from_millis(5));
        
        // Should be ready to tick after a few milliseconds
        assert!(clock.should_tick());
        
        clock.tick();
    }
}
