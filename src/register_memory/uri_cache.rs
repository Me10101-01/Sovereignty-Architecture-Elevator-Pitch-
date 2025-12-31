// URI Cache Module
// Fast UDAP address lookup and caching

use std::collections::HashMap;
use std::time::Instant;

/// LRU (Least Recently Used) cache for UDAP addresses
pub struct URICache {
    cache: HashMap<String, CacheEntry>,
    max_size: usize,
    access_order: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct CacheEntry {
    pub value: String,
    pub timestamp: Instant,
    pub hit_count: usize,
    pub metadata: HashMap<String, String>,
}

impl URICache {
    /// Create a new URI cache with specified maximum size
    pub fn new(max_size: usize) -> Self {
        URICache {
            cache: HashMap::new(),
            max_size,
            access_order: Vec::new(),
        }
    }

    /// Insert a value into the cache
    pub fn insert(&mut self, key: String, value: String) {
        // If at capacity, remove least recently used
        if self.cache.len() >= self.max_size && !self.cache.contains_key(&key) {
            if let Some(lru_key) = self.access_order.first().cloned() {
                self.cache.remove(&lru_key);
                self.access_order.remove(0);
            }
        }

        let entry = CacheEntry {
            value,
            timestamp: Instant::now(),
            hit_count: 0,
            metadata: HashMap::new(),
        };

        self.cache.insert(key.clone(), entry);
        self.update_access_order(&key);
    }

    /// Get a value from the cache
    pub fn get(&mut self, key: &str) -> Option<String> {
        if let Some(entry) = self.cache.get_mut(key) {
            entry.hit_count += 1;
            self.update_access_order(key);
            Some(entry.value.clone())
        } else {
            None
        }
    }

    /// Check if key exists in cache
    pub fn contains(&self, key: &str) -> bool {
        self.cache.contains_key(key)
    }

    /// Remove a key from cache
    pub fn remove(&mut self, key: &str) -> Option<CacheEntry> {
        self.access_order.retain(|k| k != key);
        self.cache.remove(key)
    }

    /// Update access order (move to end)
    fn update_access_order(&mut self, key: &str) {
        self.access_order.retain(|k| k != key);
        self.access_order.push(key.to_string());
    }

    /// Get cache hit rate
    pub fn hit_rate(&self) -> f64 {
        let total_hits: usize = self.cache.values().map(|e| e.hit_count).sum();
        let total_requests = total_hits + self.cache.len();
        
        if total_requests == 0 {
            0.0
        } else {
            total_hits as f64 / total_requests as f64
        }
    }

    /// Get most accessed keys
    pub fn most_accessed(&self, count: usize) -> Vec<(String, usize)> {
        let mut entries: Vec<(String, usize)> = self.cache
            .iter()
            .map(|(k, v)| (k.clone(), v.hit_count))
            .collect();

        entries.sort_by(|a, b| b.1.cmp(&a.1));
        entries.truncate(count);
        entries
    }

    /// Clear the cache
    pub fn clear(&mut self) {
        self.cache.clear();
        self.access_order.clear();
    }

    /// Get cache size
    pub fn len(&self) -> usize {
        self.cache.len()
    }

    /// Check if cache is empty
    pub fn is_empty(&self) -> bool {
        self.cache.is_empty()
    }

    /// Add metadata to a cached entry
    pub fn add_metadata(&mut self, key: &str, meta_key: String, meta_value: String) -> Result<(), String> {
        self.cache
            .get_mut(key)
            .map(|entry| {
                entry.metadata.insert(meta_key, meta_value);
            })
            .ok_or_else(|| "Key not found in cache".to_string())
    }

    /// Get metadata from a cached entry
    pub fn get_metadata(&self, key: &str, meta_key: &str) -> Option<String> {
        self.cache
            .get(key)
            .and_then(|entry| entry.metadata.get(meta_key).cloned())
    }
}

impl Default for URICache {
    fn default() -> Self {
        Self::new(1000)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_insert_and_get() {
        let mut cache = URICache::new(10);
        
        cache.insert("skhaos://pipe/run/5".to_string(), "value1".to_string());
        let result = cache.get("skhaos://pipe/run/5");
        
        assert_eq!(result, Some("value1".to_string()));
    }

    #[test]
    fn test_lru_eviction() {
        let mut cache = URICache::new(2);
        
        cache.insert("key1".to_string(), "val1".to_string());
        cache.insert("key2".to_string(), "val2".to_string());
        cache.insert("key3".to_string(), "val3".to_string());
        
        // key1 should be evicted
        assert!(!cache.contains("key1"));
        assert!(cache.contains("key2"));
        assert!(cache.contains("key3"));
    }

    #[test]
    fn test_access_order_update() {
        let mut cache = URICache::new(2);
        
        cache.insert("key1".to_string(), "val1".to_string());
        cache.insert("key2".to_string(), "val2".to_string());
        cache.get("key1"); // Access key1, making it recently used
        cache.insert("key3".to_string(), "val3".to_string());
        
        // key2 should be evicted, not key1
        assert!(cache.contains("key1"));
        assert!(!cache.contains("key2"));
        assert!(cache.contains("key3"));
    }

    #[test]
    fn test_hit_count() {
        let mut cache = URICache::new(10);
        
        cache.insert("key1".to_string(), "val1".to_string());
        cache.get("key1");
        cache.get("key1");
        cache.get("key1");
        
        let entry = cache.cache.get("key1").unwrap();
        assert_eq!(entry.hit_count, 3);
    }

    #[test]
    fn test_most_accessed() {
        let mut cache = URICache::new(10);
        
        cache.insert("key1".to_string(), "val1".to_string());
        cache.insert("key2".to_string(), "val2".to_string());
        
        cache.get("key1");
        cache.get("key1");
        cache.get("key2");
        
        let most = cache.most_accessed(2);
        assert_eq!(most[0].0, "key1");
        assert_eq!(most[0].1, 2);
    }

    #[test]
    fn test_metadata() {
        let mut cache = URICache::new(10);
        
        cache.insert("key1".to_string(), "val1".to_string());
        cache.add_metadata("key1", "domain".to_string(), "pipe".to_string()).unwrap();
        
        let metadata = cache.get_metadata("key1", "domain");
        assert_eq!(metadata, Some("pipe".to_string()));
    }

    #[test]
    fn test_clear() {
        let mut cache = URICache::new(10);
        
        cache.insert("key1".to_string(), "val1".to_string());
        cache.clear();
        
        assert_eq!(cache.len(), 0);
        assert!(cache.is_empty());
    }
}
