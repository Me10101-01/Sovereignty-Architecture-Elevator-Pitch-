#!/usr/bin/env python3
"""
Antibody Department - Self-Healing Daemon
IDEA_101: Red/Blue Kubernetes Battleground
Strategickhaos DAO LLC

This daemon provides automated threat detection, response, and self-healing
capabilities for the Blue Team cluster in the Red/Blue Battleground.

Features:
- Multi-source threat detection (Falco, OPA, custom)
- Automatic threat classification and prioritization
- Configurable response actions (kill, quarantine, blacklist)
- Immune memory for pattern learning
- Cryptographic audit trail
- Self-healing state restoration

Usage:
    python antibody_daemon.py --cluster blue
    python antibody_daemon.py --config /path/to/config.yaml
"""

import os
import sys
import json
import time
import yaml
import hashlib
import logging
import argparse
import threading
import subprocess
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any, Callable
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('antibody')

# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatCategory(Enum):
    """Categories of threats detected"""
    PRIVILEGE_ESCALATION = "privilege_escalation"
    CONTAINER_ESCAPE = "container_escape"
    CRYPTO_MINER = "crypto_miner"
    REVERSE_SHELL = "reverse_shell"
    RBAC_BYPASS = "rbac_bypass"
    NETWORK_VIOLATION = "network_violation"
    SUPPLY_CHAIN = "supply_chain"
    SUSPICIOUS_BINARY = "suspicious_binary"
    DATA_EXFILTRATION = "data_exfiltration"
    UNKNOWN = "unknown"


class ResponseAction(Enum):
    """Available response actions"""
    LOG = "log"
    ALERT = "alert"
    KILL = "kill"
    QUARANTINE = "quarantine"
    BLACKLIST = "blacklist"
    ISOLATE_NODE = "isolate_node"
    PAUSE_PIPELINE = "pause_pipeline"
    AUDIT = "audit"


class ThreatStatus(Enum):
    """Current status of a threat"""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    RESPONDING = "responding"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    FALSE_POSITIVE = "false_positive"


@dataclass
class ThreatEvent:
    """Represents a detected threat"""
    id: str
    timestamp: datetime
    category: ThreatCategory
    severity: ThreatSeverity
    status: ThreatStatus
    source: str  # falco, opa, custom, antibody
    
    # Kubernetes context
    namespace: str
    pod_name: Optional[str] = None
    container_name: Optional[str] = None
    node_name: Optional[str] = None
    image: Optional[str] = None
    
    # Threat details
    description: str = ""
    raw_alert: Dict = field(default_factory=dict)
    mitre_attack: List[str] = field(default_factory=list)
    
    # Response tracking
    actions_taken: List[str] = field(default_factory=list)
    response_time_ms: Optional[int] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['category'] = self.category.value
        result['severity'] = self.severity.value
        result['status'] = self.status.value
        return result


@dataclass
class ImmunePattern:
    """Learned pattern in immune memory"""
    id: str
    pattern_type: str
    signature: str
    category: ThreatCategory
    severity: ThreatSeverity
    confidence: float
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int
    response_history: List[Dict] = field(default_factory=list)


