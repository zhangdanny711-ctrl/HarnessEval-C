"""Deterministic HTTP contract assertions."""

from __future__ import annotations

from typing import Any


def normalize_expectation(raw: dict[str, Any], default_envelope_fields: list[str] | None = None) -> dict[str, Any]:
    value = dict(raw)
    contains = value.get("message_contains", [])
    if isinstance(contains, str):
        contains = [contains]
    if not isinstance(contains, list) or not all(isinstance(item, str) for item in contains):
        raise ValueError("message_contains must be a list of strings")
    fields = list(dict.fromkeys([*(default_envelope_fields or []), *(value.get("envelope_fields") or [])]))
    value["message_contains"] = contains
    value["envelope_fields"] = fields
    return value


def _path(value: Any, dotted: str) -> Any:
    current = value
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def check_http_response(status: int, body: Any, expectation: dict[str, Any],
                        default_envelope_fields: list[str] | None = None) -> dict[str, Any]:
    expected = normalize_expectation(expectation, default_envelope_fields)
    checks: list[dict[str, Any]] = []
    if "http_status" in expected:
        checks.append({"check": "http_status", "passed": status == int(expected["http_status"])})
    if expected["envelope_fields"]:
        checks.append({"check": "envelope_fields", "passed": isinstance(body, dict) and all(
            _path(body, field) is not None for field in expected["envelope_fields"])})
    if "equals" in expected:
        for dotted, wanted in expected["equals"].items():
            checks.append({"check": f"equals:{dotted}", "passed": _path(body, dotted) == wanted})
    message = str(_path(body, str(expected.get("message_path") or "message")) or "")
    for required in expected["message_contains"]:
        checks.append({"check": f"message_contains:{required}", "passed": required in message})
    if "min_items" in expected:
        target = _path(body, str(expected.get("items_path") or "data"))
        checks.append({"check": "min_items", "passed": isinstance(target, list) and len(target) >= int(expected["min_items"])})
    return {"passed": bool(checks) and all(item["passed"] for item in checks), "checks": checks}

