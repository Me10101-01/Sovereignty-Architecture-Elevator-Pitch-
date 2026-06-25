// event-counter-example.cs — Event and bar counter using custom Series
// Demonstrates offset math with Series<int> for counting events.
// SAGCO use: count PROVEN bars, INFLATED bars, antibody fires over rolling window.

#region Using declarations
using System;
using NinjaTrader.NinjaScript.Indicators;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
    public class SagcoEventCounterExample : Indicator
    {
        private Series<int> _provenCount;
        private Series<int> _inflatedCount;
        private Series<int> _antibodyCount;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "SAGCO Event Counter — PROVEN/INFLATED/Antibody rolling counts";
                Name        = "SagcoEventCounterExample";
                Calculate   = Calculate.OnBarClose;
                IsOverlay   = false;
            }
            else if (State == State.DataLoaded)
            {
                _provenCount   = new Series<int>(this);
                _inflatedCount = new Series<int>(this);
                _antibodyCount = new Series<int>(this);
            }
            else if (State == State.Configure)
            {
                AddPlot(System.Windows.Media.Brushes.Lime,   "ProvenCount");
                AddPlot(System.Windows.Media.Brushes.Red,    "InflatedCount");
                AddPlot(System.Windows.Media.Brushes.Yellow, "AntibodyCount");
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 1) return;

            double ratio  = Close[0] / SMA(20)[0];
            string verdict = Sagco.Debug.SagcoPrintTrace.ClassifyRatio(ratio);

            // Accumulate with offset from prior bar
            int priorProven   = _provenCount[1];
            int priorInflated = _inflatedCount[1];
            int priorAntibody = _antibodyCount[1];

            _provenCount[0]   = priorProven   + (verdict == "PROVEN"   ? 1 : 0);
            _inflatedCount[0] = priorInflated + (verdict == "INFLATED" ? 1 : 0);

            bool antibodyFired = verdict == "INFLATED" && _inflatedCount[0] - priorInflated >= 3;
            _antibodyCount[0]  = priorAntibody + (antibodyFired ? 1 : 0);

            Values[0][0] = _provenCount[0];
            Values[1][0] = _inflatedCount[0];
            Values[2][0] = _antibodyCount[0];

            Print($"[COUNTER] bar={CurrentBar} proven={_provenCount[0]} inflated={_inflatedCount[0]} antibodies={_antibodyCount[0]}");
        }
    }
}
