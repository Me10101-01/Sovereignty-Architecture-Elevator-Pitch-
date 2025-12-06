// src/differential/hypotheses.js
// Hypothesis generation and management for the Sovereign Differential Engine

import { v4 as uuid } from 'uuid';

/**
 * Represents a single hypothesis in the differential process
 */
export class Hypothesis {
  constructor({ content, source, confidence = 0.5, metadata = {} }) {
    this.id = uuid();
    this.content = content;
    this.source = source; // Which agent/phase generated this
    this.confidence = confidence; // 0.0 to 1.0
    this.status = 'active'; // active, challenged, refined, rejected, accepted
    this.challenges = [];
    this.refinements = [];
    this.metadata = metadata;
    this.created_at = new Date().toISOString();
    this.updated_at = new Date().toISOString();
  }

  challenge(challengeData) {
    this.challenges.push({
      id: uuid(),
      ...challengeData,
      timestamp: new Date().toISOString()
    });
    this.status = 'challenged';
    this.updated_at = new Date().toISOString();
  }

  refine(refinementData) {
    this.refinements.push({
      id: uuid(),
      ...refinementData,
      timestamp: new Date().toISOString()
    });
    this.status = 'refined';
    this.updated_at = new Date().toISOString();
  }

  accept(reason) {
    this.status = 'accepted';
    this.acceptance_reason = reason;
    this.updated_at = new Date().toISOString();
  }

  reject(reason) {
    this.status = 'rejected';
    this.rejection_reason = reason;
    this.updated_at = new Date().toISOString();
  }

  updateConfidence(delta) {
    this.confidence = Math.max(0, Math.min(1, this.confidence + delta));
    this.updated_at = new Date().toISOString();
  }

  toJSON() {
    return {
      id: this.id,
      content: this.content,
      source: this.source,
      confidence: this.confidence,
      status: this.status,
      challenges: this.challenges,
      refinements: this.refinements,
      metadata: this.metadata,
      created_at: this.created_at,
      updated_at: this.updated_at
    };
  }
}

/**
 * Manages the hypothesis board for a differential session
 */
export class HypothesisBoard {
  constructor() {
    this.hypotheses = new Map();
    this.evolutionHistory = [];
  }

  add(hypothesis) {
    this.hypotheses.set(hypothesis.id, hypothesis);
    this.evolutionHistory.push({
      action: 'add',
      hypothesis_id: hypothesis.id,
      timestamp: new Date().toISOString()
    });
    return hypothesis.id;
  }

  get(id) {
    return this.hypotheses.get(id);
  }

  getActive() {
    return Array.from(this.hypotheses.values())
      .filter(h => h.status === 'active' || h.status === 'refined');
  }

  getByStatus(status) {
    return Array.from(this.hypotheses.values())
      .filter(h => h.status === status);
  }

  getAll() {
    return Array.from(this.hypotheses.values());
  }

  challenge(hypothesisId, challengeData) {
    const hypothesis = this.hypotheses.get(hypothesisId);
    if (hypothesis) {
      hypothesis.challenge(challengeData);
      this.evolutionHistory.push({
        action: 'challenge',
        hypothesis_id: hypothesisId,
        data: challengeData,
        timestamp: new Date().toISOString()
      });
    }
    return hypothesis;
  }

  refine(hypothesisId, refinementData) {
    const hypothesis = this.hypotheses.get(hypothesisId);
    if (hypothesis) {
      hypothesis.refine(refinementData);
      this.evolutionHistory.push({
        action: 'refine',
        hypothesis_id: hypothesisId,
        data: refinementData,
        timestamp: new Date().toISOString()
      });
    }
    return hypothesis;
  }

  evolve(hypothesisId, newContent, reason) {
    const original = this.hypotheses.get(hypothesisId);
    if (!original) return null;

    // Create evolved hypothesis
    const evolved = new Hypothesis({
      content: newContent,
      source: `evolved_from:${original.source}`,
      confidence: original.confidence,
      metadata: {
        ...original.metadata,
        evolved_from: hypothesisId,
        evolution_reason: reason
      }
    });

    this.add(evolved);
    original.status = 'evolved';
    original.evolved_to = evolved.id;

    this.evolutionHistory.push({
      action: 'evolve',
      from_id: hypothesisId,
      to_id: evolved.id,
      reason,
      timestamp: new Date().toISOString()
    });

    return evolved;
  }

  getTopHypotheses(count = 3) {
    return Array.from(this.hypotheses.values())
      .filter(h => h.status === 'active' || h.status === 'refined' || h.status === 'accepted')
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, count);
  }

  getEvolutionGraph() {
    const nodes = Array.from(this.hypotheses.values()).map(h => ({
      id: h.id,
      content: h.content.substring(0, 100),
      status: h.status,
      confidence: h.confidence
    }));

    const edges = this.evolutionHistory
      .filter(e => e.action === 'evolve')
      .map(e => ({
        from: e.from_id,
        to: e.to_id,
        reason: e.reason
      }));

    return { nodes, edges };
  }

  toJSON() {
    return {
      hypotheses: Array.from(this.hypotheses.values()).map(h => h.toJSON()),
      evolution_history: this.evolutionHistory,
      summary: {
        total: this.hypotheses.size,
        active: this.getByStatus('active').length,
        refined: this.getByStatus('refined').length,
        accepted: this.getByStatus('accepted').length,
        rejected: this.getByStatus('rejected').length
      }
    };
  }
}

export default { Hypothesis, HypothesisBoard };
