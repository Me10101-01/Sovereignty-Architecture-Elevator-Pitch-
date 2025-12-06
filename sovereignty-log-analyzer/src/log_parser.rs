//! GKE Audit Log Parser
//!
//! Parses Kubernetes/GKE Cloud Audit Logs into structured AuditLogEntry structs.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// Represents a parsed GKE audit log entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditLogEntry {
    /// Timestamp of the log entry
    pub timestamp: DateTime<Utc>,
    /// The principal (user or service account) who made the request
    pub principal: String,
    /// The Kubernetes resource being accessed (e.g., pods, configmaps)
    pub resource_type: String,
    /// The operation performed (e.g., create, update, delete)
    pub operation: String,
    /// The namespace where the operation occurred
    pub namespace: String,
    /// The name of the resource
    pub resource_name: String,
    /// The cluster name
    pub cluster: String,
    /// Whether this was a system/automated operation
    pub is_system_operation: bool,
    /// Response status code
    pub status_code: i32,
    /// Raw log data for additional processing
    #[serde(skip_serializing_if = "Option::is_none")]
    pub raw_data: Option<serde_json::Value>,
}

impl AuditLogEntry {
    /// Determines if the operation was initiated by a system component
    pub fn is_automated(&self) -> bool {
        self.is_system_operation
            || self.principal.starts_with("system:")
            || self.principal.contains("serviceaccount")
            || self.principal.contains("controller")
            || self.principal.contains("scheduler")
    }

    /// Determines if this is a mutation operation
    pub fn is_mutation(&self) -> bool {
        matches!(
            self.operation.to_lowercase().as_str(),
            "create" | "update" | "patch" | "delete"
        )
    }

    /// Determines if this is a sensitive namespace operation
    pub fn is_sensitive_namespace(&self) -> bool {
        matches!(
            self.namespace.as_str(),
            "kube-system" | "kube-public" | "kube-node-lease" | "istio-system"
        )
    }
}

/// Parser for GKE audit logs
pub struct LogParser;

impl LogParser {
    /// Parse a JSON string containing audit log entries
    pub fn parse_logs(json_str: &str) -> Result<Vec<AuditLogEntry>, ParseError> {
        // Try parsing as array first
        if let Ok(entries) = serde_json::from_str::<Vec<serde_json::Value>>(json_str) {
            return entries
                .into_iter()
                .map(Self::parse_entry)
                .collect::<Result<Vec<_>, _>>();
        }

        // Try parsing as newline-delimited JSON
        let mut entries = Vec::new();
        for line in json_str.lines() {
            let line = line.trim();
            if line.is_empty() {
                continue;
            }
            if let Ok(value) = serde_json::from_str::<serde_json::Value>(line) {
                entries.push(Self::parse_entry(value)?);
            }
        }

        if entries.is_empty() {
            // Try parsing as single object
            let value: serde_json::Value = serde_json::from_str(json_str)?;
            entries.push(Self::parse_entry(value)?);
        }

        Ok(entries)
    }

