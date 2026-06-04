/**
 * audio-theory-app — entry point
 * Wires together CircleVisualizer, Keyboard88, and SynthEngine.
 */

import { CircleEngine }      from './core/CircleEngine.js';
import { FrequencyGenerator } from './core/FrequencyGenerator.js';
import { CircleVisualizer }  from './components/CircleVisualizer.js';
import { Keyboard88 }        from './components/Keyboard88.js';
import { synth }             from './utils/audioContext.js';

// ── Console-mode dataset (also usable as a Node.js data layer) ──────────────

export function buildDataset() {
  const fifths  = CircleEngine.getCircleOfFifths();
  const fourths = CircleEngine.getCircleOfFourths();
  const keys    = FrequencyGenerator.generate88KeyManifest();
  return {
    circleOfFifths:  fifths,
    circleOfFourths: fourths,
    pianoKeys:       keys,
    anchors: {
      key1:  keys[0],   // A0  @ 27.5 Hz
      key40: keys[39],  // C4  @ 261.626 Hz  (Middle C)
      key49: keys[48],  // A4  @ 440 Hz      (standard pitch)
      key88: keys[87],  // C8  @ 4186.009 Hz
    }
  };
}

// ── Browser UI bootstrap ────────────────────────────────────────────────────

function initUI() {
  const circleContainer   = document.getElementById('circle-container');
  const keyboardContainer = document.getElementById('keyboard-container');
  const waveSelect        = document.getElementById('wave-type');
  const volumeSlider      = document.getElementById('master-volume');
  const attackSlider      = document.getElementById('adsr-attack');
  const releaseSlider     = document.getElementById('adsr-release');
  const statusBar         = document.getElementById('status-bar');
  const infoNote          = document.getElementById('info-note');
  const infoFreq          = document.getElementById('info-freq');
  const infoMidi          = document.getElementById('info-midi');
  const allOffBtn         = document.getElementById('all-notes-off');

  if (!circleContainer || !keyboardContainer) return;  // not in browser

  const circle   = new CircleVisualizer(circleContainer);
  const keyboard = new Keyboard88(keyboardContainer);

  // ── Circle → Keyboard highlight ───────────────────────────────────────────
  circleContainer.addEventListener('noteselect', (e) => {
    keyboard.setDiatonicHighlight(e.detail.diatonicScale);
    const rel = e.detail.relativeMinor ? ` · rel: ${e.detail.relativeMinor}` : '';
    statusBar.textContent = `Key of ${e.detail.note} major${rel}`;
  });

  circleContainer.addEventListener('noteclear', () => {
    keyboard.clearHighlight();
    statusBar.textContent = 'Click a circle segment to select a key';
  });

  // ── Keyboard → Info display ───────────────────────────────────────────────
  keyboardContainer.addEventListener('keypress', (e) => {
    const { note, octave, frequencyHz, keyNumber } = e.detail;
    infoNote.textContent  = `${note}${octave}`;
    infoFreq.textContent  = `${frequencyHz} Hz`;
    infoMidi.textContent  = `MIDI ${keyNumber + 20}`;
    circle.highlightNote(note);
  });

  // ── Controls ──────────────────────────────────────────────────────────────
  waveSelect?.addEventListener('change', (e) => synth.setWaveType(e.target.value));

  volumeSlider?.addEventListener('input', (e) => {
    synth.setMasterVolume(parseFloat(e.target.value));
  });

  attackSlider?.addEventListener('input', (e) => {
    synth.setADSR({ attack: parseFloat(e.target.value) });
  });

  releaseSlider?.addEventListener('input', (e) => {
    synth.setADSR({ release: parseFloat(e.target.value) });
  });

  allOffBtn?.addEventListener('click', () => {
    synth.allNotesOff();
    keyboard.clearHighlight();
  });

  // ── Keyboard shortcut: octave 4 mappings ─────────────────────────────────
  const keyMap = {
    'a': { note: 'C', octave: 4 }, 'w': { note: 'C#', octave: 4 },
    's': { note: 'D', octave: 4 }, 'e': { note: 'D#', octave: 4 },
    'd': { note: 'E', octave: 4 }, 'f': { note: 'F', octave: 4 },
    't': { note: 'F#', octave: 4 }, 'g': { note: 'G', octave: 4 },
    'y': { note: 'G#', octave: 4 }, 'h': { note: 'A', octave: 4 },
    'u': { note: 'A#', octave: 4 }, 'j': { note: 'B', octave: 4 },
    'k': { note: 'C', octave: 5 },
  };

  const held = new Set();
  document.addEventListener('keydown', (e) => {
    if (e.repeat || held.has(e.key)) return;
    const mapping = keyMap[e.key.toLowerCase()];
    if (!mapping) return;
    held.add(e.key);
    const key = FrequencyGenerator.getKey(mapping.note, mapping.octave);
    if (key) synth.noteOn(key.keyNumber, key.frequencyHz);
  });

  document.addEventListener('keyup', (e) => {
    held.delete(e.key);
    const mapping = keyMap[e.key.toLowerCase()];
    if (!mapping) return;
    const key = FrequencyGenerator.getKey(mapping.note, mapping.octave);
    if (key) synth.noteOff(key.keyNumber);
  });
}

// ── Run ──────────────────────────────────────────────────────────────────────

if (typeof window !== 'undefined') {
  // Browser context
  document.addEventListener('DOMContentLoaded', initUI);
} else {
  // Node.js context — print dataset
  const data = buildDataset();
  console.log('Circle of 5ths:',  data.circleOfFifths.join(' → '));
  console.log('Circle of 4ths:',  data.circleOfFourths.join(' → '));
  console.log('Key  1 (A0):',     data.anchors.key1);
  console.log('Key 40 (C4):',     data.anchors.key40);
  console.log('Key 49 (A4):',     data.anchors.key49);
  console.log('Key 88 (C8):',     data.anchors.key88);
}
