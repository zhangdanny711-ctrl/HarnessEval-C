"""Observation scoring from recorded checks and optional semantic review."""

from typing import Any


def evaluate(config: dict[str, Any], evidence: dict[str, Any], semantic_score: float | None) -> dict[str, Any]:
    raw_checks = evidence.get("checks")
    checks_are_valid = (
        isinstance(raw_checks, list)
        and bool(raw_checks)
        and all(
            isinstance(item, dict) and isinstance(item.get("passed"), bool)
            for item in raw_checks
        )
    )
    checks = raw_checks if checks_are_valid else []
    deterministic_required = config.get("deterministic_required") is True
    semantic_required = config.get("semantic_required") is True
    deterministic_score = None
    if checks:
        deterministic_score = sum(item.get("passed") is True for item in checks) / len(checks)
    if deterministic_required and not checks_are_valid:
        return {"status": "invalid", "score": None,
                "diagnostics": {"reason": "required deterministic checks are missing or invalid"},
                "evidence": evidence}
    if semantic_required and semantic_score is None:
        return {"status": "invalid", "score": None,
                "diagnostics": {"reason": "required semantic judgment is missing"},
                "evidence": evidence}
    if semantic_score is None and deterministic_score is None:
        return {"status": "invalid", "score": None,
                "diagnostics": {"reason": "recorded checks or a semantic judge result are required"},
                "evidence": evidence}
    semantic = (
        max(0.0, min(1.0, float(semantic_score)))
        if semantic_score is not None else None
    )
    if deterministic_score is None:
        score = semantic
    elif semantic is None:
        score = deterministic_score
    else:
        score = min(deterministic_score, semantic)
    return {"status": "ok", "score": round(score, 6), "evidence": evidence,
            "metrics": {
                "configured_conventions": len(config.get("conventions") or []),
                "deterministic_check_rate": (
                    round(deterministic_score, 6) if deterministic_score is not None else None
                ),
                "semantic_required": semantic_required,
                "semantic_judge_used": semantic_score is not None,
            }}
