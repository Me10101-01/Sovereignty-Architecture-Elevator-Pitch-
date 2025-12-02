"""
Differential Engine - Core debate engine for multi-agent diagnosis.
Implements the House M.D. style debate system for architecture diagnosis.
"""

import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import random

from .agents import Agent, ALL_AGENTS, get_agent_by_name, HOUSE, WILSON, FOREMAN, CAMERON, CHASE, CUDDY
from .session import Session, SessionManager, Diagnosis, DiagnosisRound


# Number of rounds reserved for presentation and initial phases
RESERVED_ROUNDS = 2


class DebatePhase(Enum):
    """Phases of the differential diagnosis debate."""
    PRESENTATION = "presentation"
    HYPOTHESIS = "hypothesis"
    CHALLENGE = "challenge"
    CONVERGENCE = "convergence"
    DIAGNOSIS = "diagnosis"


@dataclass
class EngineConfig:
    """Configuration for the differential engine."""
    max_rounds: int = 5
    consensus_threshold: float = 0.67  # 2/3 majority
    timeout_seconds: float = 300.0
    include_dissent: bool = True
    output_format: str = "markdown"  # markdown, json, terminal
    
    # Agent customization
    agents: List[str] = field(default_factory=lambda: ["house", "wilson", "foreman", "cameron", "chase", "cuddy"])


