// SAGCO Antibody Classifier — maps CLI output to immune response
// License: SSL-1.0 — Strategickhaos DAO LLC

use super::types::{Antibody, CircuitRow, EurScore, Trajectory};

pub fn classify(output: &str, exit_code: i32) -> (Antibody, Trajectory) {
    let text = output.to_lowercase();

    if exit_code == 0 {
        return (Antibody::PassImmunity, Trajectory::Stabilized);
    }
    if text.contains("no such file or directory") {
        return (Antibody::PathDiscovery, Trajectory::Adaptation);
    }
    if text.contains("could not find") && text.contains("cargo.toml") {
        return (Antibody::ProjectRoot, Trajectory::Adaptation);
    }
    if text.contains("jdk 21") || text.contains("jdk 21+ (64-bit) could not be found") {
        return (Antibody::JdkGate, Trajectory::Evolution);
    }
    if text.contains("command not found") || text.contains("not installed") {
        return (Antibody::Dependency, Trajectory::Adaptation);
    }
    if text.contains("fn main") && text.contains("println") && text.len() < 300 {
        return (Antibody::StubDetected, Trajectory::Mutation);
    }
    if text.contains("decompiler") || text.contains("native") && text.contains("missing")
        || text.contains("android_aarch64")
    {
        return (Antibody::PlatformLimitation, Trajectory::Evolution);
    }

    (Antibody::UnknownVariance, Trajectory::Mutation)
}

pub fn to_eur_score(antibody: &Antibody, variance: i32) -> EurScore {
    if variance == 0 {
        return EurScore::Pass;
    }
    match antibody {
        Antibody::PassImmunity       => EurScore::Pass,
        Antibody::PathDiscovery      => EurScore::Fail,
        Antibody::ProjectRoot        => EurScore::Fail,
        Antibody::JdkGate            => EurScore::Evolve,
        Antibody::Dependency         => EurScore::Warn,
        Antibody::StubDetected       => EurScore::Fail,
        Antibody::PlatformLimitation => EurScore::Adapt,
        Antibody::UnknownVariance    => EurScore::Warn,
    }
}

pub fn build_circuit_row(
    command: &str,
    expected: &str,
    actual: &str,
    exit_code: i32,
) -> CircuitRow {
    let (antibody, trajectory) = classify(actual, exit_code);
    let variance = if exit_code == 0 { 0 } else { 1 };
    let score = to_eur_score(&antibody, variance);
    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
        .to_string();

    CircuitRow {
        stamp,
        command: command.to_string(),
        expected: expected.to_string(),
        actual: actual.to_string(),
        exit_code,
        antibody,
        trajectory,
        variance,
        score,
    }
}
