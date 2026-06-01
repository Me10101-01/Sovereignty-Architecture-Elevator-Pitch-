// SAGCO Antibody Module
pub mod classifier;
pub mod types;

pub use classifier::{build_circuit_row, classify, to_eur_score};
pub use types::{Antibody, CircuitRow, EurScore, Trajectory};
