# Architecture Layer 2 — Transactions & Recovery

**Status:** Canonical Architecture  
**System:** Temporal Coordinate Database (TCDB)  
**Layer:** 2  
**Depends On:** Architecture Layers 0–1

---

# 1. Purpose

Layer 2 defines how TCDB moves safely between the valid persistent states established by Layer 1.

Layer 2 answers:

> How does TCDB establish atomic commits, durable database history, transaction visibility, and deterministic crash recovery when processes, machines, storage operations, or client connections fail at arbitrary points?

Layer 2 defines:

- Transaction identity and lifecycle;
- transaction visibility and serialization;
- commit sequencing;
- Write-Ahead Log (WAL) authority;
- the durable commit point;
- commit acknowledgement semantics;
- materialization into Layer 1 Segments;
- checkpoint semantics;
- Manifest publication requirements;
- crash recovery;
- ambiguous client outcomes;
- WAL retention and truncation constraints;
- deterministic failure testing requirements.

Layer 2 deliberately does **not** define:

- final WAL byte encoding;
- final checksum or digest algorithms;
- query indexes;
- query language;
- network protocol encoding;
- replication;
- consensus;
- backup retention policy;
- encryption policy;
- distributed transactions.

---

# 2. Transaction and Recovery Thesis

TCDB uses an **append-oriented, WAL-first, redo-only recovery architecture**.

The central rules are:

```text
Commit is established before acknowledgement.
WAL durability precedes canonical materialization.
Uncommitted mutations never become authoritative state.
Committed state is visible independently of Segment materialization.
Recovery redoes committed work; it does not infer commit from partial files.
```

Layer 1 defines what valid persistent state looks like.

Layer 2 defines how that state changes safely.

---

# 3. Layer 2 Models

Layer 2 introduces six database-mechanics models:

```text
Transaction
Snapshot
Commit
WAL
Checkpoint
Recovery
```

These models belong to database mechanics and MUST NOT be confused with semantic TemporalFrames.

---

# 4. Transaction

A `Transaction` is an identified unit of atomic database work.

Conceptually:

```text
Transaction
├── transaction.id
├── snapshot.sequence
├── state
├── ordered mutations
└── optional metadata
```

The exact transaction identifier encoding is not frozen by Layer 2, but the identifier MUST be stable enough to support commit-status resolution and retry safety.

## 4.1 Transaction States

The logical lifecycle is:

```text
ACTIVE
   │
   ├── ABORT ───────────────→ ABORTED
   │
   └── COMMIT REQUEST
            │
            ▼
        COMMITTING
            │
            ├── failure before durable commit ─→ ABORTED / NOT COMMITTED
            │
            └── durable commit record ─────────→ COMMITTED
```

Client acknowledgement is deliberately not a transaction state.

## Invariant T2.1 — Atomicity

For every transaction, either all canonical mutations belonging to that transaction are part of committed database history or none are.

Partial transaction visibility is prohibited.

## Invariant T2.2 — Stable Transaction Identity

Retry, recovery, audit, and commit-status mechanisms MUST be able to refer to the same logical transaction without depending on connection identity, process identity, or wall-clock time.

---

# 5. Snapshot and Visibility

Every transaction executes against a defined committed database snapshot.

Conceptually:

```text
snapshot.sequence = highest committed sequence visible at snapshot acquisition
```

A transaction sees:

1. committed canonical state permitted by its snapshot;
2. its own staged mutations where transaction semantics require read-your-writes behavior.

A transaction MUST NOT observe another transaction's uncommitted mutations.

## Invariant T2.3 — Commit-Based Visibility

Canonical visibility is determined by transaction/commit semantics, not by whether committed bytes have already been copied from WAL into Layer 1 Segments.

A committed transaction may therefore be logically visible while its canonical records are still awaiting Segment materialization.

## Invariant T2.4 — Real-Time Commit Observation

If transaction A receives `COMMIT_OK` before transaction B begins, transaction B's normal current-state snapshot MUST include A.

---

# 6. Serialization Contract

The initial TCDB transaction contract targets **strict serializability** for canonical database operations.

Committed transactions MUST be explainable as a single serial history ordered by their successful commit serialization.

