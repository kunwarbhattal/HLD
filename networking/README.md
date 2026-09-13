# Networking

This section demonstrates common ways for a server to deliver updates to a
client.

| Pattern | Direction | Connection model | Status |
| --- | --- | --- | --- |
| [Server-Sent Events (SSE)](sse/README.md) | Server → client | One long-lived HTTP response | Available |
| Long polling | Server → client | Repeated HTTP requests | Planned |
| WebSockets | Bidirectional | One persistent socket | Planned |

## Choosing a pattern

- **SSE** is a good fit for one-way browser updates such as notifications,
  progress, dashboards, and live feeds. It uses ordinary HTTP and reconnects
  automatically when used through the browser `EventSource` API.
- **Long polling** keeps an HTTP request open until an update arrives, then the
  client immediately issues the next request. It is useful where streaming is
  unavailable but introduces request churn.
- **WebSockets** support low-latency, two-way messages over one connection. Use
  them when both client and server need to send frequent messages.

The current runnable examples focus on SSE. Long-polling and WebSocket samples
will be added in their respective directories.
