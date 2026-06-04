/**
 * CircleVisualizer — SVG renderer for Circle of Fifths and Circle of Fourths.
 *
 * Renders two concentric rings inside a single <svg> element:
 *   Outer ring  → Circle of Fifths  (clockwise, step = 7 semitones)
 *   Inner ring  → Circle of Fourths (clockwise, step = 5 semitones)
 *
 * Clicking a segment highlights the diatonic scale on both the circle
 * and the keyboard, and dispatches a 'noteselect' CustomEvent on the SVG.
 */

import { CircleEngine } from '../core/CircleEngine.js';
import { ENHARMONIC_FLATS, RELATIVE_MINORS } from '../constants/notes.js';

const SVG_NS = 'http://www.w3.org/2000/svg';

// Visual constants
const CX     = 240;   // centre x
const CY     = 240;   // centre y
const R_OUT  = 200;   // outer ring outer radius
const R_MID  = 145;   // outer ring inner / inner ring outer radius
const R_IN   = 100;   // inner ring inner radius
const R_MINI = 60;    // innermost tonic label ring

// Colour palette
const COLORS = {
  bgOuter:      '#1a1a2e',
  bgInner:      '#16213e',
  segDefault:   '#0f3460',
  segFifths:    '#533483',
  segFourths:   '#1a6b8a',
  segSelected:  '#e94560',
  segDiatonic:  '#f5a623',
  textLight:    '#e0e0f0',
  textDim:      '#7a8aaa',
  strokeCircle: '#2a3a6e',
  rootBadge:    '#e94560'
};

