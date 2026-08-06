# AGENTS.md — Executable Research

Inherits repository-root `AGENTS.md`.

## Purpose

`research/` contains executable prototypes used to test TCDB hypotheses. Code here is not production code and does not define canonical semantics by itself.

## Rules

- Prefer obvious reference implementations before optimization.
- Keep experiments deterministic where practical: fixed seeds, explicit parameters, reproducible datasets.
- Separate reference semantics from candidate access methods or analytical projections.
- Preserve experimental code that produced meaningful negative results when it informs later decisions.
- Do not silently convert research-specific assumptions into project-wide defaults.

## Correctness First

Where a reference implementation exists, optimized/candidate methods must be differentially tested against it.

Use explicit assertions for invariants discovered during research.

## Promotion Boundary

A successful experiment should first update `docs/research/` with evidence. Promotion into `docs/architecture/` or `specs/` requires a separate explicit decision.

## Current Focus

Current executable branches include Layer 3 indexing and Event Geometry. They are subordinate to the core TCDB model. The next central architectural research direction is Temporal Coordinate / Query Algebra, not automatic continuation of whichever prototype has the highest numbered next experiment.