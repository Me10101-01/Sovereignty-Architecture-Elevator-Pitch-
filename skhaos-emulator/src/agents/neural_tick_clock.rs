// Neural Tick Clock - Oscillates at whale/classical Hz
use std::time::{Duration, Instant};

pub struct TickClock {
    frequency_hz: f64,
    last_tick: Instant,
}

impl TickClock {
    pub fn new(hz: f64) -> Self {
        TickClock {
            frequency_hz: hz,
            last_tick: Instant::now(),
        }
    }
    
    pub fn tick(&mut self) -> bool {
        let period = Duration::from_secs_f64(1.0 / self.frequency_hz);
        if self.last_tick.elapsed() >= period {
            self.last_tick = Instant::now();
            true
        } else {
            false
        }
    }
}
