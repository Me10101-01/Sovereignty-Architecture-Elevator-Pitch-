// src/differential/agents.js
// Multi-agent thought refinement system for the Sovereign Differential Engine
// Inspired by House M.D.-style differential diagnosis methodology

import { v4 as uuid } from 'uuid';

/**
 * Base class for differential agents
 * Each agent represents a different perspective or domain of analysis
 */
export class DifferentialAgent {
  constructor({ name, role, domain, personality = 'analytical' }) {
    this.id = uuid();
    this.name = name;
    this.role = role;
    this.domain = domain;
    this.personality = personality;
    this.active = true;
  }

  /**
   * Generate hypotheses from raw thought
   * @param {string} rawThought - The externalized thought to analyze
   * @param {object} context - Additional context for analysis
   * @returns {Array} Generated hypotheses
   */
  async generateHypotheses(rawThought, context = {}) {
    // Base implementation - to be extended by specialized agents
    return [{
      content: `[${this.name}] Analysis of: ${rawThought.substring(0, 100)}...`,
      source: this.name,
      confidence: 0.5,
      domain: this.domain
    }];
  }

  /**
   * Challenge existing hypotheses from this agent's perspective
   * @param {Array} hypotheses - Current hypotheses to challenge
   * @param {string} rawThought - Original thought for reference
   * @returns {Array} Challenges to hypotheses
   */
  async challengeHypotheses(hypotheses, rawThought) {
    const challenges = [];
    for (const hypothesis of hypotheses) {
      if (hypothesis.source !== this.name) {
        challenges.push({
          hypothesis_id: hypothesis.id,
          challenger: this.name,
          type: 'perspective',
          content: `From ${this.domain} perspective: ${this.generateChallenge(hypothesis)}`,
          severity: 'moderate'
        });
      }
    }
    return challenges;
  }

  /**
   * Generate a challenge for a specific hypothesis
   */
  generateChallenge(hypothesis) {
    return `Consider alternative interpretation in ${this.domain} domain`;
  }

  /**
   * Refine hypotheses based on challenges and new data
   * @param {object} hypothesis - Hypothesis to refine
   * @param {Array} challenges - Challenges to address
   * @returns {object} Refined hypothesis content
   */
  async refineHypothesis(hypothesis, challenges) {
    const relevantChallenges = challenges.filter(c => 
      c.hypothesis_id === hypothesis.id || !c.hypothesis_id
    );
    
    return {
      refined_content: hypothesis.content,
      addressed_challenges: relevantChallenges.map(c => c.id),
      refinement_notes: `Refined by ${this.name} addressing ${relevantChallenges.length} challenges`
    };
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      role: this.role,
      domain: this.domain,
      personality: this.personality,
      active: this.active
    };
  }
}

/**
 * Structural Analyst Agent
 * Focuses on system design, patterns, and architecture
 */
export class StructuralAnalystAgent extends DifferentialAgent {
  constructor() {
    super({
      name: 'Structural Analyst',
      role: 'architect',
      domain: 'system_design',
      personality: 'systematic'
    });
  }

  async generateHypotheses(rawThought, context = {}) {
    const patterns = this.identifyPatterns(rawThought);
    return patterns.map((pattern, idx) => ({
      content: `Structural pattern identified: ${pattern.name} - ${pattern.description}`,
      source: this.name,
      confidence: 0.6 + (idx * 0.05),
      domain: this.domain,
      metadata: { pattern }
    }));
  }

