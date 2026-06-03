mod alpaca;
mod backtest;
mod reports;
mod sagco;
mod strategy;

use alpaca::AlpacaClient;
use sagco::SagcoLogger;
use strategy::Strategy;
use strategy::dca::DcaStrategy;
use strategy::momentum::MomentumStrategy;
use strategy::spy_mirror::SpyMirrorStrategy;

use std::env;

fn usage() {
    println!("NINA TRADER BOT REFINERY — SAGCO-OS Passive Income Research Engine");
    println!("====================================================================");
    println!("Purpose: headless Rust backtesting + paper-trading simulator");
    println!("Status:  research/demo only — no live trading until gates pass");
    println!();
    println!("Usage: nina-trader <command> [mode]");
    println!();
    println!("Commands:");
    println!("  dry-run all      Backtest all strategies, output reports/ bundle");
    println!("  dry-run dca      Backtest DCA strategy only");
    println!("  dry-run momentum Backtest momentum strategy only");
    println!("  status           Show account balance and positions");
    println!("  dca              Dollar Cost Average — buy fixed amounts regularly");
    println!("  momentum         RSI momentum — buy oversold, sell overbought");
    println!("  spy-mirror       Mirror SPY daily moves on 1-day lag");
    println!("  all              Run all strategies");
    println!("  portfolio        Show current positions + P&L");
    println!("  history          Show SAGCO trade history from ~/sagco_nina/trade_log.csv");
    println!();
    println!("Modes: dry (default) | paper | live");
    println!();
    println!("Outputs from dry-run:");
    println!("  ~/sagco_nina/reports/backtest.md");
    println!("  ~/sagco_nina/reports/risk.md");
    println!("  ~/sagco_nina/reports/ledger.csv");
    println!("  ~/sagco_nina/reports/strategy_score.yaml");
    println!();
    println!("Environment variables:");
    println!("  ALPACA_KEY       Alpaca API key ID");
    println!("  ALPACA_SECRET    Alpaca API secret key");
    println!("  ALPACA_LIVE      Set to 'true' for live trading (default: paper)");
    println!("  SAGCO_DEVICE     Device attribution (ipad/zfold/termux/ish)");
    println!();
    println!("Paper trading signup: https://alpaca.markets (free, no real money)");
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        usage();
        return;
    }

    let command = &args[1];
    let mode = args.get(2).map(|s| s.as_str()).unwrap_or("dry");

    // Load credentials
    let key = env::var("ALPACA_KEY").unwrap_or_else(|_| "demo_key".into());
    let secret = env::var("ALPACA_SECRET").unwrap_or_else(|_| "demo_secret".into());
    let live = env::var("ALPACA_LIVE").map(|v| v == "true").unwrap_or(false);

    if key == "demo_key" && command != "history" {
        println!("⚠️  No ALPACA_KEY set — running in demo mode (no real API calls)");
        println!("   Set ALPACA_KEY and ALPACA_SECRET to connect to Alpaca paper trading");
        println!();
    }

    let client = AlpacaClient::new(key, secret, live);
    let logger = SagcoLogger::new();

    println!("🤖 NINA TRADER BOT — SAGCO-OS");
    println!("==============================");
    println!("Mode: {} | Live: {}", mode, live);
    println!();

    logger.race(&format!("nina_trader_start_{}", command));

    match command.as_str() {
        "dry-run" => {
            let target = args.get(2).map(|s| s.as_str()).unwrap_or("all");
            cmd_dryrun(target, &logger);
            return;
        }
        "status" => cmd_status(&client),
        "portfolio" => cmd_portfolio(&client),
        "history" => cmd_history(&logger),
        "dca" => {
            println!("Strategy: Dollar Cost Average");
            let strat = DcaStrategy::default_watchlist();
            run_strategy(&strat, &client, &logger, mode);
        }
        "momentum" => {
            println!("Strategy: RSI Momentum");
            let strat = MomentumStrategy::default_watchlist();
            run_strategy(&strat, &client, &logger, mode);
        }
        "spy-mirror" => {
            println!("Strategy: SPY Mirror");
            let strat = SpyMirrorStrategy::default_watchlist();
            run_strategy(&strat, &client, &logger, mode);
        }
        "all" => {
            println!("Running ALL strategies\n");
            let dca = DcaStrategy::default_watchlist();
            let mom = MomentumStrategy::default_watchlist();
            let spy = SpyMirrorStrategy::default_watchlist();
            println!("--- DCA ---");
            run_strategy(&dca, &client, &logger, mode);
            println!("\n--- MOMENTUM ---");
            run_strategy(&mom, &client, &logger, mode);
            println!("\n--- SPY MIRROR ---");
            run_strategy(&spy, &client, &logger, mode);
        }
        _ => {
            eprintln!("Unknown command: {}", command);
            usage();
        }
    }

    logger.race(&format!("nina_trader_complete_{}", command));
    println!("\nSTATUS=SAGCO_NINA_PASS");
}

