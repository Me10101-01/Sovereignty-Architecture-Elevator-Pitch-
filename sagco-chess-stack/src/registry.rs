/// Brick-registry link: expose stack metadata as a sagco-brick entry.
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StackBrick {
    pub id:          String,
    pub name:        String,
    pub version:     String,
    pub layer:       String,
    pub cells:       usize,
    pub hidden_sq:   u32,
    pub rubik_equiv: f64,
    pub seal:        String,
}

impl StackBrick {
    pub fn build() -> Self {
        let cells      = 640usize;
        let hidden_sq  = 2040u32;
        let rubik_equiv = hidden_sq as f64 / 54.0;
        let seal = {
            let mut h = Sha256::new();
            h.update(b"sagco-chess-stack@0.1.0");
            h.update(cells.to_le_bytes());
            h.update(hidden_sq.to_le_bytes());
            hex::encode(&h.finalize()[..8])
        };
        Self {
            id:          "sagco-chess-stack".to_string(),
            name:        "SAGCO Chess Stack".to_string(),
            version:     "0.1.0".to_string(),
            layer:       "platform".to_string(),
            cells,
            hidden_sq,
            rubik_equiv,
            seal,
        }
    }

    pub fn to_json(&self) -> String {
        serde_json::to_string_pretty(self).unwrap_or_default()
    }

    pub fn summary_line(&self) -> String {
        format!(
            "[{}] {} v{} | cells={} hidden={} rubik≈{:.4} | seal={}",
            self.layer.to_uppercase(),
            self.id,
            self.version,
            self.cells,
            self.hidden_sq,
            self.rubik_equiv,
            self.seal,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn brick_cells_640() {
        assert_eq!(StackBrick::build().cells, 640);
    }

    #[test]
    fn brick_hidden_2040() {
        assert_eq!(StackBrick::build().hidden_sq, 2040);
    }

    #[test]
    fn brick_rubik_approx_37_78() {
        let r = StackBrick::build().rubik_equiv;
        assert!((r - 37.777).abs() < 0.01);
    }

    #[test]
    fn brick_seal_16_hex_chars() {
        assert_eq!(StackBrick::build().seal.len(), 16);
    }

    #[test]
    fn brick_json_roundtrip() {
        let b = StackBrick::build();
        let j = b.to_json();
        let b2: StackBrick = serde_json::from_str(&j).unwrap();
        assert_eq!(b2.id, b.id);
        assert_eq!(b2.cells, b.cells);
    }
}
