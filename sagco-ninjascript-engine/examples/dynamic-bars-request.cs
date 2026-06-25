// dynamic-bars-request.cs — BarsRequest for dynamic historical data
// Demonstrates requesting an abstract amount of bar data programmatically.
// SAGCO use: fetch prior 100 bars of ES to compute ERU expected baseline.

#region Using declarations
using System;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript.Strategies;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class DynamicBarsRequestExample : Strategy
    {
        private BarsRequest _barsRequest;
        private bool        _requestComplete = false;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Dynamic BarsRequest — SAGCO ERU baseline example";
                Name        = "DynamicBarsRequestExample";
                Calculate   = Calculate.OnBarClose;
            }
            else if (State == State.DataLoaded)
            {
                // Request 100 daily bars of ES for ERU expected baseline
                _barsRequest = new BarsRequest(Instrument, DateTime.Now.AddDays(-100), DateTime.Now);
                _barsRequest.MergePolicy   = MergePolicy.MergeBackAdjusted;
                _barsRequest.BarsPeriod    = new BarsPeriod { BarsPeriodType = BarsPeriodType.Day, Value = 1 };
                _barsRequest.TradingHours  = TradingHours.UseInstrumentSettings;
                _barsRequest.Request((bars, errorCode, errorMessage) =>
                {
                    if (errorCode != Cbi.ErrorCode.NoError) { Print($"[ERU_BASELINE] BarsRequest error: {errorMessage}"); return; }
                    _requestComplete = true;
                    double sumClose  = 0;
                    int    count     = bars.Count;
                    for (int i = 0; i < count; i++) sumClose += bars.GetClose(i);
                    double baseline  = count > 0 ? sumClose / count : 0;
                    Print($"[ERU_BASELINE] {count} bars loaded — avg close={baseline:F4} (ERU expected baseline)");
                });
            }
        }

        protected override void OnBarUpdate()
        {
            if (!_requestComplete) return;
            // Use baseline from BarsRequest as ERU expected
            double actual  = Close[0];
            Print($"[ERU] bar={CurrentBar} actual={actual:F4} — compare to loaded baseline");
        }

        protected override void OnOrderUpdate(Cbi.Order order, double limitPrice, double stopPrice,
            int quantity, string currency, double fillPrice, int fillQuantity,
            double averageFillPrice, Cbi.OrderState orderState, DateTime time, Cbi.ErrorCode error, string comment)
        { }
    }
}
