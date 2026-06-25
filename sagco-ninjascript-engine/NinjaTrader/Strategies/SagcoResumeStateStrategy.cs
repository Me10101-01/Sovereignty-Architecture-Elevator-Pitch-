// SagcoResumeStateStrategy.cs — Persistent state strategy
// Uses NinjaTrader's Strategy Analyzer resume pattern.
// Tracks position from prior session so ERU BurnRate doesn't reset on restart.

#region Using declarations
using System;
using System.IO;
using System.Text.Json;
using NinjaTrader.Cbi;
using NinjaTrader.NinjaScript.Strategies;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class SagcoResumeStateStrategy : Strategy
    {
        private record ResumeState(
            int    EruProven,
            int    EruTotal,
            double BurnRate,
            string LastVerdict,
            string LastSaveTime
        );

        private int    _eruProven = 0;
        private int    _eruTotal  = 0;
        private double _burnRate  = 0.0;
        private string _stateFile;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description         = "SAGCO Resume State Strategy — BurnRate persists across restarts";
                Name                = "SagcoResumeStateStrategy";
                Calculate           = Calculate.OnBarClose;
                TraceOrders         = true;
                IsExitOnSessionCloseStrategy = true;
                BarsRequiredToTrade = 20;
            }
            else if (State == State.DataLoaded)
            {
                _stateFile = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                    "SAGCO", "state", "resume_state.json");

                LoadState();
                Sagco.Debug.SagcoTraceOrders.SmokeTest(Name);
            }
            else if (State == State.Terminated)
            {
                SaveState("TERMINATED");
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

            Sagco.Debug.SagcoPrintTrace.ERU($"RESUME-BAR-{CurrentBar}", expected, actual);

            // Periodic auto-save every 50 bars
            if (CurrentBar % 50 == 0) SaveState(verdict);
        }

        protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice,
            int quantity, string currency, double fillPrice, int fillQuantity,
            double averageFillPrice, OrderState orderState, DateTime time, ErrorCode error, string comment)
        {
            Sagco.Debug.SagcoTraceOrders.OnOrder(order, limitPrice, stopPrice, quantity, comment);
        }

        private void LoadState()
        {
            try
            {
                if (!File.Exists(_stateFile)) { Sagco.Debug.SagcoPrintTrace.Print("RESUME", "No prior state — starting fresh", "UNCOMPUTED"); return; }
                string json     = File.ReadAllText(_stateFile);
                var    state    = JsonSerializer.Deserialize<ResumeState>(json);
                _eruProven      = state.EruProven;
                _eruTotal       = state.EruTotal;
                _burnRate       = state.BurnRate;
                Sagco.Debug.SagcoPrintTrace.Print("RESUME",
                    $"State restored — proven={_eruProven}/{_eruTotal} burnRate={_burnRate:P0} lastSave={state.LastSaveTime}", "COMPUTED");
            }
            catch (Exception ex)
            {
                Sagco.Debug.SagcoPrintTrace.Antibody("AB-STATE-LOAD-FAIL", ex.Message);
            }
        }

        private void SaveState(string lastVerdict)
        {
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(_stateFile));
                var   state = new ResumeState(_eruProven, _eruTotal, _burnRate, lastVerdict, DateTime.UtcNow.ToString("o"));
                string json = JsonSerializer.Serialize(state, new JsonSerializerOptions { WriteIndented = true });
                File.WriteAllText(_stateFile, json);
                Sagco.Debug.SagcoPrintTrace.Print("RESUME", $"State saved — burnRate={_burnRate:P0}", "COMPUTED");
            }
            catch (Exception ex)
            {
                Sagco.Debug.SagcoPrintTrace.Antibody("AB-STATE-SAVE-FAIL", ex.Message);
            }
        }
    }
}
