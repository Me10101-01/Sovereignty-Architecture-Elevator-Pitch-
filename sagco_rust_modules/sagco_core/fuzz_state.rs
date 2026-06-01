// SAGCO State Fuzzer — token-level mutation engine
// Mutates high-level opcode sequences rather than raw bytes.
// Catches logical false-green-lights that byte fuzzers miss.
// License: SSL-1.0 — Strategickhaos DAO LLC

#[derive(Debug, Clone, PartialEq)]
pub enum SagcoMutation {
    /// Swap adjacent commands at positions i and i+1
    SwapAdjacent(usize),
    /// Remove the command at position i entirely
    DropCommand(usize),
    /// Replace the pulse node-id with a foreign/invalid value
    CorruptPulse { command_idx: usize, bad_node: String },
    /// Replace the seal target with a path that will never exist
    CorruptSealTarget { command_idx: usize, bad_path: String },
    /// Replace the wave source with an empty/missing file path
    CorruptWaveSource { command_idx: usize, bad_path: String },
}

impl SagcoMutation {
    pub fn describe(&self) -> String {
        match self {
            SagcoMutation::SwapAdjacent(i)  => format!("SWAP_ADJACENT[{},{}]", i, i+1),
            SagcoMutation::DropCommand(i)   => format!("DROP_COMMAND[{}]", i),
            SagcoMutation::CorruptPulse { command_idx, bad_node } =>
                format!("CORRUPT_PULSE[{}]=>{}", command_idx, bad_node),
            SagcoMutation::CorruptSealTarget { command_idx, bad_path } =>
                format!("CORRUPT_SEAL_TARGET[{}]=>{}", command_idx, bad_path),
            SagcoMutation::CorruptWaveSource { command_idx, bad_path } =>
                format!("CORRUPT_WAVE_SOURCE[{}]=>{}", command_idx, bad_path),
        }
    }
}

/// Generates deterministic broken variants from a valid opcode pipeline.
pub struct SagcoStateFuzzer {
    pub base_pipeline: Vec<String>,
}

impl SagcoStateFuzzer {
    pub fn new(base: Vec<String>) -> Self {
        Self { base_pipeline: base }
    }

    /// Return (mutation_descriptor, mutated_pipeline) pairs.
    pub fn generate_mutations(&self) -> Vec<(SagcoMutation, Vec<String>)> {
        let mut variants = Vec::new();
        let base = &self.base_pipeline;
        let len = base.len();

        // ── 1. Structural order variance (Seal before Wave, etc.) ─────────
        for i in 0..len.saturating_sub(1) {
            let mut v = base.clone();
            v.swap(i, i + 1);
            variants.push((SagcoMutation::SwapAdjacent(i), v));
        }

        // ── 2. Command dropping (breaks dependencies) ─────────────────────
        for i in 0..len {
            let mut v = base.clone();
            v.remove(i);
            variants.push((SagcoMutation::DropCommand(i), v));
        }

        // ── 3. Pulse corruption (foreign node id) ─────────────────────────
        for (i, cmd) in base.iter().enumerate() {
            if cmd.trim_start().starts_with("pulse") {
                let mut v = base.clone();
                v[i] = "pulse 999999999999".to_string();
                variants.push((
                    SagcoMutation::CorruptPulse {
                        command_idx: i,
                        bad_node: "999999999999".to_string(),
                    },
                    v,
                ));
            }
        }

        // ── 4. Seal target corruption (path can never exist) ──────────────
        for (i, cmd) in base.iter().enumerate() {
            if cmd.trim_start().starts_with("seal") {
                let mut v = base.clone();
                v[i] = "seal /proc/sagco_ghost_artifact.bin".to_string();
                variants.push((
                    SagcoMutation::CorruptSealTarget {
                        command_idx: i,
                        bad_path: "/proc/sagco_ghost_artifact.bin".to_string(),
                    },
                    v,
                ));
            }
        }

        // ── 5. Wave source corruption (empty/missing file) ────────────────
        for (i, cmd) in base.iter().enumerate() {
            if cmd.trim_start().starts_with("wave") {
                let mut v = base.clone();
                v[i] = "wave /tmp/sagco_nonexistent_wave_src.txt".to_string();
                variants.push((
                    SagcoMutation::CorruptWaveSource {
                        command_idx: i,
                        bad_path: "/tmp/sagco_nonexistent_wave_src.txt".to_string(),
                    },
                    v,
                ));
            }
        }

        variants
    }

    /// Total mutation count for the current base pipeline.
    pub fn mutation_count(&self) -> usize {
        self.generate_mutations().len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn canonical_pipeline() -> Vec<String> {
        vec![
            "read gcp_services.txt".to_string(),
            "wave gcp_services.txt".to_string(),
            "pulse 793398609444".to_string(),
            "seal evidence.bin".to_string(),
        ]
    }

    #[test]
    fn swap_produces_correct_count() {
        let f = SagcoStateFuzzer::new(canonical_pipeline());
        let swaps: Vec<_> = f.generate_mutations()
            .into_iter()
            .filter(|(m, _)| matches!(m, SagcoMutation::SwapAdjacent(_)))
            .collect();
        // 4-command pipeline → 3 adjacent pairs
        assert_eq!(swaps.len(), 3);
    }

    #[test]
    fn drop_produces_correct_count() {
        let f = SagcoStateFuzzer::new(canonical_pipeline());
        let drops: Vec<_> = f.generate_mutations()
            .into_iter()
            .filter(|(m, _)| matches!(m, SagcoMutation::DropCommand(_)))
            .collect();
        // one drop per command
        assert_eq!(drops.len(), 4);
    }

    #[test]
    fn corrupt_pulse_replaces_node_id() {
        let f = SagcoStateFuzzer::new(canonical_pipeline());
        let corrupt: Vec<_> = f.generate_mutations()
            .into_iter()
            .filter(|(m, _)| matches!(m, SagcoMutation::CorruptPulse { .. }))
            .collect();
        assert_eq!(corrupt.len(), 1);
        let (_, variant) = &corrupt[0];
        assert!(variant.iter().any(|c| c.contains("999999999999")));
        assert!(!variant.iter().any(|c| c.contains("793398609444")));
    }

    #[test]
    fn corrupt_seal_target_changes_path() {
        let f = SagcoStateFuzzer::new(canonical_pipeline());
        let corrupt: Vec<_> = f.generate_mutations()
            .into_iter()
            .filter(|(m, _)| matches!(m, SagcoMutation::CorruptSealTarget { .. }))
            .collect();
        assert_eq!(corrupt.len(), 1);
        let (_, variant) = &corrupt[0];
        assert!(variant.iter().any(|c| c.contains("/proc/")));
    }

    #[test]
    fn swap_adjacent_reorders_commands() {
        let f = SagcoStateFuzzer::new(canonical_pipeline());
        let (_, variant) = f.generate_mutations()
            .into_iter()
            .find(|(m, _)| *m == SagcoMutation::SwapAdjacent(2))
            .expect("swap at index 2 must exist");
        // commands 2 (pulse) and 3 (seal) should be swapped
        assert!(variant[2].starts_with("seal"));
        assert!(variant[3].starts_with("pulse"));
    }

    #[test]
    fn mutation_count_is_deterministic() {
        let f = SagcoStateFuzzer::new(canonical_pipeline());
        assert_eq!(f.mutation_count(), f.mutation_count());
    }
}
