# AGENTS.md — Temporal Coordinate Database

This file governs AI-assisted work across the repository. A child `AGENTS.md` may narrow these rules for its subtree, but MUST NOT contradict them.

## Project Identity

The primary project is the **Temporal Coordinate Database (TCDB/TCD)**.

Core thesis:

> A temporal object does not merely possess timestamps. It occupies coordinates in temporal space.

Do not rename or reframe the project around Event Geometry, computational spacetime, trajectory analysis, or any other research branch unless explicit architectural evidence and a deliberate project decision justify it.

## Current Architectural Authority

Read these before making architectural changes:

1. `README.md`
2. `ARCHITECTURE.md`
3. `docs/architecture/layer-0-foundation.md`
4. the nearest applicable `AGENTS.md`

Current established architecture:

```text
Layer 0  Foundation                ESTABLISHED
Layer 1  Persistence               ESTABLISHED
Layer 2  Transactions & Recovery   ESTABLISHED
Layer 3+                           RESEARCH / NOT YET CANONICAL
```

Lower layers define contracts higher layers may depend upon but MUST NOT silently redefine.

## Semantic Spine

Preserve these root distinctions unless evidence explicitly justifies revision:

```text
TemporalFrame
TemporalExtent
TemporalObject
TemporalRelation
Commit
```

Important non-collapses include:

```text
TemporalObject != TemporalExtent
TemporalExtent != TemporalFrame
ObjectIdentity != RelationIdentity
SemanticTime != CommitOrder
CommitOrder != WallClockTime
OccurrenceTime != KnowledgeTime
Canonical != Derived
Canonical != Indexed
Canonical != Analytical
RelationSelection != TemporalGeometry
StoragePrecision != KnowledgePrecision
Observation != UnderlyingOccurrence
```

`commit.sequence` is authoritative database-history order. Wall-clock commit metadata is descriptive.

## Information Authority

Always distinguish:

```text
Canonical
Derived
Indexed
Analytical
Experimental
```

Research artifacts and experimental implementations MUST NOT silently become canonical architecture or specification.

Any rebuildable structure must remain reconstructible from authoritative state and explicit derivation rules.

## Scientific Posture

TCDB is research-driven and falsifiable.

When exploring a new idea:

1. identify prior art;
2. state the hypothesis;
3. build the simplest correct reference model;
4. test adversarial cases;
5. compare against strong baselines;
6. record failures as evidence;
7. only then propose architectural promotion.

Separate clearly:

```text
ESTABLISHED
PRIOR ART
REPRODUCED
EXPERIMENTAL
PROPOSED
REFUTED
UNRESOLVED
CANONICAL
```

Do not make novelty claims from terminology alone.

## Current Focus

The project recently explored Event Geometry and Layer 3 indexing. Those results are preserved, but they are not the main architectural driver.

The next central TCDB problem is the **Temporal Coordinate Algebra / Query Algebra**: derive the smallest precise operations over named temporal frames, extents, objects, relations, and uncertainty, then connect those semantics to access planning.

Do not continue a paused research branch merely because files exist for it.

## Change Discipline

Before changing an established architectural rule:

- identify the existing rule;
- state what evidence makes it insufficient or wrong;
- describe compatibility consequences;
- distinguish semantic correction from implementation optimization;
- update dependent documents deliberately.

Implementation behavior that contradicts established semantics is an implementation defect, not an implicit model revision.

## Testing Doctrine

Prefer reference-vs-optimized differential testing.

For valid input `x`:

```text
Optimized(x) == Reference(x)
```

For index experiments:

```text
IndexedQuery(D, q) == ReferenceScan(D, q)
```

Performance results never override semantic correctness.

## Repository Organization

- `docs/architecture/` — established architectural contracts.
- `docs/research/` — non-canonical evidence, literature reviews, experiments, failures, and interpretations.
- `research/` — executable research prototypes only.
- `benchmarks/` — reproducible measurement harnesses.
- `tests/` — correctness and regression tests.
- `specs/` — specification-track work; stricter than research, not implicitly standardized.

## AI Interaction Rules

When entering a directory, read the nearest `AGENTS.md` before editing files in that subtree.

Prefer small, explicit changes over broad rewrites. Preserve provenance and failed experiments. Do not erase contradictory evidence simply to make the project appear internally consistent.

If architectural status is unclear, default to **research/proposal**, not canonicalization.

New meaningful directories SHOULD include their own `AGENTS.md` describing local purpose, authority, validation, and drift boundaries.