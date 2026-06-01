// SAGCO Antibody Types — immune response classification
// License: SSL-1.0 — Strategickhaos DAO LLC

#[derive(Debug, Clone, PartialEq)]
pub enum Antibody {
    // core (all domains)
    PassImmunity,
    UnknownVariance,
    // shell / path
    PathDiscovery,
    ProjectRoot,
    Dependency,
    // rust
    BorrowChecker,
    CompileError,
    StubDetected,
    // python
    SyntaxError,
    ImportError,
    // sql
    SchemaError,
    // ghidra / binary
    JdkGate,
    PlatformLimitation,
    // ai / llm
    ContextCollapse,
    RateLimit,
    // academic
    PrerequisiteGate,
    CurriculumBottleneck,
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
            Antibody::PassImmunity          => "PASS_IMMUNITY",
            Antibody::UnknownVariance       => "UNKNOWN_VARIANCE_ANTIBODY",
            Antibody::PathDiscovery         => "PATH_DISCOVERY_ANTIBODY",
            Antibody::ProjectRoot           => "PROJECT_ROOT_ANTIBODY",
            Antibody::Dependency            => "DEPENDENCY_ANTIBODY",
            Antibody::BorrowChecker         => "BORROW_CHECKER_ANTIBODY",
            Antibody::CompileError          => "COMPILE_ERROR_ANTIBODY",
            Antibody::StubDetected          => "STUB_DETECTED_ANTIBODY",
            Antibody::SyntaxError           => "SYNTAX_ANTIBODY",
            Antibody::ImportError           => "IMPORT_ANTIBODY",
            Antibody::SchemaError           => "SCHEMA_ANTIBODY",
            Antibody::JdkGate               => "JDK_GATE_ANTIBODY",
            Antibody::PlatformLimitation    => "PLATFORM_LIMITATION_ANTIBODY",
            Antibody::ContextCollapse       => "CONTEXT_COLLAPSE_ANTIBODY",
            Antibody::RateLimit             => "RATE_LIMIT_ANTIBODY",
            Antibody::PrerequisiteGate      => "PREREQUISITE_ANTIBODY",
            Antibody::CurriculumBottleneck  => "CURRICULUM_BOTTLENECK_ANTIBODY",
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