  identifyPatterns(text) {
    const patterns = [];
    const keywords = {
      'recursive': { name: 'Recursive Pattern', description: 'Self-referential or looping structure' },
      'multi-agent': { name: 'Multi-Agent System', description: 'Distributed intelligence or collaboration' },
      'swarm': { name: 'Swarm Intelligence', description: 'Emergent behavior from collective agents' },
      'differential': { name: 'Differential Analysis', description: 'Comparative hypothesis evaluation' },
      'iteration': { name: 'Iterative Refinement', description: 'Progressive improvement through cycles' },
      'loop': { name: 'Feedback Loop', description: 'Circular information flow for refinement' },
      'architecture': { name: 'Architectural Pattern', description: 'Structural design blueprint' },
      'engine': { name: 'Processing Engine', description: 'Core computational mechanism' }
    };

    const lowerText = text.toLowerCase();
    for (const [keyword, pattern] of Object.entries(keywords)) {
      if (lowerText.includes(keyword)) {
        patterns.push(pattern);
      }
    }

    if (patterns.length === 0) {
      patterns.push({ name: 'Unstructured Thought', description: 'Raw conceptual input requiring structuring' });
    }

    return patterns;
  }

  generateChallenge(hypothesis) {
    return `What is the structural coherence? Does this pattern scale?`;
  }
}

/**
 * Pattern Recognition Agent
 * Identifies recurring themes, metaphors, and conceptual connections
 */
export class PatternRecognitionAgent extends DifferentialAgent {
  constructor() {
    super({
      name: 'Pattern Recognizer',
      role: 'analyst',
      domain: 'pattern_recognition',
      personality: 'intuitive'
    });
  }

  async generateHypotheses(rawThought, context = {}) {
    const themes = this.extractThemes(rawThought);
    const connections = this.findConnections(themes);
    
    const hypotheses = [];
    
    // Theme hypotheses
    for (const theme of themes) {
      hypotheses.push({
        content: `Theme identified: "${theme}" suggests underlying conceptual framework`,
        source: this.name,
        confidence: 0.55,
        domain: this.domain,
        metadata: { theme }
      });
    }
    
    // Connection hypotheses
    for (const connection of connections) {
      hypotheses.push({
        content: `Connection: "${connection.from}" relates to "${connection.to}" via ${connection.type}`,
        source: this.name,
        confidence: 0.65,
        domain: this.domain,
        metadata: { connection }
      });
    }

    return hypotheses;
  }

  extractThemes(text) {
    const themeKeywords = [
      'cognition', 'thinking', 'reasoning', 'evolution', 'refinement',
      'mirror', 'reflection', 'externalization', 'iteration',
      'hypothesis', 'diagnosis', 'analysis', 'synthesis'
    ];
    
    const lowerText = text.toLowerCase();
    return themeKeywords.filter(theme => lowerText.includes(theme));
  }

  findConnections(themes) {
    const connections = [];
    const relationshipMap = {
      'cognition-thinking': { type: 'synonym', strength: 0.9 },
      'cognition-reasoning': { type: 'component', strength: 0.8 },
      'evolution-refinement': { type: 'process', strength: 0.85 },
      'mirror-reflection': { type: 'metaphor', strength: 0.95 },
      'externalization-mirror': { type: 'mechanism', strength: 0.7 },
      'hypothesis-diagnosis': { type: 'method', strength: 0.8 },
      'analysis-synthesis': { type: 'complement', strength: 0.9 }
    };

    for (let i = 0; i < themes.length; i++) {
      for (let j = i + 1; j < themes.length; j++) {
        const key1 = `${themes[i]}-${themes[j]}`;
        const key2 = `${themes[j]}-${themes[i]}`;
        
        if (relationshipMap[key1]) {
          connections.push({
            from: themes[i],
            to: themes[j],
            ...relationshipMap[key1]
          });
        } else if (relationshipMap[key2]) {
          connections.push({
            from: themes[j],
            to: themes[i],
            ...relationshipMap[key2]
          });
        }
      }
    }

    return connections;
  }

  generateChallenge(hypothesis) {
    return `Is this pattern consistent across contexts? What counter-patterns exist?`;
  }
}

/**
 * Skeptic Agent
 * Challenges assumptions and identifies potential flaws
 */