    /// Parse a single log entry from JSON value
    fn parse_entry(value: serde_json::Value) -> Result<AuditLogEntry, ParseError> {
        // Extract timestamp
        let timestamp = Self::extract_timestamp(&value)?;

        // Extract principal (user or service account)
        let principal = Self::extract_string(&value, &["protoPayload", "authenticationInfo", "principalEmail"])
            .or_else(|| Self::extract_string(&value, &["user", "username"]))
            .or_else(|| Self::extract_string(&value, &["principal"]))
            .unwrap_or_else(|| "unknown".to_string());

        // Extract resource type
        let resource_type = Self::extract_resource_type(&value);

        // Extract operation
        let operation = Self::extract_string(&value, &["protoPayload", "methodName"])
            .or_else(|| Self::extract_string(&value, &["verb"]))
            .or_else(|| Self::extract_string(&value, &["operation"]))
            .map(|op| Self::normalize_operation(&op))
            .unwrap_or_else(|| "unknown".to_string());

        // Extract namespace
        let namespace = Self::extract_string(&value, &["protoPayload", "resourceName"])
            .and_then(|rn| Self::extract_namespace_from_resource_name(&rn))
            .or_else(|| Self::extract_string(&value, &["objectRef", "namespace"]))
            .or_else(|| Self::extract_string(&value, &["namespace"]))
            .unwrap_or_else(|| "default".to_string());

        // Extract resource name
        let resource_name = Self::extract_string(&value, &["protoPayload", "resourceName"])
            .and_then(|rn| Self::extract_name_from_resource_name(&rn))
            .or_else(|| Self::extract_string(&value, &["objectRef", "name"]))
            .or_else(|| Self::extract_string(&value, &["resource_name"]))
            .unwrap_or_else(|| "unknown".to_string());

        // Extract cluster
        let cluster = Self::extract_string(&value, &["resource", "labels", "cluster_name"])
            .or_else(|| Self::extract_string(&value, &["cluster"]))
            .or_else(|| Self::extract_cluster_from_resource_name(
                Self::extract_string(&value, &["protoPayload", "resourceName"]).as_deref().unwrap_or("")
            ))
            .unwrap_or_else(|| "unknown".to_string());

        // Determine if system operation
        let is_system_operation = principal.starts_with("system:")
            || principal.contains("serviceaccount")
            || principal.contains("controller-manager")
            || principal.contains("scheduler");

        // Extract status code
        let status_code = Self::extract_status_code(&value);

        Ok(AuditLogEntry {
            timestamp,
            principal,
            resource_type,
            operation,
            namespace,
            resource_name,
            cluster,
            is_system_operation,
            status_code,
            raw_data: Some(value),
        })
    }

    fn extract_timestamp(value: &serde_json::Value) -> Result<DateTime<Utc>, ParseError> {
        // Try various timestamp fields
        let ts_str = Self::extract_string(value, &["timestamp"])
            .or_else(|| Self::extract_string(value, &["receiveTimestamp"]))
            .or_else(|| Self::extract_string(value, &["requestReceivedTimestamp"]))
            .or_else(|| Self::extract_string(value, &["stageTimestamp"]));

        if let Some(ts) = ts_str {
            // Try parsing RFC3339
            if let Ok(dt) = DateTime::parse_from_rfc3339(&ts) {
                return Ok(dt.with_timezone(&Utc));
            }
            // Try other common formats
            if let Ok(dt) = chrono::NaiveDateTime::parse_from_str(&ts, "%Y-%m-%dT%H:%M:%S%.fZ") {
                return Ok(dt.and_utc());
            }
        }

        // Default to now if no timestamp found
        Ok(Utc::now())
    }

    fn extract_string(value: &serde_json::Value, path: &[&str]) -> Option<String> {
        let mut current = value;
        for key in path {
            current = current.get(*key)?;
        }
        current.as_str().map(|s| s.to_string())
    }

    fn extract_resource_type(value: &serde_json::Value) -> String {
        // Try protoPayload.resourceName pattern
        if let Some(resource_name) = Self::extract_string(value, &["protoPayload", "resourceName"]) {
            if resource_name.contains("/pods/") {
                return "pods".to_string();
            } else if resource_name.contains("/configmaps/") {
                return "configmaps".to_string();
            } else if resource_name.contains("/leases/") {
                return "leases".to_string();
            } else if resource_name.contains("/secrets/") {
                return "secrets".to_string();
            } else if resource_name.contains("/deployments/") {
                return "deployments".to_string();
            } else if resource_name.contains("/services/") {
                return "services".to_string();
            } else if resource_name.contains("/namespaces/") {
                return "namespaces".to_string();
            }
        }

        // Try objectRef.resource
        if let Some(resource) = Self::extract_string(value, &["objectRef", "resource"]) {
            return resource;
        }

        // Try resource.type
        if let Some(resource) = Self::extract_string(value, &["resource", "type"]) {
            return resource;
        }

        "unknown".to_string()
    }

    fn normalize_operation(method: &str) -> String {
        let method_lower = method.to_lowercase();
        if method_lower.contains("create") {
            "create".to_string()
        } else if method_lower.contains("update") || method_lower.contains("patch") {
            "update".to_string()
        } else if method_lower.contains("delete") {
            "delete".to_string()
        } else if method_lower.contains("get") || method_lower.contains("list") || method_lower.contains("watch") {
            "read".to_string()
        } else {
            method.to_string()
        }
    }

