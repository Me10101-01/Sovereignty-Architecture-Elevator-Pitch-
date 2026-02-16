// src/differential/orchestrator.js
// REST API for the Sovereign Differential Engine

import express from 'express';
import { loadConfig } from '../config.js';
import { SovereignDifferentialEngine } from './engine.js';

const app = express();
app.use(express.json({ limit: '10mb' }));

const config = loadConfig();
const differentialConfig = config.differential || {};
const port = process.env.DIFFERENTIAL_PORT || differentialConfig?.port || 8086;

// Create the engine instance
const engine = new SovereignDifferentialEngine({
  maxRounds: differentialConfig?.maxRounds || 3,
  convergenceThreshold: differentialConfig?.convergenceThreshold || 0.8
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    engine_id: engine.id,
    sessions_active: engine.sessions.size,
    agents: engine.agents.map(a => a.name)
  });
});

// Get engine configuration
app.get('/config', (req, res) => {
  res.json({
    maxRounds: engine.config.maxRounds,
    convergenceThreshold: engine.config.convergenceThreshold,
    minConfidence: engine.config.minConfidence,
    agents: engine.agents.map(a => a.toJSON())
  });
});

/**
 * Create a new differential session
 * POST /sessions
 * Body: { thought: string, context?: object }
 */
app.post('/sessions', async (req, res) => {
  try {
    const { thought, context } = req.body;
    
    if (!thought || typeof thought !== 'string') {
      return res.status(400).json({ 
        error: 'Missing or invalid required field: thought (string)' 
      });
    }
    
    const sessionId = await engine.createSession(thought, context || {});
    
    res.status(201).json({
      session_id: sessionId,
      status: 'created',
      message: 'Differential session created. Use POST /sessions/:id/run to start processing.'
    });
    
  } catch (error) {
    console.error('Error creating session:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Run the differential process on a session
 * POST /sessions/:id/run
 */
app.post('/sessions/:id/run', async (req, res) => {
  try {
    const sessionId = req.params.id;
    const session = engine.getSession(sessionId);
    
    if (!session) {
      return res.status(404).json({ error: `Session ${sessionId} not found` });
    }
    
    if (session.status === 'completed') {
      return res.status(400).json({ 
        error: 'Session already completed',
        result: session.result 
      });
    }
    
    // Run the differential process
    const result = await engine.runDifferential(sessionId);
    
    res.json({
      session_id: sessionId,
      status: 'completed',
      result
    });
    
  } catch (error) {
    console.error('Error running differential:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Quick differential - create session and run in one call
 * POST /differential
 * Body: { thought: string, context?: object }
 */
app.post('/differential', async (req, res) => {
  try {
    const { thought, context } = req.body;
    
    if (!thought || typeof thought !== 'string') {
      return res.status(400).json({ 
        error: 'Missing or invalid required field: thought (string)' 
      });
    }
    
    const sessionId = await engine.createSession(thought, context || {});
    const result = await engine.runDifferential(sessionId);
    
    res.json({
      session_id: sessionId,
      status: 'completed',
      result
    });
    
  } catch (error) {
    console.error('Error in quick differential:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get session status
 * GET /sessions/:id
 */
app.get('/sessions/:id', (req, res) => {
  try {
    const session = engine.getSession(req.params.id);
    
    if (!session) {
      return res.status(404).json({ error: `Session ${req.params.id} not found` });
    }
    
    res.json(session);
  } catch (error) {
    console.error('Error getting session:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * List all sessions
 * GET /sessions
 * Query: status (optional filter)
 */
app.get('/sessions', (req, res) => {
  try {
    const { status } = req.query;
    const sessions = engine.listSessions({ status });
    
    res.json({
      sessions,
      count: sessions.length,
      filter: { status }
    });
  } catch (error) {
    console.error('Error listing sessions:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get hypothesis board for a session
 * GET /sessions/:id/hypotheses
 */
app.get('/sessions/:id/hypotheses', (req, res) => {
  try {
    const sessionData = engine.sessions.get(req.params.id);
    
    if (!sessionData) {
      return res.status(404).json({ error: `Session ${req.params.id} not found` });
    }
    
    res.json(sessionData.hypothesisBoard.toJSON());
  } catch (error) {
    console.error('Error getting hypotheses:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get evolution graph for a session
 * GET /sessions/:id/evolution
 */
app.get('/sessions/:id/evolution', (req, res) => {
  try {
    const sessionData = engine.sessions.get(req.params.id);
    
    if (!sessionData) {
      return res.status(404).json({ error: `Session ${req.params.id} not found` });
    }
    
    res.json({
      session_id: req.params.id,
      evolution_graph: sessionData.hypothesisBoard.getEvolutionGraph()
    });
  } catch (error) {
    console.error('Error getting evolution graph:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get engine event log
 * GET /events
 * Query: sessionId (optional filter)
 */
app.get('/events', (req, res) => {
  try {
    const { sessionId } = req.query;
    const events = engine.getEventLog({ sessionId });
    
    res.json({
      events,
      count: events.length,
      filter: { sessionId }
    });
  } catch (error) {
    console.error('Error getting events:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get available agents
 * GET /agents
 */
app.get('/agents', (req, res) => {
  res.json({
    agents: engine.agents.map(a => ({
      ...a.toJSON(),
      capabilities: {
        generateHypotheses: true,
        challengeHypotheses: true,
        refineHypothesis: true
      }
    }))
  });
});

// Metrics endpoint for Prometheus
app.get('/metrics', (req, res) => {
  const activeSessions = engine.listSessions({ status: 'active' }).length;
  const completedSessions = engine.listSessions({ status: 'completed' }).length;
  
  const metrics = `
# HELP differential_sessions_total Total number of differential sessions
# TYPE differential_sessions_total counter
differential_sessions_total{status="active"} ${activeSessions}
differential_sessions_total{status="completed"} ${completedSessions}

# HELP differential_agents_count Number of active agents
# TYPE differential_agents_count gauge  
differential_agents_count ${engine.agents.length}

# HELP differential_events_total Total events logged
# TYPE differential_events_total counter
differential_events_total ${engine.eventLog.length}
`;
  
  res.set('Content-Type', 'text/plain');
  res.send(metrics.trim());
});

// Error handler
app.use((error, req, res, next) => {
  console.error('Differential Engine API error:', error);
  res.status(500).json({ 
    error: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

app.listen(port, () => {
  console.log(`🧠 Sovereign Differential Engine listening on port ${port}`);
  console.log(`🎯 Agents: ${engine.agents.map(a => a.name).join(', ')}`);
  console.log(`⚙️  Max rounds: ${engine.config.maxRounds}, Convergence threshold: ${engine.config.convergenceThreshold}`);
  console.log(`\n📖 Endpoints:`);
  console.log(`   POST /differential         - Quick differential (one-shot)`);
  console.log(`   POST /sessions             - Create new session`);
  console.log(`   POST /sessions/:id/run     - Run differential on session`);
  console.log(`   GET  /sessions             - List all sessions`);
  console.log(`   GET  /sessions/:id         - Get session status`);
  console.log(`   GET  /sessions/:id/hypotheses - Get hypothesis board`);
  console.log(`   GET  /sessions/:id/evolution - Get evolution graph`);
  console.log(`   GET  /agents               - List available agents`);
  console.log(`   GET  /events               - Get event log`);
  console.log(`   GET  /health               - Health check`);
  console.log(`   GET  /metrics              - Prometheus metrics`);
});

export default app;
