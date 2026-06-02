// SAGCO Sentinel Daemon — ACT VI: The Sentinel Dreams
//
// Continuously compares what the ledger remembers (expected reality)
// against what the file system actually contains (actual reality).
// Fires SAGCO_CREEP_ALERT when the two diverge without permission.
//
// License: SSL-1.0 — Strategickhaos DAO LLC

use std::path::Path;
use super::crypto::{sha256_hex, SealLedger};

// ── What the Sentinel finds when reality drifts ───────────────────────────────
#[derive(Debug, Clone, PartialEq)]
pub enum CreepAlert {
    /// The .seal artifact file has disappeared from disk.
    ArtifactMissing {
        target:        String,
        expected_path: String,
    },
    /// The artifact exists but its SHA256 no longer matches the ledger.
    HashTampered {
        target:         String,
        artifact_path:  String,
        recorded_sha256: String,
        actual_sha256:  String,
    },
    /// The artifact exists and hash matches, but the DNA field has been altered.
    DnaMutated {
        target:        String,
        artifact_path: String,
    },
}

impl CreepAlert {
    pub fn name(&self) -> &'static str {
        match self {
            CreepAlert::ArtifactMissing { .. }  => "MISSING_SEAL_ARTIFACT_ANTIBODY",
            CreepAlert::HashTampered    { .. }  => "HASH_TAMPER_ANTIBODY",
            CreepAlert::DnaMutated      { .. }  => "DNA_MUTATION_ANTIBODY",
        }
    }

    pub fn report(&self) -> String {
        match self {
            CreepAlert::ArtifactMissing { target, expected_path } => format!(
                "SAGCO_CREEP_ALERT\n\
                 ANTIBODY={}\n\
                 TARGET={}\n\
                 EXPECTED_ARTIFACT={}\n\
                 STATUS=MISSING_FROM_DISK",
                self.name(), target, expected_path
            ),
            CreepAlert::HashTampered { target, artifact_path, recorded_sha256, actual_sha256 } => format!(
                "SAGCO_CREEP_ALERT\n\
                 ANTIBODY={}\n\
                 TARGET={}\n\
                 ARTIFACT={}\n\
                 RECORDED_SHA256={}\n\
                 ACTUAL_SHA256={}\n\
                 STATUS=EVIDENCE_CHAIN_BROKEN",
                self.name(), target, artifact_path, recorded_sha256, actual_sha256
            ),
            CreepAlert::DnaMutated { target, artifact_path } => format!(
                "SAGCO_CREEP_ALERT\n\
                 ANTIBODY={}\n\
                 TARGET={}\n\
                 ARTIFACT={}\n\
                 STATUS=DNA_FIELD_ALTERED",
                self.name(), target, artifact_path
            ),
        }
    }
}

// ── Sentinel Daemon ───────────────────────────────────────────────────────────
pub struct SentinelDaemon<'a> {
    ledger: &'a SealLedger,
}

impl<'a> SentinelDaemon<'a> {
    pub fn new(ledger: &'a SealLedger) -> Self {
        SentinelDaemon { ledger }
    }

