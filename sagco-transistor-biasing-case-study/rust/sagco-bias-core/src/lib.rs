// sagco-bias-core library — transistor biasing calculator fleet
//
// Module map:
//   units            — SI formatting helpers
//   voltage_divider  — voltage-divider bias (Thevenin method)
//   eru              — ERU variance scoring: |expected - actual| / max(expected, ε)
//
// Planned (not yet wired):
//   fixed_bias, collector_feedback, emitter_feedback, pmi, report

pub mod units;
pub mod voltage_divider;
pub mod eru;
