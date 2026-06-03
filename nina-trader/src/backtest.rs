/// Deterministic backtesting engine — no random, reproducible results
/// Uses sine-wave + trend price model for demo/dry-run mode

#[derive(Debug, Clone)]
pub struct PriceBar {
    pub day: u32,
    pub open: f64,
    pub high: f64,
    pub low: f64,
    pub close: f64,
}

#[derive(Debug, Clone)]
pub struct BacktestResult {
    pub strategy: String,
    pub symbol: String,
    pub days: u32,
    pub initial_cash: f64,
    pub final_value: f64,
    pub total_invested: f64,
    pub total_return_pct: f64,
    pub max_drawdown_pct: f64,
    pub sharpe_ratio: f64,
    pub win_rate_pct: f64,
    pub total_trades: u32,
    pub winning_trades: u32,
    pub score: char,
    pub ready_for_paper: bool,
    pub ready_for_live: bool,
}

// Deterministic price model: trend + cycle, seeded by symbol
// Produces consistent demo output without rand crate
pub fn simulate_prices(symbol: &str, days: u32, base_price: f64) -> Vec<PriceBar> {
    let seed: f64 = symbol.bytes().map(|b| b as u64).sum::<u64>() as f64;
    let cycle_phase = (seed % 63.0) / 10.0;
    let daily_trend = 0.00038;          // ~10% annual return
    let cycle_amplitude = 0.018;        // ±1.8% cycle swing
    let vol_scale = 0.006;              // intraday spread

    let mut bars = Vec::with_capacity(days as usize);
    let mut price = base_price;

    for d in 1..=days {
        let t = d as f64;
        let daily_return = daily_trend
            + cycle_amplitude * (2.0 * std::f64::consts::PI * t / 21.0 + cycle_phase).sin()
            + cycle_amplitude * 0.4 * (2.0 * std::f64::consts::PI * t / 5.0 + seed * 0.1).cos();

        let open = price;
        price *= 1.0 + daily_return;
        let spread = price * vol_scale;
        let high = price + spread * 0.6;
        let low = price - spread * 0.4;

        bars.push(PriceBar { day: d, open, high, low, close: price });
    }
    bars
}

// Base prices for demo symbols
pub fn base_price(symbol: &str) -> f64 {
    match symbol {
        "SPY"   => 452.0,
        "QQQ"   => 388.0,
        "VTI"   => 235.0,
        "AAPL"  => 188.0,
        "MSFT"  => 415.0,
        "NVDA"  => 875.0,
        "GOOGL" => 174.0,
        "AMZN"  => 195.0,
        _       => 100.0,
    }
}

/// Run DCA strategy over price history: buy $amount every N days
pub fn backtest_dca(symbol: &str, bars: &[PriceBar], amount_per_run: f64, run_every_days: u32) -> BacktestResult {
    let mut cash = 10_000.0f64;
    let mut shares = 0.0f64;
    let mut total_invested = 0.0f64;
    let mut trades = 0u32;
    let mut peak_value = cash;
    let mut max_drawdown = 0.0f64;
    let mut daily_returns: Vec<f64> = Vec::new();
    let mut prev_portfolio = cash;

    for (i, bar) in bars.iter().enumerate() {
        // DCA buy every run_every_days
        if i % run_every_days as usize == 0 && cash >= amount_per_run {
            let qty = amount_per_run / bar.close;
            shares += qty;
            cash -= amount_per_run;
            total_invested += amount_per_run;
            trades += 1;
        }

        let portfolio_val = cash + shares * bar.close;
        if portfolio_val > peak_value { peak_value = portfolio_val; }
        let drawdown = (peak_value - portfolio_val) / peak_value * 100.0;
        if drawdown > max_drawdown { max_drawdown = drawdown; }

        let daily_ret = (portfolio_val - prev_portfolio) / prev_portfolio;
        daily_returns.push(daily_ret);
        prev_portfolio = portfolio_val;
    }

    let final_price = bars.last().map(|b| b.close).unwrap_or(1.0);
    let final_value = cash + shares * final_price;
    let total_return_pct = if total_invested > 0.0 {
        (final_value - (10_000.0 - cash + total_invested)) / total_invested * 100.0
    } else { 0.0 };

    let sharpe = compute_sharpe(&daily_returns);
    let win_rate = if trades > 0 {
        // For DCA: winning = final value > total invested
        if final_value > total_invested { 100.0 } else { 0.0 }
    } else { 0.0 };

    let score = score_strategy(total_return_pct, max_drawdown, sharpe);

    BacktestResult {
        strategy: "dca".into(),
        symbol: symbol.into(),
        days: bars.len() as u32,
        initial_cash: 10_000.0,
        final_value,
        total_invested,
        total_return_pct,
        max_drawdown_pct: max_drawdown,
        sharpe_ratio: sharpe,
        win_rate_pct: win_rate,
        total_trades: trades,
        winning_trades: if final_value > total_invested { trades } else { 0 },
        score,
        ready_for_paper: max_drawdown < 15.0 && sharpe > 0.3,
        ready_for_live: false, // never until 30+ days paper trading
    }
}

