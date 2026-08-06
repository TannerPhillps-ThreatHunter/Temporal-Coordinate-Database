# AGENTS.md — Layer 3 Research

Inherits `research/AGENTS.md` and repository-root `AGENTS.md`.

## Purpose

This subtree investigates **Coordinate Access & Indexing** before Layer 3 is canonized.

## Correctness Oracle

`reference.py` defines the research correctness boundary. Candidate indexes MUST agree with the reference evaluator for supported semantics.

Primary invariant:

```text
IndexedQuery(D, q) == ReferenceScan(D, q)
```

Candidate generation may over-select but MUST NOT lose valid results.

## Existing Baselines

Preserve strong baselines and prior-art provenance:

```text
StartSortedIndex
EndSortedIndex
AdaptiveEndpointIndex
StaticEndpointRangeTree
HINT^m reproduction
```

Do not claim a new TCDB index is useful merely because it beats full scan or a single endpoint index. HINT^m is the current strongest interval-index prior-art comparator in this subtree.

## Semantic Constraints

Index design must respect TCDB semantics, including explicit point extents, boundary-policy experiments, uncertainty when introduced, named frames, and canonical-vs-indexed separation.

Physical structures are rebuildable. They do not become semantic truth.

## Status

R3.5c and later Layer 3 work are currently paused while the project returns focus to the core Temporal Coordinate Algebra. Resume only deliberately.

If resumed, keep benchmark dimensions separate:

```text
correctness
result cardinality
unique candidates
physical reference scans
predicate comparisons
storage amplification
build cost
update/merge cost
memory/disk footprint
```