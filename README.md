# HarnessEval-C

[![Tests](https://github.com/zhangdanny711-ctrl/HarnessEval-C/actions/workflows/tests.yml/badge.svg)](https://github.com/zhangdanny711-ctrl/HarnessEval-C/actions/workflows/tests.yml)

HarnessEval-C is a reusable, evidence-grounded evaluation harness for coding
agents working on full-stack software engineering tasks. It freezes what will
be checked before a subject rollout is inspected, executes deterministic and
semantic skills, preserves an Evidence Tree, and validates results fail-closed.

This public repository contains an independently implemented framework and
fully fictional public examples. It contains no real organization, application,
or agent rollout data. ReadLater is the recorded public showcase run; Todo is an
illustrative artifact walkthrough.

## Evaluation flow

```text
Case / SPEC
    ↓
Planner + Preregistration
    ↓
Frozen Plan / EvalSpec
    ↓
Coding Agent Rollout / Subject
    ↓
Skill Registry → selected Skills execute frozen checks
    ↓
Deterministic evidence + bounded semantic judgment
    ↓
Core / Observation → Final
    ↓
Evidence Tree → fail-closed validation
```

HarnessEval-C is designed for coding-agent evaluation. The public ReadLater
showcase evaluates an included subject implementation; no coding-agent rollout
is bundled with the repository.

## Recorded showcase

The committed ReadLater result is a real local evaluation of the included
fictional full-stack subject.

| Result | Score / Status |
|---|---:|
| Spec Coverage | 1.00 |
| Runtime Behavior | 1.00 |
| API Contract | 1.00 |
| Browser Flow | 1.00 |
| Diff Hygiene | 1.00 |
| **Core** | **1.00** |
| **Observation** | **1.00** |
| **Final** | **1.00** |
| Validation | `valid` |

The run records real local HTTP/runtime probes, four API contracts, a six-step
Playwright browser journey, step-level Evidence Tree evidence, and fail-closed
validation. It does not use a remote LLM judge.

[Showcase guide](examples/readlater/README.md) ·
[Evaluation summary](examples/readlater/results/summary.md) ·
[Evidence Tree](examples/readlater/results/evidence_tree.json)

The built-in score-bearing Skills are:

- **Spec Coverage** — requirement-level traceability.
- **Runtime Behavior** — build, health, and stateful probes; objective failures
  impose deterministic score caps.
- **API Contract** — frozen requests and deterministic response assertions.
- **Browser Flow** — action evidence is retained, while assertions lead scoring.
- **Regression Guard** — frozen replay probes and configurable protected anchors.
- **Code Quality** — semantic review of maintainability and correctness risks.
- **Convention Compliance** — project-specific conventions supplied as data.
- **Diff Hygiene** — change scope, debug leftovers, and unrelated artifacts.

Core and Observation are reported separately. Final defaults to an equal-weight
combination. If any selected score-bearing Skill is missing or invalid, Final is
`null`; the evaluator never averages over a partial denominator.

## Public examples

[`examples/todo`](examples/todo/README.md) demonstrates two sequential cases for
a made-up task manager: a basic implementation followed by priority filtering.
It includes SPECs, Case definitions, frozen plans, preregistered requirements,
runtime probes, API contracts, browser journeys, regression checks, and an
explicitly illustrative Evidence Tree. No evaluated rollout is included.

[`examples/readlater`](examples/readlater/README.md) is a separate, recorded
showcase of one fictional full-stack Case. It evaluates the included subject
implementation locally and contains no coding-agent rollout.

## Quick start

Install HarnessEval-C and run the Python test suite:

```bash
python -m pip install -e '.[test]'
pytest -q
```

Verify Todo's illustrative frozen artifact walkthrough:

```bash
python -m harnesseval_c verify-example examples/todo
```

Reproduce the recorded ReadLater showcase locally:

```bash
npm install --prefix examples/readlater
python examples/readlater/freeze_case.py
python examples/readlater/run_evaluation.py
```

## Design invariants

- Planning and preregistration depend on Case/SPEC/configuration, never rollout data.
- Frozen artifacts are digest-addressed and validated before use.
- Semantic judgment may lower deterministic scores, but cannot explain away
  build, boot, API, browser-assertion, or regression failures.
- Provider credentials come from environment variables and are excluded from
  semantic configuration digests and evidence.
- Agent commands and runtime commands use argument arrays, not a shell.
- Evidence Trees retain per-Skill metrics and raw deterministic checks.

## Adapting the framework

Create a Case whose `evaluation.required_skills` references the registry, place
all stack- or application-specific behavior in the preregistered components,
and configure commands/HTTP actions as data. Add a custom Skill by registering a
`Skill` with a stable ID, role, description, and evaluator function.

The public package intentionally avoids a universal rollout adapter. The small
`CommandAgentAdapter` accepts an explicit argv template so users can integrate a
CLI agent without adding provider assumptions to the evaluator.

## License

HarnessEval-C is released under the [Apache License 2.0](LICENSE). See
[PROVENANCE.md](PROVENANCE.md) for the public release boundary and implementation
provenance.
