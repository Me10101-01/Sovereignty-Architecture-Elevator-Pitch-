// SagcoStrategyCore.cs — SAGCO ERU strategy core
// Every bar: compute V=A/E, update BurnRate, fire antibodies on drift.
// Entry/exit delegated to SagcoEntryExitEngine.
// TraceOrders = true always — this is non-negotiable.

#region Using declarations
using System;
using System.ComponentModel.DataAnnotations;
using System.IO;
using NinjaTrader.Cbi;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Strategies;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class SagcoStrategyCore : Strategy
    {
        // ERU state
        private int    _eruProven   = 0;
        private int    _eruTotal    = 0;
        private double _burnRate    = 0.0;

        private Sagco.Engine.VolumeEngine _volumeEngine;
        private Sagco.Engine.OrderEngine  _orderEngine;
        private string _receiptsPath;
        private string _riskConfigPath;

        #region Properties
        [NinjaScriptProperty]
        [Range(5, 200)]
        [Display(Name = "ERU Baseline Period", GroupName = "SAGCO ERU", Order = 0)]
        public int BaselinePeriod { get; set; }

        [NinjaScriptProperty]
        [Range(0.0, 2.0)]
        [Display(Name = "Expected Volume Delta", GroupName = "SAGCO ERU", Order = 1)]
        public double ExpectedVolumeDelta { get; set; }

        [NinjaScriptProperty]
        [Range(0.1, 1.0)]
        [Display(Name = "Min BurnRate to trade", GroupName = "SAGCO ERU", Order = 2)]
        public double MinBurnRate { get; set; }
        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description          = "SAGCO Strategy Core — ERU BurnRate engine";
                Name                 = "SagcoStrategyCore";
                Calculate            = Calculate.OnBarClose;
                TraceOrders          = true;  // SAGCO: never disable
                BarsRequiredToTrade  = 20;
                BaselinePeriod       = 20;
                ExpectedVolumeDelta  = 1.0;
                MinBurnRate          = 0.5;
            }
            else if (State == State.DataLoaded)
            {
                _volumeEngine  = new Sagco.Engine.VolumeEngine();
                _volumeEngine.SetExpectedDelta(ExpectedVolumeDelta);

                _orderEngine        = new Sagco.Engine.OrderEngine();
                _orderEngine.EnterLong  = (sig, qty) => EnterLong(OrderType.Market,  qty, 0, 0, null, null, sig);
                _orderEngine.EnterShort = (sig, qty) => EnterShort(OrderType.Market, qty, 0, 0, null, null, sig);
                _orderEngine.ExitLong   = (sig) => ExitLong(0, sig);
                _orderEngine.ExitShort  = (sig) => ExitShort(0, sig);

                string sagcoRoot = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "SAGCO");
                _receiptsPath  = Path.Combine(sagcoRoot, "reports", "trade_receipts.jsonl");
                _riskConfigPath = Path.Combine(sagcoRoot, "configs", "risk-limits.json");

                Sagco.Engine.RiskEngine.LoadLimits(_riskConfigPath);
                Sagco.Debug.SagcoTraceOrders.SmokeTest(Name);

                Sagco.Debug.SagcoPrintTrace.Print("SAGCO_CORE",
                    $"Strategy loaded — baseline={BaselinePeriod} minBurnRate={MinBurnRate:P0}", "COMPUTED");
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < BarsRequiredToTrade) return;

            // ERU: baseline = SMA(BaselinePeriod), actual = Close
            double expected = SMA(BaselinePeriod)[0];
            double actual   = Close[0];
            double ratio    = expected != 0 ? actual / expected : 0.0;
            string verdict  = Sagco.Debug.SagcoPrintTrace.ClassifyRatio(ratio);

            _eruTotal++;
            if (verdict == "PROVEN") _eruProven++;
            _burnRate = _eruTotal > 0 ? (double)_eruProven / _eruTotal : 0.0;
            _orderEngine.UpdateBurnRate(_burnRate);

            Sagco.Debug.SagcoPrintTrace.ERU($"BAR-{CurrentBar}", expected, actual);

            // Volume pulse
            var (volRatio, volVerdict) = _volumeEngine.OnBarClose();

            // Entry signal: PROVEN ERU + BUY volume pressure
            if (verdict == "PROVEN" && volVerdict == "PROVEN" && _volumeEngine.Previous.Pressure == "BUY"
                && Position.MarketPosition == MarketPosition.Flat)
            {
                double estLoss = ATR(14)[0] * 2 * Instrument.MasterInstrument.PointValue;
                _orderEngine.TryEnter(Sagco.Engine.OrderDirection.Long, 1, estLoss, "ERU_LONG");
            }

            // Exit signal: INFLATED ERU (price detached from baseline)
            if (verdict == "INFLATED" && Position.MarketPosition == MarketPosition.Long)
                _orderEngine.Exit(Sagco.Engine.OrderDirection.Long, "ERU_EXIT_INFLATED");

            // Antibody: BurnRate drift
            if (_eruTotal > BaselinePeriod && _burnRate < MinBurnRate)
                Sagco.Debug.SagcoPrintTrace.Antibody("AB-BURNRATE-DRIFT",
                    $"BurnRate={_burnRate:P0} after {_eruTotal} bars — strategy misaligned");
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
            Sagco.Debug.SagcoTraceOrders.OnExecution(execution, $"BAR-{CurrentBar}");
        }
    }
}
