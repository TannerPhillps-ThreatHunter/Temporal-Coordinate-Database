# Architecture Layer 1 — Persistence

**Status:** Canonical Architecture  
**System:** Temporal Coordinate Database (TCDB)  
**Layer:** 1  
**Depends On:** Architecture Layer 0

---

# 1. Purpose

Layer 1 defines how authoritative TCDB state is represented as persistent structures.

Layer 1 answers:

> What must exist on durable storage for a TCDB database to preserve its canonical state without depending on indexes, analytical projections, or process memory?

Layer 1 defines the steady-state persistence model and integrity contract.

It deliberately does **not** define:

- transaction isolation;
- WAL record semantics;
- fsync ordering;
- checkpoints;
- crash-recovery procedure;
- replication;
- query indexes;
- query execution;
- backup policy;
- encryption policy.

Those belong to later layers.

---

# 2. Persistence Thesis

TCDB persistence is **canonical-first, append-oriented, and rebuildability-aware**.

The central rule is:

```text
Canonical State must survive.
Derived State may be recomputed.
Indexed State may be rebuilt.
Analytical State may be discarded and regenerated.
```

Layer 1 therefore persists the smallest authoritative substrate required to reconstruct database meaning.

---

# 3. Persistence Models

Layer 1 introduces five physical models:

```text
PersistentDatabase
├── Catalog
├── Manifest
├── Segment
│   └── Block
│       └── Record
└── Rebuildable Structures
```

Only the first four participate in the authoritative persistence boundary.

---

# 4. PersistentDatabase

A `PersistentDatabase` is the durable physical realization of one logical TCDB database.

Conceptually:

```text
PersistentDatabase
├── database identity
├── format identity
├── catalog state
├── manifest state
└── canonical segments
```

## Invariant P1 — Stable Database Identity

A persistent TCDB database MUST possess an identity independent of filesystem path, host name, process identity, or deployment location.

Moving the database MUST NOT create a new logical database identity.

---

# 5. Catalog

The `Catalog` contains authoritative database metadata required to interpret canonical records.

Initial catalog responsibilities include:

- database identity;
- storage-format version;
- TemporalFrame definitions;
- required semantic/schema metadata;
- feature declarations required to decode canonical state.

The catalog is **canonical database metadata**.

It is not an analytical cache.

## Invariant P2 — Self-Describing Interpretation

Persistent canonical data MUST NOT require undocumented process-local assumptions in order to be interpreted.

All information required to distinguish storage format and required semantic features MUST be recoverable from persisted metadata.

---

# 6. Record

A `Record` is the smallest logical unit of canonical persisted information.

Layer 1 does not yet freeze the byte encoding, but every encoded record MUST conceptually provide enough information to determine:

```text
record type
record format version
commit sequence
payload length
payload
```

Additional fields MAY be added by the storage-format specification.

A Record may represent canonical information such as:

- TemporalObject state;
- TemporalFrame/catalog state;
- explicit canonical relation state;
- future canonical record classes defined by later specifications.

Layer 1 does not define logical update/delete semantics. Later layers may introduce new immutable record types such as revisions, retractions, or tombstones.

## Invariant P3 — No In-Place Canonical Record Mutation

Once a canonical Record is published as persistent database state, its bytes MUST NOT be modified in place to express a later logical change.

A later logical change is represented by additional canonical state.

This preserves lineage and makes corruption/recovery reasoning tractable.

---

# 7. Block

A `Block` is the bounded integrity and I/O unit within a Segment.

Conceptually:

```text
Block
├── header
├── one or more Records
└── integrity trailer
```

A block SHOULD include sufficient metadata to validate:

- block identity or ordinal;
- format version;
- encoded length;
- record count or equivalent parsing boundary;
- integrity checksum.

## Invariant P4 — Bounded Parsing

Corrupt or hostile persisted lengths MUST NOT cause an implementation to perform unbounded allocation or read beyond declared physical boundaries.

Every variable-length structure MUST be bounded by an enclosing validated length.

## Invariant P5 — Local Corruption Detection

A reader MUST be able to detect corruption at a bounded unit smaller than or equal to a Segment.

The initial design target is block-level integrity verification.

---

# 8. Segment

A `Segment` is an append-oriented collection of Blocks.

Segments exist in two physical states:

```text
OPEN
SEALED
```

## 8.1 Open Segment

An OPEN segment is eligible to receive additional canonical Records.

Its physical contents are append-only.

## 8.2 Sealed Segment

A SEALED segment is immutable.

A sealed segment conceptually contains:

```text
Segment
├── segment identity
├── storage-format version
├── database identity
├── Blocks
└── footer
    ├── minimum commit sequence
    ├── maximum commit sequence
    ├── record count
    ├── byte length
    └── segment integrity digest
```

The exact encoding and algorithms remain a later storage-format decision.

## Invariant P6 — Sealed Segment Immutability

After successful publication as SEALED, a Segment MUST NOT be modified.

Replacement, compaction, repair, or migration MUST create new physical structures rather than rewriting an existing sealed Segment in place.

## Invariant P7 — Commit Monotonicity Within Append Order

Canonical Records appended to the persistence stream MUST appear in non-decreasing `commit.sequence` order.

Layer 2 will define the transactional rules that establish and durably publish those commits.

---