For overlapping transactions, implementation algorithms MAY use serialized execution, locking, optimistic validation, MVCC, or another proven mechanism, provided the externally observable result satisfies the contract.

The initial single-node implementation MAY deliberately use a simpler serialized writer path before introducing higher-concurrency algorithms.

## Invariant T2.5 — Commit Order Defines Committed Serialization Order

For committed transactions A and B:

```text
A.commit.sequence < B.commit.sequence
```

establishes A before B in authoritative committed database history.

Weaker isolation levels MAY be introduced only as explicit opt-in semantics in a later specification. They MUST NOT silently weaken the default canonical contract.

---

# 7. Commit

Layer 0 established `Commit` as the authoritative database-history primitive.

Layer 2 operationalizes it.

Conceptually:

```text
Commit
├── transaction.id
├── commit.sequence
├── optional committed_at
└── commit metadata
```

`commit.sequence` is authoritative.

`committed_at`, when recorded, is descriptive wall-clock metadata.

## 7.1 Commit Sequence

Each committed transaction receives a unique monotonically increasing `commit.sequence` within one logical database history.

Layer 2 does NOT require commit sequences to be mathematically contiguous.

Consumers MUST NOT infer missing transactions solely from sequence gaps.

## Invariant T2.6 — Commit Sequence Uniqueness

No two committed transactions in the same logical database history may share the same `commit.sequence`.

## Invariant T2.7 — Commit Sequence Is Not Time

```text
commit.sequence != TemporalFrame
commit.sequence != wall-clock timestamp
commit.sequence != WAL position
```

These coordinate different domains and MUST remain distinguishable.

---

# 8. CommitRecord

A committed transaction produces a canonical `CommitRecord` representing its place in database history.

Conceptually:

```text
CommitRecord
├── transaction.id
├── commit.sequence
├── mutation count / commit metadata
└── optional committed_at
```

The final storage-format fields are not frozen here.

The CommitRecord permits commit history to remain queryable after old WAL has been safely retired.

A rebuildable transaction-status index MAY accelerate lookup, but the index is not authoritative.

## Invariant T2.8 — Commit Status Is Recoverable

Given a transaction identifier whose outcome has been durably established and retained under database policy, TCDB MUST be able to determine whether that transaction committed without relying solely on a live client connection.

---

# 9. Write-Ahead Log

The WAL is the durable transition log between Layer 1 persistent states.

Conceptually:

```text
WAL
├── WAL segments
│   ├── WAL records
│   ├── integrity metadata
│   └── ordered log positions
└── durable frontier
```

WAL is authoritative for recovery of committed state that has not yet been fully materialized and checkpointed into Layer 1 canonical Segments.

WAL is **not** a TemporalFrame and WAL position is **not** semantic time.

---

# 10. WAL Position

Every WAL record occupies an ordered physical/logical position, referred to generically as an LSN (Log Sequence Number) in this architecture.

Conceptually:

```text
LSN = ordered WAL position
```

The final representation MAY be a byte offset, `(wal_segment, offset)`, or another monotonic address.

## Invariant T2.9 — LSN Is Distinct From Commit Sequence

```text
LSN != commit.sequence
```

Multiple WAL records may belong to one transaction and therefore precede the transaction's durable commit record.

---

# 11. WAL Record Classes

Layer 2 initially requires enough WAL semantics to represent:

```text
TX_MUTATION
TX_COMMIT
CHECKPOINT
```

Additional record classes MAY include:

```text
TX_ABORT
CATALOG_CHANGE
FORMAT_CONTROL
```

if later implementation/specification evidence requires them.

Each WAL record MUST be versioned, bounded, integrity-checkable, and associated with an ordered LSN.

---

# 12. WAL-First Rule

The fundamental write-ahead requirement is:

> Information necessary to recover a canonical mutation MUST reach the configured durable WAL boundary before that mutation is acknowledged as committed or made authoritatively dependent on unsynced canonical storage.

Canonical Segment materialization may lag durable WAL.

## Invariant T2.10 — Write Ahead of Authoritative Data Publication

TCDB MUST NOT require post-crash survival of a canonical data write whose recovery information was never durably established in WAL.

Physical temporary bytes MAY be written early, but they MUST NOT become authoritative database membership merely because they exist on disk.

