# Temporal Coordinate Database

**Temporal Coordinate Database (TCDB)** is a coordinate-native temporal database architecture in which semantically distinct forms of time are modeled as named temporal frames, temporal extent is represented canonically in endpoint space, and temporal relations are derived from coordinate geometry.

> A temporal object does not merely possess timestamps. It occupies coordinates in temporal space.

For a determinate temporal extent:

```text
P = (start, end)
```

subject to:

```text
start <= end
```

TCDB is developed specification-first. Implementations conform to the semantic model and architecture rather than implicitly defining them.

## Architecture

```text
Layer 0  Foundation
Layer 1  Persistence
Layer 2  Transactions & Recovery
Layer 3  Coordinate Access & Indexing
Layer 4  Query Algebra & Execution
Layer 5  Protocol & Client Interface
Layer 6  Security & Operability
Layer 7  Availability & Distribution
```

Current state:

```text
Layer 0  Foundation                ESTABLISHED
Layer 1  Persistence               ESTABLISHED
Layer 2  Transactions & Recovery   NEXT
Layer 3+                           UNDEFINED / RESEARCH
```

## Layer 0 — Foundation

```text
Root Models
├── TemporalFrame
├── TemporalExtent
├── TemporalObject
├── TemporalRelation
└── Commit

Root Algorithms
├── Canonicalize
├── Relate
├── Evaluate Uncertainty
├── Order
├── Displace
└── Project

Information Doctrine
├── Canonical
├── Derived
├── Indexed
└── Analytical
```

## Layer 1 — Persistence

```text
PersistentDatabase
├── Catalog
├── Manifest
├── Segment
│   └── Block
│       └── Record
└── Rebuildable Structures
```

Layer 1 establishes an append-oriented canonical persistence model in which published Records are not modified in place, sealed Segments are immutable, the Manifest defines authoritative physical membership, and rebuildable indexes never become the sole source of semantic truth.

See:

- `ARCHITECTURE.md`
- `docs/architecture/layer-0-foundation.md`
- `docs/architecture/root-algorithms.md`
- `docs/architecture/layer-1-persistence.md`
- `docs/architecture/persistence-algorithms.md`

## Specification Tracks

- **TCDB-MODEL** — Temporal Coordinate Data Model
- **TCDP** — Temporal Coordinate Database Protocol
- **TCDP-QUIC** — Temporal Coordinate Database Protocol over QUIC

TCDP/1 is intended to be QUIC-native.

## Status

TCDB has transitioned from exploratory research and proof-of-concept work into formal architecture and specification development.

The next architecture target is **Layer 2 — Transactions & Recovery**: transaction boundaries, write-ahead logging, commit acknowledgement, fsync ordering, checkpoints, manifest publication, and deterministic crash recovery.
