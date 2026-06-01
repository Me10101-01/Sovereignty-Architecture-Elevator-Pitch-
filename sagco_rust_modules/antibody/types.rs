// SAGCO Antibody Types — immune response classification
// License: SSL-1.0 — Strategickhaos DAO LLC

#[derive(Debug, Clone, PartialEq)]
pub enum Antibody {
    PassImmunity,
    PathDiscovery,
    ProjectRoot,
    JdkGate,
    Dependency,
    StubDetected,
    PlatformLimitation,
    UnknownVariance,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Trajectory {
    Stabilized,
    Adaptation,
    Evolution,
    Mutation,
}

#[derive(Debug, Clone, PartialEq)]
pub enum EurScore {
    Pass,
    Warn,
    Fail,
    Adapt,
    Evolve,
}

#[derive(Debug, Clone)]
pub struct CircuitRow {
    pub stamp:      String,
    pub command:    String,
    pub expected:   String,
    pub actual:     String,
    pub exit_code:  i32,
    pub antibody:   Antibody,
    pub trajectory: Trajectory,
    pub variance:   i32,
    pub score:      EurScore,
}

impl Antibody {
    pub fn as_str(&self) -> &'static str {
        match self {
            Antibody::PassImmunity      => "PASS_IMMUNITY",
            Antibody::PathDiscovery     => "PATH_DISCOVERY_ANTIBODY",
            Antibody::ProjectRoot       => "PROJECT_ROOT_ANTIBODY",
            Antibody::JdkGate           => "JDK_GATE_ANTIBODY",
            Antibody::Dependency        => "DEPENDENCY_ANTIBODY",
            Antibody::StubDetected      => "STUB_DETECTED_ANTIBODY",
            Antibody::PlatformLimitation=> "PLATFORM_LIMITATION_ANTIBODY",
            Antibody::UnknownVariance   => "UNKNOWN_VARIANCE_ANTIBODY",
        }
    }
}

impl Trajectory {
    pub fn as_str(&self) -> &'static str {
        match self {
            Trajectory::Stabilized  => "stabilized",
            Trajectory::Adaptation  => "adaptation",
            Trajectory::Evolution   => "evolution",
            Trajectory::Mutation    => "mutation",
        }
    }
}

impl EurScore {
    pub fn as_str(&self) -> &'static str {
        match self {
            EurScore::Pass   => "PASS",
            EurScore::Warn   => "WARN",
            EurScore::Fail   => "FAIL",
            EurScore::Adapt  => "ADAPT",
            EurScore::Evolve => "EVOLVE",
        }
    }
}
