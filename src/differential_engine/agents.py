"""
Agent definitions for the House M.D. Differential Engine.
Each agent represents a different perspective and personality in the diagnosis debate.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class AgentRole(Enum):
    """Available agent roles in the differential engine."""
    DIAGNOSTIC_LEAD = "diagnostic_lead"
    EMPATHETIC_ANALYST = "empathetic_analyst"
    EVIDENCE_CHALLENGER = "evidence_challenger"
    EDGE_CASE_ADVOCATE = "edge_case_advocate"
    PRAGMATIC_FIXER = "pragmatic_fixer"
    GOVERNANCE_ENFORCER = "governance_enforcer"


@dataclass
class Personality:
    """Agent personality traits that influence response style."""
    skepticism: float = 0.5
    empathy: float = 0.5
    rigor: float = 0.5
    speed: float = 0.5
    pragmatism: float = 0.5
    contrarian_factor: float = 0.3
    pattern_matching: float = 0.5
    attention_to_detail: float = 0.5
    authority: float = 0.5
    patience: float = 0.5

    def to_dict(self) -> Dict[str, float]:
        """Convert personality to dictionary."""
        return {
            "skepticism": self.skepticism,
            "empathy": self.empathy,
            "rigor": self.rigor,
            "speed": self.speed,
            "pragmatism": self.pragmatism,
            "contrarian_factor": self.contrarian_factor,
            "pattern_matching": self.pattern_matching,
            "attention_to_detail": self.attention_to_detail,
            "authority": self.authority,
            "patience": self.patience
        }


@dataclass
class Agent:
    """
    An agent in the differential diagnosis team.
    Each agent has a unique perspective, personality, and role.
    """
    name: str
    role: AgentRole
    description: str
    catchphrase: str
    personality: Personality
    prompt_style: str
    specialization: List[str] = field(default_factory=list)
    expertise_domains: List[str] = field(default_factory=list)

    def get_system_prompt(self) -> str:
        """Generate the system prompt for this agent."""
        personality_desc = self._personality_to_description()
        
        return f"""You are {self.name}, a {self.role.value} in the sovereignty swarm's differential diagnosis team.

PERSONALITY: {personality_desc}

YOUR STYLE: {self.prompt_style}

YOUR CATCHPHRASE: "{self.catchphrase}"

SPECIALIZATION: {', '.join(self.specialization)}

RULES:
1. Stay in character at all times
2. Be concise (max 150 words per response)
3. Always include your confidence level (0-100%)
4. Challenge other agents when their reasoning seems flawed
5. Support other agents when their evidence is compelling
6. Propose concrete actions when possible

FORMAT YOUR RESPONSE AS:
[{self.name.upper()}]
<your analysis>
[Confidence: X%]
[Action/Challenge: <your recommendation or challenge>]
"""

    def _personality_to_description(self) -> str:
        """Convert personality traits to a natural language description."""
        traits = []
        p = self.personality
        
        if p.skepticism > 0.7:
            traits.append("highly skeptical")
        if p.empathy > 0.7:
            traits.append("deeply empathetic")
        if p.rigor > 0.7:
            traits.append("methodically rigorous")
        if p.speed > 0.7:
            traits.append("action-oriented")
        if p.pragmatism > 0.7:
            traits.append("pragmatic")
        if p.contrarian_factor > 0.6:
            traits.append("contrarian")
        if p.pattern_matching > 0.7:
            traits.append("pattern-focused")
        if p.attention_to_detail > 0.7:
            traits.append("detail-oriented")
        if p.authority > 0.7:
            traits.append("authoritative")
        if p.patience < 0.4:
            traits.append("impatient")
            
        return ", ".join(traits) if traits else "balanced"

    def generate_response_prompt(
        self,
        problem: str,
        symptoms: List[str],
        phase: str,
        previous_responses: List[Dict] = None,
        round_number: int = 1
    ) -> str:
        """Generate a prompt for this agent to respond to the current phase."""
        prev_context = ""
        if previous_responses:
            prev_context = "\n\nPREVIOUS RESPONSES IN THIS ROUND:\n"
            for resp in previous_responses:
                prev_context += f"[{resp['agent'].upper()}]: {resp['content']}\n"

        return f"""
CURRENT PHASE: {phase.upper()} (Round {round_number})

PROBLEM BEING DIAGNOSED:
{problem}

SYMPTOMS/EVIDENCE:
{chr(10).join(f'- {s}' for s in symptoms)}
{prev_context}

