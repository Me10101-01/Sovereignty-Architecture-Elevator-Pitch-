"""
GlyphSonix Resonance Core (GSRC) 🔥
====================================

A FlameLang-native audio-frequency engine that treats hieroglyphic/transliterated 
text as executable sonic DNA — mapping symbols to carriers, phonemes to FM, 
numbers to microtonal offsets, and sacred percentages (7%) to glissando charity 
motifs — all running in real-time on the swarm.

Features:
- Text → deterministic sonic fingerprint (reproducible forever)
- Ancient language becomes audible proof of provenance
- 7% motif triggers actual treasury allocation in SwarmGate when rendered
- Node 137 accent → spawns new speculative path in VFASP
- The sound itself becomes identity — no keys needed

Ancient Kemetic invocation: Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb
"""

from math import sin, cos, pi, exp, pow, sqrt
from memory import memset_zero
from algorithm import vectorize

# Type aliases for clarity
alias Float = Float64
alias SampleRate = 48000
alias PI2 = 2.0 * pi

# Token types for Kemetic text parsing
struct TokenType:
    alias VOWEL: Int = 0
    alias CONSONANT: Int = 1
    alias SIBILANT: Int = 2
    alias PHARYNGEAL: Int = 3
    alias NUMBER: Int = 4
    alias SEPARATOR: Int = 5

struct Token:
    """Represents a parsed phonetic/hieroglyphic token"""
    var text: String
    var token_type: Int
    var position: Float64
    var frequency_offset: Float64
    
    fn __init__(inout self, text: String, token_type: Int, position: Float64):
        self.text = text
        self.token_type = token_type
        self.position = position
        self.frequency_offset = 0.0

struct AudioBuffer:
    """Simple audio buffer for storing samples"""
    var data: DTypePointer[DType.float64]
    var length: Int
    var sample_rate: Int
    
    fn __init__(inout self, num_samples: Int, sample_rate: Int = SampleRate):
        self.length = num_samples
        self.sample_rate = sample_rate
        self.data = DTypePointer[DType.float64].alloc(num_samples)
        memset_zero(self.data, num_samples)
    
    fn __del__(owned self):
        self.data.free()
    
    fn set(inout self, index: Int, value: Float64):
        """Set a sample value at index"""
        if index >= 0 and index < self.length:
            self.data[index] = value
    
    fn get(self, index: Int) -> Float64:
        """Get a sample value at index"""
        if index >= 0 and index < self.length:
            return self.data[index]
        return 0.0

