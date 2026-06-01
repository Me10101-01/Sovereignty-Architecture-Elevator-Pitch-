// SAGCO State Integrity Verifier
// Catches "false green lights": SAGCO_CORE_PARSE_PASS reported but
// physical artifacts don't exist on disk.
// License: SSL-1.0 — Strategickhaos DAO LLC

use std::path::Path;

#[derive(Debug, PartialEq)]
pub enum VerifyError {
    /// System reported PASS but the .seal artifact file is missing from disk.
    MissingSealArtifact { target: String, expected_path: String },
    /// System reported PASS but the seal output claims are contradictory.
    SealContradiction(String),
}

impl VerifyError {
    pub fn antibody_name(&self) -> &'static str {
        match self {
            VerifyError::MissingSealArtifact { .. } => "MISSING_SEAL_ARTIFACT_ANTIBODY",
            VerifyError::SealContradiction(_)       => "SEAL_CONTRADICTION_ANTIBODY",
        }
    }

    pub fn message(&self) -> String {
        match self {
            VerifyError::MissingSealArtifact { target, expected_path } =>
                format!(
                    "Kernel reported EVIDENCE_LOCKED for '{}' but '{}' does not exist on disk. \
                     False green light detected.",
                    target, expected_path
                ),
            VerifyError::SealContradiction(msg) => msg.clone(),
        }
    }
}

pub struct StateIntegrityVerifier;

impl StateIntegrityVerifier {
    /// Parse execution stdout and verify file-system state matches claims.
    ///
    /// Rules enforced:
    ///   - Every `[SEAL] <target> SHA256=... EVIDENCE_LOCKED` line must have
    ///     a corresponding `<target>.seal` file on disk.
    ///   - These checks only fire when `STATUS=SAGCO_CORE_PARSE_PASS` is present,
    ///     so failing pipelines don't generate spurious filesystem complaints.
    pub fn verify_execution(stdout: &str) -> Vec<VerifyError> {
        let reported_pass = stdout.lines()
            .any(|l| l.contains("STATUS=SAGCO_CORE_PARSE_PASS"));

        if !reported_pass {
            // Pipeline reported failure — antibodies already fired; nothing to verify
            return Vec::new();
        }

        let mut errors = Vec::new();

        for line in stdout.lines() {
            if !line.contains("[SEAL]") || !line.contains("EVIDENCE_LOCKED") {
                continue;
            }

            // Extract target from: "[SEAL] <target> SHA256=...  EVIDENCE_LOCKED"
            if let Some(target) = Self::parse_seal_target(line) {
                let artifact_path = format!("{}.seal", target);
                if !Path::new(&artifact_path).exists() {
                    errors.push(VerifyError::MissingSealArtifact {
                        target: target.to_string(),
                        expected_path: artifact_path,
                    });
                }
            } else {
                errors.push(VerifyError::SealContradiction(
                    format!("Could not parse seal target from line: {:?}", line)
                ));
            }
        }

        errors
    }

    /// Read target field from a SEAL log line.
    /// Format: "[SEAL] <target> SHA256=<hex>  EVIDENCE_LOCKED  artifact=<path>"
    fn parse_seal_target(line: &str) -> Option<&str> {
        // tokens after [SEAL]: target is always the first one
        let after_seal = line.split("[SEAL]").nth(1)?.trim();
        after_seal.split_whitespace().next()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    fn make_pass_stdout(target: &str, sha: &str) -> String {
        format!(
            "[SEAL] {target} SHA256={sha}  EVIDENCE_LOCKED  artifact={target}.seal\n\
             STATUS=SAGCO_CORE_PARSE_PASS\n"
        )
    }

    #[test]
    fn no_errors_when_pipeline_fails() {
        let stdout = "[WAVE]: missing.txt TARGET_BYTES=0 — EMPTY_RESPONSE_ANTIBODY\n\
                      STATUS=SAGCO_CORE_VARIANCE_FAIL\n";
        let errs = StateIntegrityVerifier::verify_execution(stdout);
        assert!(errs.is_empty(), "failed pipeline must not raise verifier errors");
    }

    #[test]
    fn missing_seal_artifact_fires() {
        let stdout = make_pass_stdout("ghost_evidence.bin", "abc123");
        // ghost_evidence.bin.seal does NOT exist
        let errs = StateIntegrityVerifier::verify_execution(&stdout);
        assert_eq!(errs.len(), 1);
        assert_eq!(errs[0].antibody_name(), "MISSING_SEAL_ARTIFACT_ANTIBODY");
        assert!(errs[0].message().contains("ghost_evidence.bin"));
    }

    #[test]
    fn passes_when_artifact_file_exists() {
        let target   = "/tmp/sagco_verify_test_evidence.bin";
        let artifact = format!("{}.seal", target);
        fs::write(&artifact, b"SAGCO_SEAL_ARTIFACT=1\n").expect("write artifact");

        let stdout = make_pass_stdout(target,
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
        let errs = StateIntegrityVerifier::verify_execution(&stdout);
        let _ = fs::remove_file(&artifact);
        assert!(errs.is_empty(), "verifier must pass when artifact exists on disk");
    }

    #[test]
    fn no_seal_line_no_errors() {
        let stdout = "[PULSE] 793398609444 — SAGCO_GCP_PROJECT_NODE  PASS_IMMUNITY\n\
                      STATUS=SAGCO_CORE_PARSE_PASS\n";
        let errs = StateIntegrityVerifier::verify_execution(stdout);
        assert!(errs.is_empty());
    }

    #[test]
    fn parse_seal_target_extracts_filename() {
        let line = "[SEAL] evidence.bin SHA256=deadbeef  EVIDENCE_LOCKED  artifact=evidence.bin.seal";
        let target = StateIntegrityVerifier::parse_seal_target(line);
        assert_eq!(target, Some("evidence.bin"));
    }

    #[test]
    fn multiple_seals_all_checked() {
        let stdout = "[SEAL] a.bin SHA256=aaa  EVIDENCE_LOCKED  artifact=a.bin.seal\n\
                      [SEAL] b.bin SHA256=bbb  EVIDENCE_LOCKED  artifact=b.bin.seal\n\
                      STATUS=SAGCO_CORE_PARSE_PASS\n";
        // neither a.bin.seal nor b.bin.seal exist
        let errs = StateIntegrityVerifier::verify_execution(stdout);
        assert_eq!(errs.len(), 2);
        assert!(errs.iter().all(|e| e.antibody_name() == "MISSING_SEAL_ARTIFACT_ANTIBODY"));
    }
}