Layer 1 Manifest authority continues to apply.

---

# 13. Commit Protocol

The conceptual synchronous commit procedure is:

```text
1. Validate transaction against serialization rules.
2. Assign commit.sequence.
3. Produce deterministic canonical mutation encodings using that commit sequence.
4. Append TX_MUTATION WAL records.
5. Append canonical commit metadata / TX_COMMIT WAL record.
6. Advance WAL to the configured durable boundary.
7. Mark transaction COMMITTED in database history.
8. Make the committed transaction visible.
9. Return COMMIT_OK to the client.
10. Materialize committed records into Layer 1 Segments asynchronously or synchronously as policy allows.
```

The exact batching/fsync implementation may optimize several commits together, provided individual acknowledgement semantics remain correct.

## Invariant T2.11 — Durable Commit Point

A transaction becomes durably COMMITTED when its valid commit record and all WAL information required to reconstruct its canonical mutations have crossed the configured durable WAL boundary.

It does **not** become committed merely because:

- the client sent `COMMIT`;
- a commit sequence was tentatively assigned;
- data reached a userspace buffer;
- bytes were written without satisfying the configured durability boundary;
- canonical Segment bytes happened to be present;
- `COMMIT_OK` was attempted but not delivered.

## Invariant T2.12 — Acknowledgement Follows Commit

`COMMIT_OK` MUST NOT be emitted before the durable commit point.

Therefore:

```text
COMMIT_OK => transaction was already durably committed
```

The inverse does not necessarily hold because the network may fail after durable commit but before acknowledgement arrives.

---

# 14. Ambiguous Client Commit Outcome

Consider:

```text
Client                   TCDB
  │                        │
  ├──── COMMIT ───────────→│
  │                        ├─ durable WAL commit
  │                        ├─ transaction COMMITTED
  X──── connection loss ───X
```

The database state is not ambiguous: the transaction committed.

The **client's knowledge** is ambiguous because it did not receive `COMMIT_OK`.

This distinction is canonical.

## Invariant T2.13 — Client Uncertainty Must Not Alter Database Truth

A transport failure after the durable commit point MUST NOT roll back or duplicate the committed transaction merely because acknowledgement was lost.

TCDP is expected to expose a future operation conceptually equivalent to:

```text
COMMIT_STATUS(transaction.id)
```

so clients can resolve uncertain outcomes.

Retry mechanisms MUST use transaction identity and status semantics rather than blindly repeating side effects.

---

# 15. Redo-Only Recovery Model

TCDB's initial architecture deliberately avoids publishing uncommitted mutations into authoritative canonical state.

Therefore crash recovery is designed around **REDO of durable committed transactions**, not general UNDO of uncommitted canonical state.

Transaction mutations may exist before commit in:

- process memory;
- non-authoritative temporary/spool storage;
- WAL records not followed by a durable TX_COMMIT.

None of those constitute committed canonical database state.

## Invariant T2.14 — No Durable Commit Record, No Commit

During recovery, WAL mutations belonging to a transaction without a valid durable commit record MUST NOT be made visible as committed state.

---

# 16. Materialization

Materialization copies or transforms durable committed WAL state into Layer 1 canonical Records, Blocks, and Segments.

Materialization does not establish commit truth; it realizes already-committed truth in the steady-state persistence structures.

Conceptually:

```text
Durable WAL Commit
      │
      ├── immediately visible through committed-state machinery
      │
      ▼
Materializer
      │
      ▼
Layer 1 OPEN Segment
      │
      ▼
SEALED Segment
```

## Invariant T2.15 — Materialization Lag Is Not Commit Lag

A committed transaction remains committed even if the materializer has not yet copied its records into a canonical Segment.

---

# 17. Applied Frontier

TCDB MUST maintain enough durable state to determine which WAL history has already been safely represented in authoritative Layer 1 state.

This is the **applied frontier**.

Conceptually it may include:

```text
applied_through_lsn
applied_through_commit_sequence
manifest_generation
active segment boundary
```

The exact representation is not frozen here.

The frontier MUST advance only after the corresponding Layer 1 state is durably valid.

---

# 18. Open Segment Recovery Boundary

