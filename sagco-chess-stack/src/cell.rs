/// One square = one callable Rust node.
///
/// Cell addressing:
///   id  = layer * 64 + row * 8 + col       (0 – 639)
///   name = "L{layer}-{file}{rank}"  e.g. "L0-A1", "L9-H8"
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Cell {
    pub layer: u8,  // 0-9  (board depth)
    pub row:   u8,  // 0-7  (rank 1-8)
    pub col:   u8,  // 0-7  (file A-H)
    pub id:    u16, // 0-639
}

impl Cell {
    pub fn new(layer: u8, row: u8, col: u8) -> Self {
        debug_assert!(layer < 10 && row < 8 && col < 8);
        Self {
            layer,
            row,
            col,
            id: layer as u16 * 64 + row as u16 * 8 + col as u16,
        }
    }

    pub fn from_id(id: u16) -> Option<Self> {
        if id >= 640 { return None; }
        let layer = (id / 64) as u8;
        let pos   = id % 64;
        Some(Self::new(layer, (pos / 8) as u8, (pos % 8) as u8))
    }

    /// "L0-A1" style name
    pub fn name(&self) -> String {
        let file = (b'A' + self.col) as char;
        let rank = self.row + 1;
        format!("L{}-{}{}", self.layer, file, rank)
    }

    /// Deterministic call: cell transforms input → output.
    /// Each cell is a unique linear node in the execution grid.
    pub fn call(&self, input: u64) -> u64 {
        // Fibonacci-like mixing: unique per cell position
        let salt = (self.id as u64)
            .wrapping_mul(0x9e3779b97f4a7c15)  // golden ratio constant
            .wrapping_add(0x517cc1b727220a95);   // Knuth multiplicative hash
        input
            .wrapping_add(salt)
            .rotate_left((self.col as u32 % 64).max(1))
            .wrapping_mul((self.row as u64).wrapping_add(1))
    }

    /// Algebraic notation (without layer prefix)
    pub fn algebraic(&self) -> String {
        let file = (b'a' + self.col) as char;
        format!("{}{}", file, self.row + 1)
    }
}

impl std::fmt::Display for Cell {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.name())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cell_id_round_trip() {
        for layer in 0u8..10 {
            for row in 0u8..8 {
                for col in 0u8..8 {
                    let c = Cell::new(layer, row, col);
                    let rt = Cell::from_id(c.id).unwrap();
                    assert_eq!(c, rt, "round-trip failed for {}", c.name());
                }
            }
        }
    }

    #[test]
    fn id_range() {
        assert_eq!(Cell::new(0, 0, 0).id, 0);
        assert_eq!(Cell::new(9, 7, 7).id, 639);
    }

    #[test]
    fn call_is_deterministic() {
        let c = Cell::new(3, 4, 5);
        assert_eq!(c.call(42), c.call(42));
        assert_ne!(c.call(42), Cell::new(3, 4, 6).call(42));
    }
}
