/// Execution snapshot: one tick of the cursor walking the 640-node grid.
use std::collections::HashSet;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecState {
    pub tick:    u64,
    pub cursor:  u16,        // current cell id (0-639)
    pub visited: Vec<u16>,   // path walked so far (ordered)
    pub output:  u64,        // accumulated computation result
    pub seal:    String,     // SHA-256 of (tick || cursor || output)
}

impl ExecState {
    pub fn new(start_cell: u16) -> Self {
        let mut s = Self {
            tick:    0,
            cursor:  start_cell,
            visited: vec![start_cell],
            output:  0,
            seal:    String::new(),
        };
        s.seal = s.compute_seal();
        s
    }

    pub fn step(&mut self, next_cell: u16, cell_output: u64) {
        self.tick += 1;
        self.cursor = next_cell;
        self.visited.push(next_cell);
        self.output = self.output.wrapping_add(cell_output).rotate_left(7);
        self.seal = self.compute_seal();
    }

    fn compute_seal(&self) -> String {
        let mut h = Sha256::new();
        h.update(self.tick.to_le_bytes());
        h.update(self.cursor.to_le_bytes());
        h.update(self.output.to_le_bytes());
        hex::encode(&h.finalize()[..8])
    }

    pub fn visited_set(&self) -> HashSet<u16> {
        self.visited.iter().cloned().collect()
    }

    pub fn is_loop_closed(&self) -> bool {
        // loop closes when cursor revisits any prior cell
        let n = self.visited.len();
        if n < 2 { return false; }
        let current = self.visited[n - 1];
        self.visited[..n - 1].contains(&current)
    }

    pub fn loop_length(&self) -> Option<usize> {
        if !self.is_loop_closed() { return None; }
        let n = self.visited.len();
        let current = self.visited[n - 1];
        let first_visit = self.visited[..n - 1]
            .iter()
            .rposition(|&c| c == current)?;
        Some(n - 1 - first_visit)
    }

    pub fn unique_cells_visited(&self) -> usize {
        self.visited_set().len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn new_state_tick_zero() {
        let s = ExecState::new(0);
        assert_eq!(s.tick, 0);
        assert_eq!(s.cursor, 0);
        assert!(!s.seal.is_empty());
    }

    #[test]
    fn step_increments_tick() {
        let mut s = ExecState::new(0);
        s.step(10, 42);
        assert_eq!(s.tick, 1);
        assert_eq!(s.cursor, 10);
    }

    #[test]
    fn seal_changes_on_step() {
        let mut s = ExecState::new(0);
        let seal0 = s.seal.clone();
        s.step(1, 0);
        assert_ne!(s.seal, seal0);
    }

    #[test]
    fn loop_detection() {
        let mut s = ExecState::new(0);
        s.step(1, 0);
        s.step(2, 0);
        assert!(!s.is_loop_closed());
        s.step(0, 0); // back to origin
        assert!(s.is_loop_closed());
        assert_eq!(s.loop_length(), Some(3));
    }

    #[test]
    fn unique_cells() {
        let mut s = ExecState::new(5);
        s.step(10, 0);
        s.step(5, 0); // revisit
        assert_eq!(s.unique_cells_visited(), 2);
    }
}
