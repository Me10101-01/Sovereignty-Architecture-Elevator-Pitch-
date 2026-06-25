// SagcoDeltaRenkoSignal.cs — SAGCO ERU Ratio plotted on Renko bars
// Computes V = Close[0] / SMA(Period)[0] on every Renko bar close.
// Plots ERU ratio as oscillator. Fires antibodies on INFLATED/UNPROVEN drift.

#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Windows.Media;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;
using NinjaTrader.Data;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
    public class SagcoDeltaRenkoSignal : Indicator
    {
        private int    _provenCount  = 0;
        private int    _totalCount   = 0;
        private double _burnRate     = 0.0;
        private int    _inflatedRuns = 0;

        #region Properties
        [NinjaScriptProperty]
        [Range(5, 200)]
        [Display(Name = "SMA Period (ERU baseline)", GroupName = "SAGCO", Order = 0)]
        public int SmaPeriod { get; set; }

        [NinjaScriptProperty]
        [Range(0.01, 1.0)]
        [Display(Name = "Min BurnRate to signal", GroupName = "SAGCO", Order = 1)]
        public double MinBurnRate { get; set; }

        [NinjaScriptProperty]
        [Range(1, 10)]
        [Display(Name = "Inflated streak antibody", GroupName = "SAGCO", Order = 2)]
        public int InflatedStreakTrigger { get; set; }
        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description             = "SAGCO ERU Delta Renko Signal — V=Close/SMA";
                Name                    = "SagcoDeltaRenkoSignal";
                Calculate               = Calculate.OnBarClose;
                IsOverlay               = false;
                ScaleJustification      = NinjaTrader.Gui.Chart.ScaleJustification.Right;
                SmaPeriod               = 20;
                MinBurnRate             = 0.5;
                InflatedStreakTrigger   = 3;
            }
            else if (State == State.Configure)
            {
                AddPlot(new Stroke(Brushes.DodgerBlue, 2), PlotStyle.Line,  "ERU_Ratio");
                AddPlot(new Stroke(Brushes.Lime,       1), PlotStyle.Cross, "BurnRate");
                AddLine(Stroke.Default, 1.0, "PROVEN threshold");
                AddLine(Stroke.Default, 0.5, "PROMISING threshold");
            }
            else if (State == State.DataLoaded)
            {
                Sagco.Debug.SagcoPrintTrace.SmokeTest = true;
                Sagco.Debug.SagcoPrintTrace.Print("SAGCO_DELTA_RENKO", "Indicator loaded — ERU baseline SMA(" + SmaPeriod + ")", "COMPUTED");
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < SmaPeriod) return;

            double expected = SMA(SmaPeriod)[0];
            double actual   = Close[0];
            double ratio    = expected != 0 ? actual / expected : 0.0;

            string verdict = Sagco.Debug.SagcoPrintTrace.ClassifyRatio(ratio);

            _totalCount++;
            if (verdict == "PROVEN") { _provenCount++; _inflatedRuns = 0; }
            else if (verdict == "INFLATED") { _inflatedRuns++; }
            else { _inflatedRuns = 0; }

            _burnRate = _totalCount > 0 ? (double)_provenCount / _totalCount : 0.0;

            Values[0][0] = ratio;
            Values[1][0] = _burnRate;

            Sagco.Debug.SagcoPrintTrace.ERU(
                $"RENKO-BAR-{CurrentBar}",
                expected: expected,
                actual:   actual,
                domain:   "trading"
            );

            if (_inflatedRuns >= InflatedStreakTrigger)
            {
                Sagco.Debug.SagcoPrintTrace.Antibody(
                    "AB-RENKO-INFLATED-STREAK",
                    $"{_inflatedRuns} consecutive INFLATED bars — price detached from SMA baseline"
                );
                _inflatedRuns = 0;
            }

            if (_burnRate < MinBurnRate && _totalCount > SmaPeriod)
            {
                Sagco.Debug.SagcoPrintTrace.Antibody(
                    "AB-BURNRATE-BELOW-MIN",
                    $"BurnRate {_burnRate:P0} < min {MinBurnRate:P0} — strategy alignment degrading"
                );
            }
        }
    }
}

#region NinjaScript generated code
namespace NinjaTrader.NinjaScript.Indicators
{
    public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
    {
        private SagcoDeltaRenkoSignal[] cacheSagcoDeltaRenkoSignal;

        public SagcoDeltaRenkoSignal SagcoDeltaRenkoSignal(int smaPeriod, double minBurnRate, int inflatedStreakTrigger)
            => SagcoDeltaRenkoSignal(Input, smaPeriod, minBurnRate, inflatedStreakTrigger);

        public SagcoDeltaRenkoSignal SagcoDeltaRenkoSignal(ISeries<double> input,
            int smaPeriod, double minBurnRate, int inflatedStreakTrigger)
        {
            if (cacheSagcoDeltaRenkoSignal != null)
                foreach (var cached in cacheSagcoDeltaRenkoSignal)
                    if (cached.SmaPeriod == smaPeriod &&
                        cached.MinBurnRate == minBurnRate &&
                        cached.InflatedStreakTrigger == inflatedStreakTrigger &&
                        cached.EqualsInput(input))
                        return cached;

            return CacheIndicator<SagcoDeltaRenkoSignal>(
                new SagcoDeltaRenkoSignal { SmaPeriod = smaPeriod, MinBurnRate = minBurnRate, InflatedStreakTrigger = inflatedStreakTrigger },
                input, ref cacheSagcoDeltaRenkoSignal);
        }
    }
}
#endregion
