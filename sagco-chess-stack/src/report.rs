/// Stack audit report: geometry, loop results, and brick registration.
use crate::stack::Stack;
use crate::registry::StackBrick;
use crate::loop_closer::LoopCloser;
use crate::move_graph::PieceKind;

pub struct StackReport {
    pub stack: Stack,
    pub brick: StackBrick,
}

impl StackReport {
    pub fn new() -> Self {
        Self {
            stack: Stack::new(),
            brick: StackBrick::build(),
        }
    }

    pub fn geometry_section(&self) -> String {
        let mut out = String::new();
        out.push_str("\n  ╔═══════════════════════════════════════════════════════╗\n");
        out.push_str(  "  ║           SAGCO CHESS STACK — AUDIT REPORT            ║\n");
        out.push_str(  "  ╚═══════════════════════════════════════════════════════╝\n");
        out.push_str(&self.stack.summary());
        out.push_str(&format!(
            "\n  Chess→Rubik equivalence:\n    204 hidden squares/board × 10 boards = {} total\n    {} ÷ 54 stickers/cube = {:.4} Rubik cubes\n",
            self.stack.total_hidden_squares(),
            self.stack.total_hidden_squares(),
            self.stack.rubik_equivalent()
        ));
        out
    }

    pub fn loop_section(&self, piece: PieceKind, start: u16, max_ticks: u64) -> String {
        let mut lc = LoopCloser::new(piece, start).with_max_ticks(max_ticks);
        lc.run();
        let mut out = format!(
            "\n  Loop Trace ({} from cell {}):\n",
            piece.name(), start
        );
        out.push_str(&lc.report());
        out
    }

    pub fn registry_section(&self) -> String {
        let mut out = String::new();
        out.push_str("\n  ── Brick Registry Entry ──────────────────────────────\n");
        out.push_str(&format!("  {}\n", self.brick.summary_line()));
        out.push_str("\n  JSON:\n");
        for line in self.brick.to_json().lines() {
            out.push_str(&format!("    {}\n", line));
        }
        out.push_str("  ────────────────────────────────────────────────────\n");
        out
    }

    pub fn full_report(&self, max_ticks: u64) -> String {
        let mut out = String::new();
        out.push_str(&self.geometry_section());
        out.push_str(&self.loop_section(PieceKind::King,   0,   max_ticks));
        out.push_str(&self.loop_section(PieceKind::Knight, 0,   max_ticks));
        out.push_str(&self.loop_section(PieceKind::Queen,  320, max_ticks));
        out.push_str(&self.registry_section());
        out
    }
}

impl Default for StackReport {
    fn default() -> Self { Self::new() }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn geometry_section_contains_640() {
        let r = StackReport::new();
        assert!(r.geometry_section().contains("640"));
    }

    #[test]
    fn geometry_section_contains_2040() {
        let r = StackReport::new();
        assert!(r.geometry_section().contains("2040"));
    }

    #[test]
    fn loop_section_not_empty() {
        let r = StackReport::new();
        let s = r.loop_section(PieceKind::King, 0, 200);
        assert!(!s.is_empty());
    }

    #[test]
    fn registry_section_contains_seal() {
        let r = StackReport::new();
        let s = r.registry_section();
        assert!(s.contains("seal"));
    }
}
