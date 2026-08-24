"""Frozen API contract evaluation."""

from typing import Any
from ..http_assertions import check_http_response


def evaluate(config: dict[str, Any], evidence: dict[str, Any], semantic_score: float | None) -> dict[str, Any]:
    contracts = config.get("contracts") or []
    responses = evidence.get("responses") or {}
    defaults = config.get("default_envelope_fields") or []
    results = []
    for contract in contracts:
        response = responses.get(contract["id"]) or {}
        checked = check_http_response(int(response.get("status", 0)), response.get("body"),
                                      contract.get("expect") or {}, defaults)
        results.append({"id": contract["id"], **checked})
    rate = sum(item["passed"] for item in results) / len(results) if results else 0.0
    semantic = rate if semantic_score is None else max(0.0, min(1.0, float(semantic_score)))
    return {"status": "ok", "score": round(min(rate, semantic), 6),
            "metrics": {"contract_pass_rate": round(rate, 6)}, "evidence": {"contracts": results}}

