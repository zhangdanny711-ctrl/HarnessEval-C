"""Fictional ReadLater subject implementation using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import threading
import uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

WEB = Path(__file__).parent / "web"


class ArticleStore:
    def __init__(self) -> None:
        self._items: list[dict] = []
        self._lock = threading.Lock()

    def list(self) -> list[dict]:
        with self._lock:
            return [dict(item) for item in self._items]

    def save(self, title: str) -> dict:
        with self._lock:
            article = {"id": len(self._items) + 1, "title": title, "read": False}
            self._items.append(article)
            return dict(article)

    def mark_read(self, article_id: int) -> dict | None:
        with self._lock:
            for article in self._items:
                if article["id"] == article_id:
                    article["read"] = True
                    return dict(article)
        return None


def response_payload(code: str, message: str, data=None) -> bytes:
    return json.dumps({
        "requestId": str(uuid.uuid4()),
        "created": datetime.now(timezone.utc).isoformat(),
        "code": code,
        "message": message,
        "data": data,
    }).encode("utf-8")


def handler_factory(store: ArticleStore):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(WEB), **kwargs)

        def log_message(self, format, *args):
            return

        def send_json(self, status: int, payload: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def read_json(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            try:
                value = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                return {}
            return value if isinstance(value, dict) else {}

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/health":
                return self.send_json(200, response_payload("OK", "healthy"))
            if path == "/api/articles":
                return self.send_json(200, response_payload("OK", "articles listed", store.list()))
            return super().do_GET()

        def do_POST(self):
            if urlparse(self.path).path != "/api/articles":
                return self.send_json(404, response_payload("NOT_FOUND", "route not found"))
            title = str(self.read_json().get("title") or "").strip()
            if not title:
                return self.send_json(
                    400, response_payload("INVALID_INPUT", "title is required")
                )
            article = store.save(title)
            return self.send_json(201, response_payload("CREATED", "article saved", article))

        def do_PATCH(self):
            parts = urlparse(self.path).path.strip("/").split("/")
            if len(parts) != 4 or parts[:2] != ["api", "articles"] or parts[3] != "read":
                return self.send_json(404, response_payload("NOT_FOUND", "route not found"))
            try:
                article_id = int(parts[2])
            except ValueError:
                return self.send_json(404, response_payload("NOT_FOUND", "article not found"))
            article = store.mark_read(article_id)
            if article is None:
                return self.send_json(404, response_payload("NOT_FOUND", "article not found"))
            return self.send_json(200, response_payload("OK", "article marked read", article))

    return Handler


def create_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), handler_factory(ArticleStore()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    create_server("127.0.0.1", args.port).serve_forever()
