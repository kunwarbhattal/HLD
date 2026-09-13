# High-Level Design (HLD)

A small, runnable collection of networking patterns. Each topic contains
language-specific examples and notes for running them locally.

## Topics

- [Networking](networking/README.md)
  - [Server-Sent Events (SSE)](networking/sse/README.md)
  - Long polling *(coming next)*
  - WebSockets *(coming next)*

## Repository layout

```text
networking/
├── README.md                 # Networking topic index
├── sse/                      # Server-Sent Events examples
│   ├── java/
│   ├── javascript/
│   └── python/
├── long-polling/             # Reserved for the next example
└── websockets/               # Reserved for a future example
```

## Prerequisites

The SSE examples use only their language standard libraries:

- Java 17+ (with the `jdk.httpserver` module)
- Python 3.8+
- Node.js 18+

Start any example and connect with `curl -N` so curl does not buffer the event
stream. See the [SSE page](networking/sse/README.md) for exact commands.
