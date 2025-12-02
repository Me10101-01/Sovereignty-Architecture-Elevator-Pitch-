"""
Debate Orchestration for the Differential Engine

Manages the structured debate rounds where specialists
analyze, challenge, and evolve understanding.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

from .specialists import Specialist, TEAM, get_all_specialists


class DebatePhase(Enum):
    """Phases of the differential diagnosis debate."""
    CASE_PRESENTATION = "case_presentation"
    INITIAL_HYPOTHESES = "initial_hypotheses"
    CROSS_EXAMINATION = "cross_examination"
    SYNTHESIS = "synthesis"
    COMPLETE = "complete"


@dataclass
class DebateRound:
    """A single round of debate between specialists."""
    
    phase: DebatePhase
    speaker: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    target: Optional[str] = None  # For cross-examination
    round_number: int = 0
    
    def to_markdown(self) -> str:
        """Convert this round to markdown format."""
        if self.target:
            header = f"**{self.speaker} → {self.target}**"
        else:
            header = f"**{self.speaker}**"
        return f"{header}\n\n{self.content}\n"


@dataclass
class DebateSession:
    """A complete debate session with all rounds."""
    
    session_id: str
    raw_input: str
    rounds: list[DebateRound] = field(default_factory=list)
    current_phase: DebatePhase = DebatePhase.CASE_PRESENTATION
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def add_round(self, round_obj: DebateRound) -> None:
        """Add a round to the session."""
        round_obj.round_number = len(self.rounds) + 1
        self.rounds.append(round_obj)
    
    def get_rounds_by_phase(self, phase: DebatePhase) -> list[DebateRound]:
        """Get all rounds in a specific phase."""
        return [r for r in self.rounds if r.phase == phase]
    
    def get_rounds_by_speaker(self, speaker: str) -> list[DebateRound]:
        """Get all rounds by a specific speaker."""
        return [r for r in self.rounds if r.speaker.lower() == speaker.lower()]
    
    def to_markdown(self) -> str:
        """Convert the entire session to markdown format."""
        lines = [
            f"# Differential Session: {self.session_id}",
            f"*Started: {self.started_at.isoformat()}*",
            "",
            "## Patient Presentation",
            "",
            "```",
            self.raw_input,
            "```",
            "",
        ]
        
        # Group rounds by phase
        for phase in DebatePhase:
            phase_rounds = self.get_rounds_by_phase(phase)
            if phase_rounds:
                lines.append(f"## {phase.value.replace('_', ' ').title()}")
                lines.append("")
                for round_obj in phase_rounds:
                    lines.append(round_obj.to_markdown())
        
        if self.completed_at:
            lines.append(f"*Completed: {self.completed_at.isoformat()}*")
        
        return "\n".join(lines)


class DebateOrchestrator:
    """Orchestrates the debate between specialists."""
    
    def __init__(self) -> None:
        self.specialists = get_all_specialists()
        self.current_session: Optional[DebateSession] = None
    
    def start_session(self, raw_input: str) -> DebateSession:
        """Start a new debate session."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = DebateSession(
            session_id=session_id,
            raw_input=raw_input,
        )
        return self.current_session
    
    def present_case(self, presentation: str) -> DebateRound:
        """Present the case to all specialists."""
        if not self.current_session:
            raise ValueError("No active session. Call start_session first.")
        
        round_obj = DebateRound(
            phase=DebatePhase.CASE_PRESENTATION,
            speaker="Moderator",
            content=presentation,
        )
        self.current_session.add_round(round_obj)
        self.current_session.current_phase = DebatePhase.INITIAL_HYPOTHESES
        return round_obj
    
    def add_hypothesis(self, specialist: Specialist, content: str) -> DebateRound:
        """Add an initial hypothesis from a specialist."""
        if not self.current_session:
            raise ValueError("No active session.")
        
        round_obj = DebateRound(
            phase=DebatePhase.INITIAL_HYPOTHESES,
            speaker=specialist.name,
            content=content,
        )
        self.current_session.add_round(round_obj)
        return round_obj
    
    def add_challenge(
        self,
        challenger: Specialist,
        target: Specialist,
        content: str,
    ) -> DebateRound:
        """Add a cross-examination challenge."""
        if not self.current_session:
            raise ValueError("No active session.")
        
        round_obj = DebateRound(
            phase=DebatePhase.CROSS_EXAMINATION,
            speaker=challenger.name,
            target=target.name,
            content=content,
        )
        self.current_session.add_round(round_obj)
        return round_obj
    
    def add_response(self, responder: Specialist, content: str) -> DebateRound:
        """Add a response to a challenge."""
        if not self.current_session:
            raise ValueError("No active session.")
        
        round_obj = DebateRound(
            phase=DebatePhase.CROSS_EXAMINATION,
            speaker=responder.name,
            content=content,
        )
        self.current_session.add_round(round_obj)
        return round_obj
    
    def add_synthesis(self, content: str) -> DebateRound:
        """Add the final synthesis from House."""
        if not self.current_session:
            raise ValueError("No active session.")
        
        round_obj = DebateRound(
            phase=DebatePhase.SYNTHESIS,
            speaker="House",
            content=content,
        )
        self.current_session.add_round(round_obj)
        self.current_session.current_phase = DebatePhase.COMPLETE
        self.current_session.completed_at = datetime.now()
        return round_obj
    
    def get_context_for_specialist(self, specialist: Specialist) -> str:
        """Get the debate context formatted for a specific specialist."""
        if not self.current_session:
            return ""
        
        lines = [
            f"# Debate Context for {specialist.name}",
            "",
            "## Your Role",
            specialist.system_prompt,
            "",
            "## Case",
            self.current_session.raw_input,
            "",
            "## Debate So Far",
        ]
        
        for round_obj in self.current_session.rounds:
            lines.append(round_obj.to_markdown())
        
        lines.extend([
            "",
            "## Your Response",
            f"Respond as {specialist.name} using your distinctive style.",
            f"Token signature to use: {specialist.token_signature[0]}",
        ])
        
        return "\n".join(lines)
    
    def get_session_markdown(self) -> str:
        """Get the current session as markdown."""
        if not self.current_session:
            return ""
        return self.current_session.to_markdown()


# Cross-examination pairings (who challenges whom)
CROSS_EXAMINATION_PAIRS = [
    ("chase", "foreman"),    # Pragmatist challenges Structuralist
    ("wilson", "cameron"),   # Devil's Advocate challenges Humanist
    ("foreman", "house"),    # Structuralist challenges Synthesizer
    ("cameron", "wilson"),   # Humanist challenges Devil's Advocate
]


def get_challenge_pairs() -> list[tuple[Specialist, Specialist]]:
    """Get the cross-examination pairs as Specialist objects."""
    return [
        (TEAM[challenger], TEAM[target])
        for challenger, target in CROSS_EXAMINATION_PAIRS
    ]
