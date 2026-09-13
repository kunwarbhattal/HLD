const http = require('node:http');

const port = 8080;
let nextEventId = 1;

const server = http.createServer((request, response) => {
  if (request.url === '/health') {
    response.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('ok\n');
    return;
  }

  if (request.url !== '/events') {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('Use /events or /health\n');
    return;
  }

  response.writeHead(200, {
    'Content-Type': 'text/event-stream; charset=utf-8',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
    'X-Accel-Buffering': 'no',
  });
  response.write(': connected\n\n');

  let tick = 0;
  const interval = setInterval(() => {
    response.write(`id: ${nextEventId++}\n`);
    response.write('event: message\n');
    response.write(`data: tick=${tick++} time=${new Date().toISOString()}\n\n`);

    if (tick % 15 === 0) {
      response.write(': keep-alive\n\n');
    }
  }, 1000);

  request.on('close', () => {
    clearInterval(interval);
  });
});

server.listen(port, () => {
  console.log(`SSE server listening on http://localhost:${port}/events`);
  console.log(`Connect with: curl -N http://localhost:${port}/events`);
});
