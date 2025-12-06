// src/differential/engine.js
// Core Sovereign Differential Engine
// A multi-agent, House M.D.-style thought refinement system

import { v4 as uuid } from 'uuid';
import { Hypothesis, HypothesisBoard } from './hypotheses.js';
import { createDefaultAgentTeam } from './agents.js';

/**
 * The Sovereign Differential Engine
 * 
 * Implements the "Iterative Cognitive Externalization + Multi-Agent Differential Refinement"
 * methodology for thought refinement and conceptual architecture evolution.
 * 
 * The engine operates in phases similar to House M.D.'s diagnostic differential:
 * 1. Externalization: Raw thought is captured
 * 2. Mirroring: Agents generate structured hypotheses
 * 3. Challenge: Hypotheses are challenged from multiple perspectives
 * 4. Evolution: Hypotheses are refined and evolved
 * 5. Convergence: Final refined conceptual architecture emerges
 */
export class SovereignDifferentialEngine {
  constructor(config = {}) {
    this.id = uuid();
    this.config = {
      maxRounds: config.maxRounds || 3,
      convergenceThreshold: config.convergenceThreshold || 0.8,
      minConfidence: config.minConfidence || 0.5,
      ...config
    };
    
    this.agents = config.agents || createDefaultAgentTeam();
    this.sessions = new Map();
    this.eventLog = [];
  }

  /**
   * Create a new differential session
   * @param {string} rawThought - The externalized thought to process
   * @param {object} context - Additional context
   * @returns {string} Session ID
   */
  async createSession(rawThought, context = {}) {
    const sessionId = uuid();
    
    const session = {
      id: sessionId,
      rawThought,
      context,
      hypothesisBoard: new HypothesisBoard(),
      phases: [],
      currentPhase: 'initialized',
      currentRound: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      status: 'active'
    };

    this.sessions.set(sessionId, session);
    this.log('session_created', { sessionId, thoughtPreview: rawThought.substring(0, 100) });

    return sessionId;
  }

  /**
   * Run the complete differential process
   * @param {string} sessionId - Session to process
   * @returns {object} Final refined output
   */
  async runDifferential(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    try {
      // Phase 1: Externalization & Mirroring
      await this.phaseExternalize(session);
      
      // Phase 2-N: Iterative Challenge & Refinement Rounds
      for (let round = 1; round <= this.config.maxRounds; round++) {
        session.currentRound = round;
        
        await this.phaseChallenge(session);
        await this.phaseRefinement(session);
        
        // Check for convergence
        if (this.checkConvergence(session)) {
          this.log('convergence_reached', { sessionId, round });
          break;
        }
      }
      
      // Final Phase: Synthesis & Architecture Output
      const result = await this.phaseSynthesize(session);
      
      session.status = 'completed';
      session.result = result;
      session.updated_at = new Date().toISOString();
      
      return result;

    } catch (error) {
      session.status = 'failed';
      session.error = error.message;
      this.log('session_failed', { sessionId, error: error.message });
      throw error;
    }
  }

  /**
   * Phase 1: Externalization & Mirroring
   * Agents generate initial hypotheses from the raw thought
   */
  async phaseExternalize(session) {
    session.currentPhase = 'externalization';
    const phaseStart = Date.now();
    
    this.log('phase_start', { 
      sessionId: session.id, 
      phase: 'externalization',
      agentCount: this.agents.length 
    });

    // Each agent generates hypotheses in parallel
    const hypothesisPromises = this.agents.map(async agent => {
      const hypotheses = await agent.generateHypotheses(session.rawThought, session.context);
      return { agent: agent.name, hypotheses };
    });

    const results = await Promise.all(hypothesisPromises);

    // Add all hypotheses to the board
    for (const { agent, hypotheses } of results) {
      for (const h of hypotheses) {
        const hypothesis = new Hypothesis(h);
        session.hypothesisBoard.add(hypothesis);
      }
    }

    const phaseResult = {
      phase: 'externalization',
      duration: Date.now() - phaseStart,
      hypothesesGenerated: session.hypothesisBoard.getAll().length,
      timestamp: new Date().toISOString()
    };

    session.phases.push(phaseResult);
    this.log('phase_complete', { sessionId: session.id, ...phaseResult });

    return phaseResult;
  }

