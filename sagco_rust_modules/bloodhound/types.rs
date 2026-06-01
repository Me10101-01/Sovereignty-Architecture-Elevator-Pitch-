// SAGCO Bloodhound — trading display types + plugin input trait
// License: SSL-1.0 — Strategickhaos DAO LLC

use crate::antibody::types::{Antibody, Trajectory, EurScore};

// ── plugin input trait ────────────────────────────────────────────────────────
// Every input source implements this — PDF, URL, terminal, image, SQL, Obsidian
pub trait SagcoInput {
    fn source_id(&self) -> &str;
    fn tokenize(&self)   -> Vec<String>;
    fn fingerprint(&self) -> String;
    fn classify(&self)    -> (Antibody, Trajectory);
    fn artifact(&self)    -> SagcoArtifact;
}

#[derive(Debug, Clone)]
pub struct SagcoArtifact {
    pub source_id:   String,
    pub token_count: usize,
    pub fingerprint: String,
    pub sha256:      String,
    pub antibody:    Antibody,
    pub trajectory:  Trajectory,
    pub score:       EurScore,
}

// ── Renko brick ───────────────────────────────────────────────────────────────
#[derive(Debug, Clone, PartialEq)]
pub enum BrickDir { Up, Down, Flat }

#[derive(Debug, Clone)]
pub struct RenkoBrick {
    pub level:     u32,    // maturity % floor of this brick
    pub direction: BrickDir,
    pub antibody:  Antibody,
}

impl RenkoBrick {
    pub fn char(&self) -> &'static str {
        match self.direction {
            BrickDir::Up   => "██",
            BrickDir::Down => "▓▓",
            BrickDir::Flat => "──",
        }
    }
    pub fn signal(&self) -> &'static str {
        match self.direction {
            BrickDir::Up   => "BUY_EVOLUTION",
            BrickDir::Down => "HOLD_ADAPTATION",
            BrickDir::Flat => "STABILIZED",
        }
    }
}

// ── Candlestick (session OHLC) ────────────────────────────────────────────────
#[derive(Debug, Clone)]
pub struct Candle {
    pub epoch: String,
    pub open:  u32,
    pub high:  u32,
    pub low:   u32,
    pub close: u32,
}

impl Candle {
    pub fn body(&self) -> &'static str {
        let delta = self.close as i32 - self.open as i32;
        if delta > 5      { "  ▲███  " }
        else if delta < -5 { "  ▼▓▓▓  " }
        else if delta.abs() <= 2 { "  ─╪──  " }
        else              { "  ░░░░  " }
    }
    pub fn signal(&self) -> &'static str {
        let delta = self.close as i32 - self.open as i32;
        if delta > 5      { "EVOLUTION ↑" }
        else if delta < -5 { "ADAPTATION ↓" }
        else if delta.abs() <= 2 { "STABILIZED ─" }
        else              { "WARN adaptation" }
    }
}

// ── frequency band ────────────────────────────────────────────────────────────
#[derive(Debug, Clone)]
pub struct FrequencyBand {
    pub antibody:    String,
    pub count:       u32,
    pub pct:         f32,
    pub is_resonant: bool,
}

// ── ML WHEN gate ──────────────────────────────────────────────────────────────
#[derive(Debug, Clone)]
pub struct WhenGate {
    pub name:      &'static str,
    pub condition: String,
    pub value:     String,
    pub signal:    &'static str,
    pub active:    bool,
}

// ── unit conversion ───────────────────────────────────────────────────────────
pub enum Unit {
    Lnft, Sqft, Meters,
    Tokens, Edges,
    Bytes, Kb, Mb,
    MaturityPct, Grade, DeltaGH, TrajectoryStr,
    PassRate, SignalStr,
    Hz, Khz, Mhz,
    VarianceScore, AntibodyIntensity,
}

pub fn convert(value: f64, from: &Unit, to: &Unit) -> String {
    use Unit::*;
    match (from, to) {
        (Lnft, Meters)     => format!("{:.4}", value * 0.3048),
        (Lnft, Sqft)       => format!("{:.2}", value * std::f64::consts::PI * 0.5),
        (Tokens, Edges)    => format!("{:.0}", value - 1.0),
        (Edges, Tokens)    => format!("{:.0}", value + 1.0),
        (Bytes, Kb)        => format!("{:.3}", value / 1024.0),
        (Kb, Mb)           => format!("{:.6}", value / 1024.0),
        (MaturityPct, Grade) => {
            if value >= 95.0 { "S".into() }
            else if value >= 85.0 { "A".into() }
            else if value >= 70.0 { "B".into() }
            else if value >= 55.0 { "C".into() }
            else if value >= 40.0 { "D".into() }
            else { "F".into() }
        }
        (MaturityPct, DeltaGH) => format!("+{:.1}%", (95.0_f64 - value).max(0.0)),
        (PassRate, SignalStr) => {
            if value > 0.70      { "BUY_EVOLUTION".into() }
            else if value > 0.40 { "HOLD_ADAPTATION".into() }
            else                 { "SELL_MUTATION".into() }
        }
        (Hz, Khz) => format!("{:.3}", value / 1000.0),
        (Khz, Hz) => format!("{:.0}", value * 1000.0),
        (Mhz, Hz) => format!("{:.0}", value * 1e6),
        (VarianceScore, AntibodyIntensity) => format!("{:.3}", (value * 0.333).min(1.0)),
        _ => "UNIT_CONV_UNKNOWN".into(),
    }
}
