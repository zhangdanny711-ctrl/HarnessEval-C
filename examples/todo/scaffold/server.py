"""Tiny in-memory server used only by the fictional Todo example."""

from __future__ import annotations

import argparse
import json
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TASKS: list[dict] = []
WEB = Path(__file__).parent / "web"


def envelope(code: str, message: str, data=None) -> bytes:
    return json.dumps({"requestId": str(uuid.uuid4()), "created": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "code": code, "message": message, "data": data}).encode()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def send_json(self, status: int, payload: bytes) -> None:
        self.send_response(status); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            return self.send_json(200, envelope("OK", "healthy"))
        if self.path.startswith("/api/tasks"):
            priority = self.path.partition("priority=")[2]
            data = [item for item in TASKS if not priority or item["priority"] == priority]
            return self.send_json(200, envelope("OK", "ok", data))
        return super().do_GET()

    def do_POST(self):
        if self.path != "/api/tasks":
            return self.send_json(404, envelope("NOT_FOUND", "not found"))
        size = int(self.headers.get("Content-Length", "0")); body = json.loads(self.rfile.read(size) or b"{}")
        title = str(body.get("title") or "").strip()
        if not title:
            return self.send_json(400, envelope("INVALID_INPUT", "title is required"))
        task = {"id": str(len(TASKS) + 1), "title": title, "completed": False,
                "priority": body.get("priority", "normal")}; TASKS.append(task)
        return self.send_json(201, envelope("CREATED", "task created", task))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(); ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()

