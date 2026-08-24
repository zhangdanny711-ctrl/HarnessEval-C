"""Requirement-level coverage, bounded by deterministic evidence availability."""

from typing import Any


def evaluate(config: dict[str, Any], evidence: dict[str, Any], semantic_score: float | None) -> dict[str, Any]:
    requirements = config.get("requirements") or []
    observed = evidence.get("requirements") or {}
    passed = [item for item in requirements if observed.get(item["req_id"], {}).get("passed") is True]
    deterministic = len(passed) / len(requirements) if requirements else 0.0
    score = deterministic if semantic_score is None else min(deterministic, max(0.0, float(semantic_score)))
    return {"status": "ok", "score": round(score, 6),
            "metrics": {"requirement_pass_rate": round(deterministic, 6)},
            "evidence": {"requirements": observed}}

