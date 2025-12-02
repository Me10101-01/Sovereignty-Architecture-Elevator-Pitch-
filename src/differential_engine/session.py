"""
Session management for the Differential Engine.
Handles persistence of diagnosis sessions to data/sessions/
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid


@dataclass
class DiagnosisRound:
    """A single round of debate in the diagnosis."""
    round_number: int
    phase: str  # hypothesis, challenge, convergence
    contributions: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_contribution(self, agent_name: str, content: str, confidence: float = None, action: str = None):
        """Add an agent's contribution to this round."""
        self.contributions.append({
            "agent": agent_name,
            "content": content,
            "confidence": confidence,
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "round_number": self.round_number,
            "phase": self.phase,
            "contributions": self.contributions,
            "timestamp": self.timestamp
        }


@dataclass
class Diagnosis:
    """The final diagnosis from a session."""
    primary: str
    confidence: float
    root_cause: Optional[str] = None
    supporting_agents: List[str] = field(default_factory=list)
    dissenting_views: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "primary": self.primary,
            "confidence": self.confidence,
            "root_cause": self.root_cause,
            "supporting_agents": self.supporting_agents,
            "dissenting_views": self.dissenting_views,
            "actions": self.actions
        }


@dataclass
class Session:
    """
    A complete diagnosis session.
    Contains the problem, debate rounds, and final diagnosis.
    """
    problem: str
    domain: str = "general"
    symptoms: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    session_id: str = field(default_factory=lambda: f"{datetime.now().strftime('%Y-%m-%d')}_{uuid.uuid4().hex[:8]}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    agents_involved: List[str] = field(default_factory=list)
    rounds: List[DiagnosisRound] = field(default_factory=list)
    diagnosis: Optional[Diagnosis] = None
    
    # Metadata
    duration_seconds: float = 0.0
    total_tokens: int = 0
    consensus_reached: bool = False
    status: str = "in_progress"  # in_progress, completed, failed, timeout

    def add_round(self, phase: str) -> DiagnosisRound:
        """Start a new round of debate."""
        round_num = len(self.rounds) + 1
        new_round = DiagnosisRound(round_number=round_num, phase=phase)
        self.rounds.append(new_round)
        return new_round

    def get_current_round(self) -> Optional[DiagnosisRound]:
        """Get the current (last) round."""
        return self.rounds[-1] if self.rounds else None

    def set_diagnosis(self, diagnosis: Diagnosis):
        """Set the final diagnosis."""
        self.diagnosis = diagnosis
        self.status = "completed"
        self.consensus_reached = diagnosis.confidence >= 0.67

    def add_agent(self, agent_name: str):
        """Record an agent's participation."""
        if agent_name not in self.agents_involved:
            self.agents_involved.append(agent_name)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "problem": self.problem,
            "domain": self.domain,
            "symptoms": self.symptoms,
            "context": self.context,
            "agents_involved": self.agents_involved,
            "rounds": [r.to_dict() for r in self.rounds],
            "diagnosis": self.diagnosis.to_dict() if self.diagnosis else None,
            "metadata": {
                "duration_seconds": self.duration_seconds,
                "total_tokens": self.total_tokens,
                "consensus_reached": self.consensus_reached,
                "status": self.status
            }
        }

    def to_markdown(self) -> str:
        """Generate a human-readable markdown transcript."""
        lines = [
            "# Differential Diagnosis Session",
            "",
            f"**Session ID**: {self.session_id}",
            f"**Created**: {self.created_at}",
            f"**Domain**: {self.domain}",
            "",
            "## Problem Statement",
            "",
            self.problem,
            "",
        ]

        if self.symptoms:
            lines.extend([
                "## Symptoms/Evidence",
                "",
                *[f"- {s}" for s in self.symptoms],
                "",
            ])

        lines.extend([
            "## Debate Transcript",
            "",
        ])

        for round_data in self.rounds:
            lines.extend([
                f"### Round {round_data.round_number}: {round_data.phase.upper()}",
                "",
            ])
            for contrib in round_data.contributions:
                lines.extend([
                    f"**[{contrib['agent'].upper()}]**",
                    "",
                    contrib['content'],
                    "",
                ])
                if contrib.get('confidence'):
                    lines.append(f"*Confidence: {contrib['confidence']}%*")
                if contrib.get('action'):
                    lines.append(f"*Action: {contrib['action']}*")
                lines.append("")

        if self.diagnosis:
            lines.extend([
                "## Final Diagnosis",
                "",
                f"**Primary Diagnosis**: {self.diagnosis.primary}",
                f"**Confidence**: {self.diagnosis.confidence * 100:.0f}%",
                f"**Root Cause**: {self.diagnosis.root_cause or 'Not determined'}",
                "",
                f"**Supporting Agents**: {', '.join(self.diagnosis.supporting_agents)}",
                "",
            ])

            if self.diagnosis.dissenting_views:
                lines.extend([
                    "### Dissenting Views",
                    "",
                    *[f"- **{d['agent']}**: {d['view']}" for d in self.diagnosis.dissenting_views],
                    "",
                ])

            if self.diagnosis.actions:
                lines.extend([
                    "### Recommended Actions",
                    "",
                    *[f"{i+1}. [{a.get('priority', 'NORMAL')}] {a['description']}" 
                      for i, a in enumerate(self.diagnosis.actions)],
                    "",
                ])

        lines.extend([
            "---",
            "",
            f"*Session completed in {self.duration_seconds:.1f} seconds*",
            f"*Consensus: {'Yes' if self.consensus_reached else 'No'}*",
        ])

        return "\n".join(lines)


