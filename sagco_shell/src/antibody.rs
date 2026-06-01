// SAGCO Shell Antibody — error classifier + trajectory
// Maps every shell error signal to: ANTIBODY | TRAJECTORY | RECOVERY
// License: SSL-1.0 — Strategickhaos DAO LLC

#[derive(Debug, PartialEq)]
pub enum Trajectory {
    Stabilized,
    Adaptation,
    Evolution,
    Mutation,
}

pub struct AntibodyResult {
    pub name:       &'static str,
    pub trajectory: Trajectory,
    pub recovery:   &'static str,
}

pub fn classify_error(text: &str) -> AntibodyResult {
    let t = text.to_lowercase();

    if t.contains("no such file or directory") || t.contains("cannot stat") {
        AntibodyResult {
            name:       "PATH_DISCOVERY_ANTIBODY",
            trajectory: Trajectory::Adaptation,
            recovery:   "Quote the filename or verify the path exists",
        }
    } else if t.contains("file not found") || t.contains("not a valid directory or file") {
        AntibodyResult {
            name:       "QUOTE_PATH_ANTIBODY",
            trajectory: Trajectory::Adaptation,
            recovery:   r#"Wrap spaced filename in double quotes: "file name.pdf""#,
        }
    } else if t.contains("command not found") || t.contains("no such file") && t.contains("bin") {
        AntibodyResult {
            name:       "DEPENDENCY_ANTIBODY",
            trajectory: Trajectory::Adaptation,
            recovery:   "Install missing tool: pkg install <tool> or pip install <pkg>",
        }
    } else if t.contains("permission denied") {
        AntibodyResult {
            name:       "PERMISSION_ANTIBODY",
            trajectory: Trajectory::Evolution,
            recovery:   "chmod +x <file> or check file ownership",
        }
    } else if t.contains("borrow") || t.contains("does not live long enough") {
        AntibodyResult {
            name:       "BORROW_CHECKER_ANTIBODY",
            trajectory: Trajectory::Evolution,
            recovery:   "Clone the value or adjust lifetime annotations",
        }
    } else if t.contains("jdk 21") || t.contains("jdk") && t.contains("not be found") {
        AntibodyResult {
            name:       "JDK_GATE_ANTIBODY",
            trajectory: Trajectory::Evolution,
            recovery:   "pkg install openjdk-21; export JAVA_HOME=$PREFIX/lib/jvm/java-21-openjdk",
        }
    } else if t.contains("decompil") && t.contains("not exist") {
        AntibodyResult {
            name:       "PLATFORM_LIMITATION_ANTIBODY",
            trajectory: Trajectory::Evolution,
            recovery:   "pkg install gcc make pkg-config; build Ghidra native decompiler",
        }
    } else if t.contains("is a shell builtin")
        || (["cd", "pwd", "export", "source"].iter().any(|b| t.starts_with(b))
            && t.contains("not found"))
    {
        AntibodyResult {
            name:       "SHELL_BUILTIN_ANTIBODY",
            trajectory: Trajectory::Adaptation,
            recovery:   "cd/pwd are now native builtins in sagco_shell; pipes use sh -c fallback",
        }
    } else if t.contains("context") && t.contains("limit") {
        AntibodyResult {
            name:       "CONTEXT_COLLAPSE_ANTIBODY",
            trajectory: Trajectory::Evolution,
            recovery:   "Run /compact or start a new session; use sagco past to re-seed memory",
        }
    } else if text.is_empty() {
        AntibodyResult {
            name:       "PASS_IMMUNITY",
            trajectory: Trajectory::Stabilized,
            recovery:   "no action needed",
        }
    } else {
        AntibodyResult {
            name:       "UNKNOWN_VARIANCE_ANTIBODY",
            trajectory: Trajectory::Mutation,
            recovery:   "Inspect stderr; add classifier rule to antibody.rs",
        }
    }
}

impl AntibodyResult {
    pub fn trajectory_str(&self) -> &'static str {
        match self.trajectory {
            Trajectory::Stabilized => "stabilized",
            Trajectory::Adaptation => "adaptation",
            Trajectory::Evolution  => "evolution",
            Trajectory::Mutation   => "mutation",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn quote_path_detected() {
        let r = classify_error("file not found: SAGCO Computable Reality Engineering");
        assert_eq!(r.name, "QUOTE_PATH_ANTIBODY");
        assert_eq!(r.trajectory, Trajectory::Adaptation);
    }

    #[test]
    fn dependency_detected() {
        let r = classify_error("bash: exiftool: command not found");
        assert_eq!(r.name, "DEPENDENCY_ANTIBODY");
    }

    #[test]
    fn pass_unknown_variance() {
        let r = classify_error("some totally new error");
        assert_eq!(r.name, "UNKNOWN_VARIANCE_ANTIBODY");
        assert_eq!(r.trajectory, Trajectory::Mutation);
    }
}