export class SkepticAgent extends DifferentialAgent {
  constructor() {
    super({
      name: 'Skeptic',
      role: 'critic',
      domain: 'critical_analysis',
      personality: 'contrarian'
    });
  }

  async generateHypotheses(rawThought, context = {}) {
    const assumptions = this.identifyAssumptions(rawThought);
    
    return assumptions.map(assumption => ({
      content: `Assumption identified: "${assumption.content}" - requires validation`,
      source: this.name,
      confidence: 0.4, // Lower confidence as skeptic
      domain: this.domain,
      metadata: { assumption, requires_evidence: true }
    }));
  }

  identifyAssumptions(text) {
    const assumptions = [];
    
    // Look for definitive language that might hide assumptions
    const definitivePatterns = [
      { pattern: /always|never|must|certainly|obviously/gi, type: 'absolute' },
      { pattern: /best|optimal|perfect|ideal/gi, type: 'superlative' },
      { pattern: /because|therefore|thus|hence/gi, type: 'causal' }
    ];

    for (const { pattern, type } of definitivePatterns) {
      const matches = text.match(pattern);
      if (matches) {
        for (const match of matches) {
          assumptions.push({
            content: `Uses "${match}" - may hide unchallenged assumption`,
            type,
            severity: 'moderate'
          });
        }
      }
    }

    if (assumptions.length === 0) {
      assumptions.push({
        content: 'No obvious assumptions detected, but implicit assumptions may exist',
        type: 'implicit',
        severity: 'low'
      });
    }

    return assumptions;
  }

  async challengeHypotheses(hypotheses, rawThought) {
    const challenges = [];
    
    for (const hypothesis of hypotheses) {
      // Skeptic challenges everything with high confidence
      if (hypothesis.confidence > 0.7) {
        challenges.push({
          hypothesis_id: hypothesis.id,
          challenger: this.name,
          type: 'confidence_check',
          content: `High confidence (${hypothesis.confidence}) may indicate overconfidence. What evidence supports this?`,
          severity: 'high'
        });
      }
      
      // Challenge any hypothesis not from self
      if (hypothesis.source !== this.name) {
        challenges.push({
          hypothesis_id: hypothesis.id,
          challenger: this.name,
          type: 'alternative',
          content: `What if the opposite is true? Consider inverting: ${hypothesis.content.substring(0, 50)}...`,
          severity: 'moderate'
        });
      }
    }
    
    return challenges;
  }

  generateChallenge(hypothesis) {
    return `What evidence contradicts this? What are we missing?`;
  }
}

/**
 * Synthesizer Agent
 * Combines insights from other agents into coherent conclusions
 */
export class SynthesizerAgent extends DifferentialAgent {
  constructor() {
    super({
      name: 'Synthesizer',
      role: 'integrator',
      domain: 'synthesis',
      personality: 'holistic'
    });
  }

  async generateHypotheses(rawThought, context = {}) {
    // Synthesizer works best with existing hypotheses
    if (!context.existingHypotheses || context.existingHypotheses.length === 0) {
      return [{
        content: 'Awaiting hypotheses from other agents for synthesis',
        source: this.name,
        confidence: 0.3,
        domain: this.domain,
        metadata: { awaiting_input: true }
      }];
    }

    const synthesis = this.synthesize(context.existingHypotheses);
    return [synthesis];
  }

  synthesize(hypotheses) {
    const byDomain = {};
    for (const h of hypotheses) {
      const domain = h.domain || 'general';
      if (!byDomain[domain]) {
        byDomain[domain] = [];
      }
      byDomain[domain].push(h);
    }

    const domains = Object.keys(byDomain);
    const avgConfidence = hypotheses.reduce((sum, h) => sum + h.confidence, 0) / hypotheses.length;

    return {
      content: `Synthesis across ${domains.length} domains (${domains.join(', ')}): ${hypotheses.length} hypotheses analyzed. Key insight: converging patterns suggest coherent conceptual framework.`,
      source: this.name,
      confidence: Math.min(avgConfidence + 0.1, 0.95), // Slightly higher than average
      domain: this.domain,
      metadata: {
        domains_analyzed: domains,
        hypothesis_count: hypotheses.length,
        synthesis_type: 'cross_domain'
      }
    };
  }

