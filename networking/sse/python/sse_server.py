"""A dependency-free Server-Sent Events server at http://localhost:8080/events."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import count
from time import sleep, time


EVENT_IDS = count(1)


class SseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return

        if self.path != "/events":
            self.send_error(404, "Use /events or /health")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        tick = 0
        try:
            self._send(": connected\n\n")
            while True:
                self._send(
                    f"id: {next(EVENT_IDS)}\n"
                    "event: message\n"
                    f"data: tick={tick} time={time():.3f}\n\n"
                )
                tick += 1
                if tick % 15 == 0:
                    self._send(": keep-alive\n\n")
                sleep(1)
        except (BrokenPipeError, ConnectionResetError):
            pass  # The client closed its streaming connection.

    def _send(self, event):
        self.wfile.write(event.encode("utf-8"))
        self.wfile.flush()

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("", 8080), SseHandler)
    print("SSE server listening on http://localhost:8080/events")
    print("Connect with: curl -N http://localhost:8080/events")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
