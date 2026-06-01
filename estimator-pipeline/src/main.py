#!/usr/bin/env python3
"""
SAGCO Estimator Pipeline — CLI orchestrator
Usage:
    python -m src.main                              # runs built-in sample (701/1464/600/4)
    python -m src.main --lnft 701 --sqft 1464 --mhrs 600 --men 4
    python -m src.main --lnft 701 --sqft 1464 --mhrs 600 --men 4 --shift 8
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.project_input import ProjectInput
from src.models.pipeline_state import PipelineState
from src.passes.material_pass   import MaterialPass
from src.passes.labor_pass      import LaborPass
from src.passes.production_pass import ProductionPass
from src.passes.chrono_pass     import ChronoPass
from src.passes.bid_pass        import BidPass


PIPELINE = [
    MaterialPass(),
    LaborPass(),
    ProductionPass(),
    ChronoPass(),
    BidPass(),
]


def run_pipeline(inp: ProjectInput) -> PipelineState:
    state = PipelineState.from_input(inp)
    for p in PIPELINE:
        state = p(state)
    return state


def print_report(state: PipelineState) -> None:
    print("\n" + "=" * 56)
    print("  SAGCO ESTIMATOR PIPELINE — PASS REPORT")
    print("=" * 56)
    print(f"  INPUT:  {state.lnft} LNFT / {state.sqft} SQFT / "
          f"{state.mhrs} MHRS / {state.men} MEN / {state.shift_hours}-hr shift")
    print("-" * 56)
    print(f"  PASS 1  sqft_per_lnft    = {state.sqft_per_lnft}")
    print(f"          material_cost    = ${state.material_cost:,.2f}")
    print(f"  PASS 2  hrs_per_lnft     = {state.hrs_per_lnft}")
    print(f"          hrs_per_sqft     = {state.hrs_per_sqft}")
    print(f"          labor_cost       = ${state.labor_cost:,.2f}")
    print(f"  PASS 3  sqft_per_mhr     = {state.sqft_per_mhr}")
    print(f"          lnft_per_mhr     = {state.lnft_per_mhr}")
    print(f"          velocity_valid   = {state.crew_velocity_valid}")
    print(f"  PASS 4  hrs_per_man      = {state.hrs_per_man}")
    print(f"          total_days       = {state.total_days}")
    print(f"          total_weeks      = {state.total_weeks}")
    print(f"  PASS 5  subtotal         = ${state.subtotal:,.2f}")
    print(f"          overhead (15%)   = ${state.overhead:,.2f}")
    print(f"          profit   (12%)   = ${state.profit:,.2f}")
    print(f"          TOTAL BID        = ${state.total_bid:,.2f}")
    print("-" * 56)
    if state.warnings:
        print("  WARNINGS:")
        for w in state.warnings:
            print(f"    {w}")
    else:
        print("  STATUS: PASS — no gatekeeper warnings fired")
    print("=" * 56 + "\n")


def main():
    parser = argparse.ArgumentParser(description="SAGCO Estimator Pipeline")
    parser.add_argument("--lnft",  type=float, default=701)
    parser.add_argument("--sqft",  type=float, default=1464)
    parser.add_argument("--mhrs",  type=float, default=600)
    parser.add_argument("--men",   type=int,   default=4)
    parser.add_argument("--shift", type=int,   default=10,
                        choices=[8, 10, 12])
    args = parser.parse_args()

    inp   = ProjectInput(sqft=args.sqft, lnft=args.lnft,
                         mhrs=args.mhrs, men=args.men,
                         shift_hours=args.shift)
    state = run_pipeline(inp)
    print_report(state)
    return 0 if state.crew_velocity_valid else 1


if __name__ == "__main__":
    sys.exit(main())