  async refineHypothesis(hypothesis, challenges) {
    const synthesisNotes = [];
    const addressedChallenges = [];

    for (const challenge of challenges) {
      if (challenge.type === 'perspective') {
        synthesisNotes.push(`Integrated ${challenge.challenger}'s perspective`);
        addressedChallenges.push(challenge.id);
      } else if (challenge.type === 'alternative') {
        synthesisNotes.push(`Considered alternative from ${challenge.challenger}`);
        addressedChallenges.push(challenge.id);
      }
    }

    return {
      refined_content: `${hypothesis.content} [Synthesized with ${addressedChallenges.length} perspectives]`,
      addressed_challenges: addressedChallenges,
      refinement_notes: synthesisNotes.join('; ')
    };
  }

  generateChallenge(hypothesis) {
    return `How does this integrate with other perspectives? What's the unified view?`;
  }
}

/**
 * Implementation Strategist Agent
 * Focuses on actionable implementation paths
 */
export class ImplementationStrategistAgent extends DifferentialAgent {
  constructor() {
    super({
      name: 'Implementation Strategist',
      role: 'planner',
      domain: 'implementation',
      personality: 'pragmatic'
    });
  }

  async generateHypotheses(rawThought, context = {}) {
    const strategies = this.identifyStrategies(rawThought);
    
    return strategies.map((strategy, idx) => ({
      content: `Implementation strategy: ${strategy.name} - ${strategy.description}`,
      source: this.name,
      confidence: 0.6,
      domain: this.domain,
      metadata: { 
        strategy,
        priority: idx + 1,
        estimated_complexity: strategy.complexity
      }
    }));
  }

  identifyStrategies(text) {
    const strategies = [];
    const lowerText = text.toLowerCase();

    if (lowerText.includes('multi-agent') || lowerText.includes('swarm')) {
      strategies.push({
        name: 'Agent Orchestration',
        description: 'Build a multi-agent coordination system',
        complexity: 'high',
        components: ['agent framework', 'message bus', 'state management']
      });
    }

    if (lowerText.includes('hypothesis') || lowerText.includes('differential')) {
      strategies.push({
        name: 'Hypothesis Pipeline',
        description: 'Create a structured hypothesis generation and evaluation system',
        complexity: 'medium',
        components: ['hypothesis generator', 'evaluation engine', 'confidence scoring']
      });
    }

    if (lowerText.includes('refine') || lowerText.includes('iterate')) {
      strategies.push({
        name: 'Iterative Refinement Loop',
        description: 'Implement feedback loops for progressive improvement',
        complexity: 'medium',
        components: ['feedback collector', 'refinement engine', 'convergence detector']
      });
    }

    if (strategies.length === 0) {
      strategies.push({
        name: 'Exploratory Implementation',
        description: 'Start with prototype to discover requirements',
        complexity: 'low',
        components: ['prototype', 'feedback mechanism']
      });
    }

    return strategies;
  }

  generateChallenge(hypothesis) {
    return `Is this implementable? What are the concrete first steps?`;
  }
}

/**
 * Creates the default team of differential agents
 */
export function createDefaultAgentTeam() {
  return [
    new StructuralAnalystAgent(),
    new PatternRecognitionAgent(),
    new SkepticAgent(),
    new SynthesizerAgent(),
    new ImplementationStrategistAgent()
  ];
}

export default {
  DifferentialAgent,
  StructuralAnalystAgent,
  PatternRecognitionAgent,
  SkepticAgent,
  SynthesizerAgent,
  ImplementationStrategistAgent,
  createDefaultAgentTeam
};
