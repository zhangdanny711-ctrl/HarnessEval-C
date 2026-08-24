"""Configuration-driven regression replay and protected-anchor checks."""

from typing import Any


def evaluate(config: dict[str, Any], evidence: dict[str, Any], semantic_score: float | None) -> dict[str, Any]:
    replay = evidence.get("replay") or []
    anchors = evidence.get("anchors") or []
    checks = [*replay, *anchors]
    rate = sum(item.get("passed") is True for item in checks) / len(checks) if checks else 0.0
    semantic = rate if semantic_score is None else max(0.0, min(1.0, float(semantic_score)))
    return {"status": "ok", "score": round(min(rate, semantic), 6),
            "metrics": {"regression_pass_rate": round(rate, 6)}, "evidence": evidence}

