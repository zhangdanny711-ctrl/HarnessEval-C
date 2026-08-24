# Provenance and release boundary

This public tree is an independent, compact implementation of the HarnessEval-C
design. It was created specifically for a personal public release. Application
semantics, benchmarks, snapshots, reports, endpoints, fixtures, and experiment
evidence from the private engineering workspace were not migrated.

The high-level idea of combining skill routing, frozen evaluation inputs,
evidence collection, and hierarchical scoring was informed by the publicly
described HarnessEval family of projects. Historical private-tree annotations
identified serialization, planning, aggregation/scoring, Spec Coverage, and
validation as the small areas most directly aligned with HarnessEval-W. During
packaging, the inspected HarnessEval-W README mentioned Apache-2.0, but a
corresponding root license file could not be confirmed. None of those source
sections were carried into this tree: `io.py`, `planner.py`, `scoring.py`,
`skills/spec_coverage.py`, and `validation.py` were independently rewritten
around the required HarnessEval-C behavior.

This note is attribution and provenance, not a legal determination. Before a
LICENSE is added, the owner should confirm authorship of all remaining files and
choose the intended terms. The fictional Todo text and representative JSON were
created solely for this repository.
