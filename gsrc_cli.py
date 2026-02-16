#!/usr/bin/env python3
"""
GlyphSonix Resonance Core (GSRC) - Command Line Interface

Simple CLI wrapper for the audio sonification module.
"""

import argparse
import sys
from src.audio_sonification import (
    render_line_to_stereo,
    write_wav_stereo,
    SAMPLE_RATE,
    LINE_CARRIERS,
)
from src.audio_sonification.gsrc_full import main as render_full


def render_text(text: str, output: str, carrier: float = 110.0, duration: float = 8.0):
    """Render a single line of text to WAV."""
    print(f"Rendering: {text}")
    print(f"Carrier: {carrier} Hz, Duration: {duration}s")
    
    left, right = render_line_to_stereo(text, carrier, duration)
    write_wav_stereo(output, left, right, SAMPLE_RATE)
    
    print(f"Output: {output}")
    print(f"Samples: {len(left)} ({len(left) / SAMPLE_RATE:.2f}s)")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='GlyphSonix Resonance Core - Ancient Language Audio Renderer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render the default six lines
  %(prog)s --full
  
  # Render custom text
  %(prog)s --text "Ha.ty n Kemt" --output my_render.wav
  
  # Render with custom carrier frequency
  %(prog)s --text "ṯs‑ỉt 137 m ḫnt iwf" --carrier 220.0 --duration 6.0
  
  # Show carrier frequencies
  %(prog)s --carriers
        """
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Render the full six-line default text'
    )
    
    parser.add_argument(
        '--text',
        type=str,
        help='Text to render (Kemetic transliteration)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='output.wav',
        help='Output filename (default: output.wav)'
    )
    
    parser.add_argument(
        '--carrier',
        type=float,
        default=110.0,
        help='Carrier frequency in Hz (default: 110.0)'
    )
    
    parser.add_argument(
        '--duration',
        type=float,
        default=8.0,
        help='Duration in seconds (default: 8.0)'
    )
    
    parser.add_argument(
        '--carriers',
        action='store_true',
        help='Show available carrier frequencies'
    )
    
    args = parser.parse_args()
    
    # Show carriers
    if args.carriers:
        print("Available carrier frequencies:")
        print("=" * 40)
        for i, freq in enumerate(LINE_CARRIERS, 1):
            print(f"  Line {i}: {freq:.2f} Hz")
        return 0
    
    # Full render
    if args.full:
        print("Rendering full six-line default text...")
        print("=" * 70)
        render_full()
        return 0
    
    # Custom text render
    if args.text:
        render_text(args.text, args.output, args.carrier, args.duration)
        return 0
    
    # No action specified
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