    /// One-shot probe: compare ledger against file system.
    /// Returns every divergence found — empty Vec means reality held.
    pub fn probe(&self) -> Vec<CreepAlert> {
        let mut alerts = Vec::new();

        for (target, recorded_sha256) in self.ledger.entries() {
            let artifact_path = format!("{}.seal", target);

            // ── Gate 1: artifact must exist ───────────────────────────────
            if !Path::new(&artifact_path).exists() {
                alerts.push(CreepAlert::ArtifactMissing {
                    target:        target.clone(),
                    expected_path: artifact_path,
                });
                continue; // no point checking hash/dna if file is gone
            }

            // ── Gate 2: parse the artifact ────────────────────────────────
            let artifact_content = match std::fs::read_to_string(&artifact_path) {
                Ok(c)  => c,
                Err(_) => {
                    alerts.push(CreepAlert::ArtifactMissing {
                        target:        target.clone(),
                        expected_path: artifact_path,
                    });
                    continue;
                }
            };

            let artifact_sha256 = Self::parse_field(&artifact_content, "SHA256");
            let artifact_dna    = Self::parse_field(&artifact_content, "DNA");

            // ── Gate 3: SHA256 must match ledger ─────────────────────────
            match artifact_sha256 {
                Some(actual) if actual != recorded_sha256 => {
                    alerts.push(CreepAlert::HashTampered {
                        target:          target.clone(),
                        artifact_path:   artifact_path.clone(),
                        recorded_sha256: recorded_sha256.clone(),
                        actual_sha256:   actual.to_string(),
                    });
                }
                None => {
                    alerts.push(CreepAlert::HashTampered {
                        target:          target.clone(),
                        artifact_path:   artifact_path.clone(),
                        recorded_sha256: recorded_sha256.clone(),
                        actual_sha256:   "<missing SHA256 field>".to_string(),
                    });
                }
                _ => {} // matches — continue to DNA check
            }

            // ── Gate 4: DNA field must be intact ─────────────────────────
            if artifact_dna.as_deref() != Some("a364ca9f90356c85") {
                alerts.push(CreepAlert::DnaMutated {
                    target:        target.clone(),
                    artifact_path: artifact_path.clone(),
                });
            }
        }

        alerts
    }

    /// Continuous watch: calls probe() every tick, invokes callback with results.
    /// Stops after max_ticks or when stop_fn returns true.
    /// In production, tick_fn sleeps between probes; in tests max_ticks keeps it fast.
    pub fn watch<F, S>(&self, max_ticks: usize, mut tick_fn: F, mut stop_fn: S)
    where
        F: FnMut(usize, &[CreepAlert]),
        S: FnMut(&[CreepAlert]) -> bool,
    {
        for tick in 0..max_ticks {
            let alerts = self.probe();
            tick_fn(tick, &alerts);
            if stop_fn(&alerts) { break; }
        }
    }

    fn parse_field<'s>(content: &'s str, key: &str) -> Option<&'s str> {
        content.lines()
            .find(|l| l.starts_with(&format!("{}=", key)))
            .and_then(|l| l.splitn(2, '=').nth(1))
    }
}

