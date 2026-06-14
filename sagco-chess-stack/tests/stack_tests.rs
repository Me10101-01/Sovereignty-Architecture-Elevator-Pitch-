use sagco_chess::{Stack, StackBrick};

#[test]
fn stack_total_cells_640() {
    assert_eq!(Stack::new().total_cells(), 640);
}

#[test]
fn stack_total_hidden_2040() {
    assert_eq!(Stack::new().total_hidden_squares(), 2040);
}

#[test]
fn rubik_equiv_between_37_and_38() {
    let r = Stack::new().rubik_equivalent();
    assert!(r > 37.0 && r < 38.0, "rubik_equiv={}", r);
}

#[test]
fn all_cells_unique_ids() {
    let stack = Stack::new();
    let mut ids: Vec<u16> = stack.all_cells().map(|c| c.id).collect();
    ids.sort();
    ids.dedup();
    assert_eq!(ids.len(), 640);
}

#[test]
fn cell_by_id_every_valid() {
    let stack = Stack::new();
    for id in 0u16..640 {
        let c = stack.cell_by_id(id).expect("missing cell");
        assert_eq!(c.id, id);
    }
}

#[test]
fn brick_registration() {
    let b = StackBrick::build();
    assert_eq!(b.id, "sagco-chess-stack");
    assert_eq!(b.cells, 640);
    assert_eq!(b.hidden_sq, 2040);
    assert_eq!(b.seal.len(), 16);
}

#[test]
fn layer_id_ranges_non_overlapping() {
    let stack = Stack::new();
    let ranges: Vec<(u16, u16)> = stack.layers.iter().map(|l| l.cell_range()).collect();
    for i in 0..ranges.len() - 1 {
        assert_eq!(ranges[i].1 + 1, ranges[i + 1].0,
            "gap between layer {} and {}", i, i + 1);
    }
}
