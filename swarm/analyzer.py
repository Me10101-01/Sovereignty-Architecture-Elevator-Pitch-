"""
Swarm Log Analyzer Module
=========================

This module owns log analysis and insight extraction.
The swarm can extend this with specialized analyzers.

LLM Hint: When generating analyzers, follow the naming pattern:
- sovereignty_<domain>_analyzer
- Output structured insights to data/ directory
- Use absolute paths for all I/O
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_logs(
    input_path: Path,
    output_dir: Optional[Path] = None,
    analysis_type: str = "summary",
) -> Dict[str, Any]:
    """
    Analyze log files and extract insights.

    This function should:
    - Read log data from absolute path
    - Apply analysis algorithms
    - Output structured insights to data/

    Args:
        input_path: Absolute path to log file or directory
        output_dir: Optional output directory for analysis results
        analysis_type: Type of analysis to perform (summary, deep, pattern)

    Returns:
        Dict containing analysis results and output paths
    """
    logger.info(f"Starting log analysis: {input_path}")

    # Validate input exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    # Determine output directory
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load and analyze logs
    if input_path.is_file():
        logs = _load_log_file(input_path)
    else:
        logs = _load_log_directory(input_path)

    # Execute analysis based on type
    analysis_result = _execute_analysis(logs, analysis_type)

    # Save analysis output
    output_filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = output_dir / output_filename

    with open(output_path, "w") as f:
        json.dump(analysis_result, f, indent=2, default=str)

    logger.info(f"Analysis complete. Results saved to: {output_path}")

    return {
        "analysis_type": analysis_type,
        "input_path": str(input_path),
        "output_path": str(output_path),
        "summary": analysis_result.get("summary", {}),
        "status": "completed",
    }


def _load_log_file(log_path: Path) -> List[Dict[str, Any]]:
    """
    Load a single log file.

    LLM Hint: Extend to support formats:
    - JSON lines, structured logs
    - Plain text with regex parsing
    - Prometheus/Loki query results
    """
    suffix = log_path.suffix.lower()

    if suffix == ".json":
        with open(log_path, "r") as f:
            data = json.load(f)
            # Handle both single object and array
            return data if isinstance(data, list) else [data]
    elif suffix == ".jsonl":
        logs = []
        with open(log_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    logs.append(json.loads(line))
        return logs
    else:
        # Plain text: treat each line as a log entry
        with open(log_path, "r") as f:
            return [{"raw_line": line.strip(), "line_num": i}
                    for i, line in enumerate(f, 1) if line.strip()]


def _load_log_directory(log_dir: Path) -> List[Dict[str, Any]]:
    """Load all log files from a directory."""
    all_logs = []
    for log_file in sorted(log_dir.glob("*.json")):
        all_logs.extend(_load_log_file(log_file))
    for log_file in sorted(log_dir.glob("*.jsonl")):
        all_logs.extend(_load_log_file(log_file))
    for log_file in sorted(log_dir.glob("*.log")):
        all_logs.extend(_load_log_file(log_file))
    return all_logs


def _execute_analysis(
    logs: List[Dict[str, Any]],
    analysis_type: str,
) -> Dict[str, Any]:
    """
    Execute analysis on loaded logs.

    LLM Hint: Add specialized analyzers:
    - sovereignty_metrics_analyzer (extract key metrics)
    - sovereignty_pattern_detector (find recurring patterns)
    - sovereignty_anomaly_detector (identify anomalies)
    """
    timestamp = datetime.now().isoformat()

    if analysis_type == "summary":
        return _summary_analysis(logs, timestamp)
    elif analysis_type == "deep":
        return _deep_analysis(logs, timestamp)
    elif analysis_type == "pattern":
        return _pattern_analysis(logs, timestamp)
    else:
        logger.warning(f"Unknown analysis type: {analysis_type}, using summary")
        return _summary_analysis(logs, timestamp)


def _summary_analysis(logs: List[Dict[str, Any]], timestamp: str) -> Dict[str, Any]:
    """Generate summary statistics from logs."""
    return {
        "analysis_type": "summary",
        "timestamp": timestamp,
        "summary": {
            "total_entries": len(logs),
            "keys_found": list(set(k for log in logs for k in log.keys())),
        },
        "insights": [],
    }


def _deep_analysis(logs: List[Dict[str, Any]], timestamp: str) -> Dict[str, Any]:
    """Perform deep analysis of log content."""
    return {
        "analysis_type": "deep",
        "timestamp": timestamp,
        "summary": {
            "total_entries": len(logs),
        },
        "insights": [
            {"type": "deep_analysis_placeholder", "detail": "Swarm can extend with ML models"},
        ],
    }


def _pattern_analysis(logs: List[Dict[str, Any]], timestamp: str) -> Dict[str, Any]:
    """Detect patterns in log entries."""
    return {
        "analysis_type": "pattern",
        "timestamp": timestamp,
        "summary": {
            "total_entries": len(logs),
        },
        "patterns": [],
        "insights": [
            {"type": "pattern_placeholder", "detail": "Swarm can extend with pattern recognition"},
        ],
    }
