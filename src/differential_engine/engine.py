"""
Differential Engine: The Core Psychoanalysis System

This is the main engine that orchestrates multi-agent debate
to evolve raw thoughts into structured understanding.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

from .specialists import Specialist, TEAM, get_all_specialists
from .debate import (
    DebateOrchestrator,
    DebateSession,
    DebateRound,
    DebatePhase,
    get_challenge_pairs,
)


# Type alias for LLM callback functions
LLMCallback = Callable[[str, str], str]


@dataclass
class DiagnosisResult:
    """The result of a differential diagnosis."""
    
    session: DebateSession
    diagnosis: str = ""
    prognosis: str = ""
    treatment: str = ""
    contraindications: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session.session_id,
            "diagnosis": self.diagnosis,
            "prognosis": self.prognosis,
            "treatment": self.treatment,
            "contraindications": self.contraindications,
            "started_at": self.session.started_at.isoformat(),
            "completed_at": (
                self.session.completed_at.isoformat() 
                if self.session.completed_at else None
            ),
        }
    
    def to_markdown(self) -> str:
        """Convert to full markdown report."""
        lines = [
            self.session.to_markdown(),
            "",
            "---",
            "",
            "# Final Diagnosis",
            "",
            "## Diagnosis",
            self.diagnosis or "_Not yet determined_",
            "",
            "## Prognosis",
            self.prognosis or "_Not yet determined_",
            "",
            "## Treatment Plan",
            self.treatment or "_Not yet determined_",
            "",
            "## Contraindications",
            self.contraindications or "_Not yet determined_",
        ]
        return "\n".join(lines)


class DifferentialEngine:
    """
    The main engine for running differential diagnosis sessions.
    
    Usage:
        engine = DifferentialEngine()
        engine.set_llm_callback(your_llm_function)
        result = engine.diagnose("your raw thoughts here")
    """
    
    def __init__(
        self,
        data_dir: Optional[Path] = None,
        auto_save: bool = True,
    ) -> None:
        self.orchestrator = DebateOrchestrator()
        self.data_dir = data_dir or Path("data/sessions")
        self.auto_save = auto_save
        self.llm_callback: Optional[LLMCallback] = None
        
        # Create data directory if it doesn't exist
        if self.auto_save:
            self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def set_llm_callback(self, callback: LLMCallback) -> None:
        """
        Set the LLM callback for generating specialist responses.
        
        The callback should accept:
        - system_prompt (str): The system prompt for the specialist
        - user_prompt (str): The user/context prompt
        
        And return:
        - response (str): The LLM's response
        """
        self.llm_callback = callback
    
    def _generate_response(
        self,
        specialist: Specialist,
        context: str,
    ) -> str:
        """Generate a response for a specialist using the LLM callback."""
        if not self.llm_callback:
            # Return a placeholder if no callback is set
            return f"[{specialist.name}]: _LLM callback not configured. " \
                   f"Set with engine.set_llm_callback(your_function)_\n\n" \
                   f"Context received:\n{context[:200]}..."
        
        return self.llm_callback(specialist.system_prompt, context)
    
    def _format_case_presentation(self, raw_input: str) -> str:
        """Format raw input as a case presentation."""
        return f"""# Case Presentation

## Patient Presents With
{raw_input}

## Initial Observations
- Input length: {len(raw_input)} characters
- Input structure: {'Multi-paragraph' if raw_input.count('\\n\\n') > 1 else 'Single block'}
- Key terms detected: [Automatic detection pending]

## Request for Diagnosis
Please analyze this input from your specialist perspective.
Identify patterns, structure, intent, risks, and actionable elements."""

    def diagnose(
        self,
        raw_input: str,
        interactive: bool = False,
    ) -> DiagnosisResult:
        """
        Run a full differential diagnosis on the input.
        
        Args:
            raw_input: The unstructured thoughts to analyze
            interactive: If True, pause between phases for user input
            
        Returns:
            DiagnosisResult with the full analysis
        """
        # Start session
        session = self.orchestrator.start_session(raw_input)
        
        # Phase 1: Case Presentation
        case_presentation = self._format_case_presentation(raw_input)
        self.orchestrator.present_case(case_presentation)
        
        # Phase 2: Initial Hypotheses
        specialists = get_all_specialists()
        for specialist in specialists[:-1]:  # All except House
            context = self.orchestrator.get_context_for_specialist(specialist)
            response = self._generate_response(specialist, context)
            self.orchestrator.add_hypothesis(specialist, response)
        
        # Phase 3: Cross-Examination
        challenge_pairs = get_challenge_pairs()
        for challenger, target in challenge_pairs:
            # Generate challenge
            context = self.orchestrator.get_context_for_specialist(challenger)
            challenge_prompt = f"\nChallenge {target.name}'s analysis. " \
                             f"Find weaknesses or blind spots."
            response = self._generate_response(
                challenger,
                context + challenge_prompt,
            )
            self.orchestrator.add_challenge(challenger, target, response)
        
        # Phase 4: Synthesis by House
        house = TEAM["house"]
        synthesis_context = self.orchestrator.get_context_for_specialist(house)
        synthesis_prompt = """
Now synthesize all perspectives into a final diagnosis.

