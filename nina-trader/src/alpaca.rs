use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// Alpaca paper trading endpoint — no real money risk
const PAPER_BASE: &str = "https://paper-api.alpaca.markets";
const DATA_BASE: &str = "https://data.alpaca.markets";

#[derive(Debug, Clone)]
pub struct AlpacaClient {
    pub key: String,
    pub secret: String,
    pub live: bool,
    base_url: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Account {
    pub id: String,
    pub portfolio_value: String,
    pub cash: String,
    pub buying_power: String,
    pub equity: String,
    pub status: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Position {
    pub symbol: String,
    pub qty: String,
    pub avg_entry_price: String,
    pub current_price: String,
    pub unrealized_pl: String,
    pub unrealized_plpc: String,
    pub side: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Order {
    pub id: String,
    pub symbol: String,
    pub side: String,
    pub qty: String,
    pub status: String,
    pub filled_avg_price: Option<String>,
    pub submitted_at: String,
}

#[derive(Debug, Deserialize)]
pub struct Bar {
    pub t: String,   // timestamp
    pub o: f64,      // open
    pub h: f64,      // high
    pub l: f64,      // low
    pub c: f64,      // close
    pub v: f64,      // volume
}

#[derive(Debug, Deserialize)]
struct BarsResponse {
    bars: HashMap<String, Vec<Bar>>,
}

#[derive(Debug, Serialize)]
struct OrderRequest {
    symbol: String,
    notional: Option<String>,
    qty: Option<String>,
    side: String,
    #[serde(rename = "type")]
    order_type: String,
    time_in_force: String,
}

impl AlpacaClient {
    pub fn new(key: String, secret: String, live: bool) -> Self {
        let base_url = if live {
            "https://api.alpaca.markets".into()
        } else {
            PAPER_BASE.into()
        };
        Self { key, secret, live, base_url }
    }

    fn headers(&self) -> reqwest::header::HeaderMap {
        let mut map = reqwest::header::HeaderMap::new();
        map.insert("APCA-API-KEY-ID", self.key.parse().unwrap());
        map.insert("APCA-API-SECRET-KEY", self.secret.parse().unwrap());
        map.insert("Content-Type", "application/json".parse().unwrap());
        map
    }

    pub fn get_account(&self) -> Result<Account, String> {
        let url = format!("{}/v2/account", self.base_url);
        let client = reqwest::blocking::Client::new();
        let resp = client.get(&url).headers(self.headers())
            .send().map_err(|e| e.to_string())?;
        if !resp.status().is_success() {
            return Err(format!("HTTP {}: {}", resp.status(), resp.text().unwrap_or_default()));
        }
        resp.json::<Account>().map_err(|e| e.to_string())
    }

    pub fn get_positions(&self) -> Result<Vec<Position>, String> {
        let url = format!("{}/v2/positions", self.base_url);
        let client = reqwest::blocking::Client::new();
        let resp = client.get(&url).headers(self.headers())
            .send().map_err(|e| e.to_string())?;
        if !resp.status().is_success() {
            return Err(format!("HTTP {}", resp.status()));
        }
        resp.json::<Vec<Position>>().map_err(|e| e.to_string())
    }

    pub fn get_bars(&self, symbol: &str, timeframe: &str, limit: u32) -> Result<Vec<Bar>, String> {
        let url = format!(
            "{}/v2/stocks/bars?symbols={}&timeframe={}&limit={}",
            DATA_BASE, symbol, timeframe, limit
        );
        let client = reqwest::blocking::Client::new();
        let resp = client.get(&url).headers(self.headers())
            .send().map_err(|e| e.to_string())?;
        if !resp.status().is_success() {
            return Err(format!("HTTP {}: {}", resp.status(), resp.text().unwrap_or_default()));
        }
        let data: BarsResponse = resp.json().map_err(|e| e.to_string())?;
        Ok(data.bars.get(symbol).cloned().unwrap_or_default())
    }

    pub fn get_latest_price(&self, symbol: &str) -> Result<f64, String> {
        let bars = self.get_bars(symbol, "1Day", 1)?;
        bars.last().map(|b| b.c).ok_or_else(|| "no bars".into())
    }

    pub fn submit_order_notional(&self, symbol: &str, notional: f64, side: &str) -> Result<Order, String> {
        let url = format!("{}/v2/orders", self.base_url);
        let body = OrderRequest {
            symbol: symbol.into(),
            notional: Some(format!("{:.2}", notional)),
            qty: None,
            side: side.into(),
            order_type: "market".into(),
            time_in_force: "day".into(),
        };
        let client = reqwest::blocking::Client::new();
        let resp = client.post(&url).headers(self.headers())
            .json(&body).send().map_err(|e| e.to_string())?;
        if !resp.status().is_success() {
            return Err(format!("HTTP {}: {}", resp.status(), resp.text().unwrap_or_default()));
        }
        resp.json::<Order>().map_err(|e| e.to_string())
    }

    pub fn submit_order_qty(&self, symbol: &str, qty: f64, side: &str) -> Result<Order, String> {
        let url = format!("{}/v2/orders", self.base_url);
        let body = OrderRequest {
            symbol: symbol.into(),
            notional: None,
            qty: Some(format!("{:.4}", qty)),
            side: side.into(),
            order_type: "market".into(),
            time_in_force: "day".into(),
        };
        let client = reqwest::blocking::Client::new();
        let resp = client.post(&url).headers(self.headers())
            .json(&body).send().map_err(|e| e.to_string())?;
        if !resp.status().is_success() {
            return Err(format!("HTTP {}: {}", resp.status(), resp.text().unwrap_or_default()));
        }
        resp.json::<Order>().map_err(|e| e.to_string())
    }
}
