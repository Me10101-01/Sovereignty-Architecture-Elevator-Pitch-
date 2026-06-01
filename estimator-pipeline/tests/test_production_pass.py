import pytest
from src.passes.production_pass import ProductionPass


class TestProductionPass:
    def test_sqft_per_mhr_sample(self, sample_state):
        state = ProductionPass().execute(sample_state)
        # 1464 / 600 = 2.44
        assert abs(state.sqft_per_mhr - 2.44) < 0.001

    def test_lnft_per_mhr_sample(self, sample_state):
        state = ProductionPass().execute(sample_state)
        # 701 / 600 ≈ 1.1683
        assert abs(state.lnft_per_mhr - 1.1683) < 0.001

    def test_velocity_valid_for_sample(self, sample_state):
        state = ProductionPass().execute(sample_state)
        assert state.crew_velocity_valid is True
        assert state.warnings == []

    def test_gatekeeper_fires_slow_crew(self, slow_crew_state):
        state = ProductionPass().execute(slow_crew_state)
        assert state.crew_velocity_valid is False
        assert any("unrealistically slow" in w for w in state.warnings)

    def test_gatekeeper_fires_fast_crew(self, fast_crew_state):
        state = ProductionPass().execute(fast_crew_state)
        assert state.crew_velocity_valid is False
        assert any("unrealistically fast" in w for w in state.warnings)
