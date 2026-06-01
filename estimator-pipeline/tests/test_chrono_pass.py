import pytest
from src.passes.chrono_pass import ChronoPass


class TestChronoPass:
    def test_hrs_per_man(self, sample_state):
        state = ChronoPass().execute(sample_state)
        # 600 / 4 = 150
        assert state.hrs_per_man == pytest.approx(150.0)

    def test_total_days(self, sample_state):
        state = ChronoPass().execute(sample_state)
        # 150 hrs / 10-hr shift = 15 days
        assert state.total_days == pytest.approx(15.0)

    def test_total_weeks(self, sample_state):
        state = ChronoPass().execute(sample_state)
        # 15 days / 5 days-per-week = 3.0 weeks
        assert state.total_weeks == pytest.approx(3.0)

    def test_8hr_shift_extends_schedule(self):
        from src.models.project_input  import ProjectInput
        from src.models.pipeline_state import PipelineState
        inp   = ProjectInput(sqft=1464, lnft=701, mhrs=600, men=4, shift_hours=8)
        state = PipelineState.from_input(inp)
        state = ChronoPass().execute(state)
        # 150 hrs / 8-hr shift = 18.75 days
        assert state.total_days == pytest.approx(18.75)

    def test_no_warning_under_52_weeks(self, sample_state):
        state = ChronoPass().execute(sample_state)
        assert state.warnings == []
