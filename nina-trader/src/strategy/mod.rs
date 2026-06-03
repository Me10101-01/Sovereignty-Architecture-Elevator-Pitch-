pub mod dca;
pub mod momentum;
pub mod spy_mirror;

use crate::alpaca::{AlpacaClient, Bar};
use crate::sagco::SagcoLogger;

pub trait Strategy {
    fn name(&self) -> &str;
    fn run(&self, client: &AlpacaClient, logger: &SagcoLogger, mode: &str) -> Result<StrategyResult, String>;
}

#[derive(Debug, Clone)]
pub struct TradeSignal {
    pub symbol: String,
    pub side: String,   // "buy" | "sell"
    pub amount: f64,    // notional USD
    pub reason: String,
}

#[derive(Debug)]
pub struct StrategyResult {
    pub strategy: String,
    pub signals: Vec<TradeSignal>,
    pub executed: usize,
    pub skipped: usize,
    pub reason: String,
}

// Compute simple moving average from close prices
pub fn sma(bars: &[Bar], period: usize) -> Option<f64> {
    if bars.len() < period {
        return None;
    }
    let slice = &bars[bars.len() - period..];
    Some(slice.iter().map(|b| b.c).sum::<f64>() / period as f64)
}

// RSI(14) from close prices
pub fn rsi(bars: &[Bar], period: usize) -> Option<f64> {
    if bars.len() < period + 1 {
        return None;
    }
    let closes: Vec<f64> = bars.iter().map(|b| b.c).collect();
    let len = closes.len();
    let slice = &closes[len - period - 1..];

    let mut gains = 0.0f64;
    let mut losses = 0.0f64;
    for i in 1..slice.len() {
        let delta = slice[i] - slice[i - 1];
        if delta > 0.0 { gains += delta; } else { losses += delta.abs(); }
    }
    let avg_gain = gains / period as f64;
    let avg_loss = losses / period as f64;
    if avg_loss == 0.0 {
        return Some(100.0);
    }
    let rs = avg_gain / avg_loss;
    Some(100.0 - (100.0 / (1.0 + rs)))
}