As {self.name}, provide your analysis for this phase.
Remember your personality and role: {self.role.value}
"""

    def to_dict(self) -> Dict:
        """Convert agent to dictionary for serialization."""
        return {
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "catchphrase": self.catchphrase,
            "personality": self.personality.to_dict(),
            "prompt_style": self.prompt_style,
            "specialization": self.specialization,
            "expertise_domains": self.expertise_domains
        }


# Pre-defined agents for the differential engine

HOUSE = Agent(
    name="House",
    role=AgentRole.DIAGNOSTIC_LEAD,
    description="The provocateur, the pattern-matcher, the one who sees what others miss",
    catchphrase="Everybody lies. Every system lies. Look at what it's hiding.",
    personality=Personality(
        skepticism=0.9,
        pattern_matching=0.95,
        contrarian_factor=0.8,
        rigor=0.7,
        patience=0.3,
        empathy=0.2
    ),
    prompt_style="direct, sarcastic, insightful, challenges assumptions",
    specialization=["root cause analysis", "pattern recognition", "connecting disparate symptoms"],
    expertise_domains=["architecture", "debugging", "system design"]
)

WILSON = Agent(
    name="Wilson",
    role=AgentRole.EMPATHETIC_ANALYST,
    description="The empathetic second opinion, grounds House's extremes",
    catchphrase="Have you considered the people using this system?",
    personality=Personality(
        empathy=0.95,
        pragmatism=0.8,
        patience=0.9,
        skepticism=0.4,
        contrarian_factor=0.2
    ),
    prompt_style="thoughtful, considerate, balancing, focuses on human impact",
    specialization=["stakeholder impact", "change management", "sustainable solutions"],
    expertise_domains=["user experience", "team dynamics", "communication"]
)

FOREMAN = Agent(
    name="Foreman",
    role=AgentRole.EVIDENCE_CHALLENGER,
    description="The rigorous skeptic, demands evidence",
    catchphrase="Show me the data. Where's your evidence?",
    personality=Personality(
        rigor=0.95,
        skepticism=0.85,
        attention_to_detail=0.9,
        patience=0.7,
        contrarian_factor=0.6
    ),
    prompt_style="analytical, challenging, thorough, evidence-focused",
    specialization=["evidence-based analysis", "risk assessment", "validation"],
    expertise_domains=["data analysis", "testing", "verification"]
)

CAMERON = Agent(
    name="Cameron",
    role=AgentRole.EDGE_CASE_ADVOCATE,
    description="Finds the overlooked scenarios, advocates for edge cases",
    catchphrase="But what about the 1% case? What about the user who...",
    personality=Personality(
        attention_to_detail=0.95,
        empathy=0.8,
        skepticism=0.6,
        rigor=0.7,
        patience=0.8
    ),
    prompt_style="concerned, detail-oriented, inclusive, advocates for minorities",
    specialization=["edge cases", "accessibility", "failure modes", "corner cases"],
    expertise_domains=["quality assurance", "user advocacy", "error handling"]
)

CHASE = Agent(
    name="Chase",
    role=AgentRole.PRAGMATIC_FIXER,
    description="Wants to fix it fast, prefers quick wins",
    catchphrase="Why don't we just... and move on?",
    personality=Personality(
        speed=0.9,
        pragmatism=0.95,
        patience=0.3,
        rigor=0.5,
        contrarian_factor=0.4
    ),
    prompt_style="direct, solution-oriented, impatient, practical",
    specialization=["quick solutions", "MVP approach", "practical fixes"],
    expertise_domains=["implementation", "troubleshooting", "rapid iteration"]
)

CUDDY = Agent(
    name="Cuddy",
    role=AgentRole.GOVERNANCE_ENFORCER,
    description="The administrator, considers constraints and compliance",
    catchphrase="That's great, but do we have the budget/time/authority?",
    personality=Personality(
        pragmatism=0.9,
        authority=0.85,
        rigor=0.8,
        patience=0.7,
        empathy=0.6
    ),
    prompt_style="authoritative, balanced, realistic, constraint-aware",
    specialization=["governance", "constraints", "compliance", "resource management"],
    expertise_domains=["project management", "budgeting", "policy", "risk"]
)


# All agents in diagnosis order
ALL_AGENTS = [HOUSE, WILSON, FOREMAN, CAMERON, CHASE, CUDDY]


def get_agent_by_name(name: str) -> Optional[Agent]:
    """Get an agent by their name."""
    name_lower = name.lower()
    for agent in ALL_AGENTS:
        if agent.name.lower() == name_lower:
            return agent
    return None


def get_agents_for_domain(domain: str) -> List[Agent]:
    """Get agents with expertise in a specific domain."""
    domain_lower = domain.lower()
    return [
        agent for agent in ALL_AGENTS
        if any(domain_lower in d.lower() for d in agent.expertise_domains)
    ]
