"""Configurable registry for score-bearing and diagnostic skills."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


Evaluator = Callable[[dict[str, Any], dict[str, Any], float | None], dict[str, Any]]


@dataclass(frozen=True)
class Skill:
    skill_id: str
    role: str
    description: str
    evaluator: Evaluator


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if skill.skill_id in self._skills:
            raise ValueError(f"duplicate skill: {skill.skill_id}")
        if skill.role not in {"core", "observation", "diagnostic"}:
            raise ValueError(f"invalid skill role: {skill.role}")
        self._skills[skill.skill_id] = skill

    def get(self, skill_id: str) -> Skill:
        try:
            return self._skills[skill_id]
        except KeyError as exc:
            raise ValueError(f"unknown skill: {skill_id}") from exc

    def catalog(self) -> list[dict[str, str]]:
        return [
            {"skill_id": item.skill_id, "default_role": item.role,
             "description": item.description}
            for item in self._skills.values()
        ]

    def ids(self) -> tuple[str, ...]:
        return tuple(self._skills)

