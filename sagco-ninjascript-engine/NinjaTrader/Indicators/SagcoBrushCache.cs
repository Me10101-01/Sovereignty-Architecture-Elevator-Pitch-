// SagcoBrushCache.cs — Brush instantiation cache for SAGCO indicators
// Brushes are expensive WPF objects. Instantiate once, reuse everywhere.
// Pattern from NinjaTrader perf example adapted for SAGCO verdict colors.

#region Using declarations
using System.Collections.Generic;
using System.Windows.Media;
using NinjaTrader.NinjaScript.Indicators;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
    public class SagcoBrushCache : Indicator
    {
        // Verdict → brush mapping — allocated once in OnStateChange → State.Configure
        private readonly Dictionary<string, SolidColorBrush> _verdictBrushes = new();
        private SolidColorBrush _neutralBrush;

        public SolidColorBrush GetVerdictBrush(string verdict)
        {
            if (_verdictBrushes.TryGetValue(verdict, out var brush)) return brush;
            return _neutralBrush;
        }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "SAGCO Brush Cache — verdict color lookup";
                Name        = "SagcoBrushCache";
                IsOverlay   = false;
            }
            else if (State == State.Configure)
            {
                // Allocate once — frozen brushes are thread-safe
                _verdictBrushes["PROVEN"]    = FreezeNew(Colors.Lime);
                _verdictBrushes["PROMISING"] = FreezeNew(Colors.DodgerBlue);
                _verdictBrushes["UNPROVEN"]  = FreezeNew(Colors.Orange);
                _verdictBrushes["INFLATED"]  = FreezeNew(Colors.Red);
                _verdictBrushes["COMPUTED"]  = FreezeNew(Colors.White);
                _verdictBrushes["FAILED_COMPUTE"] = FreezeNew(Colors.Crimson);
                _neutralBrush                = FreezeNew(Colors.DimGray);
            }
        }

        protected override void OnBarUpdate() { /* cache only — no plot logic */ }

        private static SolidColorBrush FreezeNew(Color c)
        {
            var b = new SolidColorBrush(c);
            b.Freeze();
            return b;
        }
    }
}