# 9. Manifest

The `Manifest` declares which physical canonical structures constitute the current persistent database state.

Conceptually:

```text
Manifest
├── database identity
├── manifest generation
├── storage-format version
├── catalog reference/state
└── segment entries
    ├── segment identity
    ├── state
    ├── commit range
    ├── byte length
    └── integrity metadata
```

The Manifest is authoritative **physical database metadata**.

A filesystem directory listing is not authoritative database state.

## Invariant P8 — Directory Contents Are Not Membership

The presence of a file in the database directory MUST NOT by itself make that file part of the database.

Only structures referenced through valid database metadata belong to authoritative state.

This distinction permits safe handling of:

- partially built segments;
- orphaned files;
- interrupted compaction;
- temporary files;
- recovery artifacts.

## Invariant P9 — Manifest Generations Are Monotonic

Manifest state MUST carry a monotonically advancing generation or equivalent ordered identity.

Layer 2 will define atomic publication and recovery semantics for manifest transitions.

---

# 10. Canonical vs Rebuildable Persistence

Layer 0 established:

```text
Canonical != Derived != Indexed != Analytical
```

Layer 1 turns that into a physical rule.

## Canonical Persistence Plane

Must be protected as authoritative state:

```text
Catalog
Manifest
Canonical Records
Canonical Segments
Commit linkage
Required provenance
```

## Rebuildable Persistence Plane

May exist on disk but MUST NOT become the only source of semantic truth:

```text
endpoint indexes
duration indexes
relation indexes
vector projections
trajectory caches
planner statistics
analytical summaries
```

## Invariant P10 — Index Loss Is Not Data Loss

Loss of every structure designated rebuildable MUST still leave enough canonical state to reconstruct correct TCDB semantics.

---

# 11. Serialization Contract

Layer 1 does not select the final binary encoding, but establishes requirements for it.

Canonical serialization MUST be:

1. versioned;
2. deterministic within a format version;
3. independent of compiler-native struct layout;
4. explicit about byte order;
5. bounded and length-delimited;
6. capable of rejecting unsupported required features;
7. stable enough for offline verification tools;
8. exact for canonical temporal values.

## Invariant P11 — No Native Memory Images

Canonical persisted records MUST NOT consist of raw compiler/ABI-dependent object memory images.

## Invariant P12 — Exact Time On Disk

Canonical temporal values MUST use the exact production time representation required by Layer 0.

Floating-point temporal coordinates are prohibited in canonical persistent state.

---

# 12. Integrity Model

Layer 1 requires layered integrity verification.

```text
Record parsing bounds
      ↓
Block checksum
      ↓
Segment digest
      ↓
Manifest metadata
      ↓
Database verification
```

The exact checksum and digest algorithms are deliberately not frozen here.

They MUST be selected through benchmark, hardware-support, collision/error-detection, and operational analysis.

## Invariant P13 — Silent Corruption Is Unacceptable

When stored bytes fail a required integrity check, TCDB MUST surface corruption rather than interpreting unchecked data as authoritative state.

Repair policy belongs to later operational architecture; detection belongs here.

---

# 13. Format Versioning

Persistent structures MUST contain explicit format-version information.

TCDB distinguishes at least:

```text
storage format version
record format version
catalog/schema version
protocol version
```

These versions are not assumed to advance together.

## Invariant P14 — Storage Format Is Not Protocol Version

A change to TCDP MUST NOT implicitly change the on-disk storage format, and a storage migration MUST NOT implicitly redefine TCDP semantics.

---

# 14. Steady-State Physical Model

The initial conceptual layout is:

```text
TCDB Database
│
├── Catalog
├── Manifest(generation=N)
│
├── Segments
│   ├── segment-000001  SEALED
│   ├── segment-000002  SEALED
│   ├── segment-000003  SEALED
│   └── segment-000004  OPEN
│
└── Rebuildable
    ├── indexes/
    ├── projections/
    └── statistics/
```

This diagram is conceptual. Exact filenames and directory layout are not yet normative.

---

# 15. Layer Boundary With Layer 2

Layer 1 defines **valid persistent states**.

Layer 2 will define **safe state transitions**.

Layer 2 is responsible for questions such as:

- When is a commit acknowledged?
- What must be written before `COMMIT_OK`?
- What is WAL-authoritative?
- Which fsync happens first?
- How is an OPEN Segment recovered after process death?
- How is a Manifest generation atomically published?
- How are checkpoints created?
- What state is recovered after torn or partial writes?

Therefore:

```text
Layer 1: What durable state looks like.
Layer 2: How durable state changes safely.
```

---

# 16. Layer 1 Exit Criteria

Layer 1 is architecturally established when:

- [x] canonical persistence boundary is defined;
- [x] PersistentDatabase is defined;
- [x] Catalog is defined;
- [x] Record is defined;
- [x] Block is defined;
- [x] Segment lifecycle is defined;
- [x] Manifest authority is defined;
- [x] canonical/rebuildable separation is physicalized;
- [x] serialization requirements are established;
- [x] integrity requirements are established;
- [x] storage/protocol version independence is established;
- [x] Layer 1 / Layer 2 responsibility boundary is explicit.

The next architecture layer may now define transactions, WAL, durability acknowledgement, checkpoints, and crash recovery without redefining the persistence substrate.