    fn extract_namespace_from_resource_name(resource_name: &str) -> Option<String> {
        // Pattern: .../namespaces/{namespace}/...
        let parts: Vec<&str> = resource_name.split('/').collect();
        for (i, part) in parts.iter().enumerate() {
            if *part == "namespaces" && i + 1 < parts.len() {
                return Some(parts[i + 1].to_string());
            }
        }
        None
    }

    fn extract_name_from_resource_name(resource_name: &str) -> Option<String> {
        // Get the last segment after the resource type
        resource_name.split('/').last().map(|s| s.to_string())
    }

    fn extract_cluster_from_resource_name(resource_name: &str) -> Option<String> {
        // Pattern: .../clusters/{cluster}/...
        let parts: Vec<&str> = resource_name.split('/').collect();
        for (i, part) in parts.iter().enumerate() {
            if *part == "clusters" && i + 1 < parts.len() {
                return Some(parts[i + 1].to_string());
            }
        }
        None
    }

    fn extract_status_code(value: &serde_json::Value) -> i32 {
        // Try protoPayload.status.code
        if let Some(code) = value.pointer("/protoPayload/status/code").and_then(|v| v.as_i64()) {
            return code as i32;
        }
        // Try responseStatus.code
        if let Some(code) = value.pointer("/responseStatus/code").and_then(|v| v.as_i64()) {
            return code as i32;
        }
        // Default to 200 (OK)
        200
    }
}

/// Errors that can occur during log parsing
#[derive(Debug)]
pub enum ParseError {
    JsonError(serde_json::Error),
    InvalidFormat(String),
}

impl From<serde_json::Error> for ParseError {
    fn from(err: serde_json::Error) -> Self {
        ParseError::JsonError(err)
    }
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ParseError::JsonError(e) => write!(f, "JSON parsing error: {}", e),
            ParseError::InvalidFormat(msg) => write!(f, "Invalid log format: {}", msg),
        }
    }
}

impl std::error::Error for ParseError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_gke_audit_log() {
        let log_json = r#"{
            "timestamp": "2024-01-15T10:30:00Z",
            "protoPayload": {
                "authenticationInfo": {
                    "principalEmail": "system:serviceaccount:kube-system:kube-scheduler"
                },
                "methodName": "io.k8s.core.v1.pods.update",
                "resourceName": "projects/test-project/zones/us-central1-a/clusters/red-team/namespaces/kube-system/pods/scheduler-pod"
            },
            "resource": {
                "labels": {
                    "cluster_name": "red-team"
                }
            }
        }"#;

        let entries = LogParser::parse_logs(log_json).unwrap();
        assert_eq!(entries.len(), 1);
        
        let entry = &entries[0];
        assert!(entry.principal.contains("kube-scheduler"));
        assert_eq!(entry.operation, "update");
        assert_eq!(entry.namespace, "kube-system");
        assert_eq!(entry.cluster, "red-team");
        assert!(entry.is_automated());
    }

    #[test]
    fn test_parse_user_operation() {
        let log_json = r#"{
            "timestamp": "2024-01-15T10:30:00Z",
            "protoPayload": {
                "authenticationInfo": {
                    "principalEmail": "user@example.com"
                },
                "methodName": "io.k8s.core.v1.configmaps.create",
                "resourceName": "projects/test/zones/us-central1-a/clusters/jarvis-swarm/namespaces/default/configmaps/my-config"
            }
        }"#;

        let entries = LogParser::parse_logs(log_json).unwrap();
        let entry = &entries[0];
        
        assert_eq!(entry.principal, "user@example.com");
        assert_eq!(entry.operation, "create");
        assert!(!entry.is_automated());
        assert!(entry.is_mutation());
    }

    #[test]
    fn test_is_sensitive_namespace() {
        let entry = AuditLogEntry {
            timestamp: Utc::now(),
            principal: "user@example.com".to_string(),
            resource_type: "configmaps".to_string(),
            operation: "update".to_string(),
            namespace: "kube-system".to_string(),
            resource_name: "test".to_string(),
            cluster: "test-cluster".to_string(),
            is_system_operation: false,
            status_code: 200,
            raw_data: None,
        };

        assert!(entry.is_sensitive_namespace());
        assert!(entry.is_mutation());
    }
}
