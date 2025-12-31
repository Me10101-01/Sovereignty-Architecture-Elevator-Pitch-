// FlameLang DSL - Compiles music UDAP to MIDI code
// Domain-Specific Language for quantum-addressed music

grammar FlameLang;

// UDAP Music Address Syntax
udap_music: 'skhaos://' domain '/' note '/' octave '/' piece_id properties?;

domain: 'audio' | 'frequency' | 'mood';
note: MIDI_NOTE;
octave: DIGIT;
piece_id: NUMBER;

properties: '?' property ('&' property)*;
property: KEY '=' VALUE;

// Frequency Mapping
freq_map: 'freq' ':' NUMBER 'Hz' '->' 'piece' ':' NUMBER;

// Entanglement Expression
entangle: 'entangle' '(' udap_music ',' udap_music ')' 'at' NUMBER 'Hz';

// Mood Band Assignment
mood_assign: 'mood' ':' MOOD_BAND 'for' udap_music;

// Whale Overlay
whale_overlay: 'whale' ':' WHALE_SPECIES 'overlay' udap_music;

// Terminals
MIDI_NOTE: 'C' | 'C#' | 'D' | 'D#' | 'E' | 'F' | 'F#' | 'G' | 'G#' | 'A' | 'A#' | 'B';
MOOD_BAND: 'delta' | 'theta' | 'alpha' | 'beta' | 'gamma';
WHALE_SPECIES: 'blue' | 'humpback' | 'fin' | 'bowhead' | 'gray';
NUMBER: DIGIT+;
DIGIT: [0-9];
KEY: [a-zA-Z_]+;
VALUE: [a-zA-Z0-9._-]+;

WS: [ \t\r\n]+ -> skip;

// Example FlameLang Programs:

// 1. Map Beethoven Sym5 to C note at 261Hz
// freq: 261Hz -> piece: 1
// mood: beta for skhaos://audio/C/4/1

// 2. Entangle classical with whale
// entangle(skhaos://audio/A/4/3, skhaos://frequency/20/Hz/whale) at 440Hz
// whale: blue overlay skhaos://audio/A/4/3

// 3. Recon probe with music frequency
// skhaos://recon/probe/1/wave?hz=261&piece_id=1&sim=wave

// Compilation Output: Rust code that executes UDAP operations
// compile("freq: 261Hz -> piece: 1") => 
//   UdapAddress::parse("skhaos://audio/261/C/1")
//   classical_pieces::get_piece_by_id(1)