Your output MUST include these sections:
1. DIAGNOSIS: What this idea/problem actually is at its core
2. PROGNOSIS: Where this is headed, likely evolution
3. TREATMENT: Concrete next steps and recommendations
4. CONTRAINDICATIONS: What to avoid, risks to manage

Be direct. Be insightful. Make the call."""
        
        synthesis = self._generate_response(
            house,
            synthesis_context + synthesis_prompt,
        )
        self.orchestrator.add_synthesis(synthesis)
        
        # Parse synthesis into result
        result = DiagnosisResult(session=session)
        result = self._parse_synthesis(result, synthesis)
        
        # Save session
        if self.auto_save:
            self._save_session(result)
        
        return result
    
    def _parse_synthesis(
        self,
        result: DiagnosisResult,
        synthesis: str,
    ) -> DiagnosisResult:
        """Parse the synthesis into structured result fields."""
        # Simple parsing - look for section headers
        sections = {
            "diagnosis": "",
            "prognosis": "",
            "treatment": "",
            "contraindications": "",
        }
        
        current_section = None
        lines = synthesis.split("\n")
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if "diagnosis:" in line_lower or "## diagnosis" in line_lower:
                current_section = "diagnosis"
                # Get content after colon if on same line
                if ":" in line:
                    sections["diagnosis"] = line.split(":", 1)[1].strip()
            elif "prognosis:" in line_lower or "## prognosis" in line_lower:
                current_section = "prognosis"
                if ":" in line:
                    sections["prognosis"] = line.split(":", 1)[1].strip()
            elif "treatment:" in line_lower or "## treatment" in line_lower:
                current_section = "treatment"
                if ":" in line:
                    sections["treatment"] = line.split(":", 1)[1].strip()
            elif "contraindications:" in line_lower or "## contraindications" in line_lower:
                current_section = "contraindications"
                if ":" in line:
                    sections["contraindications"] = line.split(":", 1)[1].strip()
            elif current_section and line.strip():
                sections[current_section] += "\n" + line.strip()
        
        result.diagnosis = sections["diagnosis"].strip()
        result.prognosis = sections["prognosis"].strip()
        result.treatment = sections["treatment"].strip()
        result.contraindications = sections["contraindications"].strip()
        
        # If parsing failed, use the whole synthesis
        if not any([result.diagnosis, result.prognosis, result.treatment]):
            result.diagnosis = synthesis
        
        return result
    
    def _save_session(self, result: DiagnosisResult) -> Path:
        """Save the session to a markdown file."""
        filename = f"session_{result.session.session_id}.md"
        filepath = self.data_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(result.to_markdown())
        
        # Also save JSON metadata
        json_path = self.data_dir / f"session_{result.session.session_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2)
        
        return filepath
    
    def load_session(self, session_id: str) -> Optional[DiagnosisResult]:
        """Load a previous session by ID."""
        json_path = self.data_dir / f"session_{session_id}.json"
        md_path = self.data_dir / f"session_{session_id}.md"
        
        if not json_path.exists():
            return None
        
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        
        # Reconstruct minimal result
        session = DebateSession(
            session_id=data["session_id"],
            raw_input="[Loaded from saved session]",
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data["completed_at"] else None
            ),
        )
        
        result = DiagnosisResult(
            session=session,
            diagnosis=data["diagnosis"],
            prognosis=data["prognosis"],
            treatment=data["treatment"],
            contraindications=data["contraindications"],
        )
        
        return result
    
    def list_sessions(self) -> list[str]:
        """List all saved session IDs."""
        if not self.data_dir.exists():
            return []
        
        sessions = []
        for f in self.data_dir.glob("session_*.json"):
            session_id = f.stem.replace("session_", "")
            sessions.append(session_id)
        
        return sorted(sessions, reverse=True)


# Example LLM callback implementations

def mock_llm_callback(system_prompt: str, user_prompt: str) -> str:
    """A mock LLM callback for testing without API access."""
    # Extract specialist name from system prompt
    if "House" in system_prompt:
        return """
DIAGNOSIS: This is a raw idea seeking structure and validation.

PROGNOSIS: With proper iteration, this could evolve into something actionable.

TREATMENT: 
1. Define the core problem more precisely
2. Identify key stakeholders
3. Create a minimal prototype

CONTRAINDICATIONS: 
- Don't over-engineer before validating
- Avoid scope creep in early stages
"""
    elif "Foreman" in system_prompt:
        return """I see three distinct components here:
1. The core idea/problem statement
2. The proposed solution approach
3. The implementation constraints

Structurally, we need to address each layer systematically."""
    elif "Cameron" in system_prompt:
        return """But what are you really trying to achieve here? 

The deeper purpose seems to be about [understanding/creating/solving].
The human element we need to consider is [impact/values/meaning]."""
    elif "Chase" in system_prompt:
        return """Okay, but what can we actually build right now?

The next concrete step is to:
1. Define the minimal viable version
2. Identify the first user/test case
3. Set a deadline for the first iteration"""
    elif "Wilson" in system_prompt:
        return """Have you considered that this might fail because:
1. The scope is too broad initially
2. The target user isn't clearly defined
3. There may be existing solutions we're overlooking

The blind spot here is [assumption about feasibility/market/resources]."""
    else:
        return "_Unknown specialist_"