function polarToCart(cx, cy, r, angleDeg) {
  const rad = (angleDeg - 90) * (Math.PI / 180);
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function describeArc(cx, cy, r1, r2, startDeg, endDeg) {
  const gap = 1.5;
  const s1  = startDeg + gap;
  const e1  = endDeg   - gap;
  const p1  = polarToCart(cx, cy, r2, s1);
  const p2  = polarToCart(cx, cy, r2, e1);
  const p3  = polarToCart(cx, cy, r1, e1);
  const p4  = polarToCart(cx, cy, r1, s1);
  return `M ${p1.x} ${p1.y} A ${r2} ${r2} 0 0 1 ${p2.x} ${p2.y}
          L ${p3.x} ${p3.y} A ${r1} ${r1} 0 0 0 ${p4.x} ${p4.y} Z`;
}

export class CircleVisualizer {
  /**
   * @param {string|HTMLElement} container  CSS selector or DOM element
   */
  constructor(container) {
    this.root = typeof container === 'string'
      ? document.querySelector(container)
      : container;

    this.fifthsData  = CircleEngine.getCircleData('fifths');
    this.fourthsData = CircleEngine.getCircleData('fourths');

    this.selectedNote   = null;
    this.diatonicNotes  = new Set();

    this._svg    = null;
    this._segs   = {};   // note → { outer, inner }
    this._render();
  }

  // ── Build SVG ──────────────────────────────────────────────────────────────

  _render() {
    const svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('viewBox', `0 0 ${CX * 2} ${CY * 2}`);
    svg.setAttribute('width',  '100%');
    svg.setAttribute('class',  'circle-visualizer');
    svg.style.maxWidth = '480px';

    // Background
    const bg = document.createElementNS(SVG_NS, 'circle');
    bg.setAttribute('cx', CX); bg.setAttribute('cy', CY);
    bg.setAttribute('r', R_OUT + 4);
    bg.setAttribute('fill', COLORS.bgOuter);
    svg.appendChild(bg);

    // Build outer segments (Circle of Fifths)
    this.fifthsData.forEach(d => {
      const g = this._buildSegment(d, R_MID, R_OUT, 'fifths');
      svg.appendChild(g);
    });

    // Build inner segments (Circle of Fourths)
    this.fourthsData.forEach(d => {
      const g = this._buildSegment(d, R_IN, R_MID, 'fourths');
      svg.appendChild(g);
    });

    // Centre hub
    const hub = document.createElementNS(SVG_NS, 'circle');
    hub.setAttribute('cx', CX); hub.setAttribute('cy', CY);
    hub.setAttribute('r', R_IN - 2);
    hub.setAttribute('fill', COLORS.bgInner);
    hub.setAttribute('stroke', COLORS.strokeCircle);
    hub.setAttribute('stroke-width', '1');
    svg.appendChild(hub);

    // Ring separator strokes
    for (const r of [R_MID, R_OUT]) {
      const ring = document.createElementNS(SVG_NS, 'circle');
      ring.setAttribute('cx', CX); ring.setAttribute('cy', CY);
      ring.setAttribute('r', r);
      ring.setAttribute('fill', 'none');
      ring.setAttribute('stroke', COLORS.strokeCircle);
      ring.setAttribute('stroke-width', '1.5');
      svg.appendChild(ring);
    }

    // Legend labels
    this._addLabel(svg, CX, CY - R_IN + 22, '4ths', 10, COLORS.textDim);
    this._addLabel(svg, CX, CY - R_MID + 18, '5ths', 10, COLORS.textDim);

    // Centre note display
    this._hubText = document.createElementNS(SVG_NS, 'text');
    this._hubText.setAttribute('x', CX); this._hubText.setAttribute('y', CY + 6);
    this._hubText.setAttribute('text-anchor', 'middle');
    this._hubText.setAttribute('font-size', '28');
    this._hubText.setAttribute('font-weight', 'bold');
    this._hubText.setAttribute('fill', COLORS.textLight);
    this._hubText.setAttribute('font-family', 'monospace');
    this._hubText.textContent = '';
    svg.appendChild(this._hubText);

    this._relText = document.createElementNS(SVG_NS, 'text');
    this._relText.setAttribute('x', CX); this._relText.setAttribute('y', CY + 26);
    this._relText.setAttribute('text-anchor', 'middle');
    this._relText.setAttribute('font-size', '13');
    this._relText.setAttribute('fill', COLORS.textDim);
    this._relText.setAttribute('font-family', 'sans-serif');
    this._relText.textContent = '';
    svg.appendChild(this._relText);

    this._svg = svg;
    this.root.appendChild(svg);
  }

  _buildSegment(data, rInner, rOuter, ring) {
    const startDeg = data.position * 30 - 90;
    const endDeg   = startDeg + 30;

    const g = document.createElementNS(SVG_NS, 'g');
    g.style.cursor = 'pointer';

    // Arc path
    const path = document.createElementNS(SVG_NS, 'path');
    path.setAttribute('d', describeArc(CX, CY, rInner, rOuter, startDeg, endDeg));
    path.setAttribute('fill', ring === 'fifths' ? COLORS.segFifths : COLORS.segFourths);
    path.setAttribute('stroke', COLORS.strokeCircle);
    path.setAttribute('stroke-width', '0.5');
    path.dataset.note = data.note;
    path.dataset.ring = ring;
    g.appendChild(path);

    // Note label
    const midAngle = startDeg + 15;
    const rLabel   = rInner + (rOuter - rInner) * 0.52;
    const lp       = polarToCart(CX, CY, rLabel, midAngle + 90);
    const label    = document.createElementNS(SVG_NS, 'text');
    label.setAttribute('x', lp.x); label.setAttribute('y', lp.y);
    label.setAttribute('text-anchor', 'middle');
    label.setAttribute('dominant-baseline', 'central');
    label.setAttribute('font-size', ring === 'fifths' ? '13' : '11');
    label.setAttribute('font-weight', 'bold');
    label.setAttribute('font-family', 'monospace');
    label.setAttribute('fill', COLORS.textLight);
    label.setAttribute('pointer-events', 'none');
    label.textContent = ENHARMONIC_FLATS[data.note]
      ? `${data.note}/${ENHARMONIC_FLATS[data.note]}`
      : data.note;
    if (ring === 'fifths') {
      // Relative minor below note name
      const rml = document.createElementNS(SVG_NS, 'tspan');
      rml.setAttribute('x', lp.x);
      rml.setAttribute('dy', '14');
      rml.setAttribute('font-size', '9');
      rml.setAttribute('fill', COLORS.textDim);
      rml.textContent = RELATIVE_MINORS[data.note] ?? '';
      label.appendChild(rml);
    }
    g.appendChild(label);

    // Click handler
    g.addEventListener('click', () => this._onSegmentClick(data.note));

    // Store reference for highlight updates
    if (!this._segs[data.note]) this._segs[data.note] = {};
    this._segs[data.note][ring] = path;

    return g;
  }

  _addLabel(svg, x, y, text, size, fill) {
    const el = document.createElementNS(SVG_NS, 'text');
    el.setAttribute('x', x); el.setAttribute('y', y);
    el.setAttribute('text-anchor', 'middle');
    el.setAttribute('font-size', size);
    el.setAttribute('fill', fill);
    el.setAttribute('font-family', 'sans-serif');
    el.textContent = text;
    svg.appendChild(el);
  }

  // ── Interaction ────────────────────────────────────────────────────────────

  _onSegmentClick(note) {
    if (this.selectedNote === note) {
      this.clearSelection();
    } else {
      this.selectNote(note);
    }
  }

  selectNote(note) {
    this.selectedNote = note;
    this.diatonicNotes = new Set(CircleEngine.getDiatonicScale(note));
    this._updateColors();
    this._hubText.textContent = note;
    this._relText.textContent = RELATIVE_MINORS[note] ? `rel: ${RELATIVE_MINORS[note]}` : '';

    this._svg.dispatchEvent(new CustomEvent('noteselect', {
      bubbles: true,
      detail: {
        note,
        diatonicScale: [...this.diatonicNotes],
        relativeMinor: RELATIVE_MINORS[note] ?? null
      }
    }));
  }

  clearSelection() {
    this.selectedNote  = null;
    this.diatonicNotes = new Set();
    this._hubText.textContent = '';
    this._relText.textContent = '';
    this._updateColors();
    this._svg.dispatchEvent(new CustomEvent('noteclear', { bubbles: true }));
  }

  _updateColors() {
    for (const [note, rings] of Object.entries(this._segs)) {
      const isSelected = note === this.selectedNote;
      const isDiatonic = this.diatonicNotes.has(note);

      for (const [ring, path] of Object.entries(rings)) {
        if (isSelected) {
          path.setAttribute('fill', COLORS.segSelected);
        } else if (isDiatonic && this.selectedNote) {
          path.setAttribute('fill', COLORS.segDiatonic);
        } else {
          path.setAttribute('fill', ring === 'fifths' ? COLORS.segFifths : COLORS.segFourths);
        }
      }
    }
  }

  /** Programmatically highlight a note (called from keyboard component). */
  highlightNote(note) { this.selectNote(note); }
}
