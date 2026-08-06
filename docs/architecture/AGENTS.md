# AGENTS.md — Architecture

Inherits `docs/AGENTS.md` and repository-root `AGENTS.md`.

## Authority

Files in this directory describe **established TCDB architecture**. They are more authoritative than research prototypes, benchmarks, or research write-ups.

Do not introduce a new architectural primitive, invariant, layer contract, persistence rule, transaction rule, or algorithm family here without evidence and an explicit promotion decision.

## Existing Layer Status

```text
Layer 0  Foundation                ESTABLISHED
Layer 1  Persistence               ESTABLISHED
Layer 2  Transactions & Recovery   ESTABLISHED
Layer 3+                           NOT YET CANONICAL
```

Layer 0 constrains every later layer.

## Required Discipline

Before editing an established contract:

1. identify the exact current invariant;
2. identify evidence or a defect motivating change;
3. describe semantic and compatibility consequences;
4. update dependent architecture documents deliberately;
5. add or update tests/research evidence where applicable.

Optimization does not authorize semantic change.

## Root Algorithms

Maintain the distinction:

```text
Reference Algorithm -> defines correctness
Optimized Algorithm -> improves cost while preserving semantics
```

Root algorithms are semantic. B-trees, LSM compaction, compression, consensus, transport congestion control, and similar implementation algorithms do not become Layer 0 merely because TCDB uses them.

## Prohibited Drift

Do not:

- canonize Event Geometry or computational spacetime from analogy alone;
- collapse semantic time into commit order;
- make derived/indexed/analytical state authoritative by convenience;
- force total ordering where the model permits partial order or incomparability;
- replace exact production-time semantics with floating point;
- define Layer 3 based only on one benchmark or one index family.