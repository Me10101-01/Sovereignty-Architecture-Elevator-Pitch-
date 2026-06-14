/// Legal moves encoded as directed edges between cell IDs.
///
/// Intra-layer moves follow chess piece rules on the same board.
/// Inter-layer transitions move the cursor one layer up or down at the same square.
use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum PieceKind {
    King,
    Knight,
    Rook,
    Bishop,
    Queen,
}

impl PieceKind {
    pub fn name(&self) -> &'static str {
        match self {
            PieceKind::King   => "King",
            PieceKind::Knight => "Knight",
            PieceKind::Rook   => "Rook",
            PieceKind::Bishop => "Bishop",
            PieceKind::Queen  => "Queen",
        }
    }
}

/// One directed edge in the move graph.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MoveEdge {
    pub from: u16,
    pub to:   u16,
    pub kind: MoveKind,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MoveKind {
    Intra(PieceKind),   // same layer
    InterUp,            // same square, layer+1
    InterDown,          // same square, layer-1
}

/// Full adjacency map: cell_id → Vec<cell_id>
pub type MoveMap = HashMap<u16, Vec<u16>>;

/// Build legal move adjacency for a given piece kind across all 10 layers.
pub fn build_move_map(piece: PieceKind) -> MoveMap {
    let mut map: MoveMap = HashMap::new();

    for layer in 0u8..10 {
        for row in 0u8..8 {
            for col in 0u8..8 {
                let from_id = layer as u16 * 64 + row as u16 * 8 + col as u16;
                let targets = intra_targets(piece, layer, row, col);
                let entry = map.entry(from_id).or_default();
                for t in targets {
                    entry.push(t);
                }

                // inter-layer: always available (cursor lifts/drops)
                if layer > 0 {
                    let down_id = (layer as u16 - 1) * 64 + row as u16 * 8 + col as u16;
                    map.entry(from_id).or_default().push(down_id);
                }
                if layer < 9 {
                    let up_id = (layer as u16 + 1) * 64 + row as u16 * 8 + col as u16;
                    map.entry(from_id).or_default().push(up_id);
                }
            }
        }
    }
    map
}

fn cell_id(layer: u8, row: i32, col: i32) -> u16 {
    layer as u16 * 64 + row as u16 * 8 + col as u16
}

fn intra_targets(piece: PieceKind, layer: u8, row: u8, col: u8) -> Vec<u16> {
    let (r, c) = (row as i32, col as i32);
    let mut out = Vec::new();

    let raw_deltas: Vec<(i32, i32)> = match piece {
        PieceKind::Knight => vec![
            (-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1),
        ],
        PieceKind::King => vec![
            (-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1),
        ],
        PieceKind::Rook => {
            let mut d = Vec::new();
            for i in 1..8i32 { d.push((i,0)); d.push((-i,0)); d.push((0,i)); d.push((0,-i)); }
            d
        }
        PieceKind::Bishop => {
            let mut d = Vec::new();
            for i in 1..8i32 { d.push((i,i)); d.push((-i,-i)); d.push((i,-i)); d.push((-i,i)); }
            d
        }
        PieceKind::Queen => {
            let mut d = Vec::new();
            for i in 1..8i32 {
                d.push((i,0)); d.push((-i,0)); d.push((0,i)); d.push((0,-i));
                d.push((i,i)); d.push((-i,-i)); d.push((i,-i)); d.push((-i,i));
            }
            d
        }
    };

    for (dr, dc) in raw_deltas {
        let nr = r + dr;
        let nc = c + dc;
        if nr >= 0 && nr < 8 && nc >= 0 && nc < 8 {
            out.push(cell_id(layer, nr, nc));
        }
    }
    out
}

/// Count of edges from a single cell.
pub fn degree(map: &MoveMap, cell_id: u16) -> usize {
    map.get(&cell_id).map_or(0, |v| v.len())
}

/// Convert cell id to (layer, row, col) for display.
pub fn id_to_coords(id: u16) -> (u8, u8, u8) {
    let layer = (id / 64) as u8;
    let pos   = id % 64;
    (layer, (pos / 8) as u8, (pos % 8) as u8)
}

/// Check if a move id is a valid intra-layer knight move from source.
pub fn is_knight_move(from: u16, to: u16) -> bool {
    let (fl, fr, fc) = id_to_coords(from);
    let (tl, tr, tc) = id_to_coords(to);
    if fl != tl { return false; }
    let dr = (fr as i32 - tr as i32).abs();
    let dc = (fc as i32 - tc as i32).abs();
    (dr == 2 && dc == 1) || (dr == 1 && dc == 2)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn knight_corner_has_2_moves_plus_2_inter() {
        let map = build_move_map(PieceKind::Knight);
        // cell 0 = L0-A1 (layer=0,row=0,col=0): knight can reach (1,2)=10 and (2,1)=17
        // plus inter-up to layer 1 = cell 64
        let targets = map.get(&0).unwrap();
        // inter up = 64; knight moves = 2; no inter down (layer=0)
        assert!(targets.contains(&10));
        assert!(targets.contains(&17));
        assert!(targets.contains(&64));
        assert_eq!(targets.len(), 3);
    }

    #[test]
    fn inter_layer_mid_stack() {
        let map = build_move_map(PieceKind::King);
        // cell 320 = L5-A1 (layer=5,row=0,col=0)
        let targets = map.get(&320).unwrap();
        // inter down = 256 (L4), inter up = 384 (L6)
        assert!(targets.contains(&256));
        assert!(targets.contains(&384));
    }

    #[test]
    fn knight_move_check() {
        assert!(is_knight_move(0, 10));  // (0,0)->(1,2): dr=1,dc=2 ✓
        assert!(is_knight_move(0, 17)); // (0,0)->(2,1): dr=2,dc=1 ✓
        assert!(!is_knight_move(0, 1));
    }

    #[test]
    fn rook_center_16_intra_plus_2_inter() {
        let map = build_move_map(PieceKind::Rook);
        // cell = L5, row=3, col=3: id = 5*64+3*8+3 = 347
        let d = degree(&map, 347);
        // rook from (3,3): 7 in row + 7 in col - overlap = 14 intra + 2 inter = 16
        assert_eq!(d, 16);
    }
}
