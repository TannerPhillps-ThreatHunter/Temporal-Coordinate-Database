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

Layer 0 deliberately does not define page formats, file formats, WAL encoding, index algorithms, query syntax, wire encoding, authentication mechanisms, replication algorithms, consensus, sharding, or deployment topology.

## Architectural Authority

```text
Layer 0 Invariants
      ↓
TCDB-MODEL
      ↓
TCDP
      ↓
TCDP-QUIC
      ↓
Implementation
```

Implementation behavior that contradicts an accepted semantic invariant is an implementation defect, not an implicit model change.
