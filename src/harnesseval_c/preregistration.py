"""Immutable, digest-addressed evaluation specifications."""

from __future__ import annotations

import copy
from typing import Any

from .io import value_digest
from .http_assertions import normalize_expectation

PREREG_SCHEMA = "harnesseval_c.preregistration.v1"


def normalize_components(components: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(components)
    api = value.get("api_contract") or {}
    defaults = api.get("default_envelope_fields") or []
    for contract in api.get("contracts") or []:
        contract["method"] = str(contract.get("method") or "GET").upper()
        if contract["method"] not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise ValueError("unsupported HTTP method")
        if not str(contract.get("path") or "").startswith("/"):
            raise ValueError("contract path must be absolute")
        contract["expect"] = normalize_expectation(contract.get("expect") or {}, defaults)
    browser = value.get("browser_flow") or {}
    for journey in browser.get("journeys") or []:
        steps = journey.get("steps") or []
        if not steps or steps[0].get("kind") != "goto":
            raise ValueError("browser journey must start with goto")
        if not any(str(step.get("kind", "")).startswith("expect_") for step in steps):
            raise ValueError("browser journey requires an assertion")
    return value


def freeze_preregistration(case: dict[str, Any], spec_text: str,
                           components: dict[str, Any], generator_config_digest: str) -> dict[str, Any]:
    payload = {
        "schema_version": PREREG_SCHEMA,
        "case_id": case["case_id"],
        "inputs": {"case_digest": value_digest(case), "spec_digest": value_digest(spec_text),
                   "generator_config_digest": generator_config_digest},
        "components": normalize_components(components),
    }
    payload["input_digest"] = value_digest(payload["inputs"])
    payload["artifact_digest"] = value_digest(payload)
    return payload


def validate_preregistration(value: dict[str, Any], case: dict[str, Any], spec_text: str,
                             generator_config_digest: str) -> None:
    if value.get("schema_version") != PREREG_SCHEMA or value.get("case_id") != case.get("case_id"):
        raise ValueError("preregistration identity mismatch")
    inputs = {"case_digest": value_digest(case), "spec_digest": value_digest(spec_text),
              "generator_config_digest": generator_config_digest}
    if value.get("inputs") != inputs or value.get("input_digest") != value_digest(inputs):
        raise ValueError("preregistration input digest mismatch")
    clone = copy.deepcopy(value)
    stored = clone.pop("artifact_digest", None)
    if stored != value_digest(clone):
        raise ValueError("preregistration artifact digest mismatch")
    if normalize_components(value.get("components") or {}) != value.get("components"):
        raise ValueError("preregistration is not canonical")

