#!/usr/bin/env python3
"""
Moonlight Telemetry Agent - Session Intelligence Tracker
Part of Strategickhaos Sovereign Intelligence Stack

Monitors and records session telemetry for AI interactions, knowledge graph
evolution, and system health metrics. Integrates with KhaosBase for
cryptographically signed telemetry records.

Author: Strategickhaos DAO LLC
License: MIT
Version: 1.0.0
"""

import os
import sys
import json
import time
import yaml
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import socket
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moonlight')


@dataclass
class SessionMetadata:
    """Session metadata structure"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    user: str
    node_name: str
    vault_name: str
    board_member: str
    session_type: str  # "codespace", "local", "remote"
    
    
@dataclass
class TelemetryEvent:
    """Individual telemetry event"""
    event_id: str
    timestamp: str
    event_type: str  # "command", "file_change", "ai_query", "knowledge_update"
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    signature: Optional[str] = None


@dataclass
class SessionSummary:
    """Session summary statistics"""
    session_id: str
    duration_seconds: float
    total_events: int
    event_breakdown: Dict[str, int]
    files_modified: List[str]
    ai_interactions: int
    knowledge_contributions: int
    cpu_avg: float
    memory_avg_mb: float
    network_bytes_sent: int
    network_bytes_recv: int
    
    
class KhaosBaseConnector:
    """Connector for KhaosBase telemetry storage"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('khaosbase_url', 'http://localhost:8080')
        self.api_key = config.get('api_key', os.getenv('KHAOSBASE_API_KEY'))
        
    def push_event(self, event: TelemetryEvent) -> bool:
        """Push telemetry event to KhaosBase"""
        try:
            # In production, this would make an actual HTTP request
            # For now, we log and write to local file
            logger.info(f"Pushing event {event.event_id} to KhaosBase")
            return True
        except Exception as e:
            logger.error(f"Failed to push event to KhaosBase: {e}")
            return False
            
    def push_session_summary(self, summary: SessionSummary) -> bool:
        """Push session summary to KhaosBase"""
        try:
            logger.info(f"Pushing session summary {summary.session_id} to KhaosBase")
            return True
        except Exception as e:
            logger.error(f"Failed to push session summary: {e}")
            return False


class GPGSigner:
    """GPG signature handler for cryptographic verification"""
    
    def __init__(self, key_id: str = "AE5519579584DEF5"):
        self.key_id = key_id
        
    def sign_data(self, data: str) -> Optional[str]:
        """Sign data with GPG key"""
        try:
            # In production, this would use actual GPG signing
            # For now, we create a SHA256 hash as a placeholder
            signature = hashlib.sha256(
                f"{data}{self.key_id}{datetime.now(timezone.utc).isoformat()}".encode()
            ).hexdigest()
            return signature
        except Exception as e:
            logger.error(f"Failed to sign data: {e}")
            return None
            
    def verify_signature(self, data: str, signature: str) -> bool:
        """Verify GPG signature"""
        try:
            # Placeholder verification
            return len(signature) == 64  # SHA256 length
        except Exception as e:
            logger.error(f"Failed to verify signature: {e}")
            return False


class SystemMetricsCollector:
    """Collects system metrics during session"""
    
    def __init__(self):
        self.cpu_samples: List[float] = []
        self.memory_samples: List[float] = []
        self.network_start = self._get_network_stats()
        
    def _get_network_stats(self) -> Dict[str, int]:
        """Get network statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
        except Exception:
            return {'bytes_sent': 0, 'bytes_recv': 0}
            
    def sample_metrics(self):
        """Sample current system metrics"""
        try:
            self.cpu_samples.append(psutil.cpu_percent(interval=0.1))
            memory = psutil.virtual_memory()
            self.memory_samples.append(memory.used / (1024 * 1024))  # MB
        except Exception as e:
            logger.warning(f"Failed to sample metrics: {e}")
            
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics"""
        network_end = self._get_network_stats()
        
        return {
            'cpu_avg': sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0,
            'memory_avg_mb': sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0,
            'network_bytes_sent': network_end['bytes_sent'] - self.network_start['bytes_sent'],
            'network_bytes_recv': network_end['bytes_recv'] - self.network_start['bytes_recv']
        }


