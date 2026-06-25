// signal_lexer.cs — Market signal tokenizer
// Tokenizes a raw price/volume event into SAGCO signal tokens.
// Token types mirror FlameLang M1 opcodes at the market-data layer.

using System.Collections.Generic;

namespace Sagco.Lexer
{
    public enum TokenType
    {
        PRICE_ASK, PRICE_BID, PRICE_LAST,
        VOLUME_ASK, VOLUME_BID,
        BAR_OPEN, BAR_HIGH, BAR_LOW, BAR_CLOSE,
        ERU_RATIO, VERDICT, BURNRATE,
        ANTIBODY_FIRE, RISK_GATE,
        UNKNOWN
    }

    public record SignalToken(TokenType Type, double Value, string Label);

    public static class SignalLexer
    {
        public static List<SignalToken> Tokenize(
            double open, double high, double low, double close,
            double askVol, double bidVol,
            double eruRatio, string verdict, double burnRate)
        {
            return new List<SignalToken>
            {
                new(TokenType.BAR_OPEN,   open,     "OPEN"),
                new(TokenType.BAR_HIGH,   high,     "HIGH"),
                new(TokenType.BAR_LOW,    low,      "LOW"),
                new(TokenType.BAR_CLOSE,  close,    "CLOSE"),
                new(TokenType.VOLUME_ASK, askVol,   "ASK_VOL"),
                new(TokenType.VOLUME_BID, bidVol,   "BID_VOL"),
                new(TokenType.ERU_RATIO,  eruRatio, "ERU"),
                new(TokenType.VERDICT,    verdict == "PROVEN" ? 1.0 : 0.0, verdict),
                new(TokenType.BURNRATE,   burnRate, "BURNRATE"),
            };
        }
    }
}
