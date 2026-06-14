/// One layer = one chessboard + metadata in the 10-board stack.
use serde::{Deserialize, Serialize};
use crate::board::Board;
use crate::cell::Cell;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Layer {
    pub index: u8,
    pub board: Board,
    pub label: String,  // e.g. "L0-Base", "L9-Crown"
}

impl Layer {
    pub fn new(index: u8) -> Self {
        let label = match index {
            0 => "L0-Base".to_string(),
            1 => "L1-Root".to_string(),
            2 => "L2-Foundation".to_string(),
            3 => "L3-Structure".to_string(),
            4 => "L4-Circuit".to_string(),
            5 => "L5-Logic".to_string(),
            6 => "L6-Protocol".to_string(),
            7 => "L7-Interface".to_string(),
            8 => "L8-Sovereign".to_string(),
            9 => "L9-Crown".to_string(),
            _ => format!("L{}-Unknown", index),
        };
        Self {
            index,
            board: Board::new(index),
            label,
        }
    }

    pub fn cell(&self, row: u8, col: u8) -> Option<&Cell> {
        self.board.cell(row, col)
    }

    /// Global cell id base for this layer: layer * 64
    pub fn id_base(&self) -> u16 {
        self.index as u16 * 64
    }

    pub fn cell_range(&self) -> (u16, u16) {
        let base = self.id_base();
        (base, base + 63)
    }

    pub fn hidden_squares(&self) -> u32 {
        self.board.hidden_squares()
    }
}

impl std::fmt::Display for Layer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let (lo, hi) = self.cell_range();
        write!(f, "{} cells=[{}-{}] hidden_sq={}", self.label, lo, hi, self.hidden_squares())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn layer_labels() {
        assert_eq!(Layer::new(0).label, "L0-Base");
        assert_eq!(Layer::new(9).label, "L9-Crown");
    }

    #[test]
    fn layer_id_ranges() {
        assert_eq!(Layer::new(0).cell_range(), (0, 63));
        assert_eq!(Layer::new(5).cell_range(), (320, 383));
        assert_eq!(Layer::new(9).cell_range(), (576, 639));
    }

    #[test]
    fn layer_hidden_204() {
        assert_eq!(Layer::new(3).hidden_squares(), 204);
    }
}
