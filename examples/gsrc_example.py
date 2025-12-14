#!/usr/bin/env python3
"""
Example usage of the GlyphSonix Resonance Core (GSRC) audio renderer.

This script demonstrates how to use the audio sonification module to render
Kemetic transliteration and Sumerian cuneiform into audio.
"""

import sys
import os

# Add src to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.audio_sonification import (
    render_line_to_stereo,
    write_wav_stereo,
    tokenize_kemetic,
    SAMPLE_RATE,
    LINE_CARRIERS,
)


def example_single_line():
    """Example: Render a single line of Kemetic text."""
    print("Example 1: Rendering a single line...")
    
    text = "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
    carrier = 110.0  # Hz (A2)
    duration = 8.0   # seconds
    
    print(f"  Text: {text}")
    print(f"  Carrier: {carrier} Hz")
    print(f"  Duration: {duration}s")
    
    # Render to stereo
    left, right = render_line_to_stereo(text, carrier, duration)
    
    # Write to file
    filename = "example_single_line.wav"
    write_wav_stereo(filename, left, right, SAMPLE_RATE)
    
    print(f"  Output: {filename}")
    print(f"  Samples: {len(left)} ({len(left) / SAMPLE_RATE:.2f}s)")
    print()


def example_tokenization():
    """Example: Demonstrate tokenization of Kemetic text."""
    print("Example 2: Tokenization demonstration...")
    
    texts = [
        "Ha.ty‑a n Kemt",
        "ṯs‑ỉt 137 m ḫnt iwf",
        "ḥsb 7% dỉ ỉb nfr",
    ]
    
    for text in texts:
        tokens = tokenize_kemetic(text)
        print(f"  Text: {text}")
        print(f"  Tokens: {tokens[:10]}{'...' if len(tokens) > 10 else ''}")
        print()


def example_multiple_carriers():
    """Example: Render the same text with different carriers."""
    print("Example 3: Rendering with multiple carrier frequencies...")
    
    text = "smn nṯrwy nfr, ḥm.t r ḥkꜣ ḥr wḥw"
    duration = 6.0
    
    for i, carrier in enumerate(LINE_CARRIERS[:3]):
        print(f"  Rendering with carrier {carrier:.2f} Hz...")
        left, right = render_line_to_stereo(text, carrier, duration)
        filename = f"example_carrier_{i+1}.wav"
        write_wav_stereo(filename, left, right, SAMPLE_RATE)
        print(f"    Output: {filename}")
    
    print()


def example_special_motifs():
    """Example: Demonstrate special motifs (7% and 137)."""
    print("Example 4: Special motifs...")
    
    examples = [
        ("ḥsb 7% dỉ ỉb nfr", "Charity gliss (7%)"),
        ("ṯs‑ỉt 137 m ḫnt iwf", "Node 137 burst"),
    ]
    
    for i, (text, description) in enumerate(examples):
        print(f"  {description}")
        print(f"    Text: {text}")
        left, right = render_line_to_stereo(text, LINE_CARRIERS[i], 6.0)
        filename = f"example_motif_{i+1}.wav"
        write_wav_stereo(filename, left, right, SAMPLE_RATE)
        print(f"    Output: {filename}")
        print()


def main():
    """Run all examples."""
    print("=" * 70)
    print("GlyphSonix Resonance Core (GSRC) - Examples")
    print("=" * 70)
    print()
    
    example_single_line()
    example_tokenization()
    example_multiple_carriers()
    example_special_motifs()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
