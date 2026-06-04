pub struct StepperTick {
    pub tick_id: u64,
    pub timestamp_delta: u32,
    pub element_weight: f64,
}

pub struct CrawlerEngine {
    pub current_tick: u64,
    pub step_interval: u32,
}

impl CrawlerEngine {
    pub fn new(interval: u32) -> Self {
        Self { current_tick: 0, step_interval: interval }
    }

    pub fn advance_tick(&mut self, base_weight: f64) -> StepperTick {
        self.current_tick += 1;
        StepperTick {
            tick_id: self.current_tick,
            timestamp_delta: self.step_interval,
            element_weight: base_weight * self.current_tick as f64,
        }
    }
}
