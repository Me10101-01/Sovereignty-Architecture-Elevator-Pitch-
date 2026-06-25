// market_parser.cs — Signal token parser → ERU inputs
// Consumes SignalLexer tokens, produces structured MarketReading for ERU computation.

using System.Collections.Generic;
using System.Linq;
using Sagco.Lexer;

namespace Sagco.Parser
{
    public record MarketReading(
        double Close,
        double ExpectedBaseline,
        double ActualValue,
        double AskVol,
        double BidVol,
        double PriorBurnRate,
        string PriorVerdict
    );

    public static class MarketParser
    {
        public static MarketReading Parse(List<SignalToken> tokens, double smaBaseline)
        {
            double close      = tokens.FirstOrDefault(t => t.Type == TokenType.BAR_CLOSE)?.Value ?? 0;
            double askVol     = tokens.FirstOrDefault(t => t.Type == TokenType.VOLUME_ASK)?.Value ?? 0;
            double bidVol     = tokens.FirstOrDefault(t => t.Type == TokenType.VOLUME_BID)?.Value ?? 0;
            double burnRate   = tokens.FirstOrDefault(t => t.Type == TokenType.BURNRATE)?.Value ?? 0;
            string verdict    = tokens.FirstOrDefault(t => t.Type == TokenType.VERDICT)?.Label ?? "UNCOMPUTED";

            return new MarketReading(
                Close:            close,
                ExpectedBaseline: smaBaseline,
                ActualValue:      close,
                AskVol:           askVol,
                BidVol:           bidVol,
                PriorBurnRate:    burnRate,
                PriorVerdict:     verdict
            );
        }
    }
}
