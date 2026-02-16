/**
 * Sumerian cuneiform tokenizer with percussive mapping
 */
export class SumerianTokenizer {
    // Major Sumerian cuneiform glyphs
    static GLYPHS = {
        'DINGIR': { name: 'DINGIR', wedgeCount: 8, percussiveIntensity: 0.95, bronzeBellFreq: 432.0 },
        'LUGAL': { name: 'LUGAL', wedgeCount: 6, percussiveIntensity: 0.88, bronzeBellFreq: 384.0 },
        'EN': { name: 'EN', wedgeCount: 4, percussiveIntensity: 0.75, bronzeBellFreq: 288.0 },
        'NIN': { name: 'NIN', wedgeCount: 5, percussiveIntensity: 0.80, bronzeBellFreq: 324.0 },
        'KALAM': { name: 'KALAM', wedgeCount: 7, percussiveIntensity: 0.85, bronzeBellFreq: 396.0 },
        'AN': { name: 'AN', wedgeCount: 3, percussiveIntensity: 0.70, bronzeBellFreq: 256.0 },
        'KI': { name: 'KI', wedgeCount: 3, percussiveIntensity: 0.65, bronzeBellFreq: 216.0 },
        'ŠARRU': { name: 'ŠARRU', wedgeCount: 9, percussiveIntensity: 0.92, bronzeBellFreq: 486.0 },
        'NAM': { name: 'NAM', wedgeCount: 4, percussiveIntensity: 0.72, bronzeBellFreq: 288.0 },
        'ME': { name: 'ME', wedgeCount: 2, percussiveIntensity: 0.60, bronzeBellFreq: 192.0 }
    };
    /**
     * Tokenize Sumerian text (expecting glyph names in uppercase)
     */
    static tokenize(text) {
        const words = text.toUpperCase().split(/\s+/);
        const glyphs = [];
        for (const word of words) {
            if (this.GLYPHS[word]) {
                glyphs.push(this.GLYPHS[word]);
            }
            else {
                // Unknown glyph - create default
                glyphs.push({
                    name: word,
                    wedgeCount: 3,
                    percussiveIntensity: 0.5,
                    bronzeBellFreq: 220.0
                });
            }
        }
        return glyphs;
    }
    /**
     * Generate percussive transient for a wedge strike
     */
    static generateWedgeStrike(time, intensity, bronzeBellFreq, decayRate = 8.0) {
        if (time > 0.3)
            return 0.0;
        // Sharp attack with exponential decay
        const envelope = Math.exp(-time * decayRate);
        // Bronze bell harmonics
        const fundamental = Math.sin(2 * Math.PI * bronzeBellFreq * time);
        const overtone1 = Math.sin(2 * Math.PI * bronzeBellFreq * 2.87 * time) * 0.4;
        const overtone2 = Math.sin(2 * Math.PI * bronzeBellFreq * 3.13 * time) * 0.25;
        const overtone3 = Math.sin(2 * Math.PI * bronzeBellFreq * 4.21 * time) * 0.15;
        const signal = fundamental + overtone1 + overtone2 + overtone3;
        return signal * envelope * intensity;
    }
    /**
     * Generate rhythmic pattern based on wedge count
     */
    static generateRhythmicPattern(wedgeCount, duration) {
        const strikes = [];
        const interval = duration / (wedgeCount + 1);
        for (let i = 1; i <= wedgeCount; i++) {
            strikes.push(interval * i);
        }
        return strikes;
    }
    /**
     * Get all known glyphs
     */
    static getKnownGlyphs() {
        return Object.keys(this.GLYPHS);
    }
}
