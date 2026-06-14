use clap::{Parser, Subcommand};
use sagco_chess::{StackReport, LoopCloser, LoopStatus, PieceKind, Stack, StackBrick};

#[derive(Parser)]
#[command(name = "sagco-chess", version = "0.1.0",
          about = "SAGCO Chess Stack — 640-node callable execution grid")]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Print stack geometry: 10 boards, 640 cells, 2040 hidden squares, Rubik equiv
    Status,
    /// Trace a piece through the grid and show loop closure
    Trace {
        #[arg(short, long, default_value = "king",
              help = "Piece kind: king | knight | rook | bishop | queen")]
        piece: String,
        #[arg(short, long, default_value_t = 0,
              help = "Start cell ID (0-639)")]
        start: u16,
        #[arg(short, long, default_value_t = 10_000,
              help = "Max ticks before exhaustion")]
        max_ticks: u64,
    },
    /// Run loop-close proofs for king, knight, and queen and report QED status
    Loops {
        #[arg(short, long, default_value_t = 10_000)]
        max_ticks: u64,
    },
    /// Full audit: geometry + loops + brick registry entry
    Audit {
        #[arg(short, long, default_value_t = 5_000)]
        max_ticks: u64,
    },
    /// Print the brick registry JSON for sagco-chess-stack
    Registry,
    /// Display one board layer
    Board {
        #[arg(help = "Layer index 0-9")]
        layer: u8,
    },
}

fn parse_piece(s: &str) -> PieceKind {
    match s.to_lowercase().as_str() {
        "knight" => PieceKind::Knight,
        "rook"   => PieceKind::Rook,
        "bishop" => PieceKind::Bishop,
        "queen"  => PieceKind::Queen,
        _        => PieceKind::King,
    }
}

fn main() {
    let cli = Cli::parse();

    match cli.cmd {
        Cmd::Status => {
            let stack = Stack::new();
            print!("{}", stack.summary());
        }

        Cmd::Trace { piece, start, max_ticks } => {
            let pk = parse_piece(&piece);
            println!("\n  Tracing {} from cell {} (max {} ticks)...", piece, start, max_ticks);
            let mut lc = LoopCloser::new(pk, start).with_max_ticks(max_ticks);
            lc.run();
            print!("{}", lc.report());
            match &lc.status {
                LoopStatus::Closed { .. } => println!("  QED ✓  Loop closed."),
                LoopStatus::Exhausted { ticks_used } =>
                    println!("  Loop exhausted after {} ticks.", ticks_used),
                LoopStatus::Open => println!("  Loop still open."),
            }
        }

        Cmd::Loops { max_ticks } => {
            let pieces = [
                (PieceKind::King,   0u16,  "King   from L0-A1"),
                (PieceKind::Knight, 0,     "Knight from L0-A1"),
                (PieceKind::Queen,  320,   "Queen  from L5-A1"),
                (PieceKind::Rook,   35,    "Rook   from L0-D5"),
            ];
            println!("\n  ── Loop Closure Proofs ─────────────────────────────────");
            for (pk, start, label) in pieces {
                let mut lc = LoopCloser::new(pk, start).with_max_ticks(max_ticks);
                lc.run();
                let result = match &lc.status {
                    LoopStatus::Closed { at_tick, length, .. } =>
                        format!("CLOSED at tick={} length={}", at_tick, length),
                    LoopStatus::Exhausted { ticks_used } =>
                        format!("EXHAUSTED ({} ticks)", ticks_used),
                    LoopStatus::Open => "OPEN".to_string(),
                };
                println!("  {:30} → {}", label, result);
            }
            println!("  ────────────────────────────────────────────────────────");
        }

        Cmd::Audit { max_ticks } => {
            let report = StackReport::new();
            print!("{}", report.full_report(max_ticks));
        }

        Cmd::Registry => {
            let brick = StackBrick::build();
            println!("{}", brick.to_json());
        }

        Cmd::Board { layer } => {
            if layer >= 10 {
                eprintln!("Layer must be 0-9");
                std::process::exit(1);
            }
            let stack = Stack::new();
            if let Some(l) = stack.layer(layer) {
                print!("{}", l.board.display());
                println!("  Hidden squares: {}", l.hidden_squares());
            }
        }
    }
}