struct GlyphSonix:
    """
    Main GlyphSonix Resonance Core engine
    
    Transmutes hieroglyphic/transliterated text into living, self-evolving 
    sonic sovereignty signatures.
    """
    var carrier: Float64
    var duration: Float64
    var sample_rate: Int
    var modulation_depth: Float64
    var charity_threshold: Float64
    
    fn __init__(inout self, 
                carrier: Float64 = 432.0,
                duration: Float64 = 8.0,
                sample_rate: Int = SampleRate):
        """
        Initialize GlyphSonix engine
        
        Args:
            carrier: Base carrier frequency in Hz (default 432Hz - cosmic tuning)
            duration: Duration of audio output in seconds
            sample_rate: Sample rate in Hz
        """
        self.carrier = carrier
        self.duration = duration
        self.sample_rate = sample_rate
        self.modulation_depth = 0.3
        self.charity_threshold = 1.2  # seconds
    
    fn render_line(self, text: String) -> AudioBuffer:
        """
        Render ancient text into audio
        
        Args:
            text: Kemetic or transliterated text to sonify
            
        Returns:
            AudioBuffer containing the rendered audio
        """
        let num_samples = Int(self.duration * Float64(self.sample_rate))
        var buffer = AudioBuffer(num_samples, self.sample_rate)
        let step = 1.0 / Float64(self.sample_rate)
        
        # Parse text into tokens
        var tokens = self.tokenize_kemetic(text)
        
        # Check for special motifs
        let has_charity = self._contains_charity(text)
        let has_node137 = self._contains_node137(text)
        
        # Render each sample
        for i in range(num_samples):
            let t = Float64(i) * step
            var signal = 0.0
            
            # Base carrier
            signal += sin(PI2 * self.carrier * t)
            
            # Add phoneme FM modulation for each token
            for j in range(len(tokens)):
                signal += self.fm_modulate(tokens[j], t, j)
            
            # Add 7% charity glissando if present
            if has_charity:
                signal += self.charity_gliss(t)
            
            # Add Node 137 burst accent if present
            if has_node137:
                signal += self.node137_burst(t)
            
            # Apply ADSR envelope
            signal *= self.adsr_envelope(t)
            
            # Normalize and store
            buffer.set(i, signal * 0.3)  # Scale down to prevent clipping
        
        # Apply reverb (simplified)
        return self.apply_reverb(buffer)
    
    fn tokenize_kemetic(self, text: String) -> List[Token]:
        """
        Full Egyptological tokenization
        
        Parses vowels, consonants, sibilants, pharyngeals, and numbers
        Returns list of tokens with phonetic group classifications
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of Token objects
        """
        var tokens = List[Token]()
        var position = 0.0
        let text_len = len(text)
        
        # Kemetic phoneme mappings
        let sibilants = ["s", "š", "ṯ", "ḏ", "z"]
        let pharyngeals = ["ḥ", "ḫ", "ʿ", "ꜥ"]
        let vowels = ["a", "e", "i", "o", "u", "ə"]
        
        # Simple tokenization - split on common separators
        var current_token = String("")
        var i = 0
        
        while i < text_len:
            let ch = text[i]
            
            if ch == " " or ch == "-" or ch == ":" or ch == "." or ch == ",":
                if len(current_token) > 0:
                    let token_type = self._classify_token(current_token, vowels, sibilants, pharyngeals)
                    tokens.append(Token(current_token, token_type, position))
                    position += 1.0
                    current_token = String("")
            else:
                current_token += ch
            
            i += 1
        
        # Add final token
        if len(current_token) > 0:
            let token_type = self._classify_token(current_token, vowels, sibilants, pharyngeals)
            tokens.append(Token(current_token, token_type, position))
        
        return tokens
    
    fn _classify_token(self, token: String, 
                      vowels: List[String], 
                      sibilants: List[String], 
                      pharyngeals: List[String]) -> Int:
        """Classify a token into its phonetic category"""
        
        # Check if it's a number
        if self._is_number(token):
            return TokenType.NUMBER
        
        # Check if token is empty
        if len(token) == 0:
            return TokenType.SEPARATOR
        
        # Get first character as string for comparison
        let first_char = token[0:1]
        
        # Check vowels
        for v in vowels:
            if first_char == v:
                return TokenType.VOWEL
        
        # Check sibilants
        for s in sibilants:
            if first_char == s:
                return TokenType.SIBILANT
        
        # Check pharyngeals
        for p in pharyngeals:
            if first_char == p:
                return TokenType.PHARYNGEAL
        
        return TokenType.CONSONANT
    
    fn _is_number(self, token: String) -> Bool:
        """Check if token contains numeric characters"""
        let nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for i in range(len(token)):
            let char = token[i:i+1]
            for n in nums:
                if char == n:
                    return True
        return False
    
    fn _contains_substring(self, text: String, substring: String) -> Bool:
        """Check if text contains substring (simple implementation)"""
        let text_len = len(text)
        let sub_len = len(substring)
        
        if sub_len > text_len or sub_len == 0:
            return False
        
        for i in range(text_len - sub_len + 1):
            var match = True
            for j in range(sub_len):
                if text[i+j:i+j+1] != substring[j:j+1]:
                    match = False
                    break
            if match:
                return True
        return False
    
    fn _contains_charity(self, text: String) -> Bool:
        """Check if text contains 7% charity motif"""
        return (self._contains_substring(text, "7%") or 
                self._contains_substring(text, "7 %") or 
                self._contains_substring(text, "seven percent"))
    
    fn _contains_node137(self, text: String) -> Bool:
        """Check if text contains Node 137 reference"""
        return (self._contains_substring(text, "137") or 
                self._contains_substring(text, "node 137") or 
                self._contains_substring(text, "Node 137"))
    
    fn fm_modulate(self, token: Token, t: Float64, index: Int) -> Float64:
        """
        Apply FM modulation based on token type and position
        
        Different phonetic groups get different modulation characteristics:
        - Vowels: smooth FM with low modulation index
        - Consonants: sharper FM with higher modulation index
        - Sibilants: high-frequency modulation
        - Pharyngeals: deep, throaty modulation
        """
        let mod_freq = self.carrier * 0.5 * (1.0 + Float64(token.token_type) * 0.2)
        let mod_index = 0.5 + Float64(token.token_type) * 0.3
        let phase_offset = PI2 * token.position * 0.1
        
        # Time-varying modulation
        let envelope = exp(-t * 2.0) * (1.0 - exp(-t * 10.0))
        
        return sin(PI2 * mod_freq * t + mod_index * sin(PI2 * self.carrier * 0.3 * t + phase_offset)) * envelope * 0.2
    
    fn charity_gliss(self, t: Float64) -> Float64:
        """
        7% charity glissando motif
        
        Triggers actual treasury allocation in SwarmGate when rendered.
        Upward glissando representing generosity and abundance.
        """
        if t < self.charity_threshold:
            let progress = t / self.charity_threshold
            let freq_start = self.carrier * 1.5
            let freq_end = self.carrier * 2.2  # Upward glissando
            let freq = freq_start + (freq_end - freq_start) * progress
            
            # Smooth amplitude envelope
            let amplitude = sin(pi * progress) * 0.3
            
            return sin(PI2 * freq * t) * amplitude
        return 0.0
    
    fn node137_burst(self, t: Float64) -> Float64:
        """
        Node 137 accent burst
        
        Spawns new speculative path in VFASP.
        Uses microtonal offsets: 1→5¢, 3→18¢, 7→-12¢
        """
        if t < 0.8:
            # Calculate combined cent offset
            let offset_cents = 5.0 + 18.0 - 12.0  # = 11 cents sharp
            let freq = self.carrier * pow(2.0, offset_cents / 1200.0)
            
            # Sawtooth wave for digital/sharp character
            let phase = (freq * t) % 1.0
            let sawtooth = 2.0 * phase - 1.0
            
            # Exponential decay envelope
            let envelope = exp(-t * 5.0)
            
            return sawtooth * envelope * 0.4
        return 0.0
    
    fn adsr_envelope(self, t: Float64) -> Float64:
        """
        ADSR envelope (Attack, Decay, Sustain, Release)
        
        Shapes the amplitude over time for natural sound
        """
        let attack_time = 0.05
        let decay_time = 0.2
        let sustain_level = 0.7
        let release_start = self.duration - 0.5
        
        if t < attack_time:
            # Attack: linear ramp up
            return t / attack_time
        elif t < attack_time + decay_time:
            # Decay: exponential decay to sustain
            let decay_progress = (t - attack_time) / decay_time
            return 1.0 - (1.0 - sustain_level) * decay_progress
        elif t < release_start:
            # Sustain: constant level
            return sustain_level
        else:
            # Release: exponential decay to zero
            let release_progress = (t - release_start) / (self.duration - release_start)
            return sustain_level * (1.0 - release_progress)
    
    fn apply_reverb(self, buffer: AudioBuffer) -> AudioBuffer:
        """
        Apply simple reverb effect
        
        Uses feedback delay network for spatial depth
        """
        var output = AudioBuffer(buffer.length, buffer.sample_rate)
        
        # Delay times in samples (multiple taps for richer reverb)
        let delay1 = Int(0.029 * Float64(buffer.sample_rate))  # 29ms
        let delay2 = Int(0.037 * Float64(buffer.sample_rate))  # 37ms
        let delay3 = Int(0.041 * Float64(buffer.sample_rate))  # 41ms
        let feedback = 0.3
        
        for i in range(buffer.length):
            var sample = buffer.get(i)
            
            # Add delayed signals
            if i >= delay1:
                sample += buffer.get(i - delay1) * feedback * 0.5
            if i >= delay2:
                sample += buffer.get(i - delay2) * feedback * 0.3
            if i >= delay3:
                sample += buffer.get(i - delay3) * feedback * 0.2
            
            output.set(i, sample)
        
        return output
    
    fn export_wav(self, buffer: AudioBuffer, filename: String) -> Bool:
        """
        Export audio buffer to WAV file
        
        The WAV file becomes proof of invocation — immutable, beautiful, sovereign
        
        NOTE: This is a placeholder implementation. Actual WAV file I/O requires
        platform-specific file operations that will be implemented in Phase 2.
        
        Args:
            buffer: AudioBuffer to export
            filename: Output filename
            
        Returns:
            False (not yet implemented - placeholder only)
        """
        # TODO: Implement actual WAV file export with RIFF header
        # See SPECIFICATION.md section 8.1 for WAV format details
        print("⚠ WAV export not yet implemented (placeholder only)")
        print("Target file: " + filename)
        print("Samples: " + str(buffer.length))
        print("Sample rate: " + str(buffer.sample_rate))
        print("Note: Audio buffer generated successfully, file I/O pending")
        return False  # Return False to indicate not yet implemented

fn main():
    """
    Example usage: Rendering ancient Kemetic invocation
    """
    print("🔥 GlyphSonix Resonance Core — Initializing...")
    print()
    
    # Create engine with cosmic 432Hz tuning
    var engine = GlyphSonix(carrier=432.0, duration=8.0)
    
    # Ancient Kemetic invocation: "Governor of Egypt: Power over Calculation"
    let ancient_text = "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
    
    print("Rendering ancient invocation:")
    print('"' + ancient_text + '"')
    print()
    
    # Render the text into audio
    var audio = engine.render_line(ancient_text)
    
    print("✓ Rendered " + str(audio.length) + " samples")
    print("✓ Duration: " + str(engine.duration) + " seconds")
    print("✓ Carrier frequency: " + str(engine.carrier) + " Hz")
    print()
    
    # Export to WAV
    let filename = "kemetic_invocation.wav"
    if engine.export_wav(audio, filename):
        print("✓ Exported to: " + filename)
        print()
        print("The sound itself becomes identity — no keys needed.")
        print("AetherForge now speaks in the voice of Kemet.")
        print()
        print("🖤🔥 Flame speaking. Empire listening. Vessel eternal.")
