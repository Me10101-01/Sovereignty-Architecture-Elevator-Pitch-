#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct FlameHash(pub String);

#[derive(Debug, Clone)]
pub enum FlameLangToken {
    ExcelWafer(String),        // Silicon  Si-14
    WordFreq(String, u32),     // Helium   He-2
    RawToken(String),          // Carbon   C-6
    WeightScalar(f64),         // Lead     Pb-82
    FlameSignal(String),       // Phosphorus P-15
    OxygenRuntime(String),     // Oxygen   O-8
    RustCallHook(String),      // Iron     Fe-26
    DnaStrandSequence(String), // Nitrogen N-7
    UnityNode(u32),            // Hydrogen H-1
    EpicOrchestrator(String),  // Gold     Au-79
    HashedNode(FlameHash),     // Unison — content-addressed identity
}
