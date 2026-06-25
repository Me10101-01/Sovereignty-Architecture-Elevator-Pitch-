// trade_receipt.cs — SAGCO trade receipt ledger entry
// One receipt per closed trade. Sealed with SHA-256 before export.
// Format mirrors sagco-audit decision_trace.jsonl for cross-system ERU replay.

using System;
using System.IO;
using System.Text;
using System.Text.Json;

namespace Sagco.Ledger
{
    public class TradeReceipt
    {
        public string   ReceiptId   { get; set; } = string.Empty;
        public string   Instrument  { get; set; } = string.Empty;
        public string   Direction   { get; set; } = string.Empty; // LONG | SHORT
        public double   EntryPrice  { get; set; }
        public double   ExitPrice   { get; set; }
        public int      Quantity    { get; set; }
        public double   PnL         { get; set; }
        public double   Expected    { get; set; } // ERU baseline
        public double   Actual      { get; set; } // ERU actual (PnL vs target)
        public double   Ratio       { get; set; } // V = Actual/Expected
        public string   Verdict     { get; set; } = "UNCOMPUTED";
        public string   Domain      { get; set; } = "trading";
        public string   EntryTime   { get; set; } = string.Empty;
        public string   ExitTime    { get; set; } = string.Empty;
        public string   Sha256      { get; set; } = string.Empty;
        public string   Strategy    { get; set; } = string.Empty;
    }

    public static class TradeReceiptWriter
    {
        public static string DefaultReceiptsPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            "SAGCO", "reports", "trade_receipts.jsonl"
        );

        public static TradeReceipt Create(
            string instrument, string direction,
            double entryPrice, double exitPrice, int quantity,
            double expectedPnl, string strategy,
            DateTime entryTime, DateTime exitTime)
        {
            double pnl    = direction == "LONG"
                ? (exitPrice - entryPrice) * quantity
                : (entryPrice - exitPrice) * quantity;
            double ratio  = expectedPnl != 0 ? pnl / expectedPnl : 0.0;
            string verdict = Sagco.Debug.SagcoPrintTrace.ClassifyRatio(ratio);

            var receipt = new TradeReceipt
            {
                ReceiptId  = $"TR-{DateTime.UtcNow:yyyyMMddHHmmssff}",
                Instrument = instrument,
                Direction  = direction,
                EntryPrice = entryPrice,
                ExitPrice  = exitPrice,
                Quantity   = quantity,
                PnL        = Math.Round(pnl,    2),
                Expected   = expectedPnl,
                Actual     = Math.Round(pnl,    2),
                Ratio      = Math.Round(ratio,  6),
                Verdict    = verdict,
                Strategy   = strategy,
                EntryTime  = entryTime.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                ExitTime   = exitTime.ToString("yyyy-MM-ddTHH:mm:ssZ"),
            };

            string json    = JsonSerializer.Serialize(receipt);
            receipt.Sha256 = Sha256Seal.SealPayload(json, receipt.ReceiptId);

            return receipt;
        }

        public static void Append(TradeReceipt receipt, string path = null)
        {
            path ??= DefaultReceiptsPath;
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            string json = JsonSerializer.Serialize(receipt);
            File.AppendAllText(path, json + Environment.NewLine);

            Sagco.Debug.SagcoPrintTrace.ERU(
                receipt.ReceiptId,
                receipt.Expected,
                receipt.Actual,
                receipt.Domain
            );
        }
    }
}
