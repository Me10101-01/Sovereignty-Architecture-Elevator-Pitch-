from config.settings import LABOR_RATE_PER_HR
from src.models.pipeline_state import PipelineState
from src.passes.base_pass import BasePass


class LaborPass(BasePass):
    """Pass 2 — base labor unit rates and total labor cost."""

    def execute(self, state: PipelineState) -> PipelineState:
        state.hrs_per_lnft = round(state.mhrs / state.lnft, 4)
        state.hrs_per_sqft = round(state.mhrs / state.sqft, 4)
        state.labor_cost   = round(state.mhrs * LABOR_RATE_PER_HR, 2)

        state.log(self.name, "hrs_per_lnft", state.hrs_per_lnft)
        state.log(self.name, "hrs_per_sqft", state.hrs_per_sqft)
        state.log(self.name, "labor_cost",   f"${state.labor_cost:,.2f}")
        return state
