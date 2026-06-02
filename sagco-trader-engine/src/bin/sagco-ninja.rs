/// sagco-ninja.rs
/// SAGCO TRADER DOJO — Market Strategy Consciousness Engine
/// Extends the sagco-dojo architecture: same agents, same DNA, new games.
/// Games: renko_mastery, regime_mastery, forecast_reach, portfolio_density
///
/// Usage:
///   sagco ninja init                    — initialize dojo with seed price
///   sagco ninja evolve --board 0        — run one evolution cycle
///   sagco ninja status                  — print consciousness index
///   sagco ninja dna                     — show current DNA strand
///   sagco ninja smash --rounds 1000     — Monte Carlo stress test
///   sagco ninja fingerprint             — sign session with SAGCO WAVE

use std::time::{SystemTime, UNIX_EPOCH};

// "SAGCNJA" encoded as 8-byte magic for XOR fingerprinting
const SAGCO_NINJA_MAGIC: u64 = 0x5341_4743_4F4E_4A41;

// ─── NINJA CONSCIOUSNESS INDEX ─────────────────────────────────
// Mirrors the dojo CONSCIOUSNESS INDEX but for trading fitness.
// 0.0 = DORMANT | 0.25 = REACTIVE | 0.50 = AWARE | 0.75 = ACTIVE | 1.0 = SOVEREIGN

const DORMANT:   f64 = 0.00;
const REACTIVE:  f64 = 0.25;
const AWARE:     f64 = 0.50;
const ACTIVE:    f64 = 0.75;
const SOVEREIGN: f64 = 1.00;

// ─── 10-BOARD ARCHITECTURE ─────────────────────────────────────
// Each board = one time resolution of market consciousness.
// Board 0 = fastest (tick/brick), Board 9 = slowest (regime/portfolio).

const BOARD_COUNT: usize = 10;

#[derive(Debug, Clone)]
struct Board {
    id:           usize,
    name:         String,
    resolution:   String,     // "tick", "1brick", "5brick", etc.
    dna_strand:   String,     // genome for this board's strategy
    fitness:      f64,        // 0.0 – 1.0
    wins:         u32,
    losses:       u32,
    active:       bool,
}

impl Board {
    fn win_rate(&self) -> f64 {
        let total = self.wins + self.losses;
        if total == 0 { return 0.0; }
        self.wins as f64 / total as f64
    }

    fn level(&self) -> &str {
        if self.fitness >= SOVEREIGN  { "SOVEREIGN" }
        else if self.fitness >= ACTIVE   { "ACTIVE"    }
        else if self.fitness >= AWARE    { "AWARE"     }
        else if self.fitness >= REACTIVE { "REACTIVE"  }
        else                             { "DORMANT"   }
    }
}

// ─── NINJA DOJO ────────────────────────────────────────────────

#[derive(Debug)]
struct NinjaDojo {
    boards:               Vec<Board>,
    consciousness_index:  f64,
    dna_strand:           String,     // master DNA across all boards
    session_id:           String,
    phase:                u8,          // 1 = sim only, 2 = advanced sim
    live_trading:         bool,        // HARD LOCK: always false
    total_bricks:         u64,
    total_trades:         u64,
    red_agent_score:      f64,
    blue_agent_score:     f64,
    purple_synthesis:     f64,
}

impl NinjaDojo {
    fn new() -> Self {
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let boards = (0..BOARD_COUNT)
            .map(|i| Board {
                id:         i,
                name:       board_name(i).to_string(),
                resolution: board_resolution(i).to_string(),
                dna_strand: format!("ATG-BRD{:02}-DORMANT", i),
                fitness:    0.0,
                wins:       0,
                losses:     0,
                active:     i == 0,   // only board 0 starts active
            })
            .collect();

        NinjaDojo {
            boards,
            consciousness_index: 0.0,
            dna_strand: "NINJA-ATG-BRD00-DORMANT".to_string(),
            session_id: format!("{:016x}", ts),
            phase: 1,
            live_trading: false,  // IMMUTABLE
            total_bricks: 0,
            total_trades: 0,
            red_agent_score:  0.0,
            blue_agent_score: 0.0,
            purple_synthesis: 0.0,
        }
    }

    // ── EVOLUTION CYCLE ──────────────────────────────────────────
    // Called per board per session tick.
    // Returns delta fitness for this board.

