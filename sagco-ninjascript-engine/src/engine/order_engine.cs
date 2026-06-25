// order_engine.cs — Order submission wrapper with risk gate
// Every entry/exit goes through here. Risk gate checked BEFORE EnterLong/Short.

using System;

namespace Sagco.Engine
{
    public enum OrderDirection { Long, Short }

    public class OrderEngine
    {
        private readonly RiskEngine _risk;
        private double _burnRate = 1.0;

        // Delegate type so Strategy can pass its NinjaTrader order methods
        public Action<string, int> EnterLong  { get; set; }
        public Action<string, int> EnterShort { get; set; }
        public Action<string>      ExitLong   { get; set; }
        public Action<string>      ExitShort  { get; set; }

        public OrderEngine()
        {
            _risk = new RiskEngine();
        }

        public void UpdateBurnRate(double burnRate) => _burnRate = burnRate;

        public bool TryEnter(OrderDirection direction, int quantity, double estimatedMaxLoss, string signal)
        {
            var verdict = RiskEngine.Check(
                proposedSizeLots:      quantity,
                estimatedMaxLoss:      estimatedMaxLoss,
                currentBurnRate:       _burnRate
            );

            if (!verdict.Go)
            {
                Sagco.Debug.SagcoPrintTrace.Antibody(verdict.AntibodyId, verdict.Reason);
                return false;
            }

            Sagco.Debug.SagcoPrintTrace.Print(
                "ORDER_ENGINE",
                $"ENTERING {direction} qty={quantity} signal={signal} — RISK:GO",
                "COMPUTED"
            );

            if (direction == OrderDirection.Long)
                EnterLong?.Invoke(signal, quantity);
            else
                EnterShort?.Invoke(signal, quantity);

            return true;
        }

        public void Exit(OrderDirection direction, string signal)
        {
            Sagco.Debug.SagcoPrintTrace.Print(
                "ORDER_ENGINE",
                $"EXITING {direction} signal={signal}",
                "COMPUTED"
            );

            if (direction == OrderDirection.Long)
                ExitLong?.Invoke(signal);
            else
                ExitShort?.Invoke(signal);
        }
    }
}
