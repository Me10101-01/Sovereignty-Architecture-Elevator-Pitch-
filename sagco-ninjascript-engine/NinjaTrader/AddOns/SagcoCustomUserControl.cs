// SagcoCustomUserControl.cs — Reusable WPF ERU verdict gauge
// Drop into any NinjaTrader panel. Shows verdict color + ratio bar.

#region Using declarations
using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
#endregion

namespace NinjaTrader.NinjaScript.AddOns
{
    public class SagcoEruGauge : UserControl
    {
        private ProgressBar _ratioBar;
        private TextBlock   _verdictLabel;
        private TextBlock   _ratioLabel;
        private TextBlock   _claimLabel;

        private static readonly Dictionary<string, Brush> _verdictColors = new()
        {
            ["PROVEN"]        = new SolidColorBrush(Color.FromRgb(0,  230, 64))  { }.Freeze_(),
            ["PROMISING"]     = new SolidColorBrush(Color.FromRgb(30, 144, 255)) { }.Freeze_(),
            ["UNPROVEN"]      = new SolidColorBrush(Color.FromRgb(255,165,  0))  { }.Freeze_(),
            ["INFLATED"]      = new SolidColorBrush(Color.FromRgb(220,  20, 60)) { }.Freeze_(),
            ["UNCOMPUTED"]    = new SolidColorBrush(Color.FromRgb(100,100,100))  { }.Freeze_(),
        };

        public SagcoEruGauge()
        {
            var panel = new StackPanel { Margin = new Thickness(4) };

            _claimLabel = new TextBlock { Text = "—", Foreground = Brushes.Gray, FontSize = 10 };
            panel.Children.Add(_claimLabel);

            _verdictLabel = new TextBlock { Text = "UNCOMPUTED", FontSize = 14, FontWeight = FontWeights.Bold, Foreground = Brushes.Gray };
            panel.Children.Add(_verdictLabel);

            _ratioBar = new ProgressBar { Minimum = 0, Maximum = 2, Value = 0, Height = 8, Margin = new Thickness(0, 4, 0, 2) };
            panel.Children.Add(_ratioBar);

            _ratioLabel = new TextBlock { Text = "V = 0.000000", FontSize = 10, Foreground = Brushes.DimGray };
            panel.Children.Add(_ratioLabel);

            Content = panel;
        }

        public void Update(string claimId, double ratio, string verdict)
        {
            Dispatcher.InvokeAsync(() =>
            {
                _claimLabel.Text   = claimId;
                _ratioLabel.Text   = $"V = {ratio:F6}";
                _ratioBar.Value    = Math.Min(ratio, 2.0);
                _verdictLabel.Text = verdict;
                var brush = _verdictColors.GetValueOrDefault(verdict, Brushes.Gray);
                _verdictLabel.Foreground = brush;
                _ratioBar.Foreground     = brush;
            });
        }
    }

    // Freeze extension for inline use
    internal static class BrushExtensions
    {
        public static SolidColorBrush Freeze_(this SolidColorBrush b) { b.Freeze(); return b; }
    }
}