class DifferentialEngine:
    """
    The core differential diagnosis engine.
    Orchestrates multi-agent debates to diagnose problems.
    """

    def __init__(
        self,
        config: EngineConfig = None,
        sessions_dir: str = None,
        llm_provider: Callable[[str, str], str] = None
    ):
        """
        Initialize the differential engine.
        
        Args:
            config: Engine configuration
            sessions_dir: Directory for session storage
            llm_provider: Optional function(system_prompt, user_prompt) -> response
                         If not provided, uses simulated responses for testing
        """
        self.config = config or EngineConfig()
        self.session_manager = SessionManager(sessions_dir)
        self.llm_provider = llm_provider or self._simulated_llm
        
        # Load active agents
        self.agents = self._load_agents()

    def _load_agents(self) -> List[Agent]:
        """Load agents based on configuration."""
        agents = []
        for agent_name in self.config.agents:
            agent = get_agent_by_name(agent_name)
            if agent:
                agents.append(agent)
        return agents if agents else ALL_AGENTS

    def diagnose(
        self,
        problem: str,
        symptoms: List[str] = None,
        domain: str = "architecture",
        context: Dict[str, Any] = None,
        urgency: str = "normal"
    ) -> Session:
        """
        Run a differential diagnosis session.
        
        Args:
            problem: The problem to diagnose
            symptoms: List of observed symptoms/evidence
            domain: Problem domain (architecture, security, performance, etc.)
            context: Additional context for the diagnosis
            urgency: Urgency level (low, normal, high, critical)
            
        Returns:
            Session object with the complete diagnosis
        """
        start_time = time.time()
        
        # Create session
        session = Session(
            problem=problem,
            domain=domain,
            symptoms=symptoms or [],
            context=context or {}
        )
        
        # Record participating agents
        for agent in self.agents:
            session.add_agent(agent.name)

        try:
            # Phase 1: Presentation (introduce the problem)
            self._run_presentation_phase(session)
            
            # Phase 2: Initial hypotheses
            self._run_hypothesis_phase(session)
            
            # Phase 3: Challenge and debate rounds (remaining rounds after presentation and hypothesis)
            for round_num in range(self.config.max_rounds - RESERVED_ROUNDS):
                if self._check_consensus(session):
                    break
                self._run_challenge_phase(session, round_num + RESERVED_ROUNDS)
            
            # Phase 4: Convergence
            self._run_convergence_phase(session)
            
            # Phase 5: Final diagnosis
            self._generate_diagnosis(session)
            
        except Exception as e:
            session.status = "failed"
            session.context["error"] = str(e)

        # Record duration
        session.duration_seconds = time.time() - start_time
        
        # Persist session
        self.session_manager.save_session(session)
        
        return session

    def _run_presentation_phase(self, session: Session):
        """Run the presentation phase where the problem is introduced."""
        diagnosis_round = session.add_round(DebatePhase.PRESENTATION.value)
        
        # The orchestrator presents the problem
        presentation = self._format_presentation(session)
        diagnosis_round.add_contribution(
            agent_name="orchestrator",
            content=presentation,
            confidence=None,
            action="Begin differential diagnosis"
        )

    def _format_presentation(self, session: Session) -> str:
        """Format the problem presentation."""
        lines = [
            f"DIFFERENTIAL DIAGNOSIS SESSION",
            f"Domain: {session.domain}",
            f"",
            f"PRESENTING PROBLEM:",
            session.problem,
            f"",
        ]
        
        if session.symptoms:
            lines.append("SYMPTOMS/EVIDENCE:")
            for symptom in session.symptoms:
                lines.append(f"- {symptom}")
            lines.append("")
            
        if session.context:
            lines.append("ADDITIONAL CONTEXT:")
            for key, value in session.context.items():
                if key != "error":
                    lines.append(f"- {key}: {value}")
                    
        return "\n".join(lines)

    def _run_hypothesis_phase(self, session: Session):
        """Run the hypothesis phase where each agent proposes initial diagnoses."""
        diagnosis_round = session.add_round(DebatePhase.HYPOTHESIS.value)
        
        for agent in self.agents:
            response = self._get_agent_response(
                agent=agent,
                session=session,
                phase=DebatePhase.HYPOTHESIS,
                previous_responses=diagnosis_round.contributions
            )
            
            diagnosis_round.add_contribution(
                agent_name=agent.name,
                content=response["content"],
                confidence=response.get("confidence"),
                action=response.get("action")
            )

    def _run_challenge_phase(self, session: Session, round_number: int):
        """Run a challenge phase where agents debate and refine hypotheses."""
        diagnosis_round = session.add_round(DebatePhase.CHALLENGE.value)
        
        for agent in self.agents:
            response = self._get_agent_response(
                agent=agent,
                session=session,
                phase=DebatePhase.CHALLENGE,
                previous_responses=self._get_all_previous_responses(session),
                round_number=round_number
            )
            
            diagnosis_round.add_contribution(
                agent_name=agent.name,
                content=response["content"],
                confidence=response.get("confidence"),
                action=response.get("action")
            )

    def _run_convergence_phase(self, session: Session):
        """Run the convergence phase where agents work toward consensus."""
        diagnosis_round = session.add_round(DebatePhase.CONVERGENCE.value)
        
        for agent in self.agents:
            response = self._get_agent_response(
                agent=agent,
                session=session,
                phase=DebatePhase.CONVERGENCE,
                previous_responses=self._get_all_previous_responses(session)
            )
            
            diagnosis_round.add_contribution(
                agent_name=agent.name,
                content=response["content"],
                confidence=response.get("confidence"),
                action=response.get("action")
            )

    def _get_agent_response(
        self,
        agent: Agent,
        session: Session,
        phase: DebatePhase,
        previous_responses: List[Dict] = None,
        round_number: int = 1
    ) -> Dict[str, Any]:
        """Get a response from an agent."""
        system_prompt = agent.get_system_prompt()
        user_prompt = agent.generate_response_prompt(
            problem=session.problem,
            symptoms=session.symptoms,
            phase=phase.value,
            previous_responses=previous_responses,
            round_number=round_number
        )
        
        response_text = self.llm_provider(system_prompt, user_prompt)
        
        # Parse response
        return self._parse_agent_response(response_text, agent.name)

    def _parse_agent_response(self, response: str, agent_name: str) -> Dict[str, Any]:
        """Parse an agent's response to extract structured data."""
        result = {
            "content": response,
            "confidence": None,
            "action": None
        }
        
        # Try to extract confidence
        lines = response.split('\n')
        for line in lines:
            line_lower = line.lower()
            if "confidence:" in line_lower:
                try:
                    # Extract percentage
                    match = re.search(r'(\d+)%?', line)
                    if match:
                        result["confidence"] = int(match.group(1))
                except (ValueError, AttributeError):
                    pass
            elif "action:" in line_lower or "challenge:" in line_lower:
                result["action"] = line.split(":", 1)[-1].strip()
                
        return result

    def _get_all_previous_responses(self, session: Session) -> List[Dict]:
        """Get all previous responses from the session."""
        responses = []
        for round_data in session.rounds:
            for contrib in round_data.contributions:
                responses.append(contrib)
        return responses

    def _check_consensus(self, session: Session) -> bool:
        """Check if agents have reached consensus."""
        if not session.rounds:
            return False
            
        last_round = session.rounds[-1]
        confidences = [
            c.get("confidence", 0) or 0 
            for c in last_round.contributions 
            if c.get("confidence")
        ]
        
        if not confidences:
            return False
            
        avg_confidence = sum(confidences) / len(confidences)
        return avg_confidence >= self.config.consensus_threshold * 100

    def _generate_diagnosis(self, session: Session):
        """Generate the final diagnosis from the debate."""
        # Analyze all contributions to find the most supported hypothesis
        hypotheses = self._extract_hypotheses(session)
        
        if not hypotheses:
            # Fallback diagnosis if no clear hypotheses emerged
            session.set_diagnosis(Diagnosis(
                primary="Unable to reach conclusive diagnosis",
                confidence=0.3,
                root_cause="Insufficient evidence or conflicting analyses",
                supporting_agents=[],
                dissenting_views=[],
                actions=[{
                    "description": "Gather more evidence and retry diagnosis",
                    "priority": "HIGH"
                }]
            ))
            return

        # Find the most supported hypothesis
        best_hypothesis = max(hypotheses, key=lambda h: h.get("support_count", 0))
        
        # Calculate confidence
        total_agents = len(self.agents)
        support_count = best_hypothesis.get("support_count", 1)
        confidence = min(support_count / total_agents, 0.95)
        
        # Generate actions based on the diagnosis
        actions = self._generate_actions(best_hypothesis, session)
        
        # Find dissenting views
        dissenting = [
            h for h in hypotheses 
            if h["hypothesis"] != best_hypothesis["hypothesis"] 
            and h.get("support_count", 0) >= 1
        ]
        
        session.set_diagnosis(Diagnosis(
            primary=best_hypothesis["hypothesis"],
            confidence=confidence,
            root_cause=best_hypothesis.get("root_cause"),
            supporting_agents=best_hypothesis.get("supporters", []),
            dissenting_views=[
                {"agent": d.get("supporters", ["Unknown"])[0], "view": d["hypothesis"]}
                for d in dissenting[:2]  # Keep top 2 dissenting views
            ],
            actions=actions
        ))

    def _extract_hypotheses(self, session: Session) -> List[Dict]:
        """Extract hypotheses from the debate."""
        # Simple extraction based on contributions
        # In a real implementation, this would use NLP/LLM for better extraction
        hypotheses = {}
        
        for round_data in session.rounds:
            if round_data.phase in [DebatePhase.HYPOTHESIS.value, DebatePhase.CONVERGENCE.value]:
                for contrib in round_data.contributions:
                    if contrib["agent"] == "orchestrator":
                        continue
                        
                    # Use the first significant sentence as hypothesis
                    content = contrib["content"]
                    hypothesis_text = content.split('.')[0] if '.' in content else content[:100]
                    
                    # Simple deduplication by similarity
                    found_similar = False
                    for key in hypotheses:
                        if self._similar_enough(key, hypothesis_text):
                            hypotheses[key]["support_count"] += 1
                            if contrib["agent"] not in hypotheses[key]["supporters"]:
                                hypotheses[key]["supporters"].append(contrib["agent"])
                            found_similar = True
                            break
                    
                    if not found_similar:
                        hypotheses[hypothesis_text] = {
                            "hypothesis": hypothesis_text,
                            "support_count": 1,
                            "supporters": [contrib["agent"]],
                            "root_cause": None
                        }
        
        return list(hypotheses.values())

    def _similar_enough(self, text1: str, text2: str) -> bool:
        """Check if two texts are similar enough to be the same hypothesis."""
        # Simple word overlap check
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return False
            
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) > 0.5

    def _generate_actions(self, hypothesis: Dict, session: Session) -> List[Dict]:
        """Generate recommended actions based on the diagnosis."""
        actions = []
        
        # Priority 1: Immediate action
        actions.append({
            "description": f"Investigate and validate: {hypothesis['hypothesis'][:50]}...",
            "priority": "IMMEDIATE"
        })
        
        # Priority 2: Short-term action
        actions.append({
            "description": "Implement monitoring to track the identified issue",
            "priority": "24_HOURS"
        })
        
        # Priority 3: Long-term action
        actions.append({
            "description": "Document findings and update operational runbooks",
            "priority": "1_WEEK"
        })
        
        # Priority 4: Follow-up
        actions.append({
            "description": "Schedule follow-up diagnosis session in 2 weeks",
            "priority": "ONGOING"
        })
        
        return actions

    def _simulated_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Simulated LLM for testing purposes.
        In production, this would be replaced with actual LLM calls.
        """
        # Determine which agent based on system prompt
        agent_name = "Unknown"
        for agent in ALL_AGENTS:
            if agent.name in system_prompt:
                agent_name = agent.name
                break

        # Generate phase-appropriate response
        if "HYPOTHESIS" in user_prompt:
            return self._simulated_hypothesis_response(agent_name, user_prompt)
        elif "CHALLENGE" in user_prompt:
            return self._simulated_challenge_response(agent_name, user_prompt)
        elif "CONVERGENCE" in user_prompt:
            return self._simulated_convergence_response(agent_name, user_prompt)
        else:
            return f"[{agent_name.upper()}]\nAnalyzing the problem...\n[Confidence: 50%]"

    def _simulated_hypothesis_response(self, agent_name: str, prompt: str) -> str:
        """Generate a simulated hypothesis response."""
        responses = {
            "House": """[HOUSE]
