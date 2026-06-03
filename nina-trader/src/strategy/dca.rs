/// Dollar Cost Averaging — buy fixed notional on every run
/// Safe passive income: invests same $ amount regardless of price

use super::{Strategy, StrategyResult, TradeSignal};
use crate::alpaca::AlpacaClient;
use crate::sagco::SagcoLogger;

pub struct DcaStrategy {
    pub symbols: Vec<String>,
    pub amount_per_symbol: f64,  // USD per symbol per run
    pub max_portfolio_pct: f64,  // max % of portfolio per position (0.0–1.0)
}

impl DcaStrategy {
    pub fn default_watchlist() -> Self {
        Self {
            symbols: vec![
                "SPY".into(),   // S&P 500 ETF — bedrock passive income
                "QQQ".into(),   // NASDAQ 100 ETF
                "VTI".into(),   // Total market ETF
                "AAPL".into(),  // Core tech anchor
                "MSFT".into(),  // Enterprise moat
            ],
            amount_per_symbol: 10.0,
            max_portfolio_pct: 0.10,
        }
    }
}

impl Strategy for DcaStrategy {
    fn name(&self) -> &str { "dca" }

    fn run(&self, client: &AlpacaClient, logger: &SagcoLogger, mode: &str) -> Result<StrategyResult, String> {
        let account = client.get_account()?;
        let portfolio_val: f64 = account.portfolio_value.parse().unwrap_or(100_000.0);
        let cash: f64 = account.cash.parse().unwrap_or(0.0);

        println!("  [DCA] Portfolio: ${:.2} | Cash: ${:.2}", portfolio_val, cash);

        let mut signals = Vec::new();
        let mut executed = 0;
        let mut skipped = 0;

        for symbol in &self.symbols {
            let price = match client.get_latest_price(symbol) {
                Ok(p) => p,
                Err(e) => { println!("  [DCA] Skip {} — {}", symbol, e); skipped += 1; continue; }
            };

            // Check existing position size
            let positions = client.get_positions().unwrap_or_default();
            let existing_val: f64 = positions.iter()
                .find(|p| p.symbol == *symbol)
                .and_then(|p| {
                    let qty: f64 = p.qty.parse().ok()?;
                    let cp: f64 = p.current_price.parse().ok()?;
                    Some(qty * cp)
                })
                .unwrap_or(0.0);

            let position_pct = existing_val / portfolio_val;
            if position_pct >= self.max_portfolio_pct {
                println!("  [DCA] Skip {} — position {:.1}% >= max {:.0}%",
                    symbol, position_pct * 100.0, self.max_portfolio_pct * 100.0);
                skipped += 1;
                continue;
            }

            let buy_amount = self.amount_per_symbol.min(cash * 0.5);
            if buy_amount < 1.0 {
                println!("  [DCA] Skip {} — insufficient cash", symbol);
                skipped += 1;
                continue;
            }

            signals.push(TradeSignal {
                symbol: symbol.clone(),
                side: "buy".into(),
                amount: buy_amount,
                reason: format!("DCA ${:.2} @ ${:.2}", buy_amount, price),
            });

            if mode == "live" || mode == "paper" {
                match client.submit_order_notional(symbol, buy_amount, "buy") {
                    Ok(order) => {
                        println!("  [DCA] BUY {} ${:.2} — order {}", symbol, buy_amount, order.id);
                        logger.log_trade(symbol, "buy", buy_amount / price, price, "dca", mode);
                        logger.race(&format!("nina_dca_buy_{}", symbol));
                        executed += 1;
                    }
                    Err(e) => {
                        println!("  [DCA] Order failed {} — {}", symbol, e);
                        skipped += 1;
                    }
                }
            } else {
                println!("  [DCA] DRY-RUN BUY {} ${:.2} @ ${:.2}", symbol, buy_amount, price);
                logger.log_trade(symbol, "buy_dry", buy_amount / price, price, "dca", "dry");
                executed += 1;
            }
        }

        logger.ledger("nina-trader-dca",
            &format!("dca_run_{}", SagcoLogger::stamp()),
            "SAGCO_NINA_DCA_PASS");

        Ok(StrategyResult {
            strategy: "dca".into(),
            signals,
            executed,
            skipped,
            reason: format!("DCA run complete on {} symbols", self.symbols.len()),
        })
    }
}
