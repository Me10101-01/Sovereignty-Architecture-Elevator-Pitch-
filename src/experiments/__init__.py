"""
Experiments Module - Black Ops Lab Zone

This module contains code for creating experiments, running trials, and collecting
results. The ParticleCollider class is the main engine that manages experiment
lifecycle.

Key components:
- ParticleCollider: Main experiment management engine
- Experiment: Represents a single experiment instance

See docs/BLACK_OPS_LAB.md for the full specification.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import shutil
import yaml


@dataclass
class Experiment:
    """
    Represents a single experiment in the Black Ops Lab.
    
    Each experiment has its own directory under data/experiments/
    with standardized files for context, logging, and results.
    
    Attributes:
        experiment_id: Unique identifier (timestamp_name)
        name: Human-readable experiment name
        experiment_dir: Path to the experiment directory
        context_file: Original context file path
        created_at: When the experiment was created
        status: Current status (created, running, completed, archived)
    """
    experiment_id: str
    name: str
    experiment_dir: Path
    context_file: Optional[Path] = None
    created_at: str = ""
    status: str = "created"
    
    def log_phase(self, phase: str, agent: str, details: str) -> None:
        """
        Log a SWARM-HS phase to the experiment log.
        
        Args:
            phase: Phase name (SYN, SYN-ACK, ACK, DATA, APPLY, TRACE)
            agent: Agent identifier
            details: Details of what happened
        """
        log_path = self.experiment_dir / "experiment_log.md"
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = f"""
### {timestamp} - {phase}
- Agent: {agent}
- Details: {details}

"""
        
        with open(log_path, "a") as f:
            f.write(entry)
    
    def finalize(self, status: str = "completed") -> None:
        """
        Mark the experiment as finalized.
        
        Updates the results.yaml file with final status.
        
        Args:
            status: Final status (completed, failed, aborted)
        """
        results_path = self.experiment_dir / "results.yaml"
        
        if results_path.exists():
            with open(results_path) as f:
                results = yaml.safe_load(f) or {}
        else:
            results = {}
        
        results["status"] = status
        results["finalized_at"] = datetime.now(timezone.utc).isoformat()
        
        with open(results_path, "w") as f:
            yaml.dump(results, f, default_flow_style=False)
        
        self.status = status


class ParticleCollider:
    """
    The Black Ops Lab experiment engine.
    
    This class manages the lifecycle of experiments:
    - Creating experiment containers with proper structure
    - Scaffolding logging and result files
    - Tracking experiment status
    - Archiving completed experiments
    
    Attributes:
        experiments_dir: Base directory for all experiments
        
    Example:
        >>> collider = ParticleCollider()
        >>> exp = collider.create_experiment("my-test", Path("context.md"))
        >>> exp.log_phase("SYN", "claude-v1", "Requesting analyzer generation")
        >>> exp.finalize("completed")
    """
    
    def __init__(self, experiments_dir: Optional[Path] = None):
        """
        Initialize the particle collider.
        
        Args:
            experiments_dir: Base directory for experiments.
                           Defaults to data/experiments/ relative to repo root.
        """
        if experiments_dir is None:
            # Find repo root (go up from src/experiments/)
            src_dir = Path(__file__).parent.parent
            repo_root = src_dir.parent
            experiments_dir = repo_root / "data" / "experiments"
        
        self.experiments_dir = experiments_dir
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
    
    def create_experiment(self, name: str, context_file: Path) -> Experiment:
        """
        Create a new experiment with proper directory structure.
        
        Creates:
        - data/experiments/<timestamp>_<name>/
        - context.md (copy of input)
        - experiment_log.md (template)
        - results.yaml (template)
        - artifacts/ directory
        
        Args:
            name: Human-readable experiment name (will be sanitized)
            context_file: Path to context file to copy into experiment
            
        Returns:
            Experiment instance representing the new experiment
            
        Raises:
            FileNotFoundError: If context file doesn't exist
        """
        if not context_file.exists():
            raise FileNotFoundError(f"Context file not found: {context_file}")
        
        # Generate experiment ID
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in name)
        experiment_id = f"{timestamp}_{safe_name}"
        
        # Create directory structure
        exp_dir = self.experiments_dir / experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        (exp_dir / "artifacts").mkdir(exist_ok=True)
        
        # Copy context file
        context_dest = exp_dir / "context.md"
        shutil.copy(context_file, context_dest)
        
        # Create experiment log template
        log_content = f"""# Experiment: {name}

