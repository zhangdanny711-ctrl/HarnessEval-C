"""Core/Observation aggregation with fail-closed semantics."""

from __future__ import annotations

import math
from typing import Any

SCORE_SCHEMA = "harnesseval_c.score.v1"


def _valid_score(result: dict[str, Any]) -> float | None:
    value = result.get("score")
    if result.get("status") != "ok" or isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) and 0 <= value <= 1 else None


def score_case(plan: dict[str, Any], results: list[dict[str, Any]],
               core_weight: float = 0.5) -> dict[str, Any]:
    by_id = {item.get("skill_id"): item for item in results}
    resolved = []
    invalid = []
    for selected in plan.get("selected_skills") or []:
        item = dict(by_id.get(selected["skill_id"]) or {
            "skill_id": selected["skill_id"], "status": "missing", "score": None})
        item["role"] = selected["role"]
        resolved.append(item)
        if selected["role"] in {"core", "observation"} and _valid_score(item) is None:
            invalid.append({"skill_id": item["skill_id"], "status": item.get("status")})
    def average(role: str) -> float | None:
        values = [_valid_score(item) for item in resolved if item["role"] == role]
        return round(sum(values) / len(values), 6) if values and None not in values else None
    core = average("core")
    observation = average("observation")
    final = None if invalid or core is None or observation is None else round(
        core_weight * core + (1 - core_weight) * observation, 6)
    return {"schema_version": SCORE_SCHEMA, "case_id": plan.get("case_id"),
            "core_score": core, "observation_score": observation, "final_score": final,
            "evaluation_status": "invalid" if invalid else "valid",
            "invalid_reasons": invalid, "skill_results": resolved,
            "policy": {"core_weight": core_weight, "observation_weight": 1-core_weight,
                       "fail_closed": True}}
