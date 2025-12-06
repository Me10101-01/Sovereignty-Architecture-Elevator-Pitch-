const http = require('http');
const crypto = require('crypto');

const CONFIG = {
  port: process.env.PORT || 3000,
  version: '1.0.0',
  startTime: new Date().toISOString()
};

const signals = [];

const server = http.createServer(async (req, res) => {
  const url = req.url.split('?')[0];
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  if (req.method === 'GET' && url === '/') {
    return res.end(JSON.stringify({
      service: 'Estrategi-Khaos Queen',
      version: CONFIG.version,
      status: 'online',
      endpoints: ['/health', '/signals/academic', '/webhooks/github']
    }));
  }
  
  if (req.method === 'GET' && url === '/health') {
    return res.end(JSON.stringify({ ok: true, service: 'queen' }));
  }
  
  if (req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const signal = { id: crypto.randomUUID(), type: url, data: JSON.parse(body || '{}') };
        signals.push(signal);
        console.log('Signal:', signal.type, signal.id);
        res.end(JSON.stringify({ ok: true, signalId: signal.id }));
      } catch (e) {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: 'Invalid JSON' }));
      }
    });
    return;
  }
  
  res.statusCode = 404;
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(CONFIG.port, () => {
  console.log('👑 QUEEN ONLINE - Port', CONFIG.port);
});
