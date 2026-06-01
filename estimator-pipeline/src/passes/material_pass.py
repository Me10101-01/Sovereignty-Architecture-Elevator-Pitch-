from config.settings import MATERIAL_RATE_PER_SQFT
from src.models.pipeline_state import PipelineState
from src.passes.base_pass import BasePass


class MaterialPass(BasePass):
    """Pass 1 — material footprint and direct material cost."""

    def execute(self, state: PipelineState) -> PipelineState:
        state.sqft_per_lnft = round(state.sqft / state.lnft, 4)
        state.material_cost = round(state.sqft * MATERIAL_RATE_PER_SQFT, 2)

        state.log(self.name, "sqft_per_lnft", state.sqft_per_lnft)
        state.log(self.name, "material_cost", f"${state.material_cost:,.2f}")
        return state
