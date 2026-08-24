"""Deterministically gate semantic runtime judgments."""

from typing import Any


def evaluate(config: dict[str, Any], evidence: dict[str, Any], semantic_score: float | None) -> dict[str, Any]:
    builds = evidence.get("builds") or []
    health = evidence.get("health") or []
    probes = evidence.get("probes") or []
    build_ok = bool(builds) and all(item.get("passed") is True for item in builds)
    boot_ok = bool(health) and all(item.get("passed") is True for item in health)
    probe_rate = (sum(item.get("passed") is True for item in probes) / len(probes)) if probes else 0.0
    if not build_ok:
        upper = 0.2
    elif not boot_ok:
        upper = 0.4
    else:
        upper = 0.5 + 0.5 * probe_rate
    semantic = upper if semantic_score is None else max(0.0, min(1.0, float(semantic_score)))
    return {"status": "ok", "score": round(min(semantic, upper), 6),
            "metrics": {"build_ok": build_ok, "boot_ok": boot_ok,
                        "probe_pass_rate": round(probe_rate, 6), "deterministic_upper_bound": round(upper, 6)},
            "evidence": evidence}

