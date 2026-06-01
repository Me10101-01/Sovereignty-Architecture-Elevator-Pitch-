from dataclasses import dataclass, field
from typing import Optional
from src.models.project_input import ProjectInput


@dataclass
class PipelineState:
    # ── Seed inputs ───────────────────────────────────────────────────────────
    sqft: float
    lnft: float
    mhrs: float
    men: int
    shift_hours: int

    # ── Pass 1: Material ──────────────────────────────────────────────────────
    sqft_per_lnft: Optional[float] = None
    material_cost: Optional[float] = None

    # ── Pass 2: Labor ─────────────────────────────────────────────────────────
    hrs_per_lnft: Optional[float] = None
    hrs_per_sqft: Optional[float] = None
    labor_cost: Optional[float] = None

    # ── Pass 3: Production ────────────────────────────────────────────────────
    sqft_per_mhr: Optional[float] = None
    lnft_per_mhr: Optional[float] = None
    crew_velocity_valid: Optional[bool] = None

    # ── Pass 4: Chrono ────────────────────────────────────────────────────────
    hrs_per_man: Optional[float] = None
    total_days: Optional[float] = None
    total_weeks: Optional[float] = None

    # ── Pass 5: Bid ───────────────────────────────────────────────────────────
    subtotal: Optional[float] = None
    overhead: Optional[float] = None
    profit: Optional[float] = None
    total_bid: Optional[float] = None

    # ── Audit trail ───────────────────────────────────────────────────────────
    warnings: list = field(default_factory=list)
    pass_log: list = field(default_factory=list)

    @classmethod
    def from_input(cls, inp: ProjectInput) -> "PipelineState":
        return cls(
            sqft=inp.sqft,
            lnft=inp.lnft,
            mhrs=inp.mhrs,
            men=inp.men,
            shift_hours=inp.shift_hours,
        )

    def log(self, pass_name: str, key: str, value) -> None:
        self.pass_log.append(f"[{pass_name}] {key} = {value}")

    def warn(self, pass_name: str, message: str) -> None:
        entry = f"[{pass_name}] WARNING: {message}"
        self.warnings.append(entry)
        self.pass_log.append(entry)
