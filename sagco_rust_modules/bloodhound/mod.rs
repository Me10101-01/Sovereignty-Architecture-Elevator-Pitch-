// SAGCO Bloodhound module — resonant frequency + trading display + plugin registry
// License: SSL-1.0 — Strategickhaos DAO LLC

pub mod types;
pub mod plugins;

pub use types::{
    SagcoInput, SagcoArtifact, RenkoBrick, BrickDir,
    Candle, FrequencyBand, WhenGate, Unit, convert,
};
pub use plugins::{SagcoPlugin, PluginKind, PluginRegistry};
