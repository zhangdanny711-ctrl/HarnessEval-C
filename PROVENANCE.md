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

This repository is released under the Apache License 2.0 included in `LICENSE`.
The fictional Todo walkthrough and ReadLater showcase—including their SPECs,
scaffolds, frozen evaluation inputs, and public example evidence—were created
solely for this repository and do not migrate private benchmark material.