This looks like a classic case of premature optimization. Everyone's looking at the symptoms, 
but the real problem is upstream. Check your caching layer - I bet it's not the database at all.
[Confidence: 72%]
[Challenge: Prove me wrong with metrics]""",

            "Wilson": """[WILSON]
Before we dive into technical solutions, let's consider the impact. Who's affected by this? 
What's the business cost of the current state? We need to prioritize based on user impact.
[Confidence: 65%]
[Action: Map stakeholder impact first]""",

            "Foreman": """[FOREMAN]
I'm not buying the cache theory without data. Show me the metrics - latency distributions, 
error rates, and resource utilization. We need evidence before we start treating.
[Confidence: 55%]
[Challenge: Request metrics dashboard access]""",

            "Cameron": """[CAMERON]
What about edge cases? Are there specific user segments experiencing worse symptoms? 
Mobile users, international traffic, users with slow connections?
[Confidence: 60%]
[Action: Segment analysis by user type]""",

            "Chase": """[CHASE]
Why are we overcomplicating this? Add more replicas, scale horizontally. 
We can investigate while the immediate pain is resolved.
[Confidence: 70%]
[Action: Scale up resources now]""",

            "Cuddy": """[CUDDY]
Chase, scaling costs money. We need a sustainable solution, not just throwing resources 
at the problem. What's the budget impact of each proposed solution?
[Confidence: 68%]
[Action: Cost-benefit analysis required]"""
        }
        
        return responses.get(agent_name, f"[{agent_name.upper()}]\nPending analysis...\n[Confidence: 50%]")

    def _simulated_challenge_response(self, agent_name: str, prompt: str) -> str:
        """Generate a simulated challenge response."""
        responses = {
            "House": """[HOUSE]
