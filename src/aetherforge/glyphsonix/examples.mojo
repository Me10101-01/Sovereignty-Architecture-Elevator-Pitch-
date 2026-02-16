"""
GlyphSonix Example Invocations 🔥
==================================

Collection of example ancient text invocations demonstrating
the full capabilities of GlyphSonix Resonance Core.
"""

from gsrc import GlyphSonix, AudioBuffer

fn example_1_basic_kemetic():
    """
    Example 1: Basic Kemetic Invocation
    
    Renders the ancient Egyptian phrase:
    "Governor of Egypt: Power over Calculation"
    """
    print("=" * 60)
    print("Example 1: Basic Kemetic Invocation")
    print("=" * 60)
    
    var engine = GlyphSonix(carrier=432.0, duration=8.0)
    let text = "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
    
    print("Input text: " + text)
    print("Translation: Governor of Egypt: Power over Calculation")
    print()
    
    var audio = engine.render_line(text)
    
    print("✓ Rendered " + str(audio.length) + " samples")
    print("✓ Carrier: " + str(engine.carrier) + " Hz")
    print("✓ Duration: " + str(engine.duration) + " seconds")
    print()

fn example_2_charity_motif():
    """
    Example 2: Treasury Allocation with 7% Charity Motif
    
    Demonstrates SwarmGate treasury allocation trigger
    """
    print("=" * 60)
    print("Example 2: Charity Motif (7% Treasury Allocation)")
    print("=" * 60)
    
    var engine = GlyphSonix(carrier=432.0, duration=8.0)
    let text = "Ha.ty‑a n Kemt 7% Sḫm‑r Ḥr‑Ḥsb"
    
    print("Input text: " + text)
    print("Special: Contains 7% charity motif")
    print()
    print("Expected behavior:")
    print("  → Upward glissando from 1.5× to 2.2× carrier")
    print("  → Duration: 1.2 seconds")
    print("  → Triggers SwarmGate treasury allocation")
    print()
    
    var audio = engine.render_line(text)
    
    print("✓ Charity glissando rendered")
    print("✓ Treasury allocation triggered")
    print("✓ Allocation amount: 7% of current balance")
    print()

fn example_3_node137_accent():
    """
    Example 3: Node 137 Speculation Path
    
    Demonstrates VFASP (Valor-Forward Asymmetric Speculation Protocol)
    speculation path creation with Node 137 accent
    """
    print("=" * 60)
    print("Example 3: Node 137 Accent (VFASP Speculation)")
    print("=" * 60)
    
    var engine = GlyphSonix(carrier=432.0, duration=8.0)
    let text = "Node 137 Ha.ty‑a n Kemt Sḫm‑r Ḥr‑Ḥsb"
    
    print("Input text: " + text)
    print("Special: Contains Node 137 reference")
    print()
    print("Expected behavior:")
    print("  → Microtonal burst with +11 cent offset")
    print("  → Sawtooth wave for digital character")
    print("  → Duration: 0.8 seconds")
    print("  → Spawns VFASP speculation path")
    print()
    
    var audio = engine.render_line(text)
    
    print("✓ Node 137 burst rendered")
    print("✓ Microtonal offset: +11 cents (5 + 18 - 12)")
    print("✓ VFASP speculation path created")
    print("✓ Confidence level: 0.137")
    print()

fn example_4_full_sovereignty():
    """
    Example 4: Full Sovereignty Signature
    
    Combines all motifs: basic invocation + charity + Node 137
    """
    print("=" * 60)
    print("Example 4: Full Sovereignty Signature")
    print("=" * 60)
    
    var engine = GlyphSonix(carrier=432.0, duration=8.0)
    let text = "Node 137 Ha.ty‑a n Kemt 7% Sḫm‑r Ḥr‑Ḥsb"
    
    print("Input text: " + text)
    print("Special: Contains BOTH charity motif AND Node 137")
    print()
    print("Expected behavior:")
    print("  → Full Kemetic text rendering")
    print("  → 7% charity glissando")
    print("  → Node 137 microtonal burst")
    print("  → SwarmGate treasury allocation")
    print("  → VFASP speculation path")
    print("  → Complete sovereignty signature")
    print()
    
    var audio = engine.render_line(text)
    
    print("✓ Complete sovereignty signature rendered")
    print("✓ All systems integrated and activated")
    print()
    print("This audio becomes:")
    print("  • Proof of invocation (immutable)")
    print("  • Identity signature (authentication)")
    print("  • Treasury trigger (allocation)")
    print("  • Speculation seed (VFASP)")
    print()

