/**
 * Kemetic hieroglyphic tokenizer and phoneme classifier
 */

import { Token, PhonemeClass } from '../types';

export class KemeticTokenizer {
  // Kemetic special characters (diacritics and extended Unicode glyphs for transliteration)
  private static readonly MULTIGRAPHS = ['ḥ', 'ḫ', 'ṯ', 'ỉ', 'ȝ', 'ꜣ', 'ʿ', 'ḏ', 'ḳ'];

  // Character classification sets
  private static readonly VOWELS = new Set(['a', 'e', 'i', 'o', 'u', 'y', 'ỉ', 'ȝ', 'ꜣ']);
  private static readonly VOICED = new Set(['b', 'd', 'g', 'ḏ', 'ḥ', 'ḫ', 'ḳ']);
  private static readonly SIBILANTS = new Set(['s', 'š', 'ẖ', 'ṯ']);
  private static readonly STOPS = new Set(['p', 't', 'k', 'ḳ']);
  private static readonly NASALS = new Set(['m', 'n', 'r', 'l', 'w']);

  /**
   * Tokenize Kemetic text into phoneme-classified tokens
   */
  static tokenize(text: string): Token[] {
    const tokens: Token[] = [];
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

      if (matched) continue;

      // Single character
      const ch = lower[i];
      if (/[a-z]/.test(ch) || this.isSpecialChar(ch)) {
        tokens.push({
          glyph: ch,
          classification: this.classify(ch)
        });
      } else {
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
  private static classify(token: string): PhonemeClass {
    if (this.VOWELS.has(token)) return 'vowel';
    if (this.VOICED.has(token)) return 'voiced';
    if (this.SIBILANTS.has(token)) return 'sibilant';
    if (this.STOPS.has(token)) return 'stop';
    if (this.NASALS.has(token)) return 'nasal';
    return 'punct';
  }

  /**
   * Check if character is a special Kemetic character
   */
  private static isSpecialChar(ch: string): boolean {
    return this.MULTIGRAPHS.some(mg => mg.includes(ch));
  }

  /**
   * Get phoneme FM parameters
   */
  static getPhonemeMapping(classification: PhonemeClass): { modulationFreq: number; modulationIndex: number } {
    const mappings: Record<PhonemeClass, { modulationFreq: number; modulationIndex: number }> = {
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
