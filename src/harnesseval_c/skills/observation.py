"""Bounded semantic observation skill result."""

from typing import Any


def evaluate(config: dict[str, Any], evidence: dict[str, Any], semantic_score: float | None) -> dict[str, Any]:
    if semantic_score is None:
        return {"status": "invalid", "score": None,
                "diagnostics": {"reason": "semantic judge result is required"}, "evidence": evidence}
    score = max(0.0, min(1.0, float(semantic_score)))
    return {"status": "ok", "score": round(score, 6), "evidence": evidence,
            "metrics": {"configured_conventions": len(config.get("conventions") or [])}}

