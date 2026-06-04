/**
 * Keyboard88 — SVG renderer for the standard 88-key piano.
 *
 * Layout:  52 white keys × 14px wide,  36 black keys × 8px wide × 55px tall
 * White key height: 90px
 *
 * Events dispatched on the SVG:
 *   'keypress'   — { keyNumber, note, octave, frequencyHz }
 *   'keyrelease' — { keyNumber }
 */

import { FrequencyGenerator } from '../core/FrequencyGenerator.js';
import { synth } from '../utils/audioContext.js';

const SVG_NS = 'http://www.w3.org/2000/svg';

const WK_W = 14;    // white key width  (px)
const WK_H = 90;    // white key height
const BK_W = 8;     // black key width
const BK_H = 55;    // black key height

const COLORS = {
  white:          '#dde4f0',
  whiteHover:     '#c5d0e8',
  whiteActive:    '#f5a623',
  whiteDiatonic:  '#aad4f5',
  black:          '#1a1a2e',
  blackHover:     '#2a2a4e',
  blackActive:    '#e94560',
  blackDiatonic:  '#1a6b8a',
  stroke:         '#667',
  label:          '#44466a',
  labelOctave:    '#88aacc'
};

// For each note in the chromatic scale starting at A, record whether it is
// white and, if black, its fractional x-offset within the preceding white key.
const KEY_LAYOUT = [
  { note: 'A',  isWhite: true  },
  { note: 'A#', isWhite: false, offset: 0.65 },
  { note: 'B',  isWhite: true  },
  { note: 'C',  isWhite: true  },
  { note: 'C#', isWhite: false, offset: 0.65 },
  { note: 'D',  isWhite: true  },
  { note: 'D#', isWhite: false, offset: 0.65 },
  { note: 'E',  isWhite: true  },
  { note: 'F',  isWhite: true  },
  { note: 'F#', isWhite: false, offset: 0.65 },
  { note: 'G',  isWhite: true  },
  { note: 'G#', isWhite: false, offset: 0.65 },
];

export class Keyboard88 {
  /**
   * @param {string|HTMLElement} container
   */
  constructor(container) {
    this.root = typeof container === 'string'
      ? document.querySelector(container)
      : container;

    this.manifest  = FrequencyGenerator.generate88KeyManifest();
    this.diatonic  = new Set();
    this._keyEls   = new Map();   // keyNumber → SVGElement
    this._activeKeys = new Set();

    this._svg = null;
    this._render();
    this._bindGlobalEvents();
  }

  // ── Build SVG ──────────────────────────────────────────────────────────────

  _render() {
    const totalWhite = this.manifest.filter(k => k.isWhite).length;  // 52
    const svgW = totalWhite * WK_W;
    const svgH = WK_H + 20;

    const svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('viewBox', `0 0 ${svgW} ${svgH}`);
    svg.setAttribute('width',  '100%');
    svg.setAttribute('class',  'keyboard-88');

    // Background
    const bg = document.createElementNS(SVG_NS, 'rect');
    bg.setAttribute('x', 0); bg.setAttribute('y', 0);
    bg.setAttribute('width', svgW); bg.setAttribute('height', svgH);
    bg.setAttribute('fill', '#0d0d1a');
    svg.appendChild(bg);

    const whiteLayer = document.createElementNS(SVG_NS, 'g');
    const blackLayer = document.createElementNS(SVG_NS, 'g');

    let whiteX = 0;
    let prevWhiteX = 0;

    for (const key of this.manifest) {
      if (key.isWhite) {
        const rect = this._makeWhiteKey(key, whiteX);
        whiteLayer.appendChild(rect);
        this._keyEls.set(key.keyNumber, rect);
        prevWhiteX = whiteX;
        whiteX += WK_W;
      } else {
        // Black key sits to the right edge of the previous white key
        const bx = prevWhiteX + WK_W - BK_W * 0.5;
        const rect = this._makeBlackKey(key, bx);
        blackLayer.appendChild(rect);
        this._keyEls.set(key.keyNumber, rect);
      }
    }

    svg.appendChild(whiteLayer);
    svg.appendChild(blackLayer);

    // Octave labels at C positions
    for (const key of this.manifest) {
      if (key.note === 'C') {
        const el = this._keyEls.get(key.keyNumber);
        const x  = parseFloat(el.getAttribute('x')) + WK_W / 2;
        const lbl = document.createElementNS(SVG_NS, 'text');
        lbl.setAttribute('x', x);
        lbl.setAttribute('y', WK_H + 14);
        lbl.setAttribute('text-anchor', 'middle');
        lbl.setAttribute('font-size', '8');
        lbl.setAttribute('fill', COLORS.labelOctave);
        lbl.setAttribute('font-family', 'monospace');
        lbl.setAttribute('pointer-events', 'none');
        lbl.textContent = `C${key.octave}`;
        svg.appendChild(lbl);
      }
    }

    this._svg = svg;
    this.root.appendChild(svg);
  }

