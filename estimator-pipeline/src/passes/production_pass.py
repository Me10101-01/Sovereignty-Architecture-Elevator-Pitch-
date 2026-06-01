from config.settings import (
    PRODUCTION_MIN_SQFT_PER_MHR,
    PRODUCTION_MAX_SQFT_PER_MHR,
)
from src.models.pipeline_state import PipelineState
from src.passes.base_pass import BasePass


class ProductionPass(BasePass):
    """Pass 3 — crew velocity engine with gatekeeper validation."""

    def execute(self, state: PipelineState) -> PipelineState:
        state.sqft_per_mhr = round(state.sqft / state.mhrs, 4)
        state.lnft_per_mhr = round(state.lnft / state.mhrs, 4)

        low  = PRODUCTION_MIN_SQFT_PER_MHR
        high = PRODUCTION_MAX_SQFT_PER_MHR
        rate = state.sqft_per_mhr

        if rate < low:
            state.warn(
                self.name,
                f"sqft_per_mhr={rate} is below floor ({low}) — "
                "crew pace unrealistically slow; verify mhrs input",
            )
            state.crew_velocity_valid = False
        elif rate > high:
            state.warn(
                self.name,
                f"sqft_per_mhr={rate} exceeds ceiling ({high}) — "
                "crew pace unrealistically fast; verify sqft/mhrs inputs",
            )
            state.crew_velocity_valid = False
        else:
            state.crew_velocity_valid = True

        state.log(self.name, "sqft_per_mhr",        state.sqft_per_mhr)
        state.log(self.name, "lnft_per_mhr",        state.lnft_per_mhr)
        state.log(self.name, "crew_velocity_valid",  state.crew_velocity_valid)
        return state