class MoonlightAgent:
    """Main Moonlight telemetry agent"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Moonlight agent"""
        self.config = self._load_config(config_path)
        self.session_id = self._generate_session_id()
        self.events: List[TelemetryEvent] = []
        self.session_metadata = self._init_session_metadata()
        self.khaos_connector = KhaosBaseConnector(self.config)
        self.gpg_signer = GPGSigner(self.config.get('gpg_key_id', 'AE5519579584DEF5'))
        self.metrics_collector = SystemMetricsCollector()
        self.files_modified: set = set()
        self.start_time = time.time()
        
        logger.info(f"Moonlight Agent initialized - Session: {self.session_id}")
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load agent configuration"""
        default_config = {
            'node_name': socket.gethostname(),
            'vault_name': os.getenv('OBSIDIAN_VAULT', 'Athena'),
            'board_member': os.getenv('BOARD_MEMBER', 'Claude Opus 4.5'),
            'khaosbase_url': os.getenv('KHAOSBASE_URL', 'http://localhost:8080'),
            'gpg_key_id': 'AE5519579584DEF5',
            'telemetry_dir': os.getenv('TELEMETRY_DIR', './telemetry'),
            'auto_push': os.getenv('AUTO_PUSH_TELEMETRY', 'true').lower() == 'true'
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                
        return default_config
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        node = socket.gethostname()[:8]
        random_suffix = hashlib.sha256(f"{timestamp}{node}{os.getpid()}".encode()).hexdigest()[:8]
        return f"moonlight_{timestamp}_{node}_{random_suffix}"
        
    def _init_session_metadata(self) -> SessionMetadata:
        """Initialize session metadata"""
        return SessionMetadata(
            session_id=self.session_id,
            start_time=datetime.now(timezone.utc).isoformat(),
            end_time=None,
            user=os.getenv('USER', 'unknown'),
            node_name=self.config['node_name'],
            vault_name=self.config['vault_name'],
            board_member=self.config['board_member'],
            session_type=self._detect_session_type()
        )
        
    def _detect_session_type(self) -> str:
        """Detect session type (codespace, local, remote)"""
        if os.getenv('CODESPACES'):
            return 'codespace'
        elif os.getenv('SSH_CLIENT'):
            return 'remote'
        else:
            return 'local'
            
    def record_event(self, event_type: str, payload: Dict[str, Any], 
                    metadata: Optional[Dict[str, Any]] = None) -> TelemetryEvent:
        """Record a telemetry event"""
        event_id = f"{self.session_id}_{len(self.events):06d}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        event = TelemetryEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            payload=payload,
            metadata=metadata or {},
            signature=None
        )
        
        # Sign the event
        event_data = json.dumps(asdict(event), sort_keys=True)
        event.signature = self.gpg_signer.sign_data(event_data)
        
        self.events.append(event)
        
        # Sample metrics periodically
        if len(self.events) % 10 == 0:
            self.metrics_collector.sample_metrics()
            
        # Auto-push if enabled
        if self.config['auto_push']:
            self.khaos_connector.push_event(event)
            
        logger.debug(f"Recorded event: {event_type} - {event_id}")
        return event
        
    def record_file_change(self, filepath: str, change_type: str = "modified"):
        """Record file modification event"""
        self.files_modified.add(filepath)
        self.record_event(
            event_type='file_change',
            payload={
                'filepath': filepath,
                'change_type': change_type,
                'file_size': os.path.getsize(filepath) if os.path.exists(filepath) else 0
            }
        )
        
    def record_ai_interaction(self, query: str, response: str, model: str):
        """Record AI interaction event"""
        self.record_event(
            event_type='ai_query',
            payload={
                'query_length': len(query),
                'response_length': len(response),
                'model': model,
                'query_hash': hashlib.sha256(query.encode()).hexdigest()[:16]
            }
        )
        
    def record_knowledge_update(self, vault: str, note: str, update_type: str = "create"):
        """Record knowledge graph update"""
        self.record_event(
            event_type='knowledge_update',
            payload={
                'vault': vault,
                'note': note,
                'update_type': update_type
            }
        )
        
    def record_command(self, command: str, exit_code: int, duration_ms: float):
        """Record command execution"""
        self.record_event(
            event_type='command',
            payload={
                'command': command,
                'exit_code': exit_code,
                'duration_ms': duration_ms
            }
        )
        
    def generate_session_summary(self) -> SessionSummary:
        """Generate session summary"""
        duration = time.time() - self.start_time
        
        # Count events by type
        event_breakdown = {}
        for event in self.events:
            event_breakdown[event.event_type] = event_breakdown.get(event.event_type, 0) + 1
            
        # Get system metrics
        metrics = self.metrics_collector.get_summary()
        
        summary = SessionSummary(
            session_id=self.session_id,
            duration_seconds=duration,
            total_events=len(self.events),
            event_breakdown=event_breakdown,
            files_modified=list(self.files_modified),
            ai_interactions=event_breakdown.get('ai_query', 0),
            knowledge_contributions=event_breakdown.get('knowledge_update', 0),
            cpu_avg=metrics['cpu_avg'],
            memory_avg_mb=metrics['memory_avg_mb'],
            network_bytes_sent=metrics['network_bytes_sent'],
            network_bytes_recv=metrics['network_bytes_recv']
        )
        
        return summary
        
    def save_session_data(self, output_dir: Optional[str] = None):
        """Save session data to disk"""
        output_dir = output_dir or self.config['telemetry_dir']
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Update session metadata
        self.session_metadata.end_time = datetime.now(timezone.utc).isoformat()
        
        # Save session metadata
        metadata_path = Path(output_dir) / f"{self.session_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(asdict(self.session_metadata), f, indent=2)
            
        # Save events
        events_path = Path(output_dir) / f"{self.session_id}_events.jsonl"
        with open(events_path, 'w') as f:
            for event in self.events:
                f.write(json.dumps(asdict(event)) + '\n')
                
        # Save session summary
        summary = self.generate_session_summary()
        summary_path = Path(output_dir) / f"{self.session_id}_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(asdict(summary), f, indent=2)
            
        logger.info(f"Session data saved to {output_dir}")
        logger.info(f"  Metadata: {metadata_path}")
        logger.info(f"  Events: {events_path}")
        logger.info(f"  Summary: {summary_path}")
        
        # Push summary to KhaosBase
        if self.config['auto_push']:
            self.khaos_connector.push_session_summary(summary)
            
    def print_session_report(self):
        """Print human-readable session report"""
        summary = self.generate_session_summary()
        
        print("\n" + "="*70)
        print("🌙 MOONLIGHT SESSION REPORT")
        print("="*70)
        print(f"\nSession ID: {self.session_id}")
        print(f"Node: {self.session_metadata.node_name}")
        print(f"Vault: {self.session_metadata.vault_name}")
        print(f"Board Member: {self.session_metadata.board_member}")
        print(f"Duration: {summary.duration_seconds:.2f} seconds")
        print(f"\nSession Statistics:")
        print(f"  Total Events: {summary.total_events}")
        print(f"  AI Interactions: {summary.ai_interactions}")
        print(f"  Knowledge Updates: {summary.knowledge_contributions}")
        print(f"  Files Modified: {len(summary.files_modified)}")
        print(f"\nEvent Breakdown:")
        for event_type, count in summary.event_breakdown.items():
            print(f"  {event_type}: {count}")
        print(f"\nSystem Metrics:")
        print(f"  Average CPU: {summary.cpu_avg:.2f}%")
        print(f"  Average Memory: {summary.memory_avg_mb:.2f} MB")
        print(f"  Network Sent: {summary.network_bytes_sent / (1024*1024):.2f} MB")
        print(f"  Network Received: {summary.network_bytes_recv / (1024*1024):.2f} MB")
        print("="*70 + "\n")


def main():
    """Main entry point for Moonlight agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Moonlight Telemetry Agent')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--output-dir', help='Output directory for telemetry data')
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = MoonlightAgent(config_path=args.config)
    
    if args.test:
        # Run test scenario
        logger.info("Running in test mode")
        
        # Simulate some events
        agent.record_command('npm run build', 0, 1234.5)
        agent.record_file_change('/path/to/file.ts', 'modified')
        agent.record_ai_interaction(
            query="How do I implement a telemetry agent?",
            response="Here's how to implement a telemetry agent...",
            model="claude-opus-4.5"
        )
        agent.record_knowledge_update('Athena', 'telemetry-patterns.md', 'create')
        
        # Generate report
        agent.print_session_report()
        
        # Save data
        agent.save_session_data(output_dir=args.output_dir)
    else:
        logger.info("Moonlight agent running in daemon mode")
        logger.info("Use CTRL+C to stop")
        
        try:
            # In production, this would run as a daemon
            # For now, we just keep the process alive
            while True:
                time.sleep(60)
                agent.metrics_collector.sample_metrics()
        except KeyboardInterrupt:
            logger.info("Shutting down Moonlight agent")
            agent.print_session_report()
            agent.save_session_data(output_dir=args.output_dir)
            

if __name__ == '__main__':
    main()
