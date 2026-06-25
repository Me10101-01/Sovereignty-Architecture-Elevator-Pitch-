// risk_engine.cs — Pre-order risk gate
// Called BEFORE every order submission. Returns GO | NO_GO + antibody id.
// Reads risk-limits.json — limits enforced here, never inside strategy logic.

using System;
using System.IO;
using System.Text.Json;

namespace Sagco.Engine
{
    public record RiskLimits(
        double MaxDailyLossDollars,
        double MaxPositionSizeLots,
        double MaxSingleTradeLossDollars,
        double MinBurnRateToTrade,
        bool   HaltOnAntibodyFire
    );

    public record RiskVerdict(bool Go, string AntibodyId, string Reason);

    public static class RiskEngine
    {
        private static RiskLimits _limits;
        private static double     _dailyPnL = 0.0;

        public static void LoadLimits(string configPath)
        {
            if (!File.Exists(configPath))
            {
                _limits = new RiskLimits(
                    MaxDailyLossDollars:      500.0,
                    MaxPositionSizeLots:      1.0,
                    MaxSingleTradeLossDollars: 150.0,
                    MinBurnRateToTrade:        0.5,
                    HaltOnAntibodyFire:        true
                );
                Sagco.Debug.SagcoPrintTrace.Antibody("AB-RISK-CONFIG-MISSING", $"Using defaults — {configPath} not found");
                return;
            }

            string json = File.ReadAllText(configPath);
            _limits = JsonSerializer.Deserialize<RiskLimits>(json);
            Sagco.Debug.SagcoPrintTrace.Print("RISK_ENGINE", $"Limits loaded from {configPath}", "COMPUTED");
        }

        public static void UpdateDailyPnL(double pnlDelta) => _dailyPnL += pnlDelta;

        public static void ResetDailyPnL() => _dailyPnL = 0.0;

        public static RiskVerdict Check(double proposedSizeLots, double estimatedMaxLoss, double currentBurnRate)
        {
            if (_limits == null)
                return new RiskVerdict(false, "AB-RISK-NOT-LOADED", "RiskEngine not initialized — call LoadLimits() first");

            if (_dailyPnL <= -_limits.MaxDailyLossDollars)
                return new RiskVerdict(false, "AB-DAILY-LOSS-LIMIT", $"Daily PnL {_dailyPnL:F2} hit limit -{_limits.MaxDailyLossDollars}");

            if (proposedSizeLots > _limits.MaxPositionSizeLots)
                return new RiskVerdict(false, "AB-POSITION-TOO-LARGE", $"Size {proposedSizeLots} > max {_limits.MaxPositionSizeLots}");

            if (estimatedMaxLoss > _limits.MaxSingleTradeLossDollars)
                return new RiskVerdict(false, "AB-SINGLE-TRADE-LOSS", $"Est loss ${estimatedMaxLoss:F2} > limit ${_limits.MaxSingleTradeLossDollars}");

            if (currentBurnRate < _limits.MinBurnRateToTrade)
                return new RiskVerdict(false, "AB-BURNRATE-TOO-LOW", $"BurnRate {currentBurnRate:P0} < min {_limits.MinBurnRateToTrade:P0}");

            return new RiskVerdict(true, string.Empty, "GO");
        }
    }
}
