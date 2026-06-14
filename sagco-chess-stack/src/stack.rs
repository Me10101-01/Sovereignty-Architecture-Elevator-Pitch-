/// 10-board stack = 640 callable nodes, 2040 hidden square-patterns.
///
/// Rubik equivalence: 2040 / 54 ≈ 37.78 cubes.
use serde::{Deserialize, Serialize};
use crate::layer::Layer;
use crate::cell::Cell;

pub const LAYER_COUNT:          usize = 10;
pub const TOTAL_CELLS:          usize = 640;   // 10 × 64
pub const TOTAL_HIDDEN_SQUARES: u32   = 2040;  // 10 × 204
pub const RUBIK_STICKERS:       f64   = 54.0;  // 6 faces × 9 stickers

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Stack {
    pub layers: Vec<Layer>,
}

impl Stack {
    pub fn new() -> Self {
        let layers = (0u8..10).map(Layer::new).collect();
        Self { layers }
    }

    pub fn total_cells(&self) -> usize {
        self.layers.iter().map(|l| l.board.cell_count()).sum()
    }

    pub fn total_hidden_squares(&self) -> u32 {
        self.layers.iter().map(|l| l.hidden_squares()).sum()
    }

    /// 2040 / 54 = 37.777...
    pub fn rubik_equivalent(&self) -> f64 {
        self.total_hidden_squares() as f64 / RUBIK_STICKERS
    }

    pub fn layer(&self, index: u8) -> Option<&Layer> {
        self.layers.get(index as usize)
    }

    pub fn cell_by_id(&self, global_id: u16) -> Option<&Cell> {
        if global_id >= 640 { return None; }
        let layer_idx = (global_id / 64) as usize;
        let row = ((global_id % 64) / 8) as u8;
        let col = (global_id % 8) as u8;
        self.layers.get(layer_idx)?.board.cell(row, col)
    }

    pub fn all_cells(&self) -> impl Iterator<Item = &Cell> {
        self.layers.iter().flat_map(|l| l.board.cells.iter())
    }

    pub fn summary(&self) -> String {
        let mut out = String::new();
        out.push_str("  ══════════════════════════════════════════════════\n");
        out.push_str("  SAGCO CHESS STACK — Callable Execution Grid\n");
        out.push_str("  ══════════════════════════════════════════════════\n");
        out.push_str(&format!("  Layers:          {}\n", LAYER_COUNT));
        out.push_str(&format!("  Total cells:     {} (10 × 64)\n", self.total_cells()));
        out.push_str(&format!("  Hidden squares:  {} (10 × 204)\n", self.total_hidden_squares()));
        out.push_str(&format!("  Rubik equiv:     {:.4} cubes (÷54)\n", self.rubik_equivalent()));
        out.push_str("  ──────────────────────────────────────────────────\n");
        for layer in &self.layers {
            out.push_str(&format!("    {}\n", layer));
        }
        out.push_str("  ══════════════════════════════════════════════════\n");
        out
    }
}

impl Default for Stack {
    fn default() -> Self { Self::new() }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stack_640_cells() {
        assert_eq!(Stack::new().total_cells(), 640);
    }

    #[test]
    fn stack_2040_hidden() {
        assert_eq!(Stack::new().total_hidden_squares(), 2040);
    }

    #[test]
    fn rubik_equiv_approx_37_78() {
        let r = Stack::new().rubik_equivalent();
        assert!((r - 37.777).abs() < 0.01, "got {}", r);
    }

    #[test]
    fn cell_by_id_corners() {
        let s = Stack::new();
        let c0 = s.cell_by_id(0).unwrap();
        assert_eq!((c0.layer, c0.row, c0.col), (0, 0, 0));
        let c639 = s.cell_by_id(639).unwrap();
        assert_eq!((c639.layer, c639.row, c639.col), (9, 7, 7));
    }

    #[test]
    fn cell_by_id_none_out_of_range() {
        assert!(Stack::new().cell_by_id(640).is_none());
    }

    #[test]
    fn all_cells_count() {
        assert_eq!(Stack::new().all_cells().count(), 640);
    }
}
