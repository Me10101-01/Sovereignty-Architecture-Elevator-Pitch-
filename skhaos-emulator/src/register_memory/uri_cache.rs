// URI cache for storing recon results
use std::collections::HashMap;

pub struct UriCache {
    cache: HashMap<String, String>,
}

impl UriCache {
    pub fn new() -> Self {
        UriCache {
            cache: HashMap::new(),
        }
    }
    
    pub fn store(&mut self, uri: &str, result: &str) {
        self.cache.insert(uri.to_string(), result.to_string());
    }
    
    pub fn get(&self, uri: &str) -> Option<&String> {
        self.cache.get(uri)
    }
}
