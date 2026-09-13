"""A small SSE server with plain-English comments for every important step.

Run this file with ``python3 sse_server.py``. Then open a second terminal and
run ``curl -N http://localhost:8080/events``. The ``-N`` option tells curl not
to wait before showing each event.
"""

# BaseHTTPRequestHandler reads an HTTP request and lets us build its response.
# ThreadingHTTPServer gives every connected client its own thread.
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
# count creates 1, 2, 3, ... each time next(...) is called.
from itertools import count
# sleep waits between events; time supplies the current timestamp.
from time import sleep, time


# Keep one increasing event number for all clients of this server.
EVENT_IDS = count(1)


# Define how this server handles incoming HTTP requests.
class SseHandler(BaseHTTPRequestHandler):
    """Handle the /health and /events URLs."""

    # Python calls this method automatically when a client sends an HTTP GET.
    def do_GET(self):
        # A health check is a quick way to confirm that the server is running.
        if self.path == "/health":
            # Send the HTTP status code 200, which means "success".
            self.send_response(200)
            # Tell the client that the short response is plain UTF-8 text.
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            # Finish the HTTP headers before writing the response body.
            self.end_headers()
            # Write bytes (not a Python string) to the client.
            self.wfile.write(b"ok\n")
            # Do not continue into the SSE code after answering /health.
            return

        # Only /events is the streaming endpoint; all other paths are invalid.
        if self.path != "/events":
            # Return a helpful 404 ("not found") response to the client.
            self.send_error(404, "Use /events or /health")
            # Stop handling this request after the error response.
            return

        # Start a successful response for the client that requested /events.
        self.send_response(200)
        # This header is what tells a client that the body is an SSE stream.
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        # Do not let browsers or proxies save an old stream in their cache.
        self.send_header("Cache-Control", "no-cache")
        # Ask for this HTTP connection to remain open between events.
        self.send_header("Connection", "keep-alive")
        # Ask Nginx (when present) not to buffer events before forwarding them.
        self.send_header("X-Accel-Buffering", "no")
        # Send all of the headers now; event data comes next.
        self.end_headers()

        # Start this client's visible counter at zero.
        tick = 0
        try:
            # SSE comments begin with a colon; this says the stream connected.
            self._send(": connected\n\n")
            # Keep the same HTTP response open until the client disconnects.
            while True:
                # Send one complete SSE event. A blank line ends an SSE event.
                self._send(
                    # Give this event a unique ID for reconnecting clients.
                    f"id: {next(EVENT_IDS)}\n"
                    # Name this event "message" for EventSource listeners.
                    "event: message\n"
                    # Put the useful text in the SSE data field, then end it.
                    f"data: tick={tick} time={time():.3f}\n\n"
                )
                # Increase the counter that will be shown in the next event.
                tick += 1
                # Periodically send a comment to keep quiet connections active.
                if tick % 15 == 0:
                    self._send(": keep-alive\n\n")
                # Wait one second, so clients receive one message per second.
                sleep(1)
        # Writing fails normally when a browser or curl closes its connection.
        except (BrokenPipeError, ConnectionResetError):
            # There is nothing to clean up: this request handler now ends.
            pass

    # Convert text to UTF-8 bytes, write it, and flush it immediately.
    def _send(self, event):
        # HTTP response streams accept bytes, so encode our text first.
        self.wfile.write(event.encode("utf-8"))
        # Flush prevents Python from holding this event in a local buffer.
        self.wfile.flush()

    # Replace the default log format with a small, readable request log.
    def log_message(self, message_format, *args):
        # Print the client's address followed by Python's formatted log message.
        print(f"{self.address_string()} - {message_format % args}")


# Only start a server when this file is run directly, not when it is imported.
if __name__ == "__main__":
    # Listen on every local network interface, port 8080, using our handler.
    server = ThreadingHTTPServer(("", 8080), SseHandler)
    # Tell the person running the program where the event endpoint is.
    print("SSE server listening on http://localhost:8080/events")
    # Print a ready-to-copy command for watching the SSE stream.
    print("Connect with: curl -N http://localhost:8080/events")
    try:
        # Keep accepting requests until the user stops the program.
        server.serve_forever()
    # Ctrl+C raises KeyboardInterrupt, so catch it for a friendly shutdown.
    except KeyboardInterrupt:
        # Print a newline because Ctrl+C is usually displayed on this line.
        print("\nStopping server.")
    finally:
        # Release port 8080 whether the server stops normally or with Ctrl+C.
        server.server_close()
