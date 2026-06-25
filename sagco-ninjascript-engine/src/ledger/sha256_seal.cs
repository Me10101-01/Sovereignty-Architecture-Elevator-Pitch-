// sha256_seal.cs — SHA-256 seal for trade receipts and report exports
// Every report export gets a sealed entry in SHA256SUMS.txt.
// This is the NinjaScript-side mirror of sagco-audit's sha256 evidence logging.

using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;

namespace Sagco.Ledger
{
    public static class Sha256Seal
    {
        public static string HashString(string input)
        {
            using var sha = SHA256.Create();
            byte[] bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(input));
            return BitConverter.ToString(bytes).Replace("-", "").ToLowerInvariant();
        }

        public static string HashFile(string filePath)
        {
            if (!File.Exists(filePath)) return string.Empty;
            using var sha    = SHA256.Create();
            using var stream = File.OpenRead(filePath);
            byte[] bytes     = sha.ComputeHash(stream);
            return BitConverter.ToString(bytes).Replace("-", "").ToLowerInvariant();
        }

        // Append a sealed entry to reports/SHA256SUMS.txt
        public static void SealFile(string filePath, string sumsPath)
        {
            string hash    = HashFile(filePath);
            string name    = Path.GetFileName(filePath);
            string ts      = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");
            string entry   = $"{hash}  {name}  # sealed {ts}";

            Directory.CreateDirectory(Path.GetDirectoryName(sumsPath));
            File.AppendAllText(sumsPath, entry + Environment.NewLine);

            Sagco.Debug.SagcoPrintTrace.Print(
                "SHA256_SEAL",
                $"sealed {name} → {hash[..16]}...",
                "COMPUTED"
            );
        }

        // Seal a string payload (e.g. a trade receipt JSON blob)
        public static string SealPayload(string payload, string label = "receipt")
        {
            string hash = HashString(payload);
            Sagco.Debug.SagcoPrintTrace.Print(
                "SHA256_SEAL",
                $"payload={label} hash={hash[..16]}...",
                "COMPUTED"
            );
            return hash;
        }
    }
}