  /**
   * Phase 2: Challenge
   * Agents challenge each other's hypotheses
   */
  async phaseChallenge(session) {
    session.currentPhase = 'challenge';
    const phaseStart = Date.now();
    
    this.log('phase_start', { 
      sessionId: session.id, 
      phase: 'challenge',
      round: session.currentRound 
    });

    const activeHypotheses = session.hypothesisBoard.getActive();
    const allChallenges = [];

    // Each agent challenges the hypotheses
    const challengePromises = this.agents.map(async agent => {
      const challenges = await agent.challengeHypotheses(activeHypotheses, session.rawThought);
      return { agent: agent.name, challenges };
    });

    const results = await Promise.all(challengePromises);

    // Apply challenges to hypotheses
    for (const { agent, challenges } of results) {
      for (const challenge of challenges) {
        if (challenge.hypothesis_id) {
          session.hypothesisBoard.challenge(challenge.hypothesis_id, challenge);
        }
        allChallenges.push(challenge);
      }
    }

    // Adjust confidence based on challenges
    for (const hypothesis of activeHypotheses) {
      const challengeCount = hypothesis.challenges.length;
      if (challengeCount > 0) {
        // Reduce confidence based on challenges, but not too much
        const confidenceDelta = -0.05 * Math.min(challengeCount, 3);
        hypothesis.updateConfidence(confidenceDelta);
      }
    }

    const phaseResult = {
      phase: 'challenge',
      round: session.currentRound,
      duration: Date.now() - phaseStart,
      challengesIssued: allChallenges.length,
      hypothesesChallenged: activeHypotheses.filter(h => h.status === 'challenged').length,
      timestamp: new Date().toISOString()
    };

    session.phases.push(phaseResult);
    this.log('phase_complete', { sessionId: session.id, ...phaseResult });

    return phaseResult;
  }

  /**
   * Phase 3: Refinement
   * Agents refine hypotheses based on challenges
   */
  async phaseRefinement(session) {
    session.currentPhase = 'refinement';
    const phaseStart = Date.now();
    
    this.log('phase_start', { 
      sessionId: session.id, 
      phase: 'refinement',
      round: session.currentRound 
    });

    const challengedHypotheses = session.hypothesisBoard.getByStatus('challenged');
    const refinements = [];

    for (const hypothesis of challengedHypotheses) {
      // Find the best agent to refine this hypothesis
      const refiningAgent = this.agents.find(a => a.name === hypothesis.source) || 
                           this.agents.find(a => a.role === 'integrator') ||
                           this.agents[0];

      const refinement = await refiningAgent.refineHypothesis(hypothesis, hypothesis.challenges);
      
      // Evolve the hypothesis if significant refinement occurred
      if (refinement.refined_content !== hypothesis.content) {
        const evolved = session.hypothesisBoard.evolve(
          hypothesis.id,
          refinement.refined_content,
          refinement.refinement_notes
        );
        refinements.push({ original: hypothesis.id, evolved: evolved?.id });
      } else {
        // Just refine in place
        session.hypothesisBoard.refine(hypothesis.id, refinement);
        refinements.push({ original: hypothesis.id, refined: true });
      }
    }

    // Boost confidence of refined/evolved hypotheses
    for (const h of session.hypothesisBoard.getByStatus('refined')) {
      h.updateConfidence(0.1);
    }

    const phaseResult = {
      phase: 'refinement',
      round: session.currentRound,
      duration: Date.now() - phaseStart,
      refinementsApplied: refinements.length,
      evolutionsCreated: refinements.filter(r => r.evolved).length,
      timestamp: new Date().toISOString()
    };

    session.phases.push(phaseResult);
    this.log('phase_complete', { sessionId: session.id, ...phaseResult });

    return phaseResult;
  }

  /**
   * Final Phase: Synthesis
   * Generate the refined conceptual architecture
   */
  async phaseSynthesize(session) {
    session.currentPhase = 'synthesis';
    const phaseStart = Date.now();
    
    this.log('phase_start', { sessionId: session.id, phase: 'synthesis' });

    const topHypotheses = session.hypothesisBoard.getTopHypotheses(5);
    const evolutionGraph = session.hypothesisBoard.getEvolutionGraph();

    // Generate final synthesis
    const synthesis = {
      id: uuid(),
      session_id: session.id,
      original_thought: session.rawThought,
      
      // Core output
      refined_architecture: this.generateArchitectureOutput(topHypotheses),
      
      // Hypothesis summary
      hypotheses: {
        total_generated: session.hypothesisBoard.getAll().length,
        accepted: session.hypothesisBoard.getByStatus('accepted').length,
        rejected: session.hypothesisBoard.getByStatus('rejected').length,
        top_hypotheses: topHypotheses.map(h => ({
          content: h.content,
          confidence: h.confidence,
          source: h.source
        }))
      },
      
      // Process metadata
      process: {
        rounds_completed: session.currentRound,
        phases: session.phases.map(p => ({
          phase: p.phase,
          round: p.round,
          duration_ms: p.duration
        })),
        total_duration_ms: session.phases.reduce((sum, p) => sum + p.duration, 0),
        agents_participated: this.agents.map(a => a.name)
      },
      
      // Evolution graph for visualization
      evolution_graph: evolutionGraph,
      
      // Insights and recommendations
      insights: this.generateInsights(topHypotheses, session),
      next_steps: this.generateNextSteps(topHypotheses),
      
      timestamp: new Date().toISOString()
    };

    // Accept top hypotheses
    for (const h of topHypotheses) {
      session.hypothesisBoard.get(h.id)?.accept('Converged as top hypothesis');
    }

    const phaseResult = {
      phase: 'synthesis',
      duration: Date.now() - phaseStart,
      synthesisGenerated: true,
      timestamp: new Date().toISOString()
    };

    session.phases.push(phaseResult);
    this.log('phase_complete', { sessionId: session.id, ...phaseResult });

    return synthesis;
  }

