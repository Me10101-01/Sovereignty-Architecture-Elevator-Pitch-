from dataclasses import dataclass, field
from config.settings import SHIFT_HOURS


@dataclass
class ProjectInput:
    sqft: float        # total square footage
    lnft: float        # total linear footage
    mhrs: float        # total man-hours budgeted
    men: int           # crew size
    shift_hours: int = field(default_factory=lambda: SHIFT_HOURS)

    def __post_init__(self):
        if self.sqft <= 0:
            raise ValueError(f"sqft must be positive, got {self.sqft}")
        if self.lnft <= 0:
            raise ValueError(f"lnft must be positive, got {self.lnft}")
        if self.mhrs <= 0:
            raise ValueError(f"mhrs must be positive, got {self.mhrs}")
        if self.men < 1:
            raise ValueError(f"men must be >= 1, got {self.men}")
        if self.shift_hours not in (8, 10, 12):
            raise ValueError(f"shift_hours must be 8, 10, or 12 — got {self.shift_hours}")