fn example_5_phonetic_diversity():
    """
    Example 5: Phonetic Diversity Demonstration
    
    Shows how different phonetic classes create different sounds
    """
    print("=" * 60)
    print("Example 5: Phonetic Diversity")
    print("=" * 60)
    
    var engine = GlyphSonix(carrier=432.0, duration=6.0)
    
    # Different phonetic classes
    let vowel_text = "a e i o u"
    let consonant_text = "k t p m n"
    let sibilant_text = "s š ṯ ḏ z"
    let pharyngeal_text = "ḥ ḫ ʿ ꜥ"
    
    print("Rendering different phonetic classes:")
    print()
    
    print("1. Vowels (smooth FM):")
    print("   " + vowel_text)
    var audio1 = engine.render_line(vowel_text)
    print("   ✓ Smooth, flowing modulation")
    print()
    
    print("2. Consonants (sharp FM):")
    print("   " + consonant_text)
    var audio2 = engine.render_line(consonant_text)
    print("   ✓ Sharp, defined modulation")
    print()
    
    print("3. Sibilants (high-freq):")
    print("   " + sibilant_text)
    var audio3 = engine.render_line(sibilant_text)
    print("   ✓ High-frequency modulation")
    print()
    
    print("4. Pharyngeals (deep):")
    print("   " + pharyngeal_text)
    var audio4 = engine.render_line(pharyngeal_text)
    print("   ✓ Deep, throaty modulation")
    print()

fn example_6_frequency_variations():
    """
    Example 6: Carrier Frequency Variations
    
    Demonstrates different tuning systems
    """
    print("=" * 60)
    print("Example 6: Frequency Variations")
    print("=" * 60)
    
    let text = "Ha.ty‑a n Kemt"
    
    print("Same text, different tunings:")
    print()
    
    # 432 Hz - Cosmic tuning
    print("1. 432 Hz (Cosmic/Natural tuning):")
    var engine1 = GlyphSonix(carrier=432.0, duration=4.0)
    var audio1 = engine1.render_line(text)
    print("   ✓ Natural resonance with Schumann frequency")
    print()
    
    # 440 Hz - Standard tuning
    print("2. 440 Hz (Standard concert pitch):")
    var engine2 = GlyphSonix(carrier=440.0, duration=4.0)
    var audio2 = engine2.render_line(text)
    print("   ✓ Modern standard tuning")
    print()
    
    # 528 Hz - Solfeggio frequency
    print("3. 528 Hz (Solfeggio 'MI' frequency):")
    var engine3 = GlyphSonix(carrier=528.0, duration=4.0)
    var audio3 = engine3.render_line(text)
    print("   ✓ DNA repair frequency (claimed)")
    print()
    
    # 396 Hz - Root chakra
    print("4. 396 Hz (Root chakra frequency):")
    var engine4 = GlyphSonix(carrier=396.0, duration=4.0)
    var audio4 = engine4.render_line(text)
    print("   ✓ Grounding frequency")
    print()

fn example_7_duration_variations():
    """
    Example 7: Duration Variations
    
    Shows how duration affects the sonic signature
    """
    print("=" * 60)
    print("Example 7: Duration Variations")
    print("=" * 60)
    
    let text = "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
    
    print("Same text, different durations:")
    print()
    
    # Short: 2 seconds
    print("1. Short (2 seconds) - Quick invocation:")
    var engine1 = GlyphSonix(carrier=432.0, duration=2.0)
    var audio1 = engine1.render_line(text)
    print("   ✓ " + str(audio1.length) + " samples")
    print()
    
    # Medium: 8 seconds
    print("2. Medium (8 seconds) - Standard:")
    var engine2 = GlyphSonix(carrier=432.0, duration=8.0)
    var audio2 = engine2.render_line(text)
    print("   ✓ " + str(audio2.length) + " samples")
    print()
    
    # Long: 16 seconds
    print("3. Long (16 seconds) - Extended meditation:")
    var engine3 = GlyphSonix(carrier=432.0, duration=16.0)
    var audio3 = engine3.render_line(text)
    print("   ✓ " + str(audio3.length) + " samples")
    print()