  _makeWhiteKey(key, x) {
    const rect = document.createElementNS(SVG_NS, 'rect');
    rect.setAttribute('x', x);
    rect.setAttribute('y', 0);
    rect.setAttribute('width',  WK_W - 1);
    rect.setAttribute('height', WK_H);
    rect.setAttribute('rx', 2);
    rect.setAttribute('fill',   COLORS.white);
    rect.setAttribute('stroke', COLORS.stroke);
    rect.setAttribute('stroke-width', '0.8');
    rect.dataset.keyNumber = key.keyNumber;
    this._attachKeyEvents(rect, key);
    return rect;
  }

  _makeBlackKey(key, x) {
    const rect = document.createElementNS(SVG_NS, 'rect');
    rect.setAttribute('x', x);
    rect.setAttribute('y', 0);
    rect.setAttribute('width',  BK_W);
    rect.setAttribute('height', BK_H);
    rect.setAttribute('rx', 2);
    rect.setAttribute('fill',   COLORS.black);
    rect.setAttribute('stroke', '#000');
    rect.setAttribute('stroke-width', '0.5');
    rect.dataset.keyNumber = key.keyNumber;
    this._attachKeyEvents(rect, key);
    return rect;
  }

  // ── Events ─────────────────────────────────────────────────────────────────

  _attachKeyEvents(el, key) {
    const down = (e) => {
      e.preventDefault();
      this._triggerOn(key);
    };
    const up = () => this._triggerOff(key);

    el.addEventListener('mousedown',  down);
    el.addEventListener('touchstart', down, { passive: false });
    el.addEventListener('mouseup',    up);
    el.addEventListener('mouseleave', up);
    el.addEventListener('touchend',   up);
  }

  _bindGlobalEvents() {
    document.addEventListener('mouseup', () => {
      for (const kn of [...this._activeKeys]) {
        const key = this.manifest[kn - 1];
        if (key) this._triggerOff(key);
      }
    });
  }

  _triggerOn(key) {
    this._activeKeys.add(key.keyNumber);
    synth.noteOn(key.keyNumber, key.frequencyHz);
    this._setKeyColor(key.keyNumber, 'active');

    this._svg.dispatchEvent(new CustomEvent('keypress', {
      bubbles: true,
      detail: { keyNumber: key.keyNumber, note: key.note, octave: key.octave, frequencyHz: key.frequencyHz }
    }));
  }

  _triggerOff(key) {
    this._activeKeys.delete(key.keyNumber);
    synth.noteOff(key.keyNumber);
    this._setKeyColor(key.keyNumber, this.diatonic.has(key.note) ? 'diatonic' : 'default');

    this._svg.dispatchEvent(new CustomEvent('keyrelease', {
      bubbles: true, detail: { keyNumber: key.keyNumber }
    }));
  }

  // ── Visual state ───────────────────────────────────────────────────────────

  _setKeyColor(keyNumber, state) {
    const key = this.manifest[keyNumber - 1];
    if (!key) return;
    const el  = this._keyEls.get(keyNumber);
    if (!el)  return;

    if (key.isWhite) {
      el.setAttribute('fill', {
        default:  COLORS.white,
        hover:    COLORS.whiteHover,
        active:   COLORS.whiteActive,
        diatonic: COLORS.whiteDiatonic
      }[state] ?? COLORS.white);
    } else {
      el.setAttribute('fill', {
        default:  COLORS.black,
        hover:    COLORS.blackHover,
        active:   COLORS.blackActive,
        diatonic: COLORS.blackDiatonic
      }[state] ?? COLORS.black);
    }
  }

  /** Called when circle selects a key — highlights the diatonic scale. */
  setDiatonicHighlight(noteSet) {
    this.diatonic = new Set(noteSet);
    for (const key of this.manifest) {
      if (!this._activeKeys.has(key.keyNumber)) {
        this._setKeyColor(key.keyNumber, this.diatonic.has(key.note) ? 'diatonic' : 'default');
      }
    }
  }

  clearHighlight() {
    this.diatonic = new Set();
    for (const key of this.manifest) {
      if (!this._activeKeys.has(key.keyNumber)) {
        this._setKeyColor(key.keyNumber, 'default');
      }
    }
  }

  /** Scroll the keyboard wrapper so the given octave is visible. */
  scrollToOctave(octave) {
    const targetKey = this.manifest.find(k => k.note === 'C' && k.octave === octave);
    if (!targetKey || !this._keyEls.has(targetKey.keyNumber)) return;
    const el = this._keyEls.get(targetKey.keyNumber);
    el.scrollIntoView?.({ behavior: 'smooth', block: 'nearest', inline: 'center' });
  }
}
