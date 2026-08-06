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

Primary documents:

- `docs/architecture/layer-1-persistence.md`
- `docs/architecture/persistence-algorithms.md`

## Layer 2 — Transactions & Recovery

Layer 2 defines safe state transitions between Layer 1 persistent states.

```text
Transaction
├── transaction.id
├── snapshot.sequence
├── staged mutations
└── state

Commit
├── transaction.id
└── commit.sequence

WAL
├── ordered LSNs
├── TX_MUTATION
├── TX_COMMIT
└── CHECKPOINT
```

Key Layer 2 doctrines:

- the default canonical transaction contract targets strict serializability;
- `commit.sequence` defines committed database-history order;
- `commit.sequence`, WAL LSN, wall-clock time, and TemporalFrames are distinct;
- WAL durability precedes authoritative canonical materialization;
- the durable WAL commit record establishes commit truth;
- `COMMIT_OK` acknowledges an already-established durable commit;
- client uncertainty after connection loss does not create database uncertainty;
- committed visibility is independent of Segment materialization lag;
- uncommitted mutations never become authoritative canonical state;
- recovery is redo-only for durable committed transactions;
- the applied frontier identifies WAL history already represented in durable canonical state;
- checkpoints advance recovery state but do not create commits;
- Manifest generation publication must resolve after failure to complete old or new state, never a torn hybrid;
- recovery must be deterministic and idempotent;
- WAL required for acknowledged committed history must never be truncated prematurely;
- every transition boundary must be testable with deterministic failure injection.

Primary documents:

- `docs/architecture/layer-2-transactions-recovery.md`
- `docs/architecture/transaction-recovery-algorithms.md`

## Current Architecture Boundary

```text
Layer 0  Foundation                ESTABLISHED
Layer 1  Persistence               ESTABLISHED
Layer 2  Transactions & Recovery   ESTABLISHED
Layer 3  Coordinate Access         NEXT
Layer 4+                           UNDEFINED / RESEARCH
```

Layer 3 will define how canonical committed temporal state is indexed and accessed efficiently without allowing indexes to become a source of semantic or commit truth.

## Architectural Authority

```text
Layer 0 Semantic Invariants
      ↓
Layer 1 Persistence Contract
      ↓
Layer 2 Transaction & Recovery Contract
      ↓
Higher Architecture Layers
      ↓
TCDB-MODEL / Protocol Specifications
      ↓
Implementation
```

No implementation optimization may silently redefine a lower-layer invariant.

Implementation behavior that contradicts an accepted semantic, persistence, transaction, or recovery invariant is an implementation defect, not an implicit architecture change.
