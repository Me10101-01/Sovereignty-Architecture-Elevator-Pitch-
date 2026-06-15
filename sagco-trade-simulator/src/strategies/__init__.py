from . import dividend_capture, renko_trend, renko_mean_reversion

STRATEGIES = {
    "dividend":   dividend_capture,
    "trend":      renko_trend,
    "reversion":  renko_mean_reversion,
}
