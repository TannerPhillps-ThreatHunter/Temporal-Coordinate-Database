# TCDB Persistence Algorithms

**Status:** Layer 1 Algorithm Registry  
**Layer:** Architecture Layer 1 — Persistence

## 1. Purpose

Layer 0 Root Algorithms define temporal semantics.

Layer 1 Persistence Algorithms define how canonical state is encoded, appended, sealed, verified, and interpreted as valid persistent database state.

These algorithms MUST preserve Layer 0 semantics and Layer 1 persistence invariants.

## 2. Algorithm Classes

Persistence algorithms use the same maturity vocabulary as Root Algorithms:

```text
PROPOSED
EXPERIMENTAL
REFERENCE
ADOPTED
CANONICAL
DEPRECATED
REJECTED
```

A reference algorithm defines correctness. An optimized implementation may change cost but not results.

## 3. PA0 — Encode Canonical Record

**Purpose:** Convert a canonical logical record into a deterministic versioned byte representation.

Conceptually:

```text
Canonical Record
      ↓
Validate semantic preconditions
      ↓
Encode record header
      ↓
Encode exact canonical payload
      ↓
Emit length-delimited bytes
```

Required properties:

- deterministic within a record-format version;
- exact temporal representation;
- explicit byte order;
- no compiler-native layout dependency;
- bounded lengths;
- stable type/version identification.

The inverse decoder MUST either reconstruct the same canonical value or reject the bytes as invalid/unsupported.

## 4. PA1 — Decode Canonical Record

**Purpose:** Parse persisted bytes into canonical logical state.

The reference decoder MUST perform validation before trusting variable-length payloads.

Conceptually:

```text
Read bounded header
      ↓
Validate type/version
      ↓
Validate declared length
      ↓
Decode payload
      ↓
Validate Layer 0 invariants
      ↓
Return canonical record
```

A decoder MUST fail closed on malformed required fields.

## 5. PA2 — Append Record to Open Segment

**Purpose:** Add a canonical Record to an OPEN Segment without modifying previously appended Record bytes.

Preconditions:

- target Segment state is OPEN;
- Record encoding is valid;
- `commit.sequence` does not violate segment append monotonicity;
- resulting Block/Segment bounds remain valid.

Postconditions:

- previous canonical bytes are unchanged;
- new Record is addressable within the Segment;
- commit-order metadata remains valid.

Durability acknowledgement is explicitly outside PA2 and belongs to Layer 2.

## 6. PA3 — Finalize Block

**Purpose:** Convert an in-progress Block into a bounded verifiable Block.

The algorithm conceptually:

1. freezes the block payload;
2. records parsing metadata;
3. computes the selected integrity checksum;
4. emits the block integrity trailer;
5. marks the block complete within the enclosing Segment.

A finalized Block is not necessarily transactionally durable; Layer 2 controls publication semantics.

## 7. PA4 — Seal Segment

**Purpose:** Transition an OPEN Segment into immutable SEALED form.

Conceptually:

```text
OPEN Segment
    ↓
Finalize last Block
    ↓
Validate record/commit bounds
    ↓
Compute segment summary
    ↓
Compute segment digest
    ↓
Write footer
    ↓
SEALED Segment
```

A successfully sealed Segment MUST contain enough metadata to verify its structure independently of query indexes.

Sealing does not by itself make the Segment a member of authoritative database state; Manifest publication controls membership.

## 8. PA5 — Verify Block

**Purpose:** Determine whether a Block is structurally and integrally valid.

Reference checks include:

- header validity;
- supported format version;
- bounded length validation;
- record-boundary validation;
- record-count consistency where encoded;
- checksum validation.

Output SHOULD distinguish at least:

```text
VALID
CORRUPT
UNSUPPORTED
```

rather than collapsing all failures into one generic error.

## 9. PA6 — Verify Segment

**Purpose:** Validate an entire Segment without relying on indexes.

Reference process:

```text
Validate segment header
      ↓
Verify every Block
      ↓
Validate commit monotonicity
      ↓
Validate summary/footer metadata
      ↓
Validate segment digest
      ↓
Return verification result
```

The verifier SHOULD identify the first known corruption location and MAY continue in diagnostic mode to enumerate additional failures.

## 10. PA7 — Verify Manifest

**Purpose:** Determine whether a Manifest describes a structurally valid database generation.

Checks include:

- database identity consistency;
- manifest-format support;
- generation validity;
- unique Segment identities;
- legal Segment states;
- declared Segment metadata consistency;
- referenced canonical structures exist;
- format compatibility.

This algorithm does not decide crash-recovery precedence between competing partially published generations; Layer 2 will define that.

## 11. PA8 — Verify Persistent Database

**Purpose:** Perform an offline or quiescent integrity traversal of authoritative TCDB persistence.

Reference traversal:

```text
Catalog
  ↓
Manifest
  ↓
Referenced Segments
  ↓
Blocks
  ↓
Records
  ↓
Layer 0 semantic validation
```

The verifier MUST NOT require rebuildable query indexes to establish canonical database validity.

Expected output should eventually support machine-readable diagnostics such as:

```text
VALID
CORRUPT
UNSUPPORTED_FORMAT
MISSING_CANONICAL_STRUCTURE
SEMANTIC_INVARIANT_VIOLATION
```

## 12. PA9 — Enumerate Orphan Structures

**Purpose:** Identify physical files/structures that exist in the database storage location but are not members of the authoritative Manifest generation.

Output is diagnostic only.

An orphan MUST NOT be promoted into authoritative state merely because it appears structurally valid.

Recovery or salvage decisions belong to later layers/tooling.

## 13. Integrity Algorithm Selection

Layer 1 requires:

- bounded local corruption detection at Block scope;
- Segment-level integrity verification.

The concrete checksum/digest algorithms remain **PROPOSED** until benchmarked and reviewed.

Selection criteria include:

- hardware acceleration;
- throughput;
- error-detection properties;
- collision behavior appropriate to the role;
- implementation maturity;
- cross-platform availability;
- long-term specification stability.

The Block checksum and Segment digest MAY use different algorithms because they serve different operational purposes.

## 14. Algorithm Testing Doctrine

Every optimized persistence algorithm MUST be testable against a reference implementation.

Required future test classes include:

```text
round-trip encoding
boundary lengths
maximum/minimum time values
unknown record versions
corrupt headers
corrupt lengths
single-bit corruption
truncated Blocks
truncated Segments
duplicate Segment identities
commit-order violations
manifest/reference mismatch
hostile allocation lengths
cross-platform byte stability
```

Crash-injection testing is intentionally deferred to Layer 2, where durability transition semantics are defined.