class SessionManager:
    """
    Manages session persistence to disk.
    Sessions are stored in data/sessions/ as JSON and Markdown files.
    """

    def __init__(self, sessions_dir: str = None):
        """Initialize the session manager."""
        if sessions_dir is None:
            # Default to data/sessions relative to project root
            project_root = Path(__file__).parent.parent.parent
            sessions_dir = project_root / "data" / "sessions"
        
        self.sessions_dir = Path(sessions_dir)
        self._ensure_directory()
        self._index_path = self.sessions_dir / "session_index.json"

    def _ensure_directory(self):
        """Ensure the sessions directory exists."""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session: Session) -> str:
        """
        Save a session to disk.
        Creates both JSON and Markdown versions.
        Returns the session ID.
        """
        # Generate filename base
        domain_slug = session.domain.replace(" ", "_").lower()
        filename_base = f"{session.session_id}_{domain_slug}"
        
        # Save JSON
        json_path = self.sessions_dir / f"{filename_base}.json"
        with open(json_path, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)

        # Save Markdown transcript
        md_path = self.sessions_dir / f"{filename_base}.md"
        with open(md_path, 'w') as f:
            f.write(session.to_markdown())

        # Update index
        self._update_index(session, filename_base)

        return session.session_id

    def _update_index(self, session: Session, filename_base: str):
        """Update the session index with a new session."""
        index = self._load_index()
        
        index[session.session_id] = {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "problem": session.problem[:100] + "..." if len(session.problem) > 100 else session.problem,
            "domain": session.domain,
            "status": session.status,
            "consensus_reached": session.consensus_reached,
            "confidence": session.diagnosis.confidence if session.diagnosis else None,
            "files": {
                "json": f"{filename_base}.json",
                "markdown": f"{filename_base}.md"
            }
        }

        with open(self._index_path, 'w') as f:
            json.dump(index, f, indent=2)

    def _load_index(self) -> Dict:
        """Load the session index."""
        if self._index_path.exists():
            with open(self._index_path) as f:
                return json.load(f)
        return {}

    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session by ID."""
        index = self._load_index()
        
        if session_id not in index:
            return None

        json_file = index[session_id]["files"]["json"]
        json_path = self.sessions_dir / json_file

        if not json_path.exists():
            return None

        with open(json_path) as f:
            data = json.load(f)

        return self._dict_to_session(data)

    def _dict_to_session(self, data: Dict) -> Session:
        """Convert a dictionary to a Session object."""
        session = Session(
            problem=data["problem"],
            domain=data.get("domain", "general"),
            symptoms=data.get("symptoms", []),
            context=data.get("context", {}),
            session_id=data["session_id"],
            created_at=data["created_at"],
            agents_involved=data.get("agents_involved", [])
        )

        # Restore rounds
        for round_data in data.get("rounds", []):
            diagnosis_round = DiagnosisRound(
                round_number=round_data["round_number"],
                phase=round_data["phase"],
                contributions=round_data.get("contributions", []),
                timestamp=round_data.get("timestamp", "")
            )
            session.rounds.append(diagnosis_round)

        # Restore diagnosis
        if data.get("diagnosis"):
            d = data["diagnosis"]
            session.diagnosis = Diagnosis(
                primary=d["primary"],
                confidence=d["confidence"],
                root_cause=d.get("root_cause"),
                supporting_agents=d.get("supporting_agents", []),
                dissenting_views=d.get("dissenting_views", []),
                actions=d.get("actions", [])
            )

        # Restore metadata
        metadata = data.get("metadata", {})
        session.duration_seconds = metadata.get("duration_seconds", 0.0)
        session.total_tokens = metadata.get("total_tokens", 0)
        session.consensus_reached = metadata.get("consensus_reached", False)
        session.status = metadata.get("status", "unknown")

        return session

    def list_sessions(
        self,
        domain: str = None,
        status: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """List sessions with optional filtering."""
        index = self._load_index()
        sessions = list(index.values())

        # Apply filters
        if domain:
            sessions = [s for s in sessions if s.get("domain") == domain]
        if status:
            sessions = [s for s in sessions if s.get("status") == status]

        # Sort by creation date (newest first)
        sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)

        return sessions[:limit]

    def search_sessions(self, query: str, limit: int = 20) -> List[Dict]:
        """Search sessions by problem description."""
        index = self._load_index()
        query_lower = query.lower()
        
        matches = []
        for session_info in index.values():
            if query_lower in session_info.get("problem", "").lower():
                matches.append(session_info)

        matches.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        return matches[:limit]

    def get_session_stats(self) -> Dict:
        """Get statistics about sessions."""
        index = self._load_index()
        
        total = len(index)
        if total == 0:
            return {
                "total_sessions": 0,
                "by_status": {},
                "by_domain": {},
                "avg_confidence": 0,
                "consensus_rate": 0
            }

        by_status = {}
        by_domain = {}
        confidences = []
        consensus_count = 0

        for session in index.values():
            status = session.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

            domain = session.get("domain", "general")
            by_domain[domain] = by_domain.get(domain, 0) + 1

            if session.get("confidence"):
                confidences.append(session["confidence"])

            if session.get("consensus_reached"):
                consensus_count += 1

        return {
            "total_sessions": total,
            "by_status": by_status,
            "by_domain": by_domain,
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "consensus_rate": consensus_count / total if total > 0 else 0
        }
