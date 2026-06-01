// SAGCO-Core cloud_io — raw gcloud CLI bindings, no mock hardcoding
// All functions return structured results; DEPENDENCY_ANTIBODY when gcloud absent.
// License: SSL-1.0 — Strategickhaos DAO LLC

use std::process::Command;

pub const SAGCO_PROJECT: &str = "sagco-oscomputconsciousness";
pub const SAGCO_PROJECT_NUMBER: u64 = 793398609444;

// ── Response type ─────────────────────────────────────────────────────────────

#[derive(Debug)]
pub struct GcpResponse {
    pub exit_code: i32,
    pub stdout:    String,
    pub stderr:    String,
    pub bytes:     usize,
}

impl GcpResponse {
    pub fn is_pass(&self) -> bool {
        self.exit_code == 0 && self.bytes > 0
    }

    pub fn antibody(&self) -> &'static str {
        if self.exit_code != 0 && self.stderr.contains("not in allowlist") {
            "NETWORK_POLICY_ANTIBODY"
        } else if self.exit_code != 0 && self.stderr.contains("not found") {
            "PATH_DISCOVERY_ANTIBODY"
        } else if self.exit_code != 0 {
            "GCLOUD_ERROR_ANTIBODY"
        } else if self.bytes == 0 {
            "EMPTY_RESPONSE_ANTIBODY"
        } else {
            "PASS_IMMUNITY"
        }
    }
}

// ── Availability gate ─────────────────────────────────────────────────────────

pub fn gcloud_available() -> bool {
    Command::new("gcloud").arg("--version").output().is_ok()
}

// ── Raw gcloud executor ───────────────────────────────────────────────────────

fn run_gcloud(args: &[&str]) -> GcpResponse {
    match Command::new("gcloud").args(args).output() {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout).to_string();
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            let bytes  = stdout.len();
            GcpResponse {
                exit_code: output.status.code().unwrap_or(-1),
                stdout,
                stderr,
                bytes,
            }
        }
        Err(e) => GcpResponse {
            exit_code: -1,
            stdout:    String::new(),
            stderr:    format!("DEPENDENCY_ANTIBODY: gcloud not found — {}", e),
            bytes:     0,
        },
    }
}

// ── Named API probes ──────────────────────────────────────────────────────────

pub fn get_active_project() -> GcpResponse {
    run_gcloud(&["config", "get-value", "project"])
}

pub fn describe_project(project: &str) -> GcpResponse {
    run_gcloud(&["projects", "describe", project])
}

pub fn list_enabled_services(project: &str) -> GcpResponse {
    run_gcloud(&["services", "list", "--enabled", &format!("--project={}", project)])
}

pub fn list_service_accounts(project: &str) -> GcpResponse {
    run_gcloud(&["iam", "service-accounts", "list", &format!("--project={}", project)])
}

pub fn list_storage_buckets(project: &str) -> GcpResponse {
    run_gcloud(&["storage", "buckets", "list", &format!("--project={}", project)])
}

pub fn list_cloud_run_services(project: &str) -> GcpResponse {
    run_gcloud(&[
        "run", "services", "list",
        "--platform=managed",
        &format!("--project={}", project),
    ])
}

// ── GCP Reality Pass ──────────────────────────────────────────────────────────
// Runs all probes and returns a structured pass/fail ledger

pub struct GcpRealityPass {
    pub probes: Vec<(String, GcpResponse)>,
}

impl GcpRealityPass {
    pub fn run(project: &str) -> Self {
        let mut pass = GcpRealityPass { probes: Vec::new() };

        if !gcloud_available() {
            pass.probes.push((
                "gcloud_available".to_string(),
                GcpResponse {
                    exit_code: -1,
                    stdout:    String::new(),
                    stderr:    "DEPENDENCY_ANTIBODY: Install gcloud CLI".to_string(),
                    bytes:     0,
                },
            ));
            return pass;
        }

        pass.probes.push(("active_project".to_string(),   get_active_project()));
        pass.probes.push(("project_describe".to_string(),  describe_project(project)));
        pass.probes.push(("services_enabled".to_string(),  list_enabled_services(project)));
        pass.probes.push(("service_accounts".to_string(),  list_service_accounts(project)));
        pass.probes.push(("storage_buckets".to_string(),   list_storage_buckets(project)));
        pass.probes.push(("cloud_run".to_string(),         list_cloud_run_services(project)));
        pass
    }

    pub fn pass_count(&self) -> usize {
        self.probes.iter().filter(|(_, r)| r.is_pass()).count()
    }

    pub fn total(&self) -> usize { self.probes.len() }

    pub fn pass_rate(&self) -> f64 {
        if self.total() == 0 { return 0.0; }
        (self.pass_count() as f64 / self.total() as f64) * 100.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn gcp_response_antibody_empty() {
        let r = GcpResponse { exit_code: 0, stdout: String::new(), stderr: String::new(), bytes: 0 };
        assert_eq!(r.antibody(), "EMPTY_RESPONSE_ANTIBODY");
    }

    #[test]
    fn gcp_response_antibody_pass() {
        let r = GcpResponse {
            exit_code: 0,
            stdout: "sagco-oscomputconsciousness".to_string(),
            stderr: String::new(),
            bytes: 27,
        };
        assert_eq!(r.antibody(), "PASS_IMMUNITY");
        assert!(r.is_pass());
    }

    #[test]
    fn gcp_response_antibody_network_policy() {
        let r = GcpResponse {
            exit_code: 1,
            stdout: String::new(),
            stderr: "Host not in allowlist".to_string(),
            bytes: 0,
        };
        assert_eq!(r.antibody(), "NETWORK_POLICY_ANTIBODY");
    }
}
