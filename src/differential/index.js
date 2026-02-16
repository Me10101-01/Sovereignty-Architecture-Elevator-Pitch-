// src/differential/index.js
// Sovereign Differential Engine - Main exports

export { SovereignDifferentialEngine, runDifferential } from './engine.js';
export { Hypothesis, HypothesisBoard } from './hypotheses.js';
export { 
  DifferentialAgent,
  StructuralAnalystAgent,
  PatternRecognitionAgent,
  SkepticAgent,
  SynthesizerAgent,
  ImplementationStrategistAgent,
  createDefaultAgentTeam 
} from './agents.js';
