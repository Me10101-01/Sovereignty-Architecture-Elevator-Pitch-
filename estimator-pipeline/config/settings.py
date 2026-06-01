# Base configuration — override per project via ProjectInput
SHIFT_HOURS: int = 10          # 10-hr workday (standard SAGCO field ops)
WORK_DAYS_PER_WEEK: int = 5

LABOR_RATE_PER_HR: float = 45.00     # $/hr base wage (pre-burden)
MATERIAL_RATE_PER_SQFT: float = 0.85 # $/sqft direct material cost

OVERHEAD_RATE: float = 0.15          # 15% overhead burden on subtotal
PROFIT_MARGIN: float = 0.12          # 12% profit margin on burdened cost

# Production gatekeeper bounds (sqft/mhr)
PRODUCTION_MIN_SQFT_PER_MHR: float = 0.5    # below → flag: unrealistically slow
PRODUCTION_MAX_SQFT_PER_MHR: float = 8.0    # above → flag: unrealistically fast
