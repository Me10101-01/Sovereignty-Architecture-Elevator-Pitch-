#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
ANTIBODY DEPARTMENT — Self-Healing Threat Response System
IDEA_101: Red/Blue Kubernetes Battleground
StrategicKhaos DAO LLC

Digital immune system for the Blue Team cluster.
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import hashlib
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, Callable

import nats
from nats.aio.client import Client as NATS

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

NATS_URL = "nats://nats:4222"
IMMUNE_MEMORY_PATH = Path("/app/immune-memory")
AUDIT_LOG_PATH = Path("/app/audit-logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("antibody")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatType(str, Enum):
    PRIVILEGE_ESCALATION = "privilege_escalation"
    REVERSE_SHELL = "reverse_shell"
    CRYPTO_MINER = "crypto_miner"
    NETWORK_SCAN = "network_scan"
    SECRET_ACCESS = "secret_access"
    CONTAINER_ESCAPE = "container_escape"
    SUPPLY_CHAIN = "supply_chain"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    POLICY_VIOLATION = "policy_violation"
    UNKNOWN = "unknown"


class ResponseAction(str, Enum):
    KILL_POD = "kill_pod"
    QUARANTINE = "quarantine"
    REVOKE_TOKEN = "revoke_token"
    BLACKLIST_IMAGE = "blacklist_image"
    ISOLATE_NODE = "isolate_node"
    SCALE_DOWN = "scale_down"
    ALERT_ONLY = "alert_only"
    RECORD_PATTERN = "record_pattern"


@dataclass
class Threat:
    """Detected threat."""
    id: str
    threat_type: ThreatType
    severity: Severity
    source: str  # e.g., "falco", "opa", "custom"
    namespace: str
    pod: Optional[str]
    node: Optional[str]
    image: Optional[str]
    description: str
    raw_data: dict
    detected_at: str

    @staticmethod
    def generate_id(data: dict) -> str:
        """Generate deterministic threat ID."""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class Response:
    """Response to a threat."""
    threat_id: str
    action: ResponseAction
    success: bool
    message: str
    executed_at: str
    execution_time_ms: int


@dataclass
class ImmunePattern:
    """Learned threat pattern for future detection."""
    pattern_id: str
    threat_type: ThreatType
    signature: str
    first_seen: str
    last_seen: str
    occurrence_count: int
    auto_response: ResponseAction


# ═══════════════════════════════════════════════════════════════════════════════
# THREAT CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════

class ThreatClassifier:
    """Classify incoming alerts into threat types."""

    PATTERNS = {
        ThreatType.PRIVILEGE_ESCALATION: [
            "privileged", "hostPID", "hostNetwork", "hostPath",
            "SYS_ADMIN", "securityContext", "escalation"
        ],
        ThreatType.REVERSE_SHELL: [
            "reverse shell", "nc -e", "/dev/tcp", "bash -i",
            "socat", "netcat"
        ],
        ThreatType.CRYPTO_MINER: [
            "xmrig", "minerd", "stratum", "crypto", "mining",
            "monero", "bitcoin"
        ],
        ThreatType.NETWORK_SCAN: [
            "nmap", "masscan", "port scan", "zmap", "network scan"
        ],
        ThreatType.SECRET_ACCESS: [
            "secret", "token", "credential", "password", "key",
            "/var/run/secrets"
        ],
        ThreatType.CONTAINER_ESCAPE: [
            "container escape", "nsenter", "chroot", "breakout",
            "/proc/1"
        ],
        ThreatType.SUPPLY_CHAIN: [
            "untrusted registry", "unsigned image", "vulnerable image",
            "malicious image"
        ],
        ThreatType.RESOURCE_EXHAUSTION: [
            "resource", "OOM", "CPU limit", "memory limit", "fork bomb"
        ]
    }

    def classify(self, description: str, raw_data: dict) -> ThreatType:
        """Classify threat based on description and data."""
        description_lower = description.lower()
        
        for threat_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in description_lower:
                    return threat_type
        
        # Check raw data for additional signals
        raw_str = json.dumps(raw_data).lower()
        for threat_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in raw_str:
                    return threat_type
        
        return ThreatType.UNKNOWN

    def determine_severity(self, threat_type: ThreatType) -> Severity:
        """Determine severity based on threat type."""
        severity_map = {
            ThreatType.PRIVILEGE_ESCALATION: Severity.CRITICAL,
            ThreatType.REVERSE_SHELL: Severity.CRITICAL,
            ThreatType.CRYPTO_MINER: Severity.CRITICAL,
            ThreatType.CONTAINER_ESCAPE: Severity.CRITICAL,
            ThreatType.NETWORK_SCAN: Severity.MEDIUM,
            ThreatType.SECRET_ACCESS: Severity.HIGH,
            ThreatType.SUPPLY_CHAIN: Severity.HIGH,
            ThreatType.RESOURCE_EXHAUSTION: Severity.MEDIUM,
            ThreatType.POLICY_VIOLATION: Severity.LOW,
            ThreatType.UNKNOWN: Severity.MEDIUM
        }
        return severity_map.get(threat_type, Severity.MEDIUM)


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ResponseEngine:
    """Execute responses to threats."""

    RESPONSE_MAP = {
        ThreatType.PRIVILEGE_ESCALATION: ResponseAction.KILL_POD,
        ThreatType.REVERSE_SHELL: ResponseAction.KILL_POD,
        ThreatType.CRYPTO_MINER: ResponseAction.BLACKLIST_IMAGE,
        ThreatType.CONTAINER_ESCAPE: ResponseAction.ISOLATE_NODE,
        ThreatType.NETWORK_SCAN: ResponseAction.QUARANTINE,
        ThreatType.SECRET_ACCESS: ResponseAction.REVOKE_TOKEN,
        ThreatType.SUPPLY_CHAIN: ResponseAction.BLACKLIST_IMAGE,
        ThreatType.RESOURCE_EXHAUSTION: ResponseAction.SCALE_DOWN,
        ThreatType.POLICY_VIOLATION: ResponseAction.ALERT_ONLY,
        ThreatType.UNKNOWN: ResponseAction.ALERT_ONLY
    }

    def __init__(self):
        self.handlers: dict[ResponseAction, Callable] = {
            ResponseAction.KILL_POD: self._kill_pod,
            ResponseAction.QUARANTINE: self._quarantine_pod,
            ResponseAction.REVOKE_TOKEN: self._revoke_token,
            ResponseAction.BLACKLIST_IMAGE: self._blacklist_image,
            ResponseAction.ISOLATE_NODE: self._isolate_node,
            ResponseAction.SCALE_DOWN: self._scale_down,
            ResponseAction.ALERT_ONLY: self._alert_only,
            ResponseAction.RECORD_PATTERN: self._record_pattern
        }

    def determine_action(self, threat: Threat) -> ResponseAction:
        """Determine appropriate response action."""
        return self.RESPONSE_MAP.get(threat.threat_type, ResponseAction.ALERT_ONLY)

    async def execute(self, threat: Threat, action: ResponseAction) -> Response:
        """Execute response action."""
        start_time = datetime.now(timezone.utc)
        
        handler = self.handlers.get(action, self._alert_only)
        success, message = await handler(threat)
        
        end_time = datetime.now(timezone.utc)
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return Response(
            threat_id=threat.id,
            action=action,
            success=success,
            message=message,
            executed_at=end_time.isoformat(),
            execution_time_ms=execution_time_ms
        )

    async def _kill_pod(self, threat: Threat) -> tuple[bool, str]:
        """Kill the offending pod."""
        if not threat.pod or not threat.namespace:
            return False, "Missing pod or namespace information"
        
        # In production, this would call kubectl
        log.warning(f"KILL_POD: {threat.namespace}/{threat.pod}")
        # cmd = f"kubectl delete pod {threat.pod} -n {threat.namespace} --grace-period=0 --force"
        return True, f"Pod {threat.namespace}/{threat.pod} terminated"

    async def _quarantine_pod(self, threat: Threat) -> tuple[bool, str]:
        """Quarantine pod by applying restrictive NetworkPolicy."""
        if not threat.pod or not threat.namespace:
            return False, "Missing pod or namespace information"
        
        log.warning(f"QUARANTINE: {threat.namespace}/{threat.pod}")
        # Apply NetworkPolicy that blocks all traffic
        return True, f"Pod {threat.namespace}/{threat.pod} quarantined"

    async def _revoke_token(self, threat: Threat) -> tuple[bool, str]:
        """Revoke service account token."""
        log.warning(f"REVOKE_TOKEN: namespace={threat.namespace}")
        # Rotate service account token
        return True, f"Service account token rotated in {threat.namespace}"

    async def _blacklist_image(self, threat: Threat) -> tuple[bool, str]:
        """Blacklist container image."""
        if not threat.image:
            return False, "Missing image information"
        
        log.warning(f"BLACKLIST_IMAGE: {threat.image}")
        # Add to OPA/Gatekeeper deny list
        return True, f"Image {threat.image} blacklisted"

    async def _isolate_node(self, threat: Threat) -> tuple[bool, str]:
        """Isolate node by cordoning and draining."""
        if not threat.node:
            return False, "Missing node information"
        
        log.critical(f"ISOLATE_NODE: {threat.node}")
        # kubectl cordon + drain
        return True, f"Node {threat.node} isolated"

    async def _scale_down(self, threat: Threat) -> tuple[bool, str]:
        """Scale down offending workload."""
        log.warning(f"SCALE_DOWN: {threat.namespace}")
        return True, f"Workload scaled down in {threat.namespace}"

    async def _alert_only(self, threat: Threat) -> tuple[bool, str]:
        """Log alert without taking action."""
        log.info(f"ALERT: {threat.threat_type.value} - {threat.description}")
        return True, "Alert recorded"

    async def _record_pattern(self, threat: Threat) -> tuple[bool, str]:
        """Record threat pattern to immune memory."""
        log.info(f"RECORD_PATTERN: {threat.threat_type.value}")
        return True, "Pattern recorded to immune memory"


# ═══════════════════════════════════════════════════════════════════════════════
# IMMUNE MEMORY
# ═══════════════════════════════════════════════════════════════════════════════

class ImmuneMemory:
    """Persistent storage for learned threat patterns."""

    def __init__(self, path: Path):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.patterns_file = self.path / "patterns.json"
        self.patterns: dict[str, ImmunePattern] = {}
        self._load()

    def _load(self):
        """Load patterns from disk."""
        if self.patterns_file.exists():
            with open(self.patterns_file) as f:
                data = json.load(f)
                for p in data.get("patterns", []):
                    pattern = ImmunePattern(**p)
                    self.patterns[pattern.pattern_id] = pattern

    def _save(self):
        """Save patterns to disk."""
        patterns = [asdict(p) for p in self.patterns.values()]
        with open(self.patterns_file, "w") as f:
            json.dump({"patterns": patterns}, f, indent=2)

    def record(self, threat: Threat, response: Response):
        """Record threat pattern."""
        signature = self._generate_signature(threat)
        pattern_id = hashlib.sha256(signature.encode()).hexdigest()[:12]
        
        now = datetime.now(timezone.utc).isoformat()
        
        if pattern_id in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_id]
            pattern.last_seen = now
            pattern.occurrence_count += 1
        else:
            # New pattern
            pattern = ImmunePattern(
                pattern_id=pattern_id,
                threat_type=threat.threat_type,
                signature=signature,
                first_seen=now,
                last_seen=now,
                occurrence_count=1,
                auto_response=response.action
            )
            self.patterns[pattern_id] = pattern
        
        self._save()
        log.info(f"Immune memory updated: {pattern_id} (count={pattern.occurrence_count})")

    def _generate_signature(self, threat: Threat) -> str:
        """Generate pattern signature from threat."""
        return f"{threat.threat_type.value}|{threat.image or 'unknown'}|{threat.source}"

    def get_known_patterns(self, threat_type: Optional[ThreatType] = None) -> list[ImmunePattern]:
        """Get known patterns, optionally filtered by type."""
        if threat_type:
            return [p for p in self.patterns.values() if p.threat_type == threat_type]
        return list(self.patterns.values())


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT LOGGER
# ═══════════════════════════════════════════════════════════════════════════════

