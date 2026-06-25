// SagcoControlPanel.cs — SAGCO Control Panel add-on window
// Shows live ERU BurnRate, last verdict, antibody count, risk status.
// Connects to sagco-audit flat files for real-time display.

#region Using declarations
using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using NinjaTrader.Gui;
#endregion

namespace NinjaTrader.NinjaScript.AddOns
{
    public class SagcoControlPanel : NTWindow
    {
        private TextBlock _burnRateDisplay;
        private TextBlock _verdictDisplay;
        private TextBlock _antibodyDisplay;
        private TextBlock _riskDisplay;
        private System.Windows.Threading.DispatcherTimer _refreshTimer;

        private string _auditLogPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            "SAGCO", "logs", "ninjascript_print.log");

        protected override void OnInitialize()
        {
            Caption    = "SAGCO Control Panel";
            Width      = 420;
            Height     = 280;
            Loaded    += OnLoaded;
            Unloaded  += OnUnloaded;
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            var grid = new Grid { Margin = new Thickness(12) };
            for (int i = 0; i < 4; i++)
                grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            _burnRateDisplay = AddRow(grid, 0, "BurnRate",  "COMPUTING...", "#00BFFF");
            _verdictDisplay  = AddRow(grid, 1, "Verdict",   "UNCOMPUTED",   "#FFA500");
            _antibodyDisplay = AddRow(grid, 2, "Antibodies","—",            "#FF4444");
            _riskDisplay     = AddRow(grid, 3, "Risk Gate", "UNCOMPUTED",   "#888888");

            Content = grid;

            _refreshTimer = new System.Windows.Threading.DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(2)
            };
            _refreshTimer.Tick += (_, __) => RefreshFromLog();
            _refreshTimer.Start();
        }

        private void OnUnloaded(object sender, RoutedEventArgs e) => _refreshTimer?.Stop();

        private void RefreshFromLog()
        {
            if (!File.Exists(_auditLogPath)) return;
            try
            {
                string[] lines = File.ReadAllLines(_auditLogPath);
                int proven = 0, total = 0, antibodies = 0;
                string lastVerdict = "UNCOMPUTED";
                foreach (string line in lines)
                {
                    if (line.Contains("[ERU]"))          { total++; if (line.Contains("PROVEN")) proven++; lastVerdict = ParseVerdict(line); }
                    if (line.Contains("[ANTIBODY]"))     antibodies++;
                }
                double burnRate = total > 0 ? (double)proven / total : 0.0;
                _burnRateDisplay.Text = $"{burnRate:P1}  ({proven}/{total})";
                _verdictDisplay.Text  = lastVerdict;
                _antibodyDisplay.Text = antibodies.ToString();
                _riskDisplay.Text     = burnRate >= 0.5 ? "GO" : "NO-GO (BurnRate too low)";
            }
            catch { /* never crash the panel */ }
        }

        private static string ParseVerdict(string line)
        {
            foreach (string v in new[] { "PROVEN", "PROMISING", "UNPROVEN", "INFLATED" })
                if (line.Contains(v)) return v;
            return "UNKNOWN";
        }

        private static TextBlock AddRow(Grid grid, int row, string label, string value, string hexColor)
        {
            var panel = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 4, 0, 4) };
            panel.Children.Add(new TextBlock { Text = $"{label}:", Width = 100, Foreground = System.Windows.Media.Brushes.Gray });
            var val = new TextBlock { Text = value, Foreground = (System.Windows.Media.Brush)new System.Windows.Media.BrushConverter().ConvertFrom(hexColor) };
            panel.Children.Add(val);
            Grid.SetRow(panel, row);
            grid.Children.Add(panel);
            return val;
        }
    }
}
