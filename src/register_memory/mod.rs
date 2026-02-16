// Register Memory Module
// State persistence: Caches UDAP addresses, moods, frequencies
// Duration tracked in Z-axis for sustained states

pub mod uri_cache;
pub mod mood_state;

use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Register Memory for state management
pub struct RegisterMemory {
    /// UDAP address cache
    uri_cache: HashMap<String, CachedValue>,
    /// Mood state storage
    mood_states: HashMap<String, MoodState>,
    /// Temporal state tracking
    temporal_states: Vec<TemporalState>,
}

/// Cached value with timestamp
#[derive(Debug, Clone)]
pub struct CachedValue {
    pub value: String,
    pub timestamp: Instant,
    pub access_count: usize,
}

/// Mood state representation
#[derive(Debug, Clone)]
pub struct MoodState {
    pub frequency_hz: f64,
    pub color: String,
    pub state_name: String,
    pub intensity: f64,
    pub duration: Duration,
    pub created_at: Instant,
}

/// Temporal state with Z-axis duration
#[derive(Debug, Clone)]
pub struct TemporalState {
    pub address: String,
    pub start_time: Instant,
    pub duration: Duration,
    pub state_data: String,
}

impl RegisterMemory {
    /// Create a new Register Memory
    pub fn new() -> Self {
        RegisterMemory {
            uri_cache: HashMap::new(),
            mood_states: HashMap::new(),
            temporal_states: Vec::new(),
        }
    }

    /// Cache a UDAP address with value
    pub fn cache(&mut self, address: String, value: String) {
        self.uri_cache.insert(
            address.clone(),
            CachedValue {
                value,
                timestamp: Instant::now(),
                access_count: 0,
            }
        );
    }

    /// Retrieve from cache
    pub fn get_cached(&mut self, address: &str) -> Option<String> {
        if let Some(cached) = self.uri_cache.get_mut(address) {
            cached.access_count += 1;
            Some(cached.value.clone())
        } else {
            None
        }
    }

    /// Store mood state
    pub fn store_mood(&mut self, id: String, mood: MoodState) {
        self.mood_states.insert(id, mood);
    }

    /// Get mood state
    pub fn get_mood(&self, id: &str) -> Option<&MoodState> {
        self.mood_states.get(id)
    }

    /// Add temporal state with duration
    pub fn add_temporal_state(&mut self, address: String, duration: Duration, state_data: String) {
        let temporal = TemporalState {
            address,
            start_time: Instant::now(),
            duration,
            state_data,
        };
        
        self.temporal_states.push(temporal);
    }

    /// Get active temporal states
    pub fn active_temporal_states(&self) -> Vec<&TemporalState> {
        let now = Instant::now();
        self.temporal_states
            .iter()
            .filter(|s| now.duration_since(s.start_time) < s.duration)
            .collect()
    }

    /// Clear expired temporal states
    pub fn clear_expired(&mut self) {
        let now = Instant::now();
        self.temporal_states.retain(|s| {
            now.duration_since(s.start_time) < s.duration
        });
    }

    /// Get cache statistics
    pub fn cache_stats(&self) -> CacheStats {
        let total_accesses: usize = self.uri_cache.values()
            .map(|v| v.access_count)
            .sum();

        CacheStats {
            total_entries: self.uri_cache.len(),
            total_accesses,
            mood_states_count: self.mood_states.len(),
            temporal_states_count: self.temporal_states.len(),
        }
    }

    /// Clear all cache
    pub fn clear_cache(&mut self) {
        self.uri_cache.clear();
    }

    /// Clear mood states
    pub fn clear_moods(&mut self) {
        self.mood_states.clear();
    }
}

/// Cache statistics
#[derive(Debug)]
pub struct CacheStats {
    pub total_entries: usize,
    pub total_accesses: usize,
    pub mood_states_count: usize,
    pub temporal_states_count: usize,
}

impl Default for RegisterMemory {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_and_retrieve() {
        let mut memory = RegisterMemory::new();
        
        memory.cache(
            "skhaos://pipe/run/5".to_string(),
            "cached_value".to_string()
        );
        
        let retrieved = memory.get_cached("skhaos://pipe/run/5");
        assert_eq!(retrieved, Some("cached_value".to_string()));
    }

    #[test]
    fn test_access_count() {
        let mut memory = RegisterMemory::new();
        
        memory.cache("test".to_string(), "value".to_string());
        memory.get_cached("test");
        memory.get_cached("test");
        
        let cached = memory.uri_cache.get("test").unwrap();
        assert_eq!(cached.access_count, 2);
    }

    #[test]
    fn test_mood_storage() {
        let mut memory = RegisterMemory::new();
        
        let mood = MoodState {
            frequency_hz: 10.0,
            color: "blue".to_string(),
            state_name: "alpha".to_string(),
            intensity: 0.75,
            duration: Duration::from_secs(60),
            created_at: Instant::now(),
        };
        
        memory.store_mood("alpha_state".to_string(), mood);
        
        let retrieved = memory.get_mood("alpha_state");
        assert!(retrieved.is_some());
        assert_eq!(retrieved.unwrap().frequency_hz, 10.0);
    }

    #[test]
    fn test_temporal_state() {
        let mut memory = RegisterMemory::new();
        
        memory.add_temporal_state(
            "skhaos://mood/alpha".to_string(),
            Duration::from_secs(60),
            "relaxed".to_string()
        );
        
        let active = memory.active_temporal_states();
        assert_eq!(active.len(), 1);
    }

    #[test]
    fn test_cache_stats() {
        let mut memory = RegisterMemory::new();
        
        memory.cache("addr1".to_string(), "val1".to_string());
        memory.cache("addr2".to_string(), "val2".to_string());
        memory.get_cached("addr1");
        
        let stats = memory.cache_stats();
        assert_eq!(stats.total_entries, 2);
        assert_eq!(stats.total_accesses, 1);
    }

    #[test]
    fn test_clear_cache() {
        let mut memory = RegisterMemory::new();
        
        memory.cache("test".to_string(), "value".to_string());
        memory.clear_cache();
        
        assert_eq!(memory.uri_cache.len(), 0);
    }
}