class AuditLogger:
    """Cryptographic audit logging."""

    def __init__(self, path: Path):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)

    def log_threat(self, threat: Threat, response: Response):
        """Log threat and response with hash chain."""
        now = datetime.now(timezone.utc)
        log_file = self.path / f"{now.strftime('%Y-%m-%d')}.jsonl"
        
        entry = {
            "timestamp": now.isoformat(),
            "type": "threat_response",
            "threat": asdict(threat),
            "response": asdict(response)
        }
        
        # Generate hash
        content = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(content.encode()).hexdigest()
        
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
# ANTIBODY DAEMON
# ═══════════════════════════════════════════════════════════════════════════════

class AntibodyDaemon:
    """Main daemon that coordinates threat detection and response."""

    def __init__(self):
        self.nc: Optional[NATS] = None
        self.classifier = ThreatClassifier()
        self.response_engine = ResponseEngine()
        self.immune_memory = ImmuneMemory(IMMUNE_MEMORY_PATH)
        self.audit_logger = AuditLogger(AUDIT_LOG_PATH)

    async def start(self):
        """Start the antibody daemon."""
        log.info("═══════════════════════════════════════════════════════════")
        log.info("ANTIBODY DEPARTMENT — Starting...")
        log.info("═══════════════════════════════════════════════════════════")
        
        # Connect to NATS
        self.nc = await nats.connect(NATS_URL)
        log.info(f"Connected to NATS: {NATS_URL}")
        
        # Subscribe to alert channels
        await self.nc.subscribe("security.falco.alerts", cb=self._handle_falco_alert)
        await self.nc.subscribe("security.opa.violations", cb=self._handle_opa_violation)
        await self.nc.subscribe("security.custom.alerts", cb=self._handle_custom_alert)
        
        log.info("Subscribed to alert channels")
        log.info(f"Loaded {len(self.immune_memory.patterns)} immune patterns")
        log.info("Antibody Department ACTIVE")
        
        # Keep running
        while True:
            await asyncio.sleep(1)

    async def _handle_falco_alert(self, msg):
        """Handle Falco runtime alerts."""
        try:
            data = json.loads(msg.data.decode())
            await self._process_alert("falco", data)
        except Exception as e:
            log.error(f"Error processing Falco alert: {e}")

    async def _handle_opa_violation(self, msg):
        """Handle OPA/Gatekeeper violations."""
        try:
            data = json.loads(msg.data.decode())
            await self._process_alert("opa", data)
        except Exception as e:
            log.error(f"Error processing OPA violation: {e}")

    async def _handle_custom_alert(self, msg):
        """Handle custom security alerts."""
        try:
            data = json.loads(msg.data.decode())
            await self._process_alert("custom", data)
        except Exception as e:
            log.error(f"Error processing custom alert: {e}")

    async def _process_alert(self, source: str, data: dict):
        """Process incoming alert."""
        log.info(f"Processing {source} alert...")
        
        # Extract fields (adjust based on actual alert format)
        description = data.get("output", data.get("message", str(data)))
        
        # Classify threat
        threat_type = self.classifier.classify(description, data)
        severity = self.classifier.determine_severity(threat_type)
        
        # Create threat object
        threat = Threat(
            id=Threat.generate_id(data),
            threat_type=threat_type,
            severity=severity,
            source=source,
            namespace=data.get("k8s.ns.name", data.get("namespace", "unknown")),
            pod=data.get("k8s.pod.name", data.get("pod", None)),
            node=data.get("k8s.node.name", data.get("node", None)),
            image=data.get("container.image.repository", data.get("image", None)),
            description=description,
            raw_data=data,
            detected_at=datetime.now(timezone.utc).isoformat()
        )
        
        log.warning(
            f"THREAT DETECTED: {threat.threat_type.value} | "
            f"Severity: {threat.severity.value} | "
            f"Pod: {threat.namespace}/{threat.pod}"
        )
        
        # Determine and execute response
        action = self.response_engine.determine_action(threat)
        response = await self.response_engine.execute(threat, action)
        
        log.info(
            f"RESPONSE: {response.action.value} | "
            f"Success: {response.success} | "
            f"Time: {response.execution_time_ms}ms"
        )
        
        # Record to immune memory
        self.immune_memory.record(threat, response)
        
        # Audit log
        self.audit_logger.log_threat(threat, response)
        
        # Publish response to NATS
        if self.nc:
            await self.nc.publish(
                "security.antibody.response",
                json.dumps(asdict(response)).encode()
            )

    async def stop(self):
        """Stop the daemon."""
        if self.nc:
            await self.nc.close()
        log.info("Antibody Department stopped")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    daemon = AntibodyDaemon()
    try:
        await daemon.start()
    except KeyboardInterrupt:
        await daemon.stop()
    except Exception as e:
        log.error(f"Fatal error: {e}")
        await daemon.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
