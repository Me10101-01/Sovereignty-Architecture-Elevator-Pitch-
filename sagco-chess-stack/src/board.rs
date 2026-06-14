/// One 8×8 chessboard = 64 callable cells.
///
/// Hidden squares formula (all sizes on one board):
///   Σ(n=1..8) (9-n)² = 8²+7²+6²+5²+4²+3²+2²+1² = 204
use serde::{Deserialize, Serialize};
use crate::cell::Cell;

pub const BOARD_SIZE:   usize = 8;
pub const CELLS_PER_BOARD: usize = 64;    // 8×8
pub const HIDDEN_PER_BOARD: u32  = 204;   // all square-sizes counted

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Board {
    pub layer: u8,
    pub cells: Vec<Cell>,   // always 64 in row-major order
}

impl Board {
    pub fn new(layer: u8) -> Self {
        let cells = (0u8..8)
            .flat_map(|row| (0u8..8).map(move |col| Cell::new(layer, row, col)))
            .collect();
        Self { layer, cells }
    }

    pub fn cell(&self, row: u8, col: u8) -> Option<&Cell> {
        if row >= 8 || col >= 8 { return None; }
        self.cells.get((row * 8 + col) as usize)
    }

    pub fn cell_by_id(&self, global_id: u16) -> Option<&Cell> {
        let local = global_id % 64;
        let layer_offset = (global_id / 64) as u8;
        if layer_offset != self.layer { return None; }
        self.cells.get(local as usize)
    }

    /// Sum of all square-of-all-sizes counts: Σ(n=1..8)(9-n)² = 204
    pub fn hidden_squares(&self) -> u32 {
        (1u32..=8).map(|n| (9 - n) * (9 - n)).sum()
    }

    pub fn cell_count(&self) -> usize {
        self.cells.len()  // always 64
    }

    /// Print the board with cell names
    pub fn display(&self) -> String {
        let mut out = String::new();
        out.push_str(&format!("  Board Layer {} (L{}):\n", self.layer, self.layer));
        out.push_str("     A    B    C    D    E    F    G    H\n");
        for row in (0u8..8).rev() {
            out.push_str(&format!("  {}  ", row + 1));
            for col in 0u8..8 {
                let cell = self.cell(row, col).unwrap();
                out.push_str(&format!("{:4} ", cell.id));
            }
            out.push('\n');
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn board_has_64_cells() {
        let b = Board::new(0);
        assert_eq!(b.cells.len(), 64);
    }

    #[test]
    fn hidden_squares_204() {
        assert_eq!(Board::new(0).hidden_squares(), 204);
    }

    #[test]
    fn cell_lookup() {
        let b = Board::new(2);
        let c = b.cell(3, 5).unwrap();
        assert_eq!(c.layer, 2);
        assert_eq!(c.row, 3);
        assert_eq!(c.col, 5);
    }
}
