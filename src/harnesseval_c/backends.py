"""Provider-neutral OpenAI-compatible judge transport using curl."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Any

from .io import value_digest


@dataclass(frozen=True)
class JudgeConfig:
    base_url: str
    api_key: str
    model: str
    temperature: float = 0.0
    timeout: float = 120.0
    extra_headers: tuple[tuple[str, str], ...] = ()

    @classmethod
    def from_env(cls) -> "JudgeConfig":
        values = [os.getenv("JUDGE_BASE_URL"), os.getenv("JUDGE_API_KEY"), os.getenv("JUDGE_MODEL")]
        if not all(values):
            raise RuntimeError("set JUDGE_BASE_URL, JUDGE_API_KEY, and JUDGE_MODEL")
        headers = json.loads(os.getenv("JUDGE_EXTRA_HEADERS_JSON", "{}"))
        if not isinstance(headers, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in headers.items()):
            raise RuntimeError("JUDGE_EXTRA_HEADERS_JSON must contain string pairs")
        return cls(str(values[0]).rstrip("/"), str(values[1]), str(values[2]),
                   extra_headers=tuple(sorted(headers.items())))

    def semantic_digest(self) -> str:
        return value_digest({"base_url": self.base_url, "model": self.model,
                             "temperature": self.temperature,
                             "extra_header_names": sorted(k.lower() for k, _ in self.extra_headers)})


class JudgeBackend:
    def __init__(self, config: JudgeConfig):
        self.config = config

    def infer(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        request_body = json.dumps({"model": self.config.model, "messages": messages,
                                   "temperature": self.config.temperature,
                                   "response_format": {"type": "json_object"}}).encode()
        fd, body_path = tempfile.mkstemp(prefix="harnesseval-request-", suffix=".json")
        try:
            os.write(fd, request_body)
            os.close(fd)
            header_text = "\n".join([
                "Content-Type: application/json",
                f"Authorization: Bearer {self.config.api_key}",
                *(f"{key}: {value}" for key, value in self.config.extra_headers), "",
            ])
            started = time.monotonic()
            proc = subprocess.run([
                "curl", "--silent", "--show-error", "--fail-with-body",
                "--max-time", str(self.config.timeout), "--request", "POST",
                "--header", "@-", "--data-binary", f"@{body_path}",
                f"{self.config.base_url}/chat/completions"],
                input=header_text, text=True, capture_output=True, check=False)
            if proc.returncode != 0:
                raise RuntimeError(f"judge transport failed (curl exit {proc.returncode})")
            response = json.loads(proc.stdout)
            choice = response["choices"][0]["message"]["content"]
            return {"parsed": json.loads(choice), "raw_output_text": choice,
                    "response_model": response.get("model"), "usage": response.get("usage"),
                    "elapsed_seconds": round(time.monotonic() - started, 6)}
        finally:
            if os.path.exists(body_path):
                os.unlink(body_path)