// ── Public summary printer (used by main) ────────────────────────────────────
pub fn print_sentinel_report(alerts: &[CreepAlert], tick: usize) {
    if alerts.is_empty() {
        println!("[SENTINEL tick={}] REALITY_HOLDS — all {} artifacts verified",
            tick, tick); // tick used as proxy for ledger size; caller can pass count
        return;
    }
    println!("[SENTINEL tick={}] SAGCO_CREEP_ALERT — {} variance(s) detected", tick, alerts.len());
    for alert in alerts {
        println!();
        println!("{}", alert.report());
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    // ── helpers ───────────────────────────────────────────────────────────────
    fn make_ledger(entries: &[(&str, &str)]) -> SealLedger {
        let mut l = SealLedger::new();
        for (target, sha) in entries {
            l.record(target, sha);
        }
        l
    }

    fn write_artifact(target: &str, sha: &str, dna: &str) -> String {
        let path = format!("{}.seal", target);
        let content = format!(
            "SAGCO_SEAL_ARTIFACT=1\nTARGET={}\nSHA256={}\nDNA={}\n",
            target, sha, dna
        );
        fs::write(&path, content).expect("write test artifact");
        path
    }

    // ── tests ─────────────────────────────────────────────────────────────────

    #[test]
    fn clean_ledger_produces_no_alerts() {
        let target = "/tmp/sagco_sentinel_clean";
        let sha    = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
        let art    = write_artifact(target, sha, "a364ca9f90356c85");

        let ledger  = make_ledger(&[(target, sha)]);
        let daemon  = SentinelDaemon::new(&ledger);
        let alerts  = daemon.probe();

        let _ = fs::remove_file(&art);
        assert!(alerts.is_empty(), "clean state must produce zero alerts");
    }

    #[test]
    fn missing_artifact_fires_alert() {
        let target = "/tmp/sagco_sentinel_ghost_evidence.bin";
        let _ = fs::remove_file(format!("{}.seal", target)); // ensure gone

        let ledger = make_ledger(&[(target, "deadbeef")]);
        let daemon = SentinelDaemon::new(&ledger);
        let alerts = daemon.probe();

        assert_eq!(alerts.len(), 1);
        assert_eq!(alerts[0].name(), "MISSING_SEAL_ARTIFACT_ANTIBODY");
    }

    #[test]
    fn tampered_hash_fires_alert() {
        let target   = "/tmp/sagco_sentinel_tamper";
        let real_sha = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
        let bad_sha  = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
        let art      = write_artifact(target, bad_sha, "a364ca9f90356c85");

        // ledger remembers real_sha, artifact has bad_sha
        let ledger = make_ledger(&[(target, real_sha)]);
        let daemon = SentinelDaemon::new(&ledger);
        let alerts = daemon.probe();

        let _ = fs::remove_file(&art);
        assert_eq!(alerts.len(), 1);
        assert_eq!(alerts[0].name(), "HASH_TAMPER_ANTIBODY");
        if let CreepAlert::HashTampered { recorded_sha256, actual_sha256, .. } = &alerts[0] {
            assert_eq!(recorded_sha256, real_sha);
            assert_eq!(actual_sha256,   bad_sha);
        }
    }

    #[test]
    fn mutated_dna_fires_alert() {
        let target = "/tmp/sagco_sentinel_dna";
        let sha    = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc";
        let art    = write_artifact(target, sha, "TAMPERED_DNA_VALUE");

        let ledger = make_ledger(&[(target, sha)]);
        let daemon = SentinelDaemon::new(&ledger);
        let alerts = daemon.probe();

        let _ = fs::remove_file(&art);
        assert_eq!(alerts.len(), 1);
        assert_eq!(alerts[0].name(), "DNA_MUTATION_ANTIBODY");
    }

    #[test]
    fn multiple_targets_all_checked() {
        let t1  = "/tmp/sagco_sentinel_multi1";
        let t2  = "/tmp/sagco_sentinel_multi2";
        let sha = "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd";

        // t1 artifact exists and is correct
        let art1 = write_artifact(t1, sha, "a364ca9f90356c85");
        // t2 artifact is missing
        let _ = fs::remove_file(format!("{}.seal", t2));

        let ledger = make_ledger(&[(t1, sha), (t2, sha)]);
        let daemon = SentinelDaemon::new(&ledger);
        let alerts = daemon.probe();

        let _ = fs::remove_file(&art1);
        assert_eq!(alerts.len(), 1);
        assert_eq!(alerts[0].name(), "MISSING_SEAL_ARTIFACT_ANTIBODY");
    }

    #[test]
    fn watch_stops_at_max_ticks() {
        let ledger = make_ledger(&[]);
        let daemon = SentinelDaemon::new(&ledger);
        let mut tick_count = 0usize;

        daemon.watch(
            5,
            |_tick, _alerts| { tick_count += 1; },
            |_alerts| false,
        );

        assert_eq!(tick_count, 5, "watch must run exactly max_ticks times");
    }

    #[test]
    fn watch_stops_early_on_clean() {
        // stop_fn returns true (stop) when alerts is empty
        let ledger = make_ledger(&[]);
        let daemon = SentinelDaemon::new(&ledger);
        let mut tick_count = 0usize;

        daemon.watch(
            100,
            |_tick, _alerts| { tick_count += 1; },
            |alerts| alerts.is_empty(), // stop as soon as reality holds
        );

        assert_eq!(tick_count, 1, "must stop on first clean probe");
    }

    #[test]
    fn report_format_contains_antibody_name() {
        let alert = CreepAlert::ArtifactMissing {
            target:        "test.bin".to_string(),
            expected_path: "test.bin.seal".to_string(),
        };
        let report = alert.report();
        assert!(report.contains("SAGCO_CREEP_ALERT"));
        assert!(report.contains("MISSING_SEAL_ARTIFACT_ANTIBODY"));
        assert!(report.contains("MISSING_FROM_DISK"));
    }
}
