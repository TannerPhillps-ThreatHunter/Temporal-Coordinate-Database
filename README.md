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

TCDB is developed specification-first. Implementations conform to the semantic model and protocol specifications rather than implicitly defining them.

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

Layer 0 is the current architectural focus.

## Layer 0

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

See:

- `ARCHITECTURE.md`
- `docs/architecture/layer-0-foundation.md`
- `docs/architecture/root-algorithms.md`

## Specification Tracks

- **TCDB-MODEL** — Temporal Coordinate Data Model
- **TCDP** — Temporal Coordinate Database Protocol
- **TCDP-QUIC** — Temporal Coordinate Database Protocol over QUIC

TCDP/1 is intended to be QUIC-native.

## Status

TCDB is transitioning from exploratory research and proof-of-concept work into formal architecture and specification development.
