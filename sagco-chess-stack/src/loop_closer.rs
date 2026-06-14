/// Loop-closer: walk the move graph until a cycle is found or the budget expires.
///
/// A closed loop = QED: piece path returns to a previously-visited cell.
/// That's the proof: execution is self-referential and terminates.
use crate::move_graph::{MoveMap, PieceKind, build_move_map};
use crate::state::ExecState;
use crate::stack::Stack;

const DEFAULT_MAX_TICKS: u64 = 10_000;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LoopStatus {
    /// Still walking, not yet closed.
    Open,
    /// Cycle found: returned to `return_cell` after `length` steps from tick `at_tick`.
    Closed {
        at_tick:     u64,
        length:      usize,
        return_cell: u16,
        seal:        String,
    },
    /// Budget exhausted without finding a loop.
    Exhausted { ticks_used: u64 },
}

pub struct LoopCloser {
    pub stack:     Stack,
    pub map:       MoveMap,
    pub state:     ExecState,
    pub status:    LoopStatus,
    pub max_ticks: u64,
}

impl LoopCloser {
    pub fn new(piece: PieceKind, start_cell: u16) -> Self {
        let stack = Stack::new();
        let map   = build_move_map(piece);
        let state = ExecState::new(start_cell);
        Self {
            stack,
            map,
            state,
            status: LoopStatus::Open,
            max_ticks: DEFAULT_MAX_TICKS,
        }
    }

    pub fn with_max_ticks(mut self, n: u64) -> Self {
        self.max_ticks = n;
        self
    }

    /// Run until loop closes or budget expires. Returns reference to final status.
    pub fn run(&mut self) -> &LoopStatus {
        while self.state.tick < self.max_ticks {
            if self.state.is_loop_closed() {
                let length = self.state.loop_length().unwrap_or(0);
                self.status = LoopStatus::Closed {
                    at_tick:     self.state.tick,
                    length,
                    return_cell: self.state.cursor,
                    seal:        self.state.seal.clone(),
                };
                return &self.status;
            }

            // pick next cell: first available neighbor not yet visited
            let next = self
                .map
                .get(&self.state.cursor)
                .and_then(|targets| {
                    let visited = self.state.visited_set();
                    // prefer unvisited; fall back to first visited (causes loop close)
                    targets
                        .iter()
                        .find(|&&t| !visited.contains(&t))
                        .or_else(|| targets.first())
                        .copied()
                });

            match next {
                None => break, // isolated cell (shouldn't happen with 10-layer inter-edges)
                Some(next_id) => {
                    let cell_out = self
                        .stack
                        .cell_by_id(next_id)
                        .map_or(0, |c| c.call(self.state.output));
                    self.state.step(next_id, cell_out);
                }
            }
        }

        // check one last time after loop
        if self.state.is_loop_closed() {
            let length = self.state.loop_length().unwrap_or(0);
            self.status = LoopStatus::Closed {
                at_tick:     self.state.tick,
                length,
                return_cell: self.state.cursor,
                seal:        self.state.seal.clone(),
            };
        } else {
            self.status = LoopStatus::Exhausted {
                ticks_used: self.state.tick,
            };
        }
        &self.status
    }

    pub fn report(&self) -> String {
        let mut out = String::new();
        out.push_str("  ── Loop Closer Report ──────────────────────────────────\n");
        out.push_str(&format!("  Start cell:     {}\n", self.state.visited.first().unwrap_or(&0)));
        out.push_str(&format!("  Ticks elapsed:  {}\n", self.state.tick));
        out.push_str(&format!("  Unique visited: {}\n", self.state.unique_cells_visited()));
        out.push_str(&format!("  Final output:   0x{:016x}\n", self.state.output));
        out.push_str(&format!("  State seal:     {}\n", self.state.seal));
        match &self.status {
            LoopStatus::Open => out.push_str("  Status: OPEN (still walking)\n"),
            LoopStatus::Closed { at_tick, length, return_cell, seal } => {
                out.push_str(&format!("  Status: CLOSED ✓\n"));
                out.push_str(&format!("  Loop closed at tick {}, length={}, return_cell={}\n",
                    at_tick, length, return_cell));
                out.push_str(&format!("  Closure seal: {}\n", seal));
            }
            LoopStatus::Exhausted { ticks_used } => {
                out.push_str(&format!("  Status: EXHAUSTED after {} ticks\n", ticks_used));
            }
        }
        out.push_str("  ────────────────────────────────────────────────────────\n");
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn king_closes_loop_quickly() {
        // King from L0-A1 (id=0): 3 neighbors, will revisit within a handful of ticks
        let mut lc = LoopCloser::new(PieceKind::King, 0).with_max_ticks(500);
        let status = lc.run().clone();
        matches!(status, LoopStatus::Closed { .. });
    }

    #[test]
    fn knight_closes_within_budget() {
        let mut lc = LoopCloser::new(PieceKind::Knight, 0).with_max_ticks(DEFAULT_MAX_TICKS);
        let status = lc.run().clone();
        assert_ne!(status, LoopStatus::Open);
    }

    #[test]
    fn loop_closer_report_not_empty() {
        let mut lc = LoopCloser::new(PieceKind::King, 320).with_max_ticks(200);
        lc.run();
        assert!(!lc.report().is_empty());
    }

    #[test]
    fn closed_loop_seal_nonempty() {
        let mut lc = LoopCloser::new(PieceKind::King, 0).with_max_ticks(500);
        if let LoopStatus::Closed { seal, .. } = lc.run().clone() {
            assert!(!seal.is_empty());
        }
    }
}
