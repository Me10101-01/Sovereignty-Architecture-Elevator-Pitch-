pub struct OmniCalculation {
    pub source_wafer_id: String,
    pub raw_word_frequency: Vec<(String, u32)>,
    pub scalar_weight: f64,
}

impl OmniCalculation {
    pub fn new(wafer: &str, weight: f64) -> Self {
        Self {
            source_wafer_id: wafer.to_string(),
            raw_word_frequency: Vec::new(),
            scalar_weight: weight,
        }
    }

    pub fn insert_frequency(&mut self, term: &str, count: u32) {
        self.raw_word_frequency.push((term.to_string(), count));
    }
}
