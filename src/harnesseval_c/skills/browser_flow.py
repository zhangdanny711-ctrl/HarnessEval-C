"""Assertion-led browser journey scoring."""

from typing import Any

ACTION_KINDS = {"goto", "click", "fill", "select", "hover"}
ASSERTION_KINDS = {"expect_visible", "expect_text", "expect_url"}


def evaluate(config: dict[str, Any], evidence: dict[str, Any], semantic_score: float | None) -> dict[str, Any]:
    journeys = evidence.get("journeys") or []
    journey_results = []
    for journey in journeys:
        steps = journey.get("steps") or []
        actions = [item for item in steps if item.get("kind") in ACTION_KINDS]
        assertions = [item for item in steps if item.get("kind") in ASSERTION_KINDS]
        assertion_rate = sum(item.get("passed") is True for item in assertions) / len(assertions) if assertions else 0.0
        action_rate = sum(item.get("passed") is True for item in actions) / len(actions) if actions else 0.0
        journey_results.append({"journey_id": journey.get("journey_id"),
                                "passed": bool(assertions) and assertion_rate == 1.0,
                                "assertion_pass_rate": assertion_rate,
                                "action_pass_rate": action_rate, "steps": steps})
    correctness = sum(item["assertion_pass_rate"] for item in journey_results) / len(journey_results) if journey_results else 0.0
    if any(not item["passed"] for item in journey_results):
        correctness = min(correctness, 0.5)
    semantic = correctness if semantic_score is None else max(0.0, min(1.0, float(semantic_score)))
    return {"status": "ok", "score": round(min(correctness, semantic), 6),
            "metrics": {"assertion_correctness": round(correctness, 6)},
            "evidence": {"journeys": journey_results}}

