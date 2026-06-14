use sagco_chess::{build_move_map, PieceKind};
use sagco_chess::move_graph::{id_to_coords, degree};

#[test]
fn map_covers_all_640_cells() {
    for piece in [PieceKind::King, PieceKind::Knight, PieceKind::Queen] {
        let map = build_move_map(piece);
        for id in 0u16..640 {
            assert!(map.contains_key(&id), "piece {:?} missing cell {}", piece, id);
        }
    }
}

#[test]
fn no_self_loops_in_any_map() {
    for piece in [PieceKind::King, PieceKind::Knight, PieceKind::Rook,
                  PieceKind::Bishop, PieceKind::Queen] {
        let map = build_move_map(piece);
        for (from, targets) in &map {
            assert!(!targets.contains(from),
                "self-loop detected at cell {} for {:?}", from, piece);
        }
    }
}

#[test]
fn knight_l_shape_only() {
    let map = build_move_map(PieceKind::Knight);
    for (from, targets) in &map {
        for &to in targets {
            let (fl, fr, fc) = id_to_coords(*from);
            let (tl, tr, tc) = id_to_coords(to);
            if fl == tl {
                // intra-layer: must be L-shape
                let dr = (fr as i32 - tr as i32).abs();
                let dc = (fc as i32 - tc as i32).abs();
                assert!(
                    (dr == 2 && dc == 1) || (dr == 1 && dc == 2),
                    "non-L-shape knight move from {} to {}", from, to
                );
            } else {
                // inter-layer: adjacent layer, same square
                assert_eq!(fr, tr);
                assert_eq!(fc, tc);
                assert_eq!((fl as i32 - tl as i32).abs(), 1);
            }
        }
    }
}

#[test]
fn king_max_8_intra_moves_from_center() {
    let map = build_move_map(PieceKind::King);
    // L5, row=3, col=3 = id 347; center king has 8 intra + 2 inter = 10
    let d = degree(&map, 347);
    assert_eq!(d, 10, "king center degree = {}", d);
}

#[test]
fn king_corner_l0_a1_has_3_intra_1_inter() {
    let map = build_move_map(PieceKind::King);
    // id=0, L0 corner: (0,0): intra neighbors (0,1),(1,0),(1,1)=3; inter-up only=1 → total 4
    let d = degree(&map, 0);
    assert_eq!(d, 4);
}

#[test]
fn queen_center_has_27_intra_plus_2_inter() {
    // Queen from L5,row=3,col=3 (id=347):
    // Rook: 3 left + 4 right + 3 down + 4 up = 14
    // Bishop NW=3, NE=4, SW=3, SE=3 = 13
    // Total intra = 27; + 2 inter-layer = 29
    let map = build_move_map(PieceKind::Queen);
    let d = degree(&map, 347);
    assert_eq!(d, 29);
}
