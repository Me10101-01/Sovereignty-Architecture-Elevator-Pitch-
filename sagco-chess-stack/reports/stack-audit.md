# SAGCO Chess Stack — Audit Report

## Geometry

| Metric | Value |
|---|---|
| Boards | 10 |
| Cells per board | 64 (8×8) |
| Total callable cells | **640** |
| Hidden square-patterns per board | 204 |
| Total hidden square-patterns | **2040** |
| Rubik cube equivalent | **≈ 37.78** (2040 ÷ 54) |

## Layer Map

| Index | Label | Cell Range | Description |
|---|---|---|---|
| L0 | Base | 0–63 | Entry / bootstrap |
| L1 | Root | 64–127 | Kernel / root |
| L2 | Foundation | 128–191 | Core data structures |
| L3 | Structure | 192–255 | IR / transforms |
| L4 | Circuit | 256–319 | Wiring / signals |
| L5 | Logic | 320–383 | Business rules |
| L6 | Protocol | 384–447 | Adapters / serialization |
| L7 | Interface | 448–511 | API surfaces |
| L8 | Sovereign | 512–575 | Governance / sealing |
| L9 | Crown | 576–639 | Final output / closure |

## Cell Addressing

```
id  = layer × 64 + row × 8 + col       (0–639)
name = "L{layer}-{file}{rank}"          e.g. "L5-D4"
```

## Move Graph

| Piece | Intra-layer rule | Avg degree (incl. inter) |
|---|---|---|
| King | 1 step, 8 directions | ~10 |
| Knight | L-shape (±1,±2) | ~6–10 |
| Rook | Full rank/file | ~16 |
| Bishop | Full diagonal | ~11 |
| Queen | Rook + Bishop | ~30 |

Inter-layer transitions: any cell can move to the same square on layer ±1 (1 tick).

## Wafer Status

`WAFER-PASS` — all unit and integration tests green.

## Brick Registry

```
id:           sagco-chess-stack
version:      0.1.0
layer:        platform
language:     Rust
cells:        640
hidden_sq:    2040
rubik_equiv:  37.7778
```
