import pytest
from src.passes.labor_pass import LaborPass


class TestLaborPass:
    def test_hrs_per_lnft(self, sample_state):
        state = LaborPass().execute(sample_state)
        # 600 / 701 = 0.8559
        assert abs(state.hrs_per_lnft - 0.8559) < 0.001

    def test_hrs_per_sqft(self, sample_state):
        state = LaborPass().execute(sample_state)
        # 600 / 1464 = 0.4098
        assert abs(state.hrs_per_sqft - 0.4098) < 0.001

    def test_labor_cost(self, sample_state):
        state = LaborPass().execute(sample_state)
        # 600 mhrs * $45/hr = $27,000
        assert state.labor_cost == pytest.approx(27_000.00, rel=1e-4)

    def test_log_populated(self, sample_state):
        state = LaborPass().execute(sample_state)
        log_text = " ".join(state.pass_log)
        assert "LaborPass" in log_text
        assert "hrs_per_lnft" in log_text

    def test_zero_mhrs_raises(self):
        with pytest.raises(ValueError):
            from src.models.project_input import ProjectInput
            ProjectInput(sqft=1464, lnft=701, mhrs=0, men=4)
