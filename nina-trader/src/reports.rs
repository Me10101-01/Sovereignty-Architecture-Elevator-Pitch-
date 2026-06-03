/// NINA Report Generator — produces client-safe portfolio artifacts
use crate::backtest::BacktestResult;
use crate::sagco::SagcoLogger;
use std::fs;
use std::io::Write;
use std::path::PathBuf;

pub struct ReportSet {
    pub reports_dir: PathBuf,
}

impl ReportSet {
    pub fn new() -> Self {
        let home = std::env::var("HOME").unwrap_or_else(|_| "/tmp".into());
        let dir = PathBuf::from(home).join("sagco_nina").join("reports");
        fs::create_dir_all(&dir).ok();
        Self { reports_dir: dir }
    }

    pub fn write_all(&self, results: &[BacktestResult], logger: &SagcoLogger) {
        let stamp = SagcoLogger::stamp();
        self.write_backtest_md(results, &stamp);
        self.write_risk_md(results, &stamp);
        self.write_ledger_csv(results, &stamp);
        self.write_strategy_score_yaml(results, &stamp);

        // Log to SAGCO ledger
        logger.ledger(
            "nina-trader-dryrun",
            &format!("reports/dryrun_{}", stamp),
            "SAGCO_NINA_DRYRUN_PASS",
        );
    }

    fn write_backtest_md(&self, results: &[BacktestResult], stamp: &str) {
        let path = self.reports_dir.join("backtest.md");
        let mut out = String::new();

        out.push_str("# NINA Trader Bot Refinery — Backtest Report\n");
        out.push_str(&format!("Generated: {}\n", stamp));
        out.push_str("Mode: DRY-RUN (deterministic price simulation — not real market data)\n");
        out.push_str("Purpose: research/demo only\n\n");
        out.push_str("---\n\n");

        for r in results {
            out.push_str(&format!("## {} / {}\n\n", r.strategy.to_uppercase(), r.symbol));
            out.push_str(&format!("| Metric | Value |\n|--------|-------|\n"));
            out.push_str(&format!("| Simulation days | {} |\n", r.days));
            out.push_str(&format!("| Initial capital | ${:.2} |\n", r.initial_cash));
            out.push_str(&format!("| Total invested | ${:.2} |\n", r.total_invested));
            out.push_str(&format!("| Final value | ${:.2} |\n", r.final_value));
            out.push_str(&format!("| Return | {:.2}% |\n", r.total_return_pct));
            out.push_str(&format!("| Max drawdown | {:.2}% |\n", r.max_drawdown_pct));
            out.push_str(&format!("| Sharpe ratio | {:.2} |\n", r.sharpe_ratio));
            out.push_str(&format!("| Win rate | {:.1}% |\n", r.win_rate_pct));
            out.push_str(&format!("| Total trades | {} |\n", r.total_trades));
            out.push_str(&format!("| Score | {} |\n", r.score));
            out.push_str(&format!("| Ready for paper | {} |\n", r.ready_for_paper));
            out.push_str(&format!("| Ready for live | {} |\n\n", r.ready_for_live));
        }

        out.push_str("---\n\n");
        out.push_str("**Disclaimer:** Simulated results use a deterministic price model (sine-wave + trend).\n");
        out.push_str("Past simulated performance does not predict real returns.\n");
        out.push_str("No live trading until paper-trading gates pass.\n");

        fs::write(&path, &out).ok();
        println!("  [REPORT] {}", path.display());
    }

