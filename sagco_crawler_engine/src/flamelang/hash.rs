use sha3::{Digest, Sha3_256};
use std::collections::HashMap;
use crate::flamelang::token::{FlameLangToken, FlameHash};

pub struct ContentAddressableStore {
    pub store: HashMap<FlameHash, FlameLangToken>,
}

impl ContentAddressableStore {
    pub fn new() -> Self {
        Self { store: HashMap::new() }
    }

    pub fn compute_hash(token: &FlameLangToken) -> FlameHash {
        let mut hasher = Sha3_256::new();
        hasher.update(format!("{:?}", token).as_bytes());
        FlameHash(hex::encode(hasher.finalize()))
    }

    pub fn insert(&mut self, token: FlameLangToken) -> FlameHash {
        let hash = Self::compute_hash(&token);
        self.store.insert(hash.clone(), token);
        hash
    }

    pub fn resolve(&self, hash: &FlameHash) -> Option<&FlameLangToken> {
        self.store.get(hash)
    }

    pub fn len(&self) -> usize {
        self.store.len()
    }
}
