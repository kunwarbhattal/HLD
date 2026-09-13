# Server-Sent Events (SSE)

SSE is a one-way, server-to-client streaming protocol carried over HTTP. The
server keeps the response open and writes events in this format:

```text
event: message
id: 1
data: hello

```

A blank line finishes each event. The examples here emit one `message` event
per second and a keep-alive comment every 15 seconds. They set
`Content-Type: text/event-stream`, disable response buffering, and clean up the
timer/stream when the client disconnects.

## Run an example

Open two terminals. In the first, start one server from this directory:

### Java

```bash
javac --add-modules jdk.httpserver java/SseServer.java
java --add-modules jdk.httpserver -cp java SseServer
```

### Python

```bash
python3 python/sse_server.py
```

### JavaScript (Node.js)

```bash
node javascript/sse-server.js
```

In the second terminal, connect to the running server:

```bash
curl -N http://localhost:8080/events
```

`-N` is important because it asks curl to print streaming data immediately. To
check the health endpoint instead, run:

```bash
curl http://localhost:8080/health
```

Stop a server with `Ctrl+C`.

## Browser client

Browsers provide `EventSource` for consuming a stream:

```js
const stream = new EventSource('http://localhost:8080/events');
stream.addEventListener('message', (event) => console.log(event.data));
```

`EventSource` reconnects by default, and the `id` field lets a browser send
`Last-Event-ID` after reconnecting. These minimal servers generate event IDs but
do not retain old events, so a reconnect starts with new live events.
