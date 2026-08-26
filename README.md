# HarnessEval-C

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
Coding Agent Rollout
    ↓
Skill Registry → selected Skills execute frozen checks
    ↓
Deterministic evidence + bounded semantic judgment
    ↓
Core / Observation → Final
    ↓
Evidence Tree → fail-closed validation
```

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
showcase run. It contains one fictional full-stack Case, an independently built
subject implementation, frozen inputs, real local HTTP and browser execution
evidence, per-Skill scores, and a validated Evidence Tree.

```bash
python -m pip install -e '.[test]'
python -m harnesseval_c verify-example examples/todo
pytest -q
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
