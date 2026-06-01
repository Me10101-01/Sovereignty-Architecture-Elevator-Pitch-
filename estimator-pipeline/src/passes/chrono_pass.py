from config.settings import WORK_DAYS_PER_WEEK
from src.models.pipeline_state import PipelineState
from src.passes.base_pass import BasePass


class ChronoPass(BasePass):
    """Pass 4 — temporal transformation: man-hours → days → weeks."""

    def execute(self, state: PipelineState) -> PipelineState:
        state.hrs_per_man  = round(state.mhrs / state.men, 4)
        state.total_days   = round(state.hrs_per_man / state.shift_hours, 2)
        state.total_weeks  = round(state.total_days / WORK_DAYS_PER_WEEK, 2)

        state.log(self.name, "hrs_per_man",  state.hrs_per_man)
        state.log(self.name, "total_days",   state.total_days)
        state.log(self.name, "total_weeks",  state.total_weeks)

        if state.total_weeks > 52:
            state.warn(
                self.name,
                f"Schedule spans {state.total_weeks:.1f} weeks (> 1 year). "
                "Consider adding crew or splitting scope.",
            )
        return state
