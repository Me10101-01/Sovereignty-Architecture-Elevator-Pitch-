import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.models.project_input  import ProjectInput
from src.models.pipeline_state import PipelineState


# ── canonical 701/1464/600/4 sample ──────────────────────────────────────────
@pytest.fixture
def sample_input() -> ProjectInput:
    return ProjectInput(sqft=1464, lnft=701, mhrs=600, men=4, shift_hours=10)


@pytest.fixture
def sample_state(sample_input) -> PipelineState:
    return PipelineState.from_input(sample_input)


# ── edge cases ────────────────────────────────────────────────────────────────
@pytest.fixture
def slow_crew_state() -> PipelineState:
    """Triggers production gatekeeper: sqft_per_mhr = 0.3 (below 0.5 floor)."""
    inp = ProjectInput(sqft=180, lnft=100, mhrs=600, men=2, shift_hours=10)
    return PipelineState.from_input(inp)


@pytest.fixture
def fast_crew_state() -> PipelineState:
    """Triggers production gatekeeper: sqft_per_mhr = 9.75 (above 8.0 ceiling)."""
    inp = ProjectInput(sqft=5850, lnft=700, mhrs=600, men=4, shift_hours=10)
    return PipelineState.from_input(inp)
