import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicLong;

/** A dependency-free SSE server. Visit http://localhost:8080/events. */
public final class SseServer {
    private static final int PORT = 8080;
    private static final AtomicLong EVENT_ID = new AtomicLong();

    private SseServer() {
    }

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);
        server.createContext("/health", SseServer::health);
        server.createContext("/events", SseServer::events);
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();

        System.out.printf("SSE server listening on http://localhost:%d/events%n", PORT);
        System.out.println("Connect with: curl -N http://localhost:8080/events");
    }

    private static void health(HttpExchange exchange) throws IOException {
        byte[] body = "ok\n".getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(200, body.length);
        try (OutputStream output = exchange.getResponseBody()) {
            output.write(body);
        }
    }

    private static void events(HttpExchange exchange) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "text/event-stream; charset=utf-8");
        exchange.getResponseHeaders().set("Cache-Control", "no-cache");
        exchange.getResponseHeaders().set("Connection", "keep-alive");
        exchange.getResponseHeaders().set("X-Accel-Buffering", "no");
        exchange.sendResponseHeaders(200, 0);

        try (OutputStream output = exchange.getResponseBody()) {
            write(output, ": connected\n\n");
            long tick = 0;
            while (!Thread.currentThread().isInterrupted()) {
                long id = EVENT_ID.incrementAndGet();
                write(output, "id: " + id + "\n");
                write(output, "event: message\n");
                write(output, "data: tick=" + tick++ + " time=" + Instant.now() + "\n\n");

                if (tick % 15 == 0) {
                    write(output, ": keep-alive\n\n");
                }
                Thread.sleep(1_000);
            }
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
        } catch (IOException exception) {
            // A broken pipe means the SSE client disconnected.
        } finally {
            exchange.close();
        }
    }

    private static void write(OutputStream output, String event) throws IOException {
        output.write(event.getBytes(StandardCharsets.UTF_8));
        output.flush();
    }
}
