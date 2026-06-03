/// RSI Momentum — buy oversold (RSI<30), sell overbought (RSI>70)
/// Classic mean-reversion passive income strategy

use super::{Strategy, StrategyResult, TradeSignal, rsi, sma};
use crate::alpaca::AlpacaClient;
use crate::sagco::SagcoLogger;

pub struct MomentumStrategy {
    pub symbols: Vec<String>,
    pub buy_rsi: f64,          // buy when RSI <= this (oversold)
    pub sell_rsi: f64,         // sell when RSI >= this (overbought)
    pub sma_period: usize,     // trend filter: only buy above SMA
    pub notional_per_trade: f64,
}

impl MomentumStrategy {
    pub fn default_watchlist() -> Self {
        Self {
            symbols: vec![
                "SPY".into(),
                "QQQ".into(),
                "AAPL".into(),
                "MSFT".into(),
                "NVDA".into(),
                "AMZN".into(),
            ],
            buy_rsi: 35.0,
            sell_rsi: 65.0,
            sma_period: 20,
            notional_per_trade: 25.0,
        }
    }
}

impl Strategy for MomentumStrategy {
    fn name(&self) -> &str { "momentum" }

    fn run(&self, client: &AlpacaClient, logger: &SagcoLogger, mode: &str) -> Result<StrategyResult, String> {
        let account = client.get_account()?;
        let cash: f64 = account.cash.parse().unwrap_or(0.0);
        let portfolio_val: f64 = account.portfolio_value.parse().unwrap_or(100_000.0);

        println!("  [MOMENTUM] Portfolio: ${:.2} | Cash: ${:.2}", portfolio_val, cash);

        let mut signals: Vec<TradeSignal> = Vec::new();
        let mut executed = 0;
        let mut skipped = 0;

        for symbol in &self.symbols {
            let bars = match client.get_bars(symbol, "1Day", 30) {
                Ok(b) if b.len() >= 16 => b,
                Ok(_) => { println!("  [MOMENTUM] Skip {} — not enough bars", symbol); skipped += 1; continue; }
                Err(e) => { println!("  [MOMENTUM] Skip {} — {}", symbol, e); skipped += 1; continue; }
            };

            let current_price = bars.last().map(|b| b.c).unwrap_or(0.0);
            let rsi_val = match rsi(&bars, 14) {
                Some(r) => r,
                None => { skipped += 1; continue; }
            };
            let sma_val = sma(&bars, self.sma_period);

            println!("  [MOMENTUM] {} price=${:.2} RSI={:.1} SMA={:?}",
                symbol, current_price, rsi_val,
                sma_val.map(|s| format!("{:.2}", s)));

            // Check current position
            let positions = client.get_positions().unwrap_or_default();
            let has_position = positions.iter().any(|p| p.symbol == *symbol && p.side == "long");
            let position = positions.iter().find(|p| p.symbol == *symbol);

            if !has_position && rsi_val <= self.buy_rsi {
                // Buy signal — RSI oversold
                // Trend filter: price should be above SMA or SMA not available
                let above_sma = sma_val.map(|s| current_price >= s).unwrap_or(true);
                if !above_sma {
                    println!("  [MOMENTUM] Skip {} BUY — below SMA trend filter", symbol);
                    skipped += 1;
                    continue;
                }

                let buy_amount = self.notional_per_trade.min(cash * 0.3);
                if buy_amount < 1.0 { skipped += 1; continue; }

                signals.push(TradeSignal {
                    symbol: symbol.clone(),
                    side: "buy".into(),
                    amount: buy_amount,
                    reason: format!("RSI={:.1} OVERSOLD buy ${:.2}", rsi_val, buy_amount),
                });

                if mode == "live" || mode == "paper" {
                    match client.submit_order_notional(symbol, buy_amount, "buy") {
                        Ok(order) => {
                            println!("  [MOMENTUM] BUY {} ${:.2} RSI={:.1} — {}", symbol, buy_amount, rsi_val, order.id);
                            logger.log_trade(symbol, "buy", buy_amount / current_price, current_price, "momentum", mode);
                            logger.race(&format!("nina_momentum_buy_{}", symbol));
                            executed += 1;
                        }
                        Err(e) => { println!("  [MOMENTUM] Order failed — {}", e); skipped += 1; }
                    }
                } else {
                    println!("  [MOMENTUM] DRY-RUN BUY {} RSI={:.1}", symbol, rsi_val);
                    logger.log_trade(symbol, "buy_dry", buy_amount / current_price, current_price, "momentum", "dry");
                    executed += 1;
                }

            } else if has_position && rsi_val >= self.sell_rsi {
                // Sell signal — RSI overbought
                if let Some(pos) = position {
                    let qty: f64 = pos.qty.parse().unwrap_or(0.0);
                    if qty <= 0.0 { skipped += 1; continue; }

                    signals.push(TradeSignal {
                        symbol: symbol.clone(),
                        side: "sell".into(),
                        amount: qty * current_price,
                        reason: format!("RSI={:.1} OVERBOUGHT sell {:.4} shares", rsi_val, qty),
                    });

                    if mode == "live" || mode == "paper" {
                        match client.submit_order_qty(symbol, qty, "sell") {
                            Ok(order) => {
                                println!("  [MOMENTUM] SELL {} {:.4}sh RSI={:.1} — {}", symbol, qty, rsi_val, order.id);
                                logger.log_trade(symbol, "sell", qty, current_price, "momentum", mode);
                                logger.race(&format!("nina_momentum_sell_{}", symbol));
                                executed += 1;
                            }
                            Err(e) => { println!("  [MOMENTUM] Sell failed — {}", e); skipped += 1; }
                        }
                    } else {
                        println!("  [MOMENTUM] DRY-RUN SELL {} RSI={:.1}", symbol, rsi_val);
                        logger.log_trade(symbol, "sell_dry", qty, current_price, "momentum", "dry");
                        executed += 1;
                    }
                }
            } else {
                println!("  [MOMENTUM] HOLD {} RSI={:.1}", symbol, rsi_val);
            }
        }

        logger.ledger("nina-trader-momentum",
            &format!("momentum_run_{}", SagcoLogger::stamp()),
            "SAGCO_NINA_MOMENTUM_PASS");

        Ok(StrategyResult {
            strategy: "momentum".into(),
            signals,
            executed,
            skipped,
            reason: format!("Momentum scan on {} symbols", self.symbols.len()),
        })
    }
}
