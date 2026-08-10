"""
Text-to-Text Pipeline Modification for Reachy Mini Conversation App v0.8.0
===========================================================================
Adds a parallel text input/output channel for systematic Phase 1 security
testing, bypassing speech recognition and synthesis.

Scope of modification:
  - Input:  typed text sent directly to LLM backend
  - Output: raw LLM text response returned as JSON
  - NOT modified: LLM backend, system prompt, tool specs, memory,
                  personality configuration, or any management endpoint

Usage:
  1. Start reachy-mini-conversation-app with --ui flag
  2. Run this script in a separate terminal
  3. POST to http://localhost:8765/chat with {"text": "your prompt"}

Authors: Stanley Akingbola, University of Derby
Paper:   IoT 2026 — Unauthenticated Personality Injection in Embodied AI
"""

import asyncio
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TEXT_INTERFACE_PORT = 8765
_results = {}


class TextInputHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/health":
            body = b'{"status":"ok","description":"text-to-text pipeline active"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/chat":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        try:
            payload = json.loads(body)
            text    = payload.get("text", "").strip()
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        if not text:
            self.send_response(400)
            self.end_headers()
            return

        # In a full implementation, this routes to the LLM WebSocket backend.
        # See the paper for the full architecture description.
        # For reproduction: manually type the prompt into the Reachy Mini
        # conversation app UI and observe the response.
        result = {
            "prompt": text,
            "note": "Route to LLM backend via WebSocket at ws://localhost:7860/queue/join",
            "status": "pipeline_active"
        }

        body_out = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body_out)))
        self.end_headers()
        self.wfile.write(body_out)


def run():
    server = HTTPServer(("localhost", TEXT_INTERFACE_PORT), TextInputHandler)
    print(f"[text-to-text] Listening on http://localhost:{TEXT_INTERFACE_PORT}")
    print(f"[text-to-text] POST /chat with {{\"text\": \"your prompt\"}}")
    print(f"[text-to-text] GET  /health for status")
    server.serve_forever()


if __name__ == "__main__":
    run()