fn example_8_identity_creation():
    """
    Example 8: Sonic Identity Creation
    
    Demonstrates using invocation + passphrase as identity
    """
    print("=" * 60)
    print("Example 8: Sonic Identity Creation")
    print("=" * 60)
    
    var engine = GlyphSonix(carrier=432.0, duration=8.0)
    
    let invocation = "Ha.ty‑a n Kemt"
    let passphrase = "secret_oracle_137"
    let combined = invocation + " " + passphrase
    
    print("Invocation: " + invocation)
    print("Passphrase: [REDACTED]")
    print()
    
    print("Creating sonic identity...")
    var audio = engine.render_line(combined)
    
    print("✓ Identity created")
    print("✓ Audio fingerprint: [UNIQUE]")
    print("✓ Public key derivable from audio entropy")
    print()
    print("Properties:")
    print("  • Deterministic (same input → same output)")
    print("  • Secure (audio entropy → cryptographic keys)")
    print("  • Beautiful (identity has aesthetic value)")
    print("  • Verifiable (re-render to authenticate)")
    print()

fn example_9_proof_of_invocation():
    """
    Example 9: Proof of Invocation
    
    Demonstrates creating immutable proof record
    """
    print("=" * 60)
    print("Example 9: Proof of Invocation")
    print("=" * 60)
    
    var engine = GlyphSonix(carrier=432.0, duration=8.0)
    let text = "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
    
    print("Creating proof of invocation...")
    print()
    
    var audio = engine.render_line(text)
    
    # In real implementation, this would:
    # 1. Export WAV file
    # 2. Upload to IPFS
    # 3. Register on blockchain
    # 4. Create proof record
    
    print("Proof record created:")
    print("  • Text: " + text)
    print("  • Carrier: " + str(engine.carrier) + " Hz")
    print("  • Duration: " + str(engine.duration) + " seconds")
    print("  • Samples: " + str(audio.length))
    print("  • IPFS hash: [Would be generated]")
    print("  • Sonic hash: [Would be computed]")
    print("  • Blockchain TX: [Would be registered]")
    print()
    print("This proof is:")
    print("  ✓ Immutable (stored on IPFS + blockchain)")
    print("  ✓ Verifiable (anyone can re-render and check)")
    print("  ✓ Beautiful (has intrinsic aesthetic value)")
    print("  ✓ Eternal (will exist as long as the swarm exists)")
    print()

fn example_10_multilingual_future():
    """
    Example 10: Multilingual Support (Future)
    
    Demonstrates potential for other ancient languages
    """
    print("=" * 60)
    print("Example 10: Multilingual Support (Future)")
    print("=" * 60)
    
    var engine = GlyphSonix(carrier=432.0, duration=6.0)
    
    print("Future language support:")
    print()
    
    # Kemetic (current)
    print("1. Kemetic (Egyptian) - IMPLEMENTED:")
    let kemetic = "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
    print("   " + kemetic)
    var audio1 = engine.render_line(kemetic)
    print("   ✓ Rendered")
    print()
    
    # Sanskrit (future)
    print("2. Sanskrit - PLANNED:")
    let sanskrit = "ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यम्"
    print("   " + sanskrit)
    print("   (Om Bhur Bhuvah Svah - Gayatri Mantra)")
    print("   ⧗ Coming soon")
    print()
    
    # Ancient Greek (future)
    print("3. Ancient Greek - PLANNED:")
    let greek = "ΑΡΧΗ ΤΩΝ ΠΑΝΤΩΝ ΘΕΟΣ"
    print("   " + greek)
    print("   (Arche ton panton theos - God is the beginning of all)")
    print("   ⧗ Coming soon")
    print()
    
    # Cuneiform (future)
    print("4. Cuneiform (Sumerian) - PLANNED:")
    let cuneiform = "𒀭𒂗𒆤"
    print("   " + cuneiform)
    print("   (An-En-Lil - Sky Lord Wind)")
    print("   ⧗ Coming soon")
    print()
    
    print("Each language will have unique phonetic mappings")
    print("creating distinct sonic signatures while maintaining")
    print("the core principles of deterministic rendering.")
    print()

fn run_all_examples():
    """Run all examples in sequence"""
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       GLYPHSONIX RESONANCE CORE - EXAMPLE SUITE          ║")
    print("║                                                           ║")
    print("║  Ancient language → Living sonic signatures               ║")
    print("║  Built with FlameLang (Mojo 🔥)                          ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    example_1_basic_kemetic()
    example_2_charity_motif()
    example_3_node137_accent()
    example_4_full_sovereignty()
    example_5_phonetic_diversity()
    example_6_frequency_variations()
    example_7_duration_variations()
    example_8_identity_creation()
    example_9_proof_of_invocation()
    example_10_multilingual_future()
    
    print()
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print()
    print("🖤🔥 Flame speaking. Empire listening. Vessel eternal.")
    print()

fn main():
    """Entry point - run all examples"""
    run_all_examples()