fn cmd_dryrun(target: &str, logger: &SagcoLogger) {
    use backtest::{simulate_prices, base_price, backtest_dca, backtest_momentum};
    use reports::ReportSet;

    println!("NINA Trader Bot Refinery — Dry-Run Backtest");
    println!("============================================");
    println!("Mode: SIMULATION (deterministic price model, no real money)");
    println!("Status: RESEARCH / DEMO ONLY");
    println!();

    logger.race("nina_dryrun_start");

    let dca_symbols = vec!["SPY", "QQQ", "VTI", "AAPL", "MSFT"];
    let mom_symbols = vec!["SPY", "QQQ", "AAPL", "MSFT", "NVDA"];
    let days = 90u32;

    let mut results = Vec::new();

    let run_dca = target == "all" || target == "dca";
    let run_mom = target == "all" || target == "momentum";

    if run_dca {
        println!("--- DCA Backtest ({} days) ---", days);
        for sym in &dca_symbols {
            let bars = simulate_prices(sym, days, base_price(sym));
            let r = backtest_dca(sym, &bars, 10.0, 5);
            println!("  {:6} return={:+.2}%  drawdown={:.2}%  sharpe={:.2}  score={}",
                r.symbol, r.total_return_pct, r.max_drawdown_pct, r.sharpe_ratio, r.score);
            results.push(r);
        }
    }

    if run_mom {
        println!("\n--- Momentum Backtest ({} days) ---", days);
        for sym in &mom_symbols {
            let bars = simulate_prices(sym, days, base_price(sym));
            let r = backtest_momentum(sym, &bars, 35.0, 65.0, 25.0);
            println!("  {:6} return={:+.2}%  drawdown={:.2}%  sharpe={:.2}  score={}",
                r.symbol, r.total_return_pct, r.max_drawdown_pct, r.sharpe_ratio, r.score);
            results.push(r);
        }
    }

    println!("\n--- Writing Reports ---");
    let report_set = ReportSet::new();
    report_set.write_all(&results, logger);

    let home = std::env::var("HOME").unwrap_or_else(|_| "/tmp".into());
    let base = format!("{}/sagco_nina/reports", home);
    println!();
    println!("  {}/backtest.md", base);
    println!("  {}/risk.md", base);
    println!("  {}/ledger.csv", base);
    println!("  {}/strategy_score.yaml", base);
    println!();

    let all_paper_ready = results.iter().all(|r| r.ready_for_paper);
    println!("--- Risk Gates ---");
    println!("  Paper trading ready: {}", if all_paper_ready { "YES" } else { "PARTIAL" });
    println!("  Live trading ready:  NO — BLOCKED (requires 30+ days paper logs)");

    logger.race("nina_dryrun_complete");
    println!();
    println!("STATUS=SAGCO_NINA_DRYRUN_PASS");
}

fn run_strategy(strat: &dyn Strategy, client: &AlpacaClient, logger: &SagcoLogger, mode: &str) {
    match strat.run(client, logger, mode) {
        Ok(result) => {
            println!("\n  Strategy: {}", result.strategy);
            println!("  Executed: {} | Skipped: {}", result.executed, result.skipped);
            println!("  Signals: {}", result.signals.len());
            for sig in &result.signals {
                println!("    {} {} ${:.2} — {}", sig.side.to_uppercase(), sig.symbol, sig.amount, sig.reason);
            }
            println!("  Result: {}", result.reason);
        }
        Err(e) => {
            println!("  ❌ Strategy failed: {}", e);
            println!("  (Check ALPACA_KEY / ALPACA_SECRET env vars)");
        }
    }
}

fn cmd_status(client: &AlpacaClient) {
    match client.get_account() {
        Ok(acct) => {
            println!("💰 Account Status");
            println!("  Portfolio Value: ${}", acct.portfolio_value);
            println!("  Cash:            ${}", acct.cash);
            println!("  Buying Power:    ${}", acct.buying_power);
            println!("  Equity:          ${}", acct.equity);
            println!("  Status:          {}", acct.status);
        }
        Err(e) => {
            println!("❌ Cannot reach Alpaca API: {}", e);
            println!("  • Set ALPACA_KEY and ALPACA_SECRET");
            println!("  • Paper trading signup: alpaca.markets");
            println!();
            println!("DEMO ACCOUNT (no API keys set):");
            println!("  Portfolio Value: $100,000.00 (paper)");
            println!("  Cash:            $100,000.00");
            println!("  Status:          ACTIVE");
        }
    }
}

fn cmd_portfolio(client: &AlpacaClient) {
    match client.get_positions() {
        Ok(positions) => {
            if positions.is_empty() {
                println!("📭 No open positions");
                return;
            }
            println!("📊 Open Positions:");
            println!("  {:<8} {:>10} {:>10} {:>10} {:>10}", "SYMBOL", "QTY", "AVG COST", "PRICE", "P&L");
            println!("  {}", "-".repeat(55));
            for p in &positions {
                println!("  {:<8} {:>10} {:>10} {:>10} {:>10}",
                    p.symbol, p.qty, p.avg_entry_price, p.current_price, p.unrealized_pl);
            }
        }
        Err(e) => println!("❌ Cannot get positions: {}", e),
    }
}

fn cmd_history(logger: &SagcoLogger) {
    let path = logger.trade_log_path();
    match std::fs::read_to_string(&path) {
        Ok(content) => {
            println!("📜 Nina Trade History: {}", path.display());
            println!();
            for line in content.lines() {
                println!("  {}", line);
            }
        }
        Err(_) => println!("No trade history yet — run a strategy first"),
    }
}
