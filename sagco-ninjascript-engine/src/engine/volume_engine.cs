// volume_engine.cs — Bid/ask delta volume engine
// Tracks cumulative bid/ask pressure per bar (the SAGCO Volume Pulse).
// Input: individual tick events from OnMarketData().
// Output: DeltaRatio = AskVol / BidVol — feeds ERU expected/actual.

using System;

namespace Sagco.Engine
{
    public class VolumeBar
    {
        public long   AskVolume  { get; private set; }
        public long   BidVolume  { get; private set; }
        public long   TotalTicks { get; private set; }
        public double DeltaRatio => BidVolume != 0 ? (double)AskVolume / BidVolume : 0.0;
        public string Pressure   => DeltaRatio > 1.1 ? "BUY" : DeltaRatio < 0.9 ? "SELL" : "NEUTRAL";

        public void AddAsk(long volume) { AskVolume += volume; TotalTicks++; }
        public void AddBid(long volume) { BidVolume += volume; TotalTicks++; }
        public void Reset()             { AskVolume = 0; BidVolume = 0; TotalTicks = 0; }
    }

    public class VolumeEngine
    {
        private VolumeBar _current  = new();
        private VolumeBar _previous = new();
        private double    _eruExpected = 1.0; // neutral baseline

        public VolumeBar Current  => _current;
        public VolumeBar Previous => _previous;

        // Call from OnMarketData() for every tick
        public void ProcessTick(double price, long volume, bool isAsk)
        {
            if (isAsk) _current.AddAsk(volume);
            else       _current.AddBid(volume);
        }

        // Call from OnBarUpdate() at bar close — rotate and compute ERU
        public (double ratio, string verdict) OnBarClose()
        {
            _previous = _current;
            _current  = new VolumeBar();

            double ratio   = _eruExpected != 0 ? _previous.DeltaRatio / _eruExpected : 0.0;
            string verdict = Sagco.Debug.SagcoPrintTrace.ClassifyRatio(ratio);

            Sagco.Debug.SagcoPrintTrace.Print(
                "VOLUME_ENGINE",
                $"ask={_previous.AskVolume} bid={_previous.BidVolume} " +
                $"delta={_previous.DeltaRatio:F4} pressure={_previous.Pressure} " +
                $"V={ratio:F4} verdict={verdict}",
                verdict
            );

            return (ratio, verdict);
        }

        public void SetExpectedDelta(double expected) => _eruExpected = expected;
    }
}
