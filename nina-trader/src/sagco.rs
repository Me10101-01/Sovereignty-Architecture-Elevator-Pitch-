use chrono::Local;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::PathBuf;

pub struct SagcoLogger {
    ledger_path: PathBuf,
    race_path: PathBuf,
    device: String,
}

impl SagcoLogger {
    pub fn new() -> Self {
        let home = std::env::var("HOME").unwrap_or_else(|_| "/tmp".into());
        let device = std::env::var("SAGCO_DEVICE").unwrap_or_else(|_| "unknown".into());

        let ledger = PathBuf::from(&home).join("sagco_ledger.csv");
        let race_dir = PathBuf::from(&home).join("sagco_race");
        fs::create_dir_all(&race_dir).ok();
        let race = race_dir.join("race_log.csv");

        // ensure headers
        if !ledger.exists() {
            if let Ok(mut f) = fs::File::create(&ledger) {
                writeln!(f, "timestamp,device,command,artifact,hash,status").ok();
            }
        }
        if !race.exists() {
            if let Ok(mut f) = fs::File::create(&race) {
                writeln!(f, "timestamp,device,event,pwd,battery,status").ok();
            }
        }

        Self { ledger_path: ledger, race_path: race, device }
    }

    pub fn stamp() -> String {
        Local::now().format("%Y%m%d_%H%M%S").to_string()
    }

    pub fn ledger(&self, command: &str, artifact: &str, status: &str) {
        let ts = Self::stamp();
        let raw = format!("{}{}", ts, command);
        let hash = sha256_short(&raw);
        let line = format!("{},{},{},{},{},{}\n", ts, self.device, command, artifact, hash, status);
        if let Ok(mut f) = OpenOptions::new().append(true).open(&self.ledger_path) {
            f.write_all(line.as_bytes()).ok();
        }
        println!("LEDGER_ENTRY={}", hash);
    }

    pub fn race(&self, event: &str) {
        let ts = Self::stamp();
        let pwd = std::env::current_dir()
            .map(|p| p.display().to_string())
            .unwrap_or_else(|_| "unknown".into());
        let bat = read_battery();
        let line = format!("{},{},{},{},{},SAGCO_RACE_TICK\n", ts, self.device, event, pwd, bat);
        if let Ok(mut f) = OpenOptions::new().append(true).open(&self.race_path) {
            f.write_all(line.as_bytes()).ok();
        }
    }

    pub fn trade_log_path(&self) -> PathBuf {
        let home = std::env::var("HOME").unwrap_or_else(|_| "/tmp".into());
        let dir = PathBuf::from(&home).join("sagco_nina");
        fs::create_dir_all(&dir).ok();
        dir.join("trade_log.csv")
    }

    pub fn log_trade(&self, symbol: &str, side: &str, qty: f64, price: f64, strategy: &str, mode: &str) {
        let path = self.trade_log_path();
        if !path.exists() {
            if let Ok(mut f) = fs::File::create(&path) {
                writeln!(f, "timestamp,device,symbol,side,qty,price,strategy,mode,pnl").ok();
            }
        }
        let ts = Self::stamp();
        let line = format!("{},{},{},{},{:.4},{:.4},{},{},0.00\n",
            ts, self.device, symbol, side, qty, price, strategy, mode);
        if let Ok(mut f) = OpenOptions::new().append(true).open(&path) {
            f.write_all(line.as_bytes()).ok();
        }
    }
}

fn sha256_short(input: &str) -> String {
    // simple djb2-based hash for portability (no sha2 dep needed)
    let mut h: u64 = 5381;
    for b in input.bytes() {
        h = h.wrapping_mul(33).wrapping_add(b as u64);
    }
    format!("{:012x}", h & 0xFFFFFFFFFFFF)
}

fn read_battery() -> String {
    std::fs::read_to_string("/sys/class/power_supply/battery/capacity")
        .unwrap_or_else(|_| "unknown".into())
        .trim()
        .to_string()
}
