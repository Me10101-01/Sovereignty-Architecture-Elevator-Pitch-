"""
Analyzers Module - Log Analysis Zone

This module contains code for parsing log files, computing sovereignty metrics,
and generating reports. It integrates with external analysis tools like the
Rust sovereignty-log-analyzer.

Key components:
- SovereigntyLogAnalyzer: Main analyzer that wraps the Rust binary
- SovereigntyMetrics: Dataclass holding computed metrics

See docs/SOVEREIGNTY_DOCTRINE.md for the architecture overview.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import subprocess
import json
import shutil


@dataclass
class SovereigntyMetrics:
    """
    Container for sovereignty metrics computed from log analysis.
    
    Attributes:
        total_events: Total number of log events processed
        sovereignty_violations: Number of sovereignty boundary violations
        handshake_compliance: Percentage of actions with proper handshakes
        agent_activity: Dict mapping agent IDs to event counts
        mutation_count: Number of file/state mutations
        audit_coverage: Percentage of events with full audit trails
        analysis_timestamp: When this analysis was performed
    """
    total_events: int = 0
    sovereignty_violations: int = 0
    handshake_compliance: float = 0.0
    agent_activity: Dict[str, int] = field(default_factory=dict)
    mutation_count: int = 0
    audit_coverage: float = 0.0
    analysis_timestamp: str = ""
    raw_output: Optional[str] = None
    
    @classmethod
    def from_rust_output(cls, output: str) -> "SovereigntyMetrics":
        """
        Parse metrics from Rust analyzer output.
        
        The Rust analyzer outputs JSON with metric fields.
        
        Args:
            output: Raw output from sovereignty-log-analyzer
            
        Returns:
            Parsed SovereigntyMetrics instance
        """
        try:
            data = json.loads(output)
            return cls(
                total_events=data.get("total_events", 0),
                sovereignty_violations=data.get("violations", 0),
                handshake_compliance=data.get("handshake_compliance", 0.0),
                agent_activity=data.get("agent_activity", {}),
                mutation_count=data.get("mutations", 0),
                audit_coverage=data.get("audit_coverage", 0.0),
                analysis_timestamp=datetime.now(timezone.utc).isoformat(),
                raw_output=output
            )
        except json.JSONDecodeError:
            # If not JSON, return metrics with raw output
            return cls(
                analysis_timestamp=datetime.now(timezone.utc).isoformat(),
                raw_output=output
            )
    
    @classmethod
    def from_fallback_analysis(cls, data: Dict[str, Any]) -> "SovereigntyMetrics":
        """
        Create metrics from Python fallback analysis.
        
        Args:
            data: Dict with metric fields
            
        Returns:
            SovereigntyMetrics instance
        """
        return cls(
            total_events=data.get("total_events", 0),
            sovereignty_violations=data.get("violations", 0),
            handshake_compliance=data.get("handshake_compliance", 0.0),
            agent_activity=data.get("agent_activity", {}),
            mutation_count=data.get("mutations", 0),
            audit_coverage=data.get("audit_coverage", 0.0),
            analysis_timestamp=datetime.now(timezone.utc).isoformat()
        )


class SovereigntyLogAnalyzer:
    """
    Analyzer that wraps the Rust sovereignty-log-analyzer binary.
    
    This class provides a Python interface to the Rust log analyzer,
    with a fallback to pure Python analysis when the binary isn't available.
    
    The analyzer can:
    - Process GKE audit log JSON files
    - Compute sovereignty metrics
    - Generate markdown reports
    
    Attributes:
        binary_path: Path to the Rust binary (auto-detected)
        
    Example:
        >>> analyzer = SovereigntyLogAnalyzer()
        >>> metrics = analyzer.analyze(Path("/path/to/audit.json"))
        >>> analyzer.print_metrics(metrics)
    """
    
    # Common locations to search for the binary
    BINARY_SEARCH_PATHS = [
        "sovereignty-log-analyzer",  # In PATH
        "./target/release/sovereignty-log-analyzer",  # Local Rust build
        "./target/debug/sovereignty-log-analyzer",  # Debug build
        "../sovereignty-log-analyzer/target/release/sovereignty-log-analyzer",  # Sibling project
    ]
    
    # Default timeout for Rust binary execution (seconds)
    DEFAULT_TIMEOUT = 60
    
    def __init__(self, binary_path: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the analyzer.
        
        Args:
            binary_path: Optional explicit path to Rust binary.
                        If None, searches common locations.
            timeout: Timeout in seconds for Rust binary execution (default: 60)
        """
        self._binary_path = binary_path or self._find_binary()
        self._timeout = timeout
    
    def _find_binary(self) -> Optional[str]:
        """Find the sovereignty-log-analyzer binary."""
        for path in self.BINARY_SEARCH_PATHS:
            if shutil.which(path) or Path(path).exists():
                return path
        return None
    
    def binary_available(self) -> bool:
        """Check if the Rust binary is available."""
        return self._binary_path is not None
    
    def analyze(self, input_path: Path) -> SovereigntyMetrics:
        """
        Analyze a log file and return sovereignty metrics.
        
        If the Rust binary is available, uses it for analysis.
        Otherwise falls back to Python-based analysis.
        
        Args:
            input_path: Path to the GKE audit log JSON file
            
        Returns:
            SovereigntyMetrics with computed values
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If analysis fails
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if self.binary_available():
            return self._analyze_with_rust(input_path)
        else:
            return self._analyze_with_python(input_path)
    
    def _analyze_with_rust(self, input_path: Path) -> SovereigntyMetrics:
        """Run analysis using the Rust binary."""
        try:
            result = subprocess.run(
                [self._binary_path, "metrics", "--input", str(input_path)],
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode != 0:
                # Try to use output anyway, or fall back
                if result.stdout:
                    return SovereigntyMetrics.from_rust_output(result.stdout)
                raise RuntimeError(f"Rust analyzer failed: {result.stderr}")
            
            return SovereigntyMetrics.from_rust_output(result.stdout)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Rust analyzer timed out")
        except FileNotFoundError:
            # Binary not actually executable
            return self._analyze_with_python(input_path)
    
    def _analyze_with_python(self, input_path: Path) -> SovereigntyMetrics:
        """
        Fallback Python-based log analysis.
        
        This is a simplified analysis that looks for common patterns
        in GKE audit logs. The Rust version is more comprehensive.
        """
        try:
            content = input_path.read_text()
            
            # Try to parse as JSON
            try:
                data = json.loads(content)
                return self._analyze_json(data)
            except json.JSONDecodeError:
                # Try line-by-line JSON (NDJSON format)
                return self._analyze_ndjson(content)
                
        except Exception as e:
            raise RuntimeError(f"Python analysis failed: {e}")
    
    def _analyze_json(self, data: Any) -> SovereigntyMetrics:
        """Analyze parsed JSON data."""
        events = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            events = data
        elif isinstance(data, dict):
            if "entries" in data:
                events = data["entries"]
            elif "items" in data:
                events = data["items"]
            else:
                events = [data]
        
        total_events = len(events)
        violations = 0
        mutations = 0
        agent_activity: Dict[str, int] = {}
        audited = 0
        
        for event in events:
            if not isinstance(event, dict):
                continue
            
            # Count agent activity
            principal = event.get("protoPayload", {}).get("authenticationInfo", {}).get("principalEmail", "unknown")
            agent_activity[principal] = agent_activity.get(principal, 0) + 1
            
            # Count mutations
            method = event.get("protoPayload", {}).get("methodName", "")
            if any(m in method.lower() for m in ["create", "update", "delete", "patch"]):
                mutations += 1
            
            # Check for audit info
            if event.get("protoPayload", {}).get("requestMetadata"):
                audited += 1
            
            # Check for violations (unauthorized access, etc.)
            status = event.get("protoPayload", {}).get("status", {})
            if isinstance(status, dict) and status.get("code", 0) in [401, 403, 7, 16]:
                violations += 1
        
        audit_coverage = audited / total_events if total_events > 0 else 0.0
        
        # Handshake compliance is estimated based on proper audit trails
        handshake_compliance = audit_coverage * 0.8  # Rough estimate
        
        return SovereigntyMetrics.from_fallback_analysis({
            "total_events": total_events,
            "violations": violations,
            "handshake_compliance": handshake_compliance,
            "agent_activity": agent_activity,
            "mutations": mutations,
            "audit_coverage": audit_coverage,
        })
    
    def _analyze_ndjson(self, content: str) -> SovereigntyMetrics:
        """Analyze newline-delimited JSON content."""
        events = []
        for line in content.strip().split("\n"):
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return self._analyze_json(events)
    
    def print_metrics(self, metrics: SovereigntyMetrics) -> None:
        """
        Pretty-print metrics to stdout.
        
        Args:
            metrics: The metrics to display
        """
        print(f"\n  Total Events:          {metrics.total_events:,}")
        print(f"  Sovereignty Violations: {metrics.sovereignty_violations:,}")
        
        bar = "█" * int(metrics.handshake_compliance * 20)
        print(f"  Handshake Compliance:  [{bar:<20}] {metrics.handshake_compliance:.1%}")
        
        bar = "█" * int(metrics.audit_coverage * 20)
        print(f"  Audit Coverage:        [{bar:<20}] {metrics.audit_coverage:.1%}")
        
        print(f"  Total Mutations:       {metrics.mutation_count:,}")
        
        if metrics.agent_activity:
            print(f"\n  Agent Activity:")
            sorted_agents = sorted(metrics.agent_activity.items(), key=lambda x: -x[1])
            for agent, count in sorted_agents[:5]:
                print(f"    {agent}: {count:,} events")
            if len(sorted_agents) > 5:
                print(f"    ... and {len(sorted_agents) - 5} more agents")
    
    def write_report(self, metrics: SovereigntyMetrics, output_path: Path, input_path: Path) -> None:
        """
        Write a markdown report to the given path.
        
        Args:
            metrics: The metrics to report
            output_path: Where to write the report
            input_path: Original input file for reference
        """
        report = f"""# Sovereignty Analysis Report

