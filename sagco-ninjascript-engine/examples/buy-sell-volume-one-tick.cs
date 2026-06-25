// buy-sell-volume-one-tick.cs — Adapted from NinjaTrader docs example
// Demonstrates collecting ask/bid tick volume using OnMarketData().
// SAGCO adaptation: feeds VolumeEngine, computes ERU delta ratio.

#region Using declarations
using System;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript.Indicators;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
    // Minimal standalone example — NOT a full SAGCO indicator.
    // See SagcoVolumePulse.cs for the production version.
    public class BuySellVolumeExample : Indicator
    {
        private long _askVolume;
        private long _bidVolume;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Buy/Sell Volume One Tick — SAGCO example";
                Name        = "BuySellVolumeExample";
                Calculate   = Calculate.OnEachTick;
                IsOverlay   = false;
            }
            else if (State == State.Configure)
            {
                AddPlot(System.Windows.Media.Brushes.Lime, "AskVol");
                AddPlot(System.Windows.Media.Brushes.Red,  "BidVol");
            }
        }

        protected override void OnMarketData(MarketDataEventArgs e)
        {
            // Ask = buy-side aggression. Bid = sell-side aggression.
            if      (e.MarketDataType == MarketDataType.Ask) _askVolume += (long)e.Volume;
            else if (e.MarketDataType == MarketDataType.Bid) _bidVolume += (long)e.Volume;
        }

        protected override void OnBarUpdate()
        {
            Values[0][0] = _askVolume;
            Values[1][0] = _bidVolume;

            // ERU: expected neutral delta=1.0, actual = ask/bid ratio
            double delta = _bidVolume != 0 ? (double)_askVolume / _bidVolume : 0.0;
            Print($"[VOLUME] bar={CurrentBar} askVol={_askVolume} bidVol={_bidVolume} delta={delta:F4}");

            // Reset per bar
            _askVolume = 0;
            _bidVolume = 0;
        }
    }
}
