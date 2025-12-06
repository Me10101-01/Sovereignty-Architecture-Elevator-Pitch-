"""
Swarm Experiment Module
=======================

This module owns experiment execution and trace capture.
The swarm can extend this module with new experiment types.

LLM Hint: When generating new experiments, follow the naming pattern:
- sovereignty_experiment_<name>
- Use absolute paths for all I/O operations
- Capture traces to logs/ directory
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def run_experiment(
    input_path: Path,
    name: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Execute a swarm experiment with captured traces.

    This function should:
    - Read input data from the absolute path
    - Execute the experiment logic
    - Capture traces to logs/
    - Return experiment results

    Args:
        input_path: Absolute path to input data file
        name: Dynamic experiment name (swarm will extend)
        output_dir: Optional output directory for results

    Returns:
        Dict containing experiment results and trace metadata
    """
    experiment_name = name or f"sovereignty_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"Starting experiment: {experiment_name}")

    # Validate input path exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    # Determine output directory
    if output_dir is None:
        # Default to logs/ directory relative to repo root
        output_dir = Path(__file__).parent.parent / "logs"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Read input data
    input_data = _load_input_data(input_path)

    # Execute experiment (swarm can extend this logic)
    results = _execute_experiment_logic(experiment_name, input_data)

    # Capture trace
    trace_path = output_dir / f"{experiment_name}_trace.json"
    trace_data = {
        "experiment_name": experiment_name,
        "input_path": str(input_path),
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }

    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, indent=2, default=str)

    logger.info(f"Experiment complete. Trace saved to: {trace_path}")

    return {
        "experiment_name": experiment_name,
        "trace_path": str(trace_path),
        "results": results,
        "status": "completed",
    }


def _load_input_data(input_path: Path) -> Dict[str, Any]:
    """
    Load input data from file.

    LLM Hint: Extend this to support more formats:
    - JSON, YAML, CSV, Parquet
    - Add validation schemas as needed
    """
    suffix = input_path.suffix.lower()

    if suffix == ".json":
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Default: read as text
        with open(input_path, "r", encoding="utf-8") as f:
            return {"raw_text": f.read()}


def _execute_experiment_logic(
    experiment_name: str,
    input_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Core experiment execution logic.

    LLM Hint: This is the main extension point for new experiment types.
    The swarm should generate specialized experiment modules like:
    - sovereignty_log_analyzer
    - black_ops_lab
    - quantum_symbolic_emulator

    Each should follow the same trace capture pattern.
    """
    # Base experiment: echo input with metadata
    return {
        "experiment_type": "base",
        "input_summary": {
            "keys": list(input_data.keys()) if isinstance(input_data, dict) else ["raw"],
            "size_bytes": len(str(input_data)),
        },
        "processed": True,
    }
