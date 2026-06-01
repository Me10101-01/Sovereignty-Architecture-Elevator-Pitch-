from config.settings import OVERHEAD_RATE, PROFIT_MARGIN
from src.models.pipeline_state import PipelineState
from src.passes.base_pass import BasePass


class BidPass(BasePass):
    """Pass 5 — overhead burden + profit margin → final bid price."""

    def execute(self, state: PipelineState) -> PipelineState:
        if not state.crew_velocity_valid:
            state.warn(
                self.name,
                "Compiling bid on state with invalid crew velocity — "
                "review production pass warnings before submitting",
            )

        subtotal        = (state.labor_cost or 0.0) + (state.material_cost or 0.0)
        overhead        = round(subtotal * OVERHEAD_RATE, 2)
        burdened        = subtotal + overhead
        profit          = round(burdened * PROFIT_MARGIN, 2)
        total_bid       = round(burdened + profit, 2)

        state.subtotal  = round(subtotal, 2)
        state.overhead  = overhead
        state.profit    = profit
        state.total_bid = total_bid

        state.log(self.name, "subtotal",  f"${state.subtotal:,.2f}")
        state.log(self.name, "overhead",  f"${state.overhead:,.2f}")
        state.log(self.name, "profit",    f"${state.profit:,.2f}")
        state.log(self.name, "total_bid", f"${state.total_bid:,.2f}")
        return state