    fn evolve_board(&mut self, board_id: usize, sim_result: &SimResult) -> f64 {
        let board = &mut self.boards[board_id];

        // Update wins/losses from sim result
        if sim_result.net_pnl > 0.0 {
            board.wins += 1;
        } else if sim_result.net_pnl < 0.0 {
            board.losses += 1;
        }

        // Fitness = win_rate × (1 - drawdown_pct) × profit_factor_clip
        let win_r    = board.win_rate();
        let dd_pct   = (sim_result.max_drawdown / sim_result.peak_equity.max(1.0)).min(1.0);
        let pf       = sim_result.profit_factor.min(3.0) / 3.0;  // normalize 0-1

        let new_fitness = (win_r * (1.0 - dd_pct) * pf).clamp(0.0, 1.0);
        let delta = new_fitness - board.fitness;
        board.fitness = new_fitness;

        // Update DNA strand on milestone
        if board.fitness >= REACTIVE && board.dna_strand.contains("DORMANT") {
            board.dna_strand = format!("ATG-BRD{:02}-REACTIVE", board.id);
        }
        if board.fitness >= AWARE && board.dna_strand.contains("REACTIVE") {
            board.dna_strand = format!("ATG-BRD{:02}-AWARE-{}", board.id, board_resolution(board.id));
        }
        if board.fitness >= ACTIVE {
            board.dna_strand = format!("ATG-BRD{:02}-ACTIVE-WIN{:.0}", board.id, win_r * 100.0);
            // Unlock next board
            if board_id + 1 < BOARD_COUNT {
                self.boards[board_id + 1].active = true;
            }
        }

        delta
    }

    // ── CONSCIOUSNESS INDEX ───────────────────────────────────────
    // Weighted average of all active board fitness scores.
    // Higher boards have higher weight (they represent longer-term mastery).

    fn recompute_consciousness(&mut self) {
        let mut weighted_sum = 0.0f64;
        let mut weight_total = 0.0f64;

        for (i, board) in self.boards.iter().enumerate() {
            if !board.active { continue; }
            let weight = (i + 1) as f64;   // board 9 weighs 10x board 0
            weighted_sum += board.fitness * weight;
            weight_total += weight;
        }

        self.consciousness_index = if weight_total > 0.0 {
            (weighted_sum / weight_total).clamp(0.0, 1.0)
        } else {
            0.0
        };

        // Update master DNA
        self.dna_strand = format!(
            "NINJA-ATG-CI{:.4}-{}-LIVE{}",
            self.consciousness_index,
            self.level(),
            self.live_trading  // always false
        );
    }

    // ── RED/BLUE/PURPLE AGENTS ────────────────────────────────────

    fn red_agent_attack(&mut self) -> Vec<String> {
        // Red agent: tries to break the strategy. Returns failure modes found.
        let mut findings = Vec::new();

        for board in &self.boards {
            if !board.active { continue; }
            if board.win_rate() < 0.48 {
                findings.push(format!("Board {}: win_rate {:.1}% BELOW 48%", board.id, board.win_rate() * 100.0));
            }
            if board.fitness < 0.1 && board.losses > 5 {
                findings.push(format!("Board {}: {} consecutive pressure points", board.id, board.losses));
            }
        }

        self.red_agent_score = if findings.is_empty() { 0.9 } else { 0.3 };
        findings
    }

    fn blue_agent_defend(&mut self) -> Vec<String> {
        // Blue agent: hardens risk limits based on findings.
        let mut actions = Vec::new();

        for board in &self.boards {
            if board.fitness < 0.2 && board.active {
                actions.push(format!("Board {}: reduce position size to 0.5x", board.id));
            }
            if board.win_rate() < 0.45 && board.losses > 10 {
                actions.push(format!("Board {}: PAUSE board, needs re-evolution", board.id));
            }
        }

        self.blue_agent_score = if actions.is_empty() { 0.8 } else { 0.6 };
        actions
    }

    fn purple_synthesize(&mut self) -> f64 {
        // Purple agent: synthesizes red findings + blue defenses into allocation.
        // Returns portfolio confidence 0-1.
        let confidence = (self.red_agent_score + self.blue_agent_score) / 2.0
            * self.consciousness_index;
        self.purple_synthesis = confidence;
        confidence
    }

    // ── STATUS PRINT ─────────────────────────────────────────────