An OPEN Segment may contain bytes written after the last durably established applied frontier.

Those bytes MUST NOT be trusted solely because they parse successfully.

Recovery MUST either:

1. truncate/ignore the OPEN Segment beyond the last trusted boundary and redo from WAL; or
2. prove through equivalent durable metadata that those bytes are already authoritative.

## Invariant T2.16 — Presence Beyond Frontier Is Not Authority

Physical bytes beyond the durable applied frontier are not sufficient evidence of canonical membership.

---

# 19. Checkpoint

A `Checkpoint` establishes that a prefix of committed WAL history has been fully and durably incorporated into valid Layer 1 persistent state.

Conceptually:

```text
Checkpoint
├── checkpoint.id / generation
├── redo_start_lsn or applied_through_lsn
├── commit high-water mark
├── manifest generation
└── required integrity metadata
```

The exact encoding is deferred.

## Invariant T2.17 — Checkpoint Does Not Create Commit

Checkpointing changes recovery cost and WAL-retention requirements.

It does not change whether an already-durable transaction is committed.

## Invariant T2.18 — Checkpoint Publication Is Ordered After Durable Materialization

A checkpoint MUST NOT claim WAL history is safely materialized before all canonical state needed to reconstruct that history is durably valid and its authoritative Manifest state is durably published.

---

# 20. Manifest Publication

Layer 1 established the Manifest as authoritative physical membership.

Layer 2 requires Manifest transitions to be atomically and durably publishable.

A conceptual publication procedure is:

```text
1. Construct candidate generation G+1.
2. Encode and validate candidate Manifest.
3. Write candidate to a non-authoritative location/name.
4. Synchronize candidate to the durability boundary.
5. Atomically install/select G+1 as current.
6. Synchronize the publication metadata / containing directory as required by the platform.
7. Retain enough prior state for deterministic recovery until G+1 is known durable.
```

The exact OS-specific primitive is delegated to a storage-platform specification.

## Invariant T2.19 — Manifest Publication Must Be All-or-Previous

After recovery from a publication failure, TCDB MUST select either the complete previous valid Manifest generation or the complete new valid generation.

A torn hybrid generation is not valid authoritative state.

---

# 21. Crash Recovery Procedure

The reference recovery procedure is conceptually:

```text
1. Open database in recovery mode; do not serve normal requests.
2. Validate database identity and required format metadata.
3. Select the latest valid authoritative Manifest generation.
4. Validate referenced canonical structures required for recovery.
5. Locate the latest valid Checkpoint/applied frontier.
6. Validate WAL continuity and integrity from the required recovery LSN.
7. Scan WAL in order.
8. Identify transactions with valid durable TX_COMMIT records.
9. Ignore uncommitted/incomplete transactions.
10. Redo committed mutations not represented by the trusted applied frontier.
11. Reconstruct or replace the OPEN Segment as required.
12. Verify resulting canonical state.
13. Publish recovery Manifest/checkpoint state atomically.
14. Rebuild or schedule rebuild of non-authoritative indexes/projections as needed.
15. Enter normal service only after recovery invariants hold.
```

## Invariant T2.20 — Recovery Must Be Deterministic

Given the same valid durable database state and WAL prefix, the reference recovery algorithm MUST derive the same committed logical database state.

---

# 22. Recovery Idempotence

Recovery may itself crash.

Therefore recovery procedures MUST be safe to repeat.

Preferred strategies include:

- redo into non-authoritative recovery structures and publish only when complete;
- retain explicit applied frontiers;
- use stable transaction/commit identity to avoid duplicate semantic application.

No recovery algorithm may depend on "this probably ran already".

## Invariant T2.21 — Repeated Recovery Must Not Duplicate Committed Semantics

Running recovery multiple times over the same durable history MUST converge on the same logical committed state.

---

# 23. WAL Integrity and Continuity

WAL structures MUST be:

- versioned;
- length-bounded;
- ordered;
- integrity-checkable;
- capable of detecting missing or corrupted required log regions.

Recovery MUST distinguish at least:

```text
valid complete WAL
valid tail ending before a commit record
corrupt required WAL
missing required WAL
```

A valid incomplete transaction tail may be ignored.