    fn write_risk_md(&self, results: &[BacktestResult], stamp: &str) {
        let path = self.reports_dir.join("risk.md");
        let mut out = String::new();

        out.push_str("# NINA Trader Bot Refinery — Risk Assessment\n");
        out.push_str(&format!("Generated: {}\n", stamp));
        out.push_str("Status: RESEARCH / DEMO ONLY\n\n");
        out.push_str("---\n\n");

        out.push_str("## Live Trading Gates\n\n");
        out.push_str("All gates must pass before any real money is connected:\n\n");
        out.push_str("- [ ] 30+ days continuous paper trading logs\n");
        out.push_str("- [ ] Max drawdown < 10% across all strategies\n");
        out.push_str("- [ ] Sharpe ratio > 1.0 on 30-day paper period\n");
        out.push_str("- [ ] Win rate > 50% on momentum strategy\n");
        out.push_str("- [ ] SAGCO variance < 20% (system stability)\n");
        out.push_str("- [ ] Manual audit of 10 paper trades reviewed\n\n");
        out.push_str("**LIVE TRADING STATUS: BLOCKED** — gates not yet met\n\n");
        out.push_str("---\n\n");

        out.push_str("## Simulation Risk Summary\n\n");
        for r in results {
            let dd_status = if r.max_drawdown_pct < 10.0 { "PASS" } else { "WARN" };
            let sh_status = if r.sharpe_ratio > 1.0 { "PASS" } else { "PENDING" };
            out.push_str(&format!("### {} / {}\n", r.strategy, r.symbol));
            out.push_str(&format!("- Max drawdown: {:.2}% [{}]\n", r.max_drawdown_pct, dd_status));
            out.push_str(&format!("- Sharpe ratio: {:.2} [{}]\n", r.sharpe_ratio, sh_status));
            out.push_str(&format!("- Score: {}\n\n", r.score));
        }

        out.push_str("---\n\n");
        out.push_str("## Risk Rules Embedded in Bot\n\n");
        out.push_str("- Max 10% portfolio per position (hard limit)\n");
        out.push_str("- DCA buys limited to 50% available cash per run\n");
        out.push_str("- Momentum only buys above 20-day SMA (trend filter)\n");
        out.push_str("- SPY Mirror only acts on >0.5% daily move\n");
        out.push_str("- All strategies default to paper mode (`ALPACA_LIVE=false`)\n");

        fs::write(&path, &out).ok();
        println!("  [REPORT] {}", path.display());
    }

    fn write_ledger_csv(&self, results: &[BacktestResult], stamp: &str) {
        let path = self.reports_dir.join("ledger.csv");
        let mut out = String::new();
        out.push_str("timestamp,strategy,symbol,days,invested,final_value,return_pct,max_drawdown,sharpe,score,ready_paper,ready_live\n");

        for r in results {
            out.push_str(&format!(
                "{},{},{},{},{:.2},{:.2},{:.2},{:.2},{:.2},{},{},{}\n",
                stamp,
                r.strategy, r.symbol, r.days,
                r.total_invested, r.final_value,
                r.total_return_pct, r.max_drawdown_pct,
                r.sharpe_ratio, r.score,
                r.ready_for_paper, r.ready_for_live
            ));
        }

        fs::write(&path, &out).ok();
        println!("  [REPORT] {}", path.display());
    }

    fn write_strategy_score_yaml(&self, results: &[BacktestResult], stamp: &str) {
        let path = self.reports_dir.join("strategy_score.yaml");
        let mut out = String::new();

        out.push_str(&format!("timestamp: {}\n", stamp));
        out.push_str("mode: dry_run\n");
        out.push_str("status: RESEARCH_DEMO_ONLY\n");
        out.push_str("live_trading_enabled: false\n");
        out.push_str("case_study: SAGCO-NINA-001\n\n");
        out.push_str("strategies:\n");

        for r in results {
            let key = format!("{}_{}", r.strategy, r.symbol.to_lowercase());
            out.push_str(&format!("  {}:\n", key));
            out.push_str(&format!("    strategy: {}\n", r.strategy));
            out.push_str(&format!("    symbol: {}\n", r.symbol));
            out.push_str(&format!("    score: {}\n", r.score));
            out.push_str(&format!("    return_simulated_pct: {:.2}\n", r.total_return_pct));
            out.push_str(&format!("    max_drawdown_pct: {:.2}\n", r.max_drawdown_pct));
            out.push_str(&format!("    sharpe_ratio: {:.2}\n", r.sharpe_ratio));
            out.push_str(&format!("    win_rate_pct: {:.1}\n", r.win_rate_pct));
            out.push_str(&format!("    total_trades: {}\n", r.total_trades));
            out.push_str(&format!("    ready_for_paper: {}\n", r.ready_for_paper));
            out.push_str(&format!("    ready_for_live: {}\n", r.ready_for_live));
        }

        out.push_str("\nrisk_gates:\n");
        out.push_str("  paper_trading_days_required: 30\n");
        out.push_str("  max_drawdown_threshold_pct: 10\n");
        out.push_str("  min_sharpe_ratio: 1.0\n");
        out.push_str("  min_win_rate_pct: 50\n");
        out.push_str("  gates_passed: false\n");
        out.push_str("  gates_status: LOCKED_PENDING_PAPER_VALIDATION\n");

        fs::write(&path, &out).ok();
        println!("  [REPORT] {}", path.display());
    }
}