## Experiment ID
{experiment_id}

## Hypothesis
<!-- TODO: Define what you're testing -->

## Timeline

<!-- Phases will be logged below as they occur -->

"""
        (exp_dir / "experiment_log.md").write_text(log_content)
        
        # Create results template
        results = {
            "experiment_id": experiment_id,
            "name": name,
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "phases_executed": [],
            "metrics": {},
            "artifacts": [],
        }
        
        with open(exp_dir / "results.yaml", "w") as f:
            yaml.dump(results, f, default_flow_style=False)
        
        # Create conclusions placeholder
        conclusions_content = f"""# Conclusions: {name}

## What Worked

<!-- TODO: Document successful aspects -->

## What Failed

<!-- TODO: Document failures and issues -->

## Lessons Learned

<!-- TODO: What should change in the architecture? -->

## Recommendations

<!-- TODO: Next steps based on findings -->
"""
        (exp_dir / "conclusions.md").write_text(conclusions_content)
        
        return Experiment(
            experiment_id=experiment_id,
            name=name,
            experiment_dir=exp_dir,
            context_file=context_dest,
            created_at=results["created_at"],
            status="created"
        )
    
    def list_experiments(self) -> List[Dict[str, Any]]:
        """
        List all experiments in the experiments directory.
        
        Returns:
            List of dicts with experiment info (id, status, created, completed)
        """
        experiments = []
        
        for exp_dir in sorted(self.experiments_dir.iterdir()):
            if not exp_dir.is_dir():
                continue
            
            results_file = exp_dir / "results.yaml"
            if results_file.exists():
                try:
                    with open(results_file) as f:
                        results = yaml.safe_load(f) or {}
                except Exception:
                    results = {}
            else:
                results = {}
            
            experiments.append({
                "id": exp_dir.name,
                "status": results.get("status", "unknown"),
                "created": results.get("created_at", "unknown"),
                "completed": results.get("status") in ["completed", "archived"],
                "directory": str(exp_dir),
            })
        
        return experiments
    
    def get_experiment_status(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed status of a specific experiment.
        
        Args:
            experiment_id: The experiment identifier
            
        Returns:
            Dict with experiment details, or None if not found
        """
        exp_dir = self.experiments_dir / experiment_id
        
        if not exp_dir.exists():
            return None
        
        results_file = exp_dir / "results.yaml"
        if results_file.exists():
            try:
                with open(results_file) as f:
                    results = yaml.safe_load(f) or {}
            except Exception:
                results = {}
        else:
            results = {}
        
        # Count logged phases
        log_file = exp_dir / "experiment_log.md"
        phases_completed = 0
        if log_file.exists():
            content = log_file.read_text()
            for phase in ["SYN", "SYN-ACK", "ACK", "DATA", "APPLY", "TRACE"]:
                if f"- {phase}" in content or f"### " in content and phase in content:
                    phases_completed += 1
        
        return {
            "id": experiment_id,
            "name": results.get("name", experiment_id),
            "status": results.get("status", "unknown"),
            "created": results.get("created_at", "unknown"),
            "phases_completed": phases_completed,
            "directory": str(exp_dir),
        }
    
    def archive_experiment(self, experiment_id: str) -> bool:
        """
        Archive a completed experiment.
        
        Updates the results.yaml to mark as archived.
        
        Args:
            experiment_id: The experiment to archive
            
        Returns:
            True if successful, False if experiment not found
        """
        exp_dir = self.experiments_dir / experiment_id
        
        if not exp_dir.exists():
            return False
        
        results_file = exp_dir / "results.yaml"
        
        if results_file.exists():
            try:
                with open(results_file) as f:
                    results = yaml.safe_load(f) or {}
            except Exception:
                results = {}
        else:
            results = {}
        
        results["status"] = "archived"
        results["archived_at"] = datetime.now(timezone.utc).isoformat()
        
        with open(results_file, "w") as f:
            yaml.dump(results, f, default_flow_style=False)
        
        return True


# Export public API
__all__ = ["ParticleCollider", "Experiment"]
