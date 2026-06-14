use sagco_chess::{Board, Stack};

#[test]
fn all_boards_have_64_cells() {
    for layer in 0u8..10 {
        let b = Board::new(layer);
        assert_eq!(b.cells.len(), 64, "layer {} has {} cells", layer, b.cells.len());
    }
}

#[test]
fn board_hidden_squares_formula() {
    // Σ(n=1..8)(9-n)² = 64+49+36+25+16+9+4+1 = 204
    let expected: u32 = [64,49,36,25,16,9,4,1].iter().sum();
    assert_eq!(expected, 204);
    assert_eq!(Board::new(0).hidden_squares(), 204);
}

#[test]
fn cell_address_lookup_all_boards() {
    for layer in 0u8..10 {
        let b = Board::new(layer);
        for row in 0u8..8 {
            for col in 0u8..8 {
                let c = b.cell(row, col).expect("cell not found");
                assert_eq!(c.layer, layer);
                assert_eq!(c.row,   row);
                assert_eq!(c.col,   col);
            }
        }
    }
}

#[test]
fn board_display_not_empty() {
    let b = Board::new(0);
    let d = b.display();
    assert!(d.contains("L0"));
    assert!(d.contains("A"));
}

#[test]
fn cell_by_id_each_layer() {
    for layer in 0u8..10 {
        let b = Board::new(layer);
        let base = layer as u16 * 64;
        let c = b.cell_by_id(base + 35).expect("cell not found");
        assert_eq!(c.layer, layer);
    }
}

#[test]
fn stack_ten_boards_all_correct() {
    let stack = Stack::new();
    assert_eq!(stack.layers.len(), 10);
    for (i, layer) in stack.layers.iter().enumerate() {
        assert_eq!(layer.index, i as u8);
        assert_eq!(layer.board.cells.len(), 64);
    }
}
