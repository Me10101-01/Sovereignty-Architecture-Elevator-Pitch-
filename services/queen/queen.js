/**
 * Queen Orchestrator Service
 * 
 * The central router and orchestration service for SovereignMesh.
 * Queen acts as the control plane for all microservices within a 
 * Codespace-based sovereign compute node.
 * 
 * Architecture:
 * - Each Codespace = One SovereignMesh Node
 * - Each services/ folder = One Microservice  
 * - Queen = The Router that coordinates all services
 * 
 * Future services to be routed:
 * - swarmgate: Financial operations
 * - knowledge-node: Obsidian sync
 * - sentinel: Security monitoring
 */

import express from 'express';

const app = express();
const PORT = process.env.QUEEN_PORT || 3100;

// Middleware
app.use(express.json());

// Service registry - tracks all registered microservices
const serviceRegistry = new Map();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'queen',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Service registry endpoints
app.get('/services', (req, res) => {
  const services = Array.from(serviceRegistry.entries()).map(([name, info]) => ({
    name,
    ...info
  }));
  res.json({ services, count: services.length });
});

app.post('/services/register', (req, res) => {
  const { name, url, type } = req.body;
  if (!name || !url) {
    return res.status(400).json({ error: 'name and url are required' });
  }
  
  serviceRegistry.set(name, {
    url,
    type: type || 'unknown',
    registeredAt: new Date().toISOString(),
    status: 'active'
  });
  
  console.log(`[Queen] Service registered: ${name} at ${url}`);
  res.json({ success: true, message: `Service ${name} registered` });
});

app.delete('/services/:name', (req, res) => {
  const { name } = req.params;
  if (serviceRegistry.has(name)) {
    serviceRegistry.delete(name);
    console.log(`[Queen] Service deregistered: ${name}`);
    res.json({ success: true, message: `Service ${name} deregistered` });
  } else {
    res.status(404).json({ error: `Service ${name} not found` });
  }
});

// Route requests to registered services
app.all('/route/:service/*', async (req, res) => {
  const { service } = req.params;
  const servicePath = req.params[0] || '';
  
  if (!serviceRegistry.has(service)) {
    return res.status(404).json({ error: `Service ${service} not registered` });
  }
  
  const serviceInfo = serviceRegistry.get(service);
  const targetUrl = `${serviceInfo.url}/${servicePath}`;
  
  try {
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...req.headers
      },
      body: ['POST', 'PUT', 'PATCH'].includes(req.method) ? JSON.stringify(req.body) : undefined
    });
    
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error(`[Queen] Route error to ${service}:`, error.message);
    res.status(502).json({ error: `Failed to route to ${service}`, details: error.message });
  }
});

// Node information endpoint
app.get('/node', (req, res) => {
  res.json({
    node: 'SovereignMesh Node',
    codespace: process.env.CODESPACE_NAME || 'local',
    orchestrator: 'Queen',
    services: serviceRegistry.size,
    architecture: {
      description: 'Codespaces as sovereign compute nodes with Queen as orchestrator',
      thesis: 'Scattered tools',
      antithesis: 'Need unified control',
      synthesis: 'SovereignMesh via Codespaces'
    }
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`
  ╔═══════════════════════════════════════════════════════════════╗
  ║                                                               ║
  ║   👑 QUEEN ORCHESTRATOR                                       ║
  ║   SovereignMesh Node Control Plane                            ║
  ║                                                               ║
  ║   Port: ${PORT}                                                 ║
  ║   Status: ACTIVE                                              ║
  ║                                                               ║
  ║   Endpoints:                                                  ║
  ║   - GET  /health              Health check                    ║
  ║   - GET  /services            List registered services        ║
  ║   - POST /services/register   Register a service              ║
  ║   - GET  /node                Node information                ║
  ║   - ALL  /route/:service/*    Route to service                ║
  ║                                                               ║
  ╚═══════════════════════════════════════════════════════════════╝
  `);
});

export { app, serviceRegistry };
