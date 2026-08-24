"""Built-in, configuration-driven skill evaluators."""

from __future__ import annotations

from ..registry import Skill, SkillRegistry
from .api_contract import evaluate as api_contract
from .browser_flow import evaluate as browser_flow
from .observation import evaluate as observation
from .regression_guard import evaluate as regression_guard
from .runtime_behavior import evaluate as runtime_behavior
from .spec_coverage import evaluate as spec_coverage


def default_registry() -> SkillRegistry:
    registry = SkillRegistry()
    definitions = [
        ("spec_coverage", "core", "Trace preregistered requirements to implementation evidence", spec_coverage),
        ("runtime_behavior", "core", "Verify deterministic build, boot, and behavior probes", runtime_behavior),
        ("api_contract", "core", "Check frozen HTTP request and response contracts", api_contract),
        ("browser_flow", "core", "Execute frozen browser journeys with assertion-led scoring", browser_flow),
        ("regression_guard", "core", "Replay prior behavior and verify configured protected anchors", regression_guard),
        ("code_quality", "observation", "Inspect maintainability and correctness risks", observation),
        ("convention_compliance", "observation", "Compare changes with configured project conventions", observation),
        ("diff_hygiene", "observation", "Inspect change scope and unrelated artifacts", observation),
    ]
    for skill_id, role, description, evaluator in definitions:
        registry.register(Skill(skill_id, role, description, evaluator))
    return registry

