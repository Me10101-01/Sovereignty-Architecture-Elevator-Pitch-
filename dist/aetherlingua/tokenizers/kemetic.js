/**
 * Kemetic hieroglyphic tokenizer and phoneme classifier
 */
export class KemeticTokenizer {
    // Kemetic special characters (diacritics and extended Unicode glyphs for transliteration)
    static MULTIGRAPHS = ['ḥ', 'ḫ', 'ṯ', 'ỉ', 'ȝ', 'ꜣ', 'ʿ', 'ḏ', 'ḳ'];
    // Character classification sets
    static VOWELS = new Set(['a', 'e', 'i', 'o', 'u', 'y', 'ỉ', 'ȝ', 'ꜣ']);
    static VOICED = new Set(['b', 'd', 'g', 'ḏ', 'ḥ', 'ḫ', 'ḳ']);
    static SIBILANTS = new Set(['s', 'š', 'ẖ', 'ṯ']);
    static STOPS = new Set(['p', 't', 'k', 'ḳ']);
    static NASALS = new Set(['m', 'n', 'r', 'l', 'w']);
    /**
     * Tokenize Kemetic text into phoneme-classified tokens
     */
    static tokenize(text) {
        const tokens = [];
        const lower = text.toLowerCase();
        let i = 0;
        while (i < lower.length) {
            let matched = false;
            // Check for multigraphs first
            for (const mg of this.MULTIGRAPHS) {
                if (lower.substring(i).startsWith(mg)) {
                    tokens.push({
                        glyph: mg,
                        classification: this.classify(mg)
                    });
                    i += mg.length;
                    matched = true;
                    break;
                }
            }
            if (matched)
                continue;
            // Single character
            const ch = lower[i];
            if (/[a-z]/.test(ch) || this.isSpecialChar(ch)) {
                tokens.push({
                    glyph: ch,
                    classification: this.classify(ch)
                });
            }
            else {
                tokens.push({
                    glyph: ch,
                    classification: 'punct'
                });
            }
            i++;
        }
        return tokens;
    }
    /**
     * Classify a token into phoneme class
     */
    static classify(token) {
        if (this.VOWELS.has(token))
            return 'vowel';
        if (this.VOICED.has(token))
            return 'voiced';
        if (this.SIBILANTS.has(token))
            return 'sibilant';
        if (this.STOPS.has(token))
            return 'stop';
        if (this.NASALS.has(token))
            return 'nasal';
        return 'punct';
    }
    /**
     * Check if character is a special Kemetic character
     */
    static isSpecialChar(ch) {
        return this.MULTIGRAPHS.some(mg => mg.includes(ch));
    }
    /**
     * Get phoneme FM parameters
     */
    static getPhonemeMapping(classification) {
        const mappings = {
            vowel: { modulationFreq: 5.0, modulationIndex: 1.8 },
            voiced: { modulationFreq: 7.0, modulationIndex: 2.4 },
            sibilant: { modulationFreq: 12.0, modulationIndex: 1.2 },
            stop: { modulationFreq: 18.0, modulationIndex: 0.9 },
            nasal: { modulationFreq: 3.5, modulationIndex: 1.1 },
            punct: { modulationFreq: 0.5, modulationIndex: 0.6 }
        };
        return mappings[classification];
    }
}