Foreman's right - we need the data. But I still think it's caching. The symptom pattern 
matches cache invalidation storms. Look at the cache hit rate during peak hours.
[Confidence: 78%]
[Challenge: Check cache metrics during incident windows]""",

            "Wilson": """[WILSON]
House and Foreman are both making good points. Can we run both investigations in parallel? 
User impact data + technical metrics. We need the full picture.
[Confidence: 72%]
[Action: Parallel investigation tracks]""",

            "Foreman": """[FOREMAN]
I pulled some preliminary data. House might be onto something - cache hit rate drops 30% 
during peak hours. But why? We need to trace the invalidation triggers.
[Confidence: 75%]
[Action: Trace cache invalidation patterns]""",

            "Cameron": """[CAMERON]
I found an interesting pattern - the symptoms correlate with a feature flag rollout last week. 
Could the new feature be bypassing the cache?
[Confidence: 80%]
[Action: Review feature flag impact on caching]""",

            "Chase": """[CHASE]
Cameron's onto something. New feature + cache bypass = increased DB load. 
Feature flag it down to 10% while we fix the caching.
[Confidence: 82%]
[Action: Rollback feature flag to 10%]""",

            "Cuddy": """[CUDDY]
Good work, team. Cameron and Chase have a viable hypothesis. The feature flag rollback 
is low-risk and reversible. Let's do that while we implement proper caching.
[Confidence: 85%]
[Action: Approve feature flag rollback]"""
        }
        
        return responses.get(agent_name, f"[{agent_name.upper()}]\nChallenging assumptions...\n[Confidence: 60%]")

    def _simulated_convergence_response(self, agent_name: str, prompt: str) -> str:
        """Generate a simulated convergence response."""
        confidence = random.randint(78, 92)
        
        return f"""[{agent_name.upper()}]
Based on the evidence, I support the diagnosis: New feature route bypassing cache layer. 
The feature flag rollback is the right immediate action while we implement proper caching.
[Confidence: {confidence}%]
[Action: Support the recommended remediation plan]"""


def create_engine(
    sessions_dir: str = None,
    llm_provider: Callable[[str, str], str] = None,
    **config_kwargs
) -> DifferentialEngine:
    """
    Factory function to create a configured differential engine.
    
    Args:
        sessions_dir: Directory for session storage
        llm_provider: Optional LLM provider function
        **config_kwargs: Additional configuration options
        
    Returns:
        Configured DifferentialEngine instance
    """
    config = EngineConfig(**config_kwargs)
    return DifferentialEngine(
        config=config,
        sessions_dir=sessions_dir,
        llm_provider=llm_provider
    )