  /**
   * Check if the differential process has converged
   */
  checkConvergence(session) {
    const activeHypotheses = session.hypothesisBoard.getActive();
    
    if (activeHypotheses.length === 0) return true;
    
    // Check if top hypotheses have high confidence
    const topHypotheses = session.hypothesisBoard.getTopHypotheses(3);
    const avgConfidence = topHypotheses.reduce((sum, h) => sum + h.confidence, 0) / topHypotheses.length;
    
    // Check if hypotheses are stabilizing (few new challenges in last round)
    const lastPhase = session.phases[session.phases.length - 1];
    const stabilizing = lastPhase?.challengesIssued < 3;
    
    return avgConfidence >= this.config.convergenceThreshold || stabilizing;
  }

  /**
   * Generate the refined architecture output
   */
  generateArchitectureOutput(topHypotheses) {
    const domains = new Set(topHypotheses.map(h => h.domain));
    
    return {
      name: 'Refined Conceptual Architecture',
      domains: Array.from(domains),
      core_concepts: topHypotheses.map(h => ({
        concept: h.content,
        confidence: h.confidence,
        domain: h.domain
      })),
      structure: {
        type: 'multi-domain synthesis',
        coherence_score: topHypotheses.reduce((sum, h) => sum + h.confidence, 0) / topHypotheses.length
      }
    };
  }

  /**
   * Generate insights from the differential process
   */
  generateInsights(topHypotheses, session) {
    const insights = [];
    
    // Pattern insight
    const domains = topHypotheses.map(h => h.domain);
    const uniqueDomains = [...new Set(domains)];
    insights.push({
      type: 'pattern',
      content: `Your thinking spans ${uniqueDomains.length} domain(s): ${uniqueDomains.join(', ')}`
    });
    
    // Evolution insight
    const evolutionGraph = session.hypothesisBoard.getEvolutionGraph();
    if (evolutionGraph.edges.length > 0) {
      insights.push({
        type: 'evolution',
        content: `${evolutionGraph.edges.length} hypothesis evolution(s) occurred, showing iterative refinement of ideas`
      });
    }
    
    // Confidence insight
    const avgConfidence = topHypotheses.reduce((sum, h) => sum + h.confidence, 0) / topHypotheses.length;
    insights.push({
      type: 'confidence',
      content: avgConfidence > 0.7 
        ? 'High confidence in refined hypotheses suggests strong conceptual coherence'
        : 'Moderate confidence suggests room for further exploration'
    });

    return insights;
  }

  /**
   * Generate next steps recommendations
   */
  generateNextSteps(topHypotheses) {
    const steps = [];
    
    for (const h of topHypotheses.slice(0, 3)) {
      if (h.metadata?.strategy) {
        steps.push({
          action: `Implement: ${h.metadata.strategy.name}`,
          complexity: h.metadata.strategy.complexity,
          components: h.metadata.strategy.components
        });
      } else if (h.metadata?.pattern) {
        steps.push({
          action: `Apply pattern: ${h.metadata.pattern.name}`,
          description: h.metadata.pattern.description
        });
      } else {
        steps.push({
          action: `Explore further: ${h.content.substring(0, 50)}...`,
          confidence: h.confidence
        });
      }
    }

    return steps;
  }

  /**
   * Get session status
   */
  getSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) return null;

    return {
      id: session.id,
      status: session.status,
      currentPhase: session.currentPhase,
      currentRound: session.currentRound,
      hypothesesCount: session.hypothesisBoard.getAll().length,
      phases: session.phases,
      result: session.result,
      created_at: session.created_at,
      updated_at: session.updated_at
    };
  }

  /**
   * List all sessions
   */
  listSessions(filter = {}) {
    const sessions = Array.from(this.sessions.values());
    
    if (filter.status) {
      return sessions.filter(s => s.status === filter.status);
    }
    
    return sessions.map(s => ({
      id: s.id,
      status: s.status,
      currentPhase: s.currentPhase,
      hypothesesCount: s.hypothesisBoard.getAll().length,
      created_at: s.created_at
    }));
  }

  /**
   * Log events for observability
   */
  log(event, data) {
    const entry = {
      timestamp: new Date().toISOString(),
      event,
      engine_id: this.id,
      ...data
    };
    this.eventLog.push(entry);
    console.log(`🧠 [DifferentialEngine] ${event}:`, JSON.stringify(data));
  }

  /**
   * Get event log
   */
  getEventLog(filter = {}) {
    if (filter.sessionId) {
      return this.eventLog.filter(e => e.sessionId === filter.sessionId);
    }
    return this.eventLog;
  }
}

/**
 * Quick helper to run a single differential analysis
 */
export async function runDifferential(rawThought, config = {}) {
  const engine = new SovereignDifferentialEngine(config);
  const sessionId = await engine.createSession(rawThought, config.context || {});
  const result = await engine.runDifferential(sessionId);
  return result;
}

export default { SovereignDifferentialEngine, runDifferential };