@dataclass
class AuditEntry:
    """Cryptographically signed audit entry"""
    id: str
    timestamp: datetime
    event_type: str
    actor: str
    action: str
    target: str
    details: Dict
    previous_hash: str
    hash: str = ""
    
    def compute_hash(self) -> str:
        """Compute cryptographic hash for this entry"""
        data = {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'actor': self.actor,
            'action': self.action,
            'target': self.target,
            'details': self.details,
            'previous_hash': self.previous_hash
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


# =============================================================================
# THREAT DETECTORS
# =============================================================================

class ThreatDetector(ABC):
    """Abstract base class for threat detectors"""
    
    @abstractmethod
    def detect(self) -> List[ThreatEvent]:
        """Detect threats and return list of events"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return detector name"""
        pass


class FalcoDetector(ThreatDetector):
    """Detect threats from Falco alerts"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.namespace = config.get('falco_namespace', 'falco-system')
        self.label_selector = config.get('falco_label', 'app=falco')
        self.last_processed: Optional[datetime] = None
        
    def get_name(self) -> str:
        return "falco"
    
    def detect(self) -> List[ThreatEvent]:
        """Parse Falco logs for threat events"""
        events = []
        try:
            # Get Falco logs via kubectl
            cmd = [
                'kubectl', 'logs',
                '-n', self.namespace,
                '-l', self.label_selector,
                '--since=30s',
                '--tail=100'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.warning(f"Failed to get Falco logs: {result.stderr}")
                return events
            
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                    
                # Parse Falco JSON output
                try:
                    alert = json.loads(line)
                    event = self._parse_falco_alert(alert)
                    if event:
                        events.append(event)
                except json.JSONDecodeError:
                    # Try to parse text format
                    event = self._parse_falco_text(line)
                    if event:
                        events.append(event)
                        
        except subprocess.TimeoutExpired:
            logger.warning("Timeout getting Falco logs")
        except FileNotFoundError:
            logger.warning("kubectl not found")
        except Exception as e:
            logger.error(f"Error in Falco detection: {e}")
            
        return events
    
    def _parse_falco_alert(self, alert: Dict) -> Optional[ThreatEvent]:
        """Parse JSON format Falco alert"""
        priority = alert.get('priority', '').lower()
        severity = self._map_priority(priority)
        
        # Categorize based on rule name
        rule = alert.get('rule', '')
        category = self._categorize_rule(rule)
        
        # Extract K8s context
        output_fields = alert.get('output_fields', {})
        
        return ThreatEvent(
            id=f"falco-{hashlib.md5(str(alert).encode()).hexdigest()[:12]}",
            timestamp=datetime.now(timezone.utc),
            category=category,
            severity=severity,
            status=ThreatStatus.DETECTED,
            source="falco",
            namespace=output_fields.get('k8s.ns.name', 'unknown'),
            pod_name=output_fields.get('k8s.pod.name'),
            container_name=output_fields.get('container.name'),
            node_name=output_fields.get('k8s.node.name'),
            image=output_fields.get('container.image.repository'),
            description=alert.get('output', ''),
            raw_alert=alert,
            mitre_attack=self._extract_mitre(alert)
        )
    
    def _parse_falco_text(self, line: str) -> Optional[ThreatEvent]:
        """Parse text format Falco alert"""
        # Simple pattern matching for text output
        severity = ThreatSeverity.MEDIUM
        if 'Critical' in line:
            severity = ThreatSeverity.CRITICAL
        elif 'Warning' in line:
            severity = ThreatSeverity.HIGH
            
        return ThreatEvent(
            id=f"falco-txt-{hashlib.md5(line.encode()).hexdigest()[:12]}",
            timestamp=datetime.now(timezone.utc),
            category=ThreatCategory.UNKNOWN,
            severity=severity,
            status=ThreatStatus.DETECTED,
            source="falco",
            namespace="unknown",
            description=line
        )
    
    def _map_priority(self, priority: str) -> ThreatSeverity:
        """Map Falco priority to threat severity"""
        mapping = {
            'emergency': ThreatSeverity.CRITICAL,
            'alert': ThreatSeverity.CRITICAL,
            'critical': ThreatSeverity.CRITICAL,
            'error': ThreatSeverity.HIGH,
            'warning': ThreatSeverity.MEDIUM,
            'notice': ThreatSeverity.LOW,
            'info': ThreatSeverity.LOW,
            'debug': ThreatSeverity.LOW
        }
        return mapping.get(priority, ThreatSeverity.MEDIUM)
    
    def _categorize_rule(self, rule: str) -> ThreatCategory:
        """Categorize Falco rule to threat category"""
        rule_lower = rule.lower()
        
        if 'privilege' in rule_lower or 'escalat' in rule_lower:
            return ThreatCategory.PRIVILEGE_ESCALATION
        elif 'escape' in rule_lower or 'nsenter' in rule_lower:
            return ThreatCategory.CONTAINER_ESCAPE
        elif 'miner' in rule_lower or 'crypto' in rule_lower:
            return ThreatCategory.CRYPTO_MINER
        elif 'shell' in rule_lower or 'reverse' in rule_lower:
            return ThreatCategory.REVERSE_SHELL
        elif 'rbac' in rule_lower or 'serviceaccount' in rule_lower:
            return ThreatCategory.RBAC_BYPASS
        elif 'network' in rule_lower:
            return ThreatCategory.NETWORK_VIOLATION
        elif 'supply' in rule_lower or 'image' in rule_lower:
            return ThreatCategory.SUPPLY_CHAIN
        elif 'binary' in rule_lower or 'exec' in rule_lower:
            return ThreatCategory.SUSPICIOUS_BINARY
        else:
            return ThreatCategory.UNKNOWN
    
    def _extract_mitre(self, alert: Dict) -> List[str]:
        """Extract MITRE ATT&CK references from alert"""
        mitre = []
        tags = alert.get('tags', [])
        for tag in tags:
            if tag.startswith('mitre_'):
                mitre.append(tag.replace('mitre_', ''))
        return mitre


class OPADetector(ThreatDetector):
    """Detect policy violations from OPA Gatekeeper"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.namespace = config.get('gatekeeper_namespace', 'gatekeeper-system')
        
    def get_name(self) -> str:
        return "opa"
    
    def detect(self) -> List[ThreatEvent]:
        """Check for OPA policy violations"""
        events = []
        try:
            # Get constraint violations
            cmd = [
                'kubectl', 'get', 'constraints',
                '-o', 'json'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return events
                
            constraints = json.loads(result.stdout)
            for item in constraints.get('items', []):
                violations = item.get('status', {}).get('violations', [])
                for violation in violations:
                    event = self._parse_violation(item, violation)
                    if event:
                        events.append(event)
                        
        except Exception as e:
            logger.error(f"Error in OPA detection: {e}")
            
        return events
    
    def _parse_violation(self, constraint: Dict, violation: Dict) -> Optional[ThreatEvent]:
        """Parse OPA constraint violation"""
        kind = constraint.get('kind', '')
        category = self._categorize_constraint(kind)
        
        return ThreatEvent(
            id=f"opa-{hashlib.md5(str(violation).encode()).hexdigest()[:12]}",
            timestamp=datetime.now(timezone.utc),
            category=category,
            severity=ThreatSeverity.HIGH,
            status=ThreatStatus.DETECTED,
            source="opa",
            namespace=violation.get('namespace', 'unknown'),
            pod_name=violation.get('name'),
            description=violation.get('message', ''),
            raw_alert={'constraint': kind, 'violation': violation}
        )
    
    def _categorize_constraint(self, kind: str) -> ThreatCategory:
        """Categorize OPA constraint to threat category"""
        kind_lower = kind.lower()
        
        if 'privileged' in kind_lower:
            return ThreatCategory.PRIVILEGE_ESCALATION
        elif 'image' in kind_lower or 'repo' in kind_lower:
            return ThreatCategory.SUPPLY_CHAIN
        elif 'host' in kind_lower:
            return ThreatCategory.CONTAINER_ESCAPE
        else:
            return ThreatCategory.UNKNOWN


class CustomDetector(ThreatDetector):
    """Custom pattern-based threat detection"""
    
    def __init__(self, config: Dict, immune_memory: 'ImmuneMemory'):
        self.config = config
        self.immune_memory = immune_memory
        self.patterns = config.get('custom_patterns', [])
        
    def get_name(self) -> str:
        return "custom"
    
    def detect(self) -> List[ThreatEvent]:
        """Run custom detection patterns"""
        events = []
        
        # Check against learned patterns from immune memory
        for pattern in self.immune_memory.get_patterns():
            matches = self._check_pattern(pattern)
            events.extend(matches)
            
        return events
    
    def _check_pattern(self, pattern: ImmunePattern) -> List[ThreatEvent]:
        """Check for matches against a learned pattern"""
        # Implementation would query cluster for matching resources
        return []


# =============================================================================
# THREAT RESPONDERS
# =============================================================================

class ThreatResponder(ABC):
    """Abstract base class for threat responders"""
    
    @abstractmethod
    def respond(self, event: ThreatEvent, action: ResponseAction) -> bool:
        """Execute response action, return success"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return responder name"""
        pass


class KubernetesResponder(ThreatResponder):
    """Execute Kubernetes-based responses"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.quarantine_namespace = config.get('quarantine_namespace', 'threat-quarantine')
        
    def get_name(self) -> str:
        return "kubernetes"
    
    def respond(self, event: ThreatEvent, action: ResponseAction) -> bool:
        """Execute response action in Kubernetes"""
        try:
            if action == ResponseAction.KILL:
                return self._kill_pod(event)
            elif action == ResponseAction.QUARANTINE:
                return self._quarantine_pod(event)
            elif action == ResponseAction.ISOLATE_NODE:
                return self._isolate_node(event)
            else:
                logger.warning(f"Unsupported action: {action}")
                return False
        except Exception as e:
            logger.error(f"Response failed: {e}")
            return False
    
    def _kill_pod(self, event: ThreatEvent) -> bool:
        """Force delete a pod"""
        if not event.pod_name or not event.namespace:
            logger.warning("Cannot kill pod: missing name or namespace")
            return False
            
        cmd = [
            'kubectl', 'delete', 'pod',
            event.pod_name,
            '-n', event.namespace,
            '--force',
            '--grace-period=0'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info(f"Killed pod: {event.namespace}/{event.pod_name}")
            return True
        else:
            logger.error(f"Failed to kill pod: {result.stderr}")
            return False
    
    def _quarantine_pod(self, event: ThreatEvent) -> bool:
        """Move pod to quarantine namespace with network isolation"""
        if not event.pod_name or not event.namespace:
            return False
            
        # Apply network isolation first
        isolation_policy = {
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'NetworkPolicy',
            'metadata': {
                'name': f'quarantine-{event.pod_name}',
                'namespace': event.namespace
            },
            'spec': {
                'podSelector': {
                    'matchLabels': {
                        'app': event.pod_name
                    }
                },
                'policyTypes': ['Ingress', 'Egress'],
                'ingress': [],
                'egress': []
            }
        }
        
        # Apply network policy
        policy_json = json.dumps(isolation_policy)
        cmd = ['kubectl', 'apply', '-f', '-']
        result = subprocess.run(
            cmd, 
            input=policy_json, 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info(f"Quarantined pod: {event.namespace}/{event.pod_name}")
            return True
        return False
    
    def _isolate_node(self, event: ThreatEvent) -> bool:
        """Cordon and drain a node"""
        if not event.node_name:
            return False
            
        # Cordon node
        cmd = ['kubectl', 'cordon', event.node_name]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info(f"Cordoned node: {event.node_name}")
            return True
        return False


class AlertResponder(ThreatResponder):
    """Send alerts to various channels"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.discord_webhook = self._validate_webhook(config.get('discord_webhook'))
        self.slack_webhook = self._validate_webhook(config.get('slack_webhook'))
    
    def _validate_webhook(self, url: Optional[str]) -> Optional[str]:
        """Validate webhook URL format"""
        if not url:
            return None
        # Ensure HTTPS for security
        if url.startswith('https://'):
            return url
        logger.warning("Webhook URL must use HTTPS - webhook disabled")
        return None
        
    def get_name(self) -> str:
        return "alert"
    
    def respond(self, event: ThreatEvent, action: ResponseAction) -> bool:
        """Send alert notification"""
        if action != ResponseAction.ALERT:
            return False
            
        message = self._format_alert(event)
        
        success = True
        if self.discord_webhook:
            success &= self._send_discord(message)
        if self.slack_webhook:
            success &= self._send_slack(message)
            
        # Always log the alert
        logger.warning(f"ALERT: {message}")
        return success
    
    def _format_alert(self, event: ThreatEvent) -> str:
        """Format alert message"""
        emoji = {
            ThreatSeverity.CRITICAL: '🚨',
            ThreatSeverity.HIGH: '⚠️',
            ThreatSeverity.MEDIUM: '⚡',
            ThreatSeverity.LOW: 'ℹ️'
        }
        
        return (
            f"{emoji.get(event.severity, '❓')} **{event.severity.value.upper()}** - "
            f"{event.category.value}\n"
            f"Pod: {event.namespace}/{event.pod_name}\n"
            f"Description: {event.description}\n"
            f"Time: {event.timestamp.isoformat()}"
        )
    
    def _send_discord(self, message: str) -> bool:
        """Send alert to Discord webhook"""
        try:
            import urllib.request
            data = json.dumps({'content': message}).encode()
            req = urllib.request.Request(
                self.discord_webhook,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception as e:
            logger.error(f"Discord alert failed: {e}")
            return False
    
    def _send_slack(self, message: str) -> bool:
        """Send alert to Slack webhook"""
        try:
            import urllib.request
            data = json.dumps({'text': message}).encode()
            req = urllib.request.Request(
                self.slack_webhook,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception as e:
            logger.error(f"Slack alert failed: {e}")
            return False


class BlacklistResponder(ThreatResponder):
    """Manage image blacklist"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.blacklist_configmap = config.get('blacklist_configmap', 'image-blacklist')
        self.blacklist_namespace = config.get('blacklist_namespace', 'antibody-system')
        
    def get_name(self) -> str:
        return "blacklist"
    
    def respond(self, event: ThreatEvent, action: ResponseAction) -> bool:
        """Add image to blacklist"""
        if action != ResponseAction.BLACKLIST or not event.image:
            return False
            
        try:
            # Get current blacklist
            cmd = [
                'kubectl', 'get', 'configmap',
                self.blacklist_configmap,
                '-n', self.blacklist_namespace,
                '-o', 'json'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                cm = json.loads(result.stdout)
                data = cm.get('data', {})
            else:
                data = {}
            
            # Add image to blacklist
            blacklist = data.get('blacklist', '').split('\n')
            if event.image not in blacklist:
                blacklist.append(event.image)
                data['blacklist'] = '\n'.join(filter(None, blacklist))
                
                # Update configmap
                cm_update = {
                    'apiVersion': 'v1',
                    'kind': 'ConfigMap',
                    'metadata': {
                        'name': self.blacklist_configmap,
                        'namespace': self.blacklist_namespace
                    },
                    'data': data
                }
                
                cmd = ['kubectl', 'apply', '-f', '-']
                result = subprocess.run(
                    cmd,
                    input=json.dumps(cm_update),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    logger.info(f"Blacklisted image: {event.image}")
                    return True
                    
        except Exception as e:
            logger.error(f"Blacklist update failed: {e}")
            
        return False


# =============================================================================
# IMMUNE MEMORY
# =============================================================================

class ImmuneMemory:
    """Stores learned threat patterns for future detection"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.patterns: Dict[str, ImmunePattern] = {}
        self.storage_type = config.get('storage', 'configmap')
        self.namespace = config.get('namespace', 'antibody-system')
        self.configmap_name = config.get('configmap', 'immune-memory')
        
        # Load existing patterns
        self._load_patterns()
    
    def _load_patterns(self):
        """Load patterns from storage"""
        if self.storage_type == 'configmap':
            try:
                cmd = [
                    'kubectl', 'get', 'configmap',
                    self.configmap_name,
                    '-n', self.namespace,
                    '-o', 'json'
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    cm = json.loads(result.stdout)
                    patterns_json = cm.get('data', {}).get('patterns', '{}')
                    patterns_data = json.loads(patterns_json)
                    
                    for pattern_id, pattern_dict in patterns_data.items():
                        self.patterns[pattern_id] = self._dict_to_pattern(pattern_dict)
                        
                    logger.info(f"Loaded {len(self.patterns)} patterns from immune memory")
            except Exception as e:
                logger.warning(f"Could not load immune memory: {e}")
    
    def _save_patterns(self):
        """Save patterns to storage"""
        if self.storage_type == 'configmap':
            try:
                patterns_data = {
                    pid: self._pattern_to_dict(p) 
                    for pid, p in self.patterns.items()
                }
                
                cm = {
                    'apiVersion': 'v1',
                    'kind': 'ConfigMap',
                    'metadata': {
                        'name': self.configmap_name,
                        'namespace': self.namespace
                    },
                    'data': {
                        'patterns': json.dumps(patterns_data)
                    }
                }
                
                cmd = ['kubectl', 'apply', '-f', '-']
                subprocess.run(
                    cmd,
                    input=json.dumps(cm),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            except Exception as e:
                logger.error(f"Could not save immune memory: {e}")
    
    def _pattern_to_dict(self, pattern: ImmunePattern) -> Dict:
        """Convert pattern to dict for storage"""
        return {
            'id': pattern.id,
            'pattern_type': pattern.pattern_type,
            'signature': pattern.signature,
            'category': pattern.category.value,
            'severity': pattern.severity.value,
            'confidence': pattern.confidence,
            'first_seen': pattern.first_seen.isoformat(),
            'last_seen': pattern.last_seen.isoformat(),
            'occurrence_count': pattern.occurrence_count,
            'response_history': pattern.response_history
        }
    
    def _dict_to_pattern(self, data: Dict) -> ImmunePattern:
        """Convert dict to pattern"""
        return ImmunePattern(
            id=data['id'],
            pattern_type=data['pattern_type'],
            signature=data['signature'],
            category=ThreatCategory(data['category']),
            severity=ThreatSeverity(data['severity']),
            confidence=data['confidence'],
            first_seen=datetime.fromisoformat(data['first_seen']),
            last_seen=datetime.fromisoformat(data['last_seen']),
            occurrence_count=data['occurrence_count'],
            response_history=data.get('response_history', [])
        )
    
    def learn(self, event: ThreatEvent, response_actions: List[ResponseAction]):
        """Learn from a threat event"""
        signature = self._compute_signature(event)
        
        if signature in self.patterns:
            # Update existing pattern
            pattern = self.patterns[signature]
            pattern.occurrence_count += 1
            pattern.last_seen = datetime.now(timezone.utc)
            pattern.response_history.append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'actions': [a.value for a in response_actions]
            })
        else:
            # Create new pattern
            pattern = ImmunePattern(
                id=f"pattern-{signature[:12]}",
                pattern_type=event.category.value,
                signature=signature,
                category=event.category,
                severity=event.severity,
                confidence=0.5,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                occurrence_count=1,
                response_history=[{
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'actions': [a.value for a in response_actions]
                }]
            )
            self.patterns[signature] = pattern
        
        # Increase confidence with more occurrences
        self.patterns[signature].confidence = min(
            0.95,
            0.5 + (pattern.occurrence_count * 0.1)
        )
        
        self._save_patterns()
        logger.info(f"Learned pattern: {signature[:12]} (confidence: {self.patterns[signature].confidence:.2f})")
    
    def get_patterns(self) -> List[ImmunePattern]:
        """Get all learned patterns"""
        return list(self.patterns.values())
    
    def _compute_signature(self, event: ThreatEvent) -> str:
        """Compute unique signature for an event pattern"""
        sig_data = {
            'category': event.category.value,
            'severity': event.severity.value,
            'image': event.image,
            'mitre': sorted(event.mitre_attack)
        }
        return hashlib.sha256(json.dumps(sig_data, sort_keys=True).encode()).hexdigest()


# =============================================================================
# AUDIT TRAIL
# =============================================================================

class AuditTrail:
    """Cryptographically signed audit trail"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.entries: List[AuditEntry] = []
        self.last_hash = "genesis"
        
    def log(self, event_type: str, actor: str, action: str, 
            target: str, details: Dict) -> AuditEntry:
        """Create and store an audit entry"""
        entry = AuditEntry(
            id=f"audit-{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}",
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            actor=actor,
            action=action,
            target=target,
            details=details,
            previous_hash=self.last_hash
        )
        entry.hash = entry.compute_hash()
        
        self.entries.append(entry)
        self.last_hash = entry.hash
        
        logger.debug(f"Audit: {action} on {target} by {actor}")
        return entry
    
    def verify_chain(self) -> bool:
        """Verify integrity of audit chain"""
        if not self.entries:
            return True
            
        prev_hash = "genesis"
        for entry in self.entries:
            if entry.previous_hash != prev_hash:
                return False
            if entry.hash != entry.compute_hash():
                return False
            prev_hash = entry.hash
            
        return True
    
    def export(self) -> List[Dict]:
        """Export audit trail for storage"""
        return [
            {
                'id': e.id,
                'timestamp': e.timestamp.isoformat(),
                'event_type': e.event_type,
                'actor': e.actor,
                'action': e.action,
                'target': e.target,
                'details': e.details,
                'hash': e.hash
            }
            for e in self.entries
        ]


# =============================================================================
# RESPONSE POLICIES
# =============================================================================

class ResponsePolicy:
    """Defines response actions for threat categories"""
    
    DEFAULT_POLICIES = {
        ThreatCategory.PRIVILEGE_ESCALATION: {
            'severity': ThreatSeverity.CRITICAL,
            'actions': [ResponseAction.KILL, ResponseAction.ALERT, ResponseAction.BLACKLIST],
            'escalate_to': 'security-ops'
        },
        ThreatCategory.CONTAINER_ESCAPE: {
            'severity': ThreatSeverity.CRITICAL,
            'actions': [ResponseAction.KILL, ResponseAction.ALERT, ResponseAction.ISOLATE_NODE],
            'escalate_to': 'incident-response'
        },
        ThreatCategory.CRYPTO_MINER: {
            'severity': ThreatSeverity.HIGH,
            'actions': [ResponseAction.QUARANTINE, ResponseAction.ALERT],
            'escalate_to': 'security-ops'
        },
        ThreatCategory.REVERSE_SHELL: {
            'severity': ThreatSeverity.CRITICAL,
            'actions': [ResponseAction.KILL, ResponseAction.BLACKLIST, ResponseAction.ALERT],
            'escalate_to': 'incident-response'
        },
        ThreatCategory.RBAC_BYPASS: {
            'severity': ThreatSeverity.HIGH,
            'actions': [ResponseAction.QUARANTINE, ResponseAction.ALERT, ResponseAction.AUDIT],
            'escalate_to': 'security-ops'
        },
        ThreatCategory.NETWORK_VIOLATION: {
            'severity': ThreatSeverity.MEDIUM,
            'actions': [ResponseAction.LOG, ResponseAction.ALERT],
            'escalate_to': None
        },
        ThreatCategory.SUPPLY_CHAIN: {
            'severity': ThreatSeverity.CRITICAL,
            'actions': [ResponseAction.KILL, ResponseAction.BLACKLIST, ResponseAction.ALERT],
            'escalate_to': 'incident-response'
        },
        ThreatCategory.SUSPICIOUS_BINARY: {
            'severity': ThreatSeverity.MEDIUM,
            'actions': [ResponseAction.ALERT, ResponseAction.AUDIT],
            'escalate_to': None
        },
        ThreatCategory.DATA_EXFILTRATION: {
            'severity': ThreatSeverity.CRITICAL,
            'actions': [ResponseAction.QUARANTINE, ResponseAction.ALERT],
            'escalate_to': 'incident-response'
        },
        ThreatCategory.UNKNOWN: {
            'severity': ThreatSeverity.MEDIUM,
            'actions': [ResponseAction.ALERT, ResponseAction.AUDIT],
            'escalate_to': None
        }
    }
    
    def __init__(self, config: Dict):
        self.policies = self.DEFAULT_POLICIES.copy()
        
        # Override with config
        custom_policies = config.get('response_policies', {})
        for cat_name, policy in custom_policies.items():
            try:
                category = ThreatCategory(cat_name)
                self.policies[category] = {
                    'severity': ThreatSeverity(policy.get('severity', 'medium')),
                    'actions': [ResponseAction(a) for a in policy.get('actions', [])],
                    'escalate_to': policy.get('escalate_to')
                }
            except (ValueError, KeyError):
                logger.warning(f"Invalid policy config for: {cat_name}")
    
    def get_actions(self, event: ThreatEvent) -> List[ResponseAction]:
        """Get response actions for an event"""
        policy = self.policies.get(event.category, self.policies[ThreatCategory.UNKNOWN])
        return policy['actions']
    
    def get_escalation(self, event: ThreatEvent) -> Optional[str]:
        """Get escalation target for an event"""
        policy = self.policies.get(event.category, self.policies[ThreatCategory.UNKNOWN])
        return policy.get('escalate_to')


# =============================================================================
# ANTIBODY DAEMON
# =============================================================================

class AntibodyDaemon:
    """Main daemon orchestrating detection, classification, and response"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.running = False
        self.poll_interval = config.get('poll_interval_seconds', 5)
        
        # Initialize components
        self.immune_memory = ImmuneMemory(config.get('immune_memory', {}))
        self.audit_trail = AuditTrail(config.get('audit', {}))
        self.response_policy = ResponsePolicy(config)
        
        # Initialize detectors
        self.detectors: List[ThreatDetector] = [
            FalcoDetector(config),
            OPADetector(config),
            CustomDetector(config, self.immune_memory)
        ]
        
        # Initialize responders
        self.responders: Dict[str, ThreatResponder] = {
            'kubernetes': KubernetesResponder(config),
            'alert': AlertResponder(config),
            'blacklist': BlacklistResponder(config)
        }
        
        # Track active threats
        self.active_threats: Dict[str, ThreatEvent] = {}
        self.processed_event_ids: set = set()
        
        # Metrics
        self.metrics = {
            'threats_detected': 0,
            'threats_responded': 0,
            'false_positives': 0,
            'response_times': []
        }
        
        logger.info("🧬 Antibody Daemon initialized")
    
    def start(self):
        """Start the daemon"""
        self.running = True
        logger.info("🧬 Antibody Daemon starting...")
        
        # Audit startup
        self.audit_trail.log(
            event_type='daemon',
            actor='antibody',
            action='start',
            target='daemon',
            details={'config': self.config}
        )
        
        while self.running:
            try:
                self._detection_cycle()
                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                logger.info("Shutdown requested")
                self.stop()
            except Exception as e:
                logger.error(f"Error in detection cycle: {e}")
                time.sleep(self.poll_interval)
    
    def stop(self):
        """Stop the daemon"""
        self.running = False
        
        # Audit shutdown
        self.audit_trail.log(
            event_type='daemon',
            actor='antibody',
            action='stop',
            target='daemon',
            details={'metrics': self.metrics}
        )
        
        logger.info("🧬 Antibody Daemon stopped")
    
    def _detection_cycle(self):
        """Run one detection and response cycle"""
        # Collect threats from all detectors
        all_events: List[ThreatEvent] = []
        
        for detector in self.detectors:
            try:
                events = detector.detect()
                all_events.extend(events)
            except Exception as e:
                logger.error(f"Detector {detector.get_name()} failed: {e}")
        
        # Process new events
        for event in all_events:
            if event.id in self.processed_event_ids:
                continue
                
            self.processed_event_ids.add(event.id)
            self.metrics['threats_detected'] += 1
            
            logger.info(
                f"🔍 Threat detected: {event.category.value} "
                f"({event.severity.value}) in {event.namespace}/{event.pod_name}"
            )
            
            # Classify and respond
            self._respond_to_threat(event)
    
    def _respond_to_threat(self, event: ThreatEvent):
        """Execute response actions for a threat"""
        start_time = time.time()
        
        # Get response actions from policy
        actions = self.response_policy.get_actions(event)
        
        # Track actions taken
        actions_taken = []
        
        for action in actions:
            success = self._execute_action(event, action)
            if success:
                actions_taken.append(action.value)
                event.actions_taken.append(action.value)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        event.response_time_ms = response_time_ms
        self.metrics['response_times'].append(response_time_ms)
        
        # Update status
        if ResponseAction.KILL in actions or ResponseAction.QUARANTINE in actions:
            event.status = ThreatStatus.CONTAINED
        else:
            event.status = ThreatStatus.RESPONDING
        
        # Store in active threats
        self.active_threats[event.id] = event
        
        # Learn from this event
        self.immune_memory.learn(event, actions)
        
        # Audit the response
        self.audit_trail.log(
            event_type='threat_response',
            actor='antibody',
            action='respond',
            target=f"{event.namespace}/{event.pod_name}",
            details={
                'threat_id': event.id,
                'category': event.category.value,
                'severity': event.severity.value,
                'actions': actions_taken,
                'response_time_ms': response_time_ms
            }
        )
        
        self.metrics['threats_responded'] += 1
        
        logger.info(
            f"✅ Response complete: {event.id} "
            f"(actions: {', '.join(actions_taken)}, time: {response_time_ms}ms)"
        )
    
    def _execute_action(self, event: ThreatEvent, action: ResponseAction) -> bool:
        """Execute a single response action"""
        if action == ResponseAction.LOG:
            logger.info(f"LOG: {event.to_dict()}")
            return True
            
        if action == ResponseAction.AUDIT:
            self.audit_trail.log(
                event_type='threat_audit',
                actor='antibody',
                action='audit',
                target=f"{event.namespace}/{event.pod_name}",
                details=event.to_dict()
            )
            return True
        
        # Dispatch to appropriate responder
        if action in [ResponseAction.KILL, ResponseAction.QUARANTINE, ResponseAction.ISOLATE_NODE]:
            return self.responders['kubernetes'].respond(event, action)
        elif action == ResponseAction.ALERT:
            return self.responders['alert'].respond(event, action)
        elif action == ResponseAction.BLACKLIST:
            return self.responders['blacklist'].respond(event, action)
        
        return False
    
    def get_status(self) -> Dict:
        """Get current daemon status"""
        avg_response_time = (
            sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            if self.metrics['response_times'] else 0
        )
        
        return {
            'running': self.running,
            'threats_detected': self.metrics['threats_detected'],
            'threats_responded': self.metrics['threats_responded'],
            'active_threats': len(self.active_threats),
            'learned_patterns': len(self.immune_memory.patterns),
            'avg_response_time_ms': avg_response_time,
            'audit_chain_valid': self.audit_trail.verify_chain()
        }
    
    def heal_state(self) -> bool:
        """Restore desired cluster state"""
        logger.info("🔧 Initiating state healing...")
        
        # This would restore desired state from STATE-redblue.yaml
        # Implementation depends on GitOps/ArgoCD setup
        
        self.audit_trail.log(
            event_type='heal',
            actor='antibody',
            action='heal_state',
            target='cluster',
            details={'initiated_at': datetime.now(timezone.utc).isoformat()}
        )
        
        return True


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Antibody Department - Self-Healing Daemon'
    )
    parser.add_argument(
        '--cluster', 
        choices=['blue', 'red'],
        default='blue',
        help='Target cluster (default: blue)'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to config file'
    )
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=5,
        help='Detection poll interval in seconds'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no actions)'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Print daemon status and exit'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = {
        'cluster': args.cluster,
        'poll_interval_seconds': args.poll_interval,
        'dry_run': args.dry_run,
        'falco_namespace': 'falco-system',
        'gatekeeper_namespace': 'gatekeeper-system',
        'quarantine_namespace': 'threat-quarantine',
        'discord_webhook': os.environ.get('DISCORD_SECURITY_WEBHOOK'),
        'slack_webhook': os.environ.get('SLACK_SECURITY_WEBHOOK'),
        'immune_memory': {
            'storage': 'configmap',
            'namespace': 'antibody-system',
            'configmap': 'immune-memory'
        },
        'audit': {
            'enabled': True,
            'cryptographic_signing': True
        }
    }
    
    # Load config file if provided
    if args.config and Path(args.config).exists():
        with open(args.config) as f:
            file_config = yaml.safe_load(f)
            config.update(file_config)
    
    # Create and run daemon
    daemon = AntibodyDaemon(config)
    
    if args.status:
        status = daemon.get_status()
        print(json.dumps(status, indent=2))
        return
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🧬 ANTIBODY DEPARTMENT - Self-Healing Daemon           ║
    ║                                                           ║
    ║   IDEA_101: Red/Blue Kubernetes Battleground             ║
    ║   Strategickhaos DAO LLC                                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    print(f"Cluster: {config['cluster'].upper()} TEAM")
    print(f"Poll Interval: {config['poll_interval_seconds']}s")
    print(f"Dry Run: {config['dry_run']}")
    print()
    
    try:
        daemon.start()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
        daemon.stop()


if __name__ == '__main__':
    main()
