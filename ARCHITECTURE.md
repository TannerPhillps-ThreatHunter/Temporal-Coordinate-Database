# TCDB Architecture

TCDB architecture is layered by **authority**, not merely implementation order.

```text
Layer 0  Foundation
   ↓
Layer 1  Persistence
   ↓
Layer 2  Transactions & Recovery
   ↓
Layer 3  Coordinate Access & Indexing
   ↓
Layer 4  Query Algebra & Execution
   ↓
Layer 5  Protocol & Client Interface
   ↓
Layer 6  Security & Operability
   ↓
Layer 7  Availability & Distribution
```

Lower layers define contracts higher layers may depend upon but MUST NOT silently redefine.

## Layer 0 — Foundation

Layer 0 defines:

1. system identity;
2. Root Models;
3. Root Algorithms;
4. semantic invariants;
5. database-history invariants;
6. information authority boundaries;
7. dependency rules for later layers.

Primary documents:

- `docs/architecture/layer-0-foundation.md`
- `docs/architecture/root-algorithms.md`

## Layer 1 — Persistence

Layer 1 defines the authoritative persistent substrate required to preserve Layer 0 semantics.

Its initial physical models are:

```text
PersistentDatabase
├── Catalog
├── Manifest
├── Segment
│   └── Block
│       └── Record
└── Rebuildable Structures
```

Key Layer 1 doctrines:

- canonical persistence is append-oriented;
- published canonical Records are not mutated in place;
- OPEN Segments may receive appends;
- SEALED Segments are immutable;
- the Manifest defines physical database membership;
- directory contents alone are never authoritative;
- canonical state is distinct from rebuildable indexes and projections;
- serialization is versioned, deterministic, bounded, and platform-independent;
- canonical time is exact on disk;
- local corruption must be detectable;
- storage-format versioning is independent of protocol versioning.

Layer 1 defines valid persistent states. Layer 2 will define how state transitions become transactionally durable and recoverable.

Primary documents:

- `docs/architecture/layer-1-persistence.md`
- `docs/architecture/persistence-algorithms.md`

## Current Architecture Boundary

```text
Layer 0  Foundation                ESTABLISHED
Layer 1  Persistence               ESTABLISHED
Layer 2  Transactions & Recovery   NEXT
Layer 3+                           UNDEFINED / RESEARCH
```

Layer 2 will own transaction boundaries, WAL, durability acknowledgement, fsync ordering, checkpoints, manifest publication, and crash recovery.

## Architectural Authority

```text
Layer 0 Invariants
      ↓
Layer 1 Persistence Contract
      ↓
Higher Architecture Layers
      ↓
TCDB-MODEL / Protocol Specifications
      ↓
Implementation
```

No implementation optimization may silently redefine a lower-layer invariant.

Implementation behavior that contradicts an accepted semantic or persistence invariant is an implementation defect, not an implicit architecture change.