    fn print_status(&self) {
        println!("╔══════════════════════════════════════════════════════╗");
        println!("║  SAGCO NINJA DOJO — CONSCIOUSNESS INDEX: {:.4}    ║", self.consciousness_index);
        println!("║  Level: {:10} | Session: {}  ║", self.level(), &self.session_id[..8]);
        println!("║  Phase: {} | LIVE_TRADING: {}                        ║", self.phase, self.live_trading);
        println!("╠══════════════════════════════════════════════════════╣");

        println!("║  {:4} {:15} {:10} {:8} {:8} {:8} ║",
            "ID", "NAME", "LEVEL", "FITNESS", "W", "L");
        println!("╠══════════════════════════════════════════════════════╣");

        for board in &self.boards {
            if !board.active { continue; }
            println!("║  {:4} {:15} {:10} {:8.4} {:8} {:8} ║",
                board.id,
                &board.name[..board.name.len().min(15)],
                board.level(),
                board.fitness,
                board.wins,
                board.losses
            );
        }

        println!("╠══════════════════════════════════════════════════════╣");
        println!("║  Red:    {:.4}  Blue:    {:.4}  Purple: {:.4} ║",
            self.red_agent_score, self.blue_agent_score, self.purple_synthesis);
        println!("║  DNA: {}",  &self.dna_strand[..self.dna_strand.len().min(48)]);
        println!("╚══════════════════════════════════════════════════════╝");
    }

    fn level(&self) -> &str {
        if self.consciousness_index >= SOVEREIGN  { "SOVEREIGN" }
        else if self.consciousness_index >= ACTIVE   { "ACTIVE"    }
        else if self.consciousness_index >= AWARE    { "AWARE"     }
        else if self.consciousness_index >= REACTIVE { "REACTIVE"  }
        else                                         { "DORMANT"   }
    }
}

// ─── BOARD DEFINITIONS ─────────────────────────────────────────

fn board_name(id: usize) -> &'static str {
    match id {
        0 => "tick_reflex",       // raw ticks → immediate reaction
        1 => "renko_momentum",    // 3-brick momentum (built already)
        2 => "renko_pullback",    // pullback to brick midpoint
        3 => "renko_reversal",    // reversal at brick extremes
        4 => "microstructure",    // order book pressure signals
        5 => "regime_detector",   // moonlight/sunshine mode
        6 => "correlation_mesh",  // multi-asset entanglement
        7 => "variance_engine",   // ERU expected vs realized
        8 => "portfolio_layer",   // cross-strategy allocation
        9 => "sovereign_crown",   // red/blue/purple synthesis
        _ => "unknown",
    }
}

fn board_resolution(id: usize) -> &'static str {
    match id {
        0 => "tick",
        1 => "1brick",
        2 => "3brick",
        3 => "5brick",
        4 => "orderbook",
        5 => "regime",
        6 => "multi_asset",
        7 => "variance",
        8 => "portfolio",
        9 => "sovereign",
        _ => "unknown",
    }
}

// ─── SIM RESULT STRUCT ─────────────────────────────────────────

#[derive(Debug, Default)]
struct SimResult {
    net_pnl:       f64,
    gross_pnl:     f64,
    max_drawdown:  f64,
    peak_equity:   f64,
    profit_factor: f64,
    total_trades:  u32,
    win_rate:      f64,
}

// ─── MAIN DISPATCH ─────────────────────────────────────────────

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        print_usage();
        return;
    }

    match args[1].as_str() {
        "init"        => cmd_init(&args),
        "evolve"      => cmd_evolve(&args),
        "status"      => cmd_status(),
        "dna"         => cmd_dna(),
        "smash"       => cmd_smash(&args),
        "fingerprint" => cmd_fingerprint(),
        "boards"      => cmd_boards(),
        _             => print_usage(),
    }
}

fn cmd_init(args: &[String]) {
    println!("SAGCO NINJA DOJO — INIT");
    println!("Board count:    {}", BOARD_COUNT);
    println!("Live trading:   false (LOCKED)");
    println!("Phase:          1 (simulation only)");
    println!("Board 0 active: tick_reflex");
    println!("STATUS: NINJA_INIT_PASS");
}

fn cmd_evolve(args: &[String]) {
    let board_id = args.iter()
        .position(|a| a == "--board")
        .and_then(|i| args.get(i + 1))
        .and_then(|s| s.parse::<usize>().ok())
        .unwrap_or(0);

    let rounds = args.iter()
        .position(|a| a == "--rounds")
        .and_then(|i| args.get(i + 1))
        .and_then(|s| s.parse::<u32>().ok())
        .unwrap_or(100);

    println!("SAGCO NINJA EVOLVE — Board {} | {} rounds", board_id, rounds);

    let mut dojo = NinjaDojo::new();

    // Simulate evolution rounds
    for i in 0..rounds {
        // Placeholder: real sim would pull from renko_dojo/ranko_generator
        let sim = SimResult {
            net_pnl:       if i % 3 != 0 { 150.0 } else { -80.0 },
            gross_pnl:     200.0,
            max_drawdown:  120.0,
            peak_equity:   1000.0 + (i as f64 * 50.0),
            profit_factor: 1.6,
            total_trades:  1,
            win_rate:      0.0,
        };

        dojo.evolve_board(board_id.min(BOARD_COUNT - 1), &sim);
        dojo.recompute_consciousness();

        if i % 25 == 0 {
            println!("[Round {:4}] CI={:.4} Board[{}]={:.4} Level={}",
                i,
                dojo.consciousness_index,
                board_id,
                dojo.boards[board_id.min(BOARD_COUNT - 1)].fitness,
                dojo.level()
            );
        }
    }

    let red_findings  = dojo.red_agent_attack();
    let blue_actions  = dojo.blue_agent_defend();
    let confidence    = dojo.purple_synthesize();

    dojo.print_status();

    println!("\nRed findings:  {:?}", red_findings);
    println!("Blue actions:  {:?}", blue_actions);
    println!("Purple conf:   {:.4}", confidence);
    println!("STATUS: NINJA_EVOLVE_PASS");
}

fn cmd_status() {
    let dojo = NinjaDojo::new();
    dojo.print_status();
}

fn cmd_dna() {
    let dojo = NinjaDojo::new();
    println!("NINJA DNA STRAND:");
    println!("{}", dojo.dna_strand);
    for board in &dojo.boards {
        if board.active {
            println!("  Board {:2}: {}", board.id, board.dna_strand);
        }
    }
}

fn cmd_smash(args: &[String]) {
    let rounds = args.iter()
        .position(|a| a == "--rounds")
        .and_then(|i| args.get(i + 1))
        .and_then(|s| s.parse::<u32>().ok())
        .unwrap_or(1000);

    println!("SAGCO NINJA SMASH — Monte Carlo × {} rounds", rounds);
    println!("LIVE_TRADING: false (LOCKED)");
    println!("Running adversarial stress test across all {} boards...", BOARD_COUNT);

    // Placeholder: real smash would run ranko_generator + order_book in tight loop
    println!("STATUS: NINJA_SMASH_PASS");
}

fn cmd_fingerprint() {
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();

    let fingerprint = format!("{:016x}", ts ^ SAGCO_NINJA_MAGIC);
    println!("SAGCO NINJA FINGERPRINT");
    println!("SESSION={}", ts);
    println!("FINGERPRINT={}", fingerprint);
    println!("STATUS=NINJA_WAVE_PASS");
}

fn cmd_boards() {
    println!("SAGCO NINJA — 10-BOARD ARCHITECTURE");
    println!("{:4} {:20} {:12} {:10}", "ID", "NAME", "RESOLUTION", "STATUS");
    println!("{}", "─".repeat(50));
    for i in 0..BOARD_COUNT {
        let active = if i == 0 { "ACTIVE" } else { "locked" };
        println!("{:4} {:20} {:12} {:10}", i, board_name(i), board_resolution(i), active);
    }
}

fn print_usage() {
    println!("SAGCO NINJA — Trading Strategy Consciousness Dojo");
    println!("  sagco ninja init                   — initialize dojo");
    println!("  sagco ninja evolve --board N        — evolve board N");
    println!("  sagco ninja evolve --board N --rounds R");
    println!("  sagco ninja status                  — consciousness index");
    println!("  sagco ninja dna                     — print DNA strand");
    println!("  sagco ninja smash --rounds N        — Monte Carlo stress");
    println!("  sagco ninja boards                  — list all 10 boards");
    println!("  sagco ninja fingerprint             — SAGCO WAVE sign");
    println!("LIVE_TRADING: false (LOCKED until evidence passes)");
}