/// Run RSI momentum over price history
pub fn backtest_momentum(symbol: &str, bars: &[PriceBar], buy_rsi: f64, sell_rsi: f64, notional: f64) -> BacktestResult {
    let mut cash = 10_000.0f64;
    let mut shares = 0.0f64;
    let mut total_invested = 0.0f64;
    let mut trades = 0u32;
    let mut winning_trades = 0u32;
    let mut peak_value = cash;
    let mut max_drawdown = 0.0f64;
    let mut daily_returns: Vec<f64> = Vec::new();
    let mut prev_portfolio = cash;
    let mut buy_price = 0.0f64;

    let closes: Vec<f64> = bars.iter().map(|b| b.close).collect();

    for (i, bar) in bars.iter().enumerate() {
        if i < 14 { continue; }

        let rsi = simple_rsi(&closes[..=i], 14);
        let in_position = shares > 0.0;

        if !in_position && rsi <= buy_rsi && cash >= notional {
            let qty = notional / bar.close;
            shares += qty;
            cash -= notional;
            total_invested += notional;
            buy_price = bar.close;
            trades += 1;
        } else if in_position && rsi >= sell_rsi {
            let proceeds = shares * bar.close;
            if bar.close > buy_price { winning_trades += 1; }
            cash += proceeds;
            shares = 0.0;
            trades += 1;
        }

        let portfolio_val = cash + shares * bar.close;
        if portfolio_val > peak_value { peak_value = portfolio_val; }
        let drawdown = (peak_value - portfolio_val) / peak_value * 100.0;
        if drawdown > max_drawdown { max_drawdown = drawdown; }

        let daily_ret = (portfolio_val - prev_portfolio) / prev_portfolio;
        daily_returns.push(daily_ret);
        prev_portfolio = portfolio_val;
    }

    let final_price = bars.last().map(|b| b.close).unwrap_or(1.0);
    let final_value = cash + shares * final_price;
    let total_return_pct = if total_invested > 0.0 {
        (final_value - 10_000.0) / 10_000.0 * 100.0
    } else { 0.0 };

    let sharpe = compute_sharpe(&daily_returns);
    let win_rate = if trades > 0 { winning_trades as f64 / (trades as f64 / 2.0).max(1.0) * 100.0 } else { 0.0 };
    let score = score_strategy(total_return_pct, max_drawdown, sharpe);

    BacktestResult {
        strategy: "momentum".into(),
        symbol: symbol.into(),
        days: bars.len() as u32,
        initial_cash: 10_000.0,
        final_value,
        total_invested,
        total_return_pct,
        max_drawdown_pct: max_drawdown,
        sharpe_ratio: sharpe,
        win_rate_pct: win_rate,
        total_trades: trades,
        winning_trades,
        score,
        ready_for_paper: max_drawdown < 15.0 && sharpe > 0.3,
        ready_for_live: false,
    }
}

fn simple_rsi(closes: &[f64], period: usize) -> f64 {
    if closes.len() < period + 1 { return 50.0; }
    let slice = &closes[closes.len() - period - 1..];
    let mut gains = 0.0f64;
    let mut losses = 0.0f64;
    for i in 1..slice.len() {
        let d = slice[i] - slice[i-1];
        if d > 0.0 { gains += d; } else { losses += d.abs(); }
    }
    let ag = gains / period as f64;
    let al = losses / period as f64;
    if al == 0.0 { return 100.0; }
    100.0 - (100.0 / (1.0 + ag / al))
}

fn compute_sharpe(returns: &[f64]) -> f64 {
    if returns.len() < 2 { return 0.0; }
    let mean = returns.iter().sum::<f64>() / returns.len() as f64;
    let variance = returns.iter().map(|r| (r - mean).powi(2)).sum::<f64>() / returns.len() as f64;
    let std_dev = variance.sqrt();
    if std_dev == 0.0 { return 0.0; }
    // annualize: mean * 252 / (std_dev * sqrt(252))
    mean * 252.0_f64.sqrt() / std_dev
}

pub fn score_strategy(return_pct: f64, max_dd: f64, sharpe: f64) -> char {
    let score =
        if return_pct > 8.0 && max_dd < 5.0 && sharpe > 1.0 { 'S' }
        else if return_pct > 4.0 && max_dd < 10.0 && sharpe > 0.5 { 'A' }
        else if return_pct > 1.0 && max_dd < 15.0 { 'B' }
        else if return_pct > 0.0 { 'C' }
        else { 'D' };
    score
}