**Generated:** {metrics.analysis_timestamp}
**Input File:** {input_path}

---

## Summary Metrics

| Metric | Value |
|--------|-------|
| Total Events | {metrics.total_events:,} |
| Sovereignty Violations | {metrics.sovereignty_violations:,} |
| Handshake Compliance | {metrics.handshake_compliance:.1%} |
| Audit Coverage | {metrics.audit_coverage:.1%} |
| Total Mutations | {metrics.mutation_count:,} |

---

## Agent Activity

| Agent | Events |
|-------|--------|
"""
        for agent, count in sorted(metrics.agent_activity.items(), key=lambda x: -x[1]):
            report += f"| {agent} | {count:,} |\n"
        
        report += """
---

## Interpretation

"""
        # Add interpretation based on metrics
        if metrics.sovereignty_violations == 0:
            report += "✅ **No sovereignty violations detected.** All actions stayed within boundaries.\n\n"
        else:
            report += f"⚠️ **{metrics.sovereignty_violations} sovereignty violations detected.** Review agent permissions.\n\n"
        
        if metrics.handshake_compliance >= 0.9:
            report += "✅ **High handshake compliance.** Agents are following SWARM-HS protocol.\n\n"
        elif metrics.handshake_compliance >= 0.5:
            report += "⚠️ **Moderate handshake compliance.** Some actions lack proper authorization.\n\n"
        else:
            report += "❌ **Low handshake compliance.** Review agent configuration and protocol.\n\n"
        
        if metrics.audit_coverage >= 0.9:
            report += "✅ **Excellent audit coverage.** Full traceability available.\n\n"
        else:
            report += f"⚠️ **Audit coverage at {metrics.audit_coverage:.0%}.** Enable more detailed logging.\n\n"
        
        report += """---

*Report generated by Sovereignty Log Analyzer*
*See docs/SOVEREIGNTY_DOCTRINE.md for architecture details*
"""
        
        output_path.write_text(report)


# Export public API
__all__ = ["SovereigntyLogAnalyzer", "SovereigntyMetrics"]