Corruption or absence of WAL required to reconstruct acknowledged committed state is a database integrity failure and MUST NOT be silently skipped.

---

# 24. WAL Retention and Truncation

WAL may be retired only when it is no longer required for any authoritative recovery obligation.

At minimum, WAL required by the current recovery/checkpoint frontier MUST be retained.

Later layers may introduce additional retention constraints for:

- backups;
- replicas;
- change streams;
- audit requirements.

## Invariant T2.22 — Never Truncate Required Recovery History

TCDB MUST NOT remove WAL that is still required to reconstruct any acknowledged committed state from the authoritative checkpoint/Manifest state.

---

# 25. Durability Modes

Layer 2 defines one canonical acknowledgement meaning:

```text
DURABLE COMMIT
```

A future implementation MAY offer explicitly weaker asynchronous modes, but such a mode MUST use different documented acknowledgement semantics and MUST NOT overload `COMMIT_OK` in a way that falsely implies the Layer 2 durable commit guarantee.

Secure enterprise defaults SHOULD use the durable commit contract.

---

# 26. Failure Model

Layer 2 assumes failures may occur at every boundary, including:

```text
before WAL append
during WAL append
after mutation WAL / before commit WAL
during commit WAL write
before WAL sync
during WAL sync
after durable commit / before COMMIT_OK
during Segment materialization
during Block finalization
during Segment sealing
during Manifest publication
during checkpoint publication
during recovery
```

The architecture MUST define a correct outcome for every such cut point.

---

# 27. Deterministic Failure Testing Doctrine

Every state-transition algorithm in Layer 2 MUST be testable with deterministic failure injection.

For a transaction whose client received `COMMIT_OK`:

```text
RecoveredState MUST include that transaction exactly once.
```

For a transaction whose durable commit point was never reached:

```text
RecoveredState MUST NOT expose it as committed.
```

For a transaction durably committed but whose acknowledgement was lost:

```text
RecoveredState MUST include it exactly once,
and COMMIT_STATUS(transaction.id) must be resolvable from retained authoritative history.
```

---

# 28. Layer 2 Non-Collapses

Layer 2 canonically preserves:

```text
TransactionID != CommitSequence
CommitSequence != LSN
CommitSequence != WallClockTime
CommitSequence != TemporalFrame
DurableCommit != ClientAcknowledgement
CommitVisibility != SegmentMaterialization
WALPresence != Commit
FilesystemPresence != ManifestMembership
Checkpoint != Commit
Recovery != SemanticMutation
```

These distinctions MUST NOT be collapsed by later layers.

---

# 29. Layer Boundary With Layer 3

Layer 2 establishes a crash-safe canonical transaction history.

Layer 3 may now build acceleration structures over that history.

Layer 3 MUST assume:

- canonical state may span sealed Segments, the active committed state, and recovery/materialization boundaries;
- indexes are rebuildable;
- indexes MUST NOT define commit truth;
- query results MUST respect transaction snapshots and commit visibility;
- index publication must never make uncommitted data visible.

Therefore:

```text
Layer 2: Which canonical state is committed and recoverable?
Layer 3: How do we find that state efficiently?
```

---

# 30. Layer 2 Exit Criteria

Layer 2 is architecturally established when:

- [x] Transaction identity and lifecycle are defined;
- [x] snapshot visibility is defined;
- [x] strict-serializable baseline is established;
- [x] commit.sequence semantics are defined;
- [x] CommitRecord is defined;
- [x] WAL authority and LSN distinction are defined;
- [x] write-ahead ordering is defined;
- [x] durable commit point is defined;
- [x] `COMMIT_OK` semantics are defined;
- [x] ambiguous client outcomes are explicitly modeled;
- [x] redo-only recovery is established;
- [x] materialization/applied-frontier semantics are defined;
- [x] Checkpoint semantics are defined;
- [x] atomic Manifest publication requirements are defined;
- [x] crash recovery is defined;
- [x] recovery idempotence is required;
- [x] WAL retention constraints are defined;
- [x] deterministic failure testing is required;
- [x] Layer 2 / Layer 3 responsibility boundary is explicit.

The next architecture layer may now define coordinate access and indexing without becoming a source of transaction or commit truth.
