// SagcoEntryExitEngine.cs — Entry/exit signal logic separated from core
// SagcoStrategyCore handles ERU + BurnRate. This handles when to pull the trigger.
// Signal taxonomy:
//   ERU_LONG      — PROVEN ERU + BUY volume + BurnRate above threshold
//   ERU_SHORT     — INFLATED ERU + SELL volume pressure
//   ERU_TRAIL     — PROMISING ERU + trailing stop tighten
//   ERU_EXIT_*    — Any antibody-triggered exit

#region Using declarations
using System;
using NinjaTrader.Cbi;
using NinjaTrader.NinjaScript.Strategies;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class SagcoEntryExitEngine : Strategy
    {
        private SolidColorBrush _entryBrush;
        private SolidColorBrush _exitBrush;

        private int    _eruProven = 0;
        private int    _eruTotal  = 0;
        private double _burnRate  = 0.0;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description         = "SAGCO Entry/Exit Engine — signal taxonomy";
                Name                = "SagcoEntryExitEngine";
                Calculate           = Calculate.OnBarClose;
                TraceOrders         = true;
                BarsRequiredToTrade = 20;
            }
            else if (State == State.Configure)
            {
                _entryBrush = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Colors.Lime);
                _entryBrush.Freeze();
                _exitBrush = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Colors.Red);
                _exitBrush.Freeze();
            }
            else if (State == State.DataLoaded)
            {
                Sagco.Debug.SagcoTraceOrders.SmokeTest(Name);
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < BarsRequiredToTrade) return;

            double expected = SMA(20)[0];
            double actual   = Close[0];
            double ratio    = expected != 0 ? actual / expected : 0.0;
            string verdict  = Sagco.Debug.SagcoPrintTrace.ClassifyRatio(ratio);

            _eruTotal++;
            if (verdict == "PROVEN") _eruProven++;
            _burnRate = _eruTotal > 0 ? (double)_eruProven / _eruTotal : 0.0;

            bool flatPosition = Position.MarketPosition == MarketPosition.Flat;
            bool longPosition = Position.MarketPosition == MarketPosition.Long;

            switch (verdict)
            {
                case "PROVEN" when flatPosition && _burnRate >= 0.5:
                    EnterLong(OrderType.Market, 1, 0, 0, null, null, "ERU_LONG");
                    Draw.ArrowUp(this, $"entry_{CurrentBar}", false, 0, Low[0] - TickSize, _entryBrush);
                    Sagco.Debug.SagcoPrintTrace.Print("ENTRY_EXIT", $"ERU_LONG at {Close[0]:F4} BurnRate={_burnRate:P0}", "COMPUTED");
                    break;

                case "INFLATED" when longPosition:
                    ExitLong(0, "ERU_EXIT_INFLATED");
                    Draw.ArrowDown(this, $"exit_{CurrentBar}", false, 0, High[0] + TickSize, _exitBrush);
                    Sagco.Debug.SagcoPrintTrace.Print("ENTRY_EXIT", $"ERU_EXIT_INFLATED at {Close[0]:F4}", "FAILED_COMPUTE");
                    break;

                case "PROMISING" when longPosition:
                    // Tighten trailing stop on PROMISING — don't exit, just protect
                    SetTrailStop(CalculationMode.Ticks, ATR(14)[0] / TickSize);
                    Sagco.Debug.SagcoPrintTrace.Print("ENTRY_EXIT", "ERU_TRAIL — stop tightened", "COMPUTED");
                    break;
            }
        }

        protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice,
            int quantity, string currency, double fillPrice, int fillQuantity,
            double averageFillPrice, OrderState orderState, DateTime time, ErrorCode error, string comment)
        {
            Sagco.Debug.SagcoTraceOrders.OnOrder(order, limitPrice, stopPrice, quantity, comment);
        }

        protected override void OnExecutionUpdate(Execution execution, string executionId,
            double price, int quantity, MarketPosition marketPosition, string orderId, DateTime time)
        {
            Sagco.Debug.SagcoTraceOrders.OnExecution(execution, $"E{CurrentBar}");
        }
    }
}
