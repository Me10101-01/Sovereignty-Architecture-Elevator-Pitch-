/// SPY Mirror — mirror S&P 500 daily move on a 1-day lag
/// If SPY was up >0.5% yesterday → buy basket today
/// If SPY was down >0.5% yesterday → hold or reduce

use super::{Strategy, StrategyResult, TradeSignal};
use crate::alpaca::AlpacaClient;
use crate::sagco::SagcoLogger;

pub struct SpyMirrorStrategy {
    pub mirror_symbols: Vec<String>,
    pub spy_threshold: f64,     // % SPY move to trigger signal
    pub notional_per_trade: f64,
}

impl SpyMirrorStrategy {
    pub fn default_watchlist() -> Self {
        Self {
            mirror_symbols: vec![
                "AAPL".into(),
                "MSFT".into(),
                "GOOGL".into(),
                "AMZN".into(),
            ],
            spy_threshold: 0.5,
            notional_per_trade: 15.0,
        }
    }
}

impl Strategy for SpyMirrorStrategy {
    fn name(&self) -> &str { "spy_mirror" }

    fn run(&self, client: &AlpacaClient, logger: &SagcoLogger, mode: &str) -> Result<StrategyResult, String> {
        // Get SPY yesterday's move
        let spy_bars = client.get_bars("SPY", "1Day", 3)?;
        if spy_bars.len() < 2 {
            return Err("Not enough SPY bars".into());
        }

        let yesterday = &spy_bars[spy_bars.len() - 2];
        let spy_move_pct = (yesterday.c - yesterday.o) / yesterday.o * 100.0;

        println!("  [SPY MIRROR] Yesterday SPY move: {:.2}%", spy_move_pct);

        let account = client.get_account()?;
        let cash: f64 = account.cash.parse().unwrap_or(0.0);

        let mut signals = Vec::new();
        let mut executed = 0;
        let mut skipped = 0;

        if spy_move_pct >= self.spy_threshold {
            // SPY was bullish — mirror buy
            println!("  [SPY MIRROR] BULLISH signal — buying basket");

            for symbol in &self.mirror_symbols {
                let price = match client.get_latest_price(symbol) {
                    Ok(p) => p,
                    Err(e) => { println!("  [SPY MIRROR] Skip {} — {}", symbol, e); skipped += 1; continue; }
                };

                let buy_amount = self.notional_per_trade.min(cash * 0.2);
                if buy_amount < 1.0 { skipped += 1; continue; }

                signals.push(TradeSignal {
                    symbol: symbol.clone(),
                    side: "buy".into(),
                    amount: buy_amount,
                    reason: format!("SPY+{:.2}% mirror buy ${:.2}", spy_move_pct, buy_amount),
                });

                if mode == "live" || mode == "paper" {
                    match client.submit_order_notional(symbol, buy_amount, "buy") {
                        Ok(order) => {
                            println!("  [SPY MIRROR] BUY {} ${:.2} — {}", symbol, buy_amount, order.id);
                            logger.log_trade(symbol, "buy", buy_amount / price, price, "spy_mirror", mode);
                            logger.race(&format!("nina_spy_mirror_buy_{}", symbol));
                            executed += 1;
                        }
                        Err(e) => { println!("  [SPY MIRROR] Order failed — {}", e); skipped += 1; }
                    }
                } else {
                    println!("  [SPY MIRROR] DRY-RUN BUY {} ${:.2} @ ${:.2}", symbol, buy_amount, price);
                    logger.log_trade(symbol, "buy_dry", buy_amount / price, price, "spy_mirror", "dry");
                    executed += 1;
                }
            }
        } else if spy_move_pct <= -self.spy_threshold {
            println!("  [SPY MIRROR] BEARISH signal — holding (no sells in passive mode)");
        } else {
            println!("  [SPY MIRROR] NEUTRAL — SPY move {:.2}% within threshold", spy_move_pct);
        }

        logger.ledger("nina-trader-spy-mirror",
            &format!("spy_mirror_run_{}", SagcoLogger::stamp()),
            "SAGCO_NINA_SPY_PASS");

        Ok(StrategyResult {
            strategy: "spy_mirror".into(),
            signals,
            executed,
            skipped,
            reason: format!("SPY mirror: yesterday {:.2}%", spy_move_pct),
        })
    }
}
