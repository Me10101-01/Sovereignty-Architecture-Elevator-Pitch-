// SagcoVolumePulse.cs — Bid/ask delta volume indicator
// Collects ask volume and bid volume tick-by-tick (one-tick granularity).
// Plots delta ratio per bar. Feeds VolumeEngine ERU computation.

#region Using declarations
using System;
using System.ComponentModel.DataAnnotations;
using System.Windows.Media;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
    public class SagcoVolumePulse : Indicator
    {
        private Sagco.Engine.VolumeEngine _volumeEngine;

        #region Properties
        [NinjaScriptProperty]
        [Range(0.1, 5.0)]
        [Display(Name = "Expected Delta Ratio", GroupName = "SAGCO", Order = 0)]
        public double ExpectedDelta { get; set; }
        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description        = "SAGCO Volume Pulse — bid/ask delta with ERU";
                Name               = "SagcoVolumePulse";
                Calculate          = Calculate.OnEachTick;
                IsOverlay          = false;
                ExpectedDelta      = 1.0;
            }
            else if (State == State.Configure)
            {
                AddPlot(new Stroke(Brushes.Cyan,   2), PlotStyle.Bar,  "DeltaRatio");
                AddPlot(new Stroke(Brushes.Orange, 1), PlotStyle.Line, "ERU_Ratio");
                AddLine(Stroke.Default, 1.0, "Neutral");
            }
            else if (State == State.DataLoaded)
            {
                _volumeEngine = new Sagco.Engine.VolumeEngine();
                _volumeEngine.SetExpectedDelta(ExpectedDelta);
                Sagco.Debug.SagcoPrintTrace.Print("SAGCO_VOLUME_PULSE", $"Loaded — expected delta={ExpectedDelta}", "COMPUTED");
            }
        }

        protected override void OnMarketData(MarketDataEventArgs e)
        {
            if (e.MarketDataType == MarketDataType.Ask)
                _volumeEngine?.ProcessTick(e.Price, (long)e.Volume, isAsk: true);
            else if (e.MarketDataType == MarketDataType.Bid)
                _volumeEngine?.ProcessTick(e.Price, (long)e.Volume, isAsk: false);
        }

        protected override void OnBarUpdate()
        {
            if (_volumeEngine == null) return;

            var (ratio, verdict) = _volumeEngine.OnBarClose();

            Values[0][0] = _volumeEngine.Previous.DeltaRatio;
            Values[1][0] = ratio;

            // Color bars by bid/ask pressure
            PlotBrushes[0][0] = _volumeEngine.Previous.Pressure switch
            {
                "BUY"     => Brushes.Lime,
                "SELL"    => Brushes.Red,
                _         => Brushes.DimGray,
            };
        }
    }
}
