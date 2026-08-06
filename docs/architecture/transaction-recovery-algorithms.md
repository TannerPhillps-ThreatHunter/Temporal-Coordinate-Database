# TCDB Transaction & Recovery Algorithms

**Status:** Foundational Registry  
**Layer:** Architecture Layer 2

---

# 1. Purpose

This document registers the reference algorithm families used to implement Layer 2 transaction, durability, checkpoint, and recovery semantics.

Layer 2 algorithms are database-mechanics algorithms. They do not redefine TemporalFrame, TemporalExtent, TemporalObject, or TemporalRelation semantics.

Every optimized implementation MUST preserve the externally observable behavior of the corresponding reference algorithm.

---

# 2. Algorithm Contract

Each Layer 2 algorithm SHOULD define:

```text
Identifier
Name
Purpose
Status
Inputs
Outputs
Preconditions
Postconditions
Durability boundary
Failure points
Idempotence requirements
Complexity
Reference algorithm
Optimized implementations
Test vectors / failure seeds
```

---

# 3. Algorithm Status

Layer 2 algorithms may be:

```text
PROPOSED
EXPERIMENTAL
REFERENCE
ADOPTED
CANONICAL
DEPRECATED
REJECTED
```

A reference algorithm prioritizes correctness and falsifiability over throughput.

---

# 4. TR0 — Begin Transaction

**Purpose:** Establish a transaction identity and committed snapshot.

Reference procedure:

```text
1. Allocate or validate transaction.id.
2. Read the current durable committed high-water sequence.
3. Set transaction.snapshot.sequence to that high-water mark.
4. Initialize transaction state ACTIVE.
5. Initialize an ordered mutation set.
6. Return transaction identity and snapshot metadata.
```

Postconditions:

- transaction is ACTIVE;
- snapshot references committed history only;
- no canonical mutation is yet visible outside the transaction.

---

# 5. TR1 — Stage Mutation

**Purpose:** Add a mutation to an ACTIVE transaction without publishing it.

Reference procedure:

```text
1. Verify transaction is ACTIVE.
2. Validate mutation semantics against Layer 0/1 rules.
3. Assign mutation ordinal within transaction.
4. Stage mutation in memory or non-authoritative spool storage.
5. Make staged mutation visible only to the owning transaction where read-your-writes applies.
```

Invariant:

```text
STAGED != COMMITTED
```

Temporary/spool bytes never become authoritative solely through filesystem presence.

---

# 6. TR2 — Validate Commit

**Purpose:** Determine whether an ACTIVE transaction may serialize successfully.

Reference procedure:

```text
1. Freeze the transaction's staged mutation set.
2. Determine commits that occurred after snapshot.sequence.
3. Evaluate conflicts required by the serializability model.
4. Validate uniqueness, catalog, object-version, and other canonical constraints.
5. If conflict exists, reject commit and transition toward ABORTED.
6. Otherwise permit commit serialization.
```

The first implementation MAY serialize all writers, reducing conflict logic to a simpler reference path.

A later optimized implementation MAY use locks, MVCC, SSI-like validation, optimistic validation, or another mechanism if it preserves strict serializability.

---

# 7. TR3 — Assign Commit Sequence

**Purpose:** Establish the proposed position of a successfully validating transaction in database history.

Reference procedure:

```text
1. Enter the commit serialization critical section.
2. Choose a sequence greater than every previously committed sequence.
3. Associate the tentative sequence with the COMMITTING transaction.
4. Do not expose a Commit object until durable commit is established.
```

Requirements:

- committed sequences are unique;
- committed sequences increase monotonically;
- consumers MUST NOT depend on gaplessness.

---

# 8. TR4 — Encode Commit Batch

**Purpose:** Produce deterministic WAL payloads for one committing transaction.

Reference procedure:

```text
1. Use the assigned commit.sequence.
2. Canonically encode each staged mutation in mutation-ordinal order.
3. Produce TX_MUTATION WAL records containing all information required for redo.
4. Produce the canonical CommitRecord representation.
5. Produce TX_COMMIT WAL record referencing transaction.id, commit.sequence, mutation count, and required integrity metadata.
6. Validate all lengths and encodings before append.
```

Where practical, the same canonical record bytes SHOULD be reused during later Segment materialization to avoid semantic differences between WAL replay and ordinary persistence.

---

# 9. TR5 — Append WAL Commit Batch

**Purpose:** Append a complete transaction commit batch in ordered WAL position.

Reference procedure:

```text
1. Append TX_MUTATION records in canonical mutation order.
2. Append TX_COMMIT after all required mutation records.
3. Record the commit record's ending LSN.
4. Do not acknowledge commit yet.
```

Failure before a complete valid TX_COMMIT leaves the transaction uncommitted for recovery purposes.

---

# 10. TR6 — Establish Durable Commit

**Purpose:** Cross the authoritative durability boundary.

Reference procedure:

```text
1. Request WAL synchronization through the transaction's complete TX_COMMIT record.
2. Wait for the configured durable storage boundary to report success.
3. If synchronization fails, do not report COMMITTED.
4. On success, atomically advance in-memory committed history to include commit.sequence.
5. Mark transaction COMMITTED.
6. Make the transaction logically visible.
```

Postcondition:

```text
Durable TX_COMMIT + required WAL mutations => COMMITTED
```

This is the authoritative commit point.

---

# 11. TR7 — Acknowledge Commit

**Purpose:** Report a previously established commit to the client/protocol layer.

Reference procedure:

```text
1. Verify transaction state is COMMITTED.
2. Return COMMIT_OK(transaction.id, commit.sequence, optional committed_at).
```

If delivery fails, database state remains COMMITTED.

The protocol layer MUST treat transport delivery as distinct from commit establishment.

---

# 12. TR8 — Abort Transaction

**Purpose:** Terminate a transaction that did not reach durable commit.

Reference procedure:

```text
1. If transaction is already durably COMMITTED, abort is invalid.
2. Discard staged authoritative intent.
3. Remove or invalidate non-authoritative spool resources.
4. Mark transaction ABORTED.
5. Optionally append diagnostic/cleanup WAL metadata if required by implementation.
```

No CommitRecord is created for an aborted transaction.

---

# 13. TR9 — Resolve Commit Status

**Purpose:** Resolve a client's uncertain commit outcome using transaction identity.

Reference procedure:

```text
1. Check current committed transaction-status structures.
2. If necessary, consult canonical CommitRecords.
3. If still within recovery-only history, consult valid WAL.
4. Return COMMITTED with commit.sequence, ABORTED/NOT_COMMITTED where provable, or NOT_FOUND/EXPIRED according to retention semantics.
```

A rebuildable index MAY accelerate lookup but cannot define commit truth.

---

# 14. TR10 — Materialize Committed Transaction

**Purpose:** Convert already-committed WAL state into Layer 1 canonical Segment state.

Reference procedure:

```text
1. Select next committed transaction beyond the durable applied frontier.
2. Decode/validate its canonical WAL mutation payloads.
3. Append canonical Records to the active Layer 1 Segment.
4. Finalize Blocks as required.
5. Synchronize canonical data required by the intended applied-frontier advance.
6. Advance applied metadata only after all required bytes are durable and valid.
```

Materialization NEVER decides whether the transaction committed.

---

# 15. TR11 — Seal Active Segment

**Purpose:** Transition a valid OPEN Segment into immutable SEALED state under Layer 1 rules.

Reference procedure:

```text
1. Stop selecting the current Segment for new materialization.
2. Finalize remaining valid Block state.
3. Compute footer metadata and Segment digest.
4. Validate complete Segment.
5. Synchronize Segment bytes.
6. Prepare next Manifest generation referencing the SEALED Segment and replacement OPEN Segment as needed.
7. Publish Manifest atomically using TR12.
```

A partially sealed file not selected by a valid Manifest is non-authoritative/orphan state.

---

# 16. TR12 — Publish Manifest Generation

**Purpose:** Atomically advance authoritative physical membership.

Reference procedure:

```text
1. Load current valid Manifest generation G.
2. Construct generation G+1.
3. Validate all referenced identities, lengths, commit ranges, and integrity metadata.
4. Write G+1 to a non-authoritative candidate location.
5. Synchronize candidate Manifest.
6. Atomically install/select G+1 as current using the platform publication primitive.
7. Synchronize directory/publication metadata where required.
8. Retain G until G+1 durability is established.
```

Postcondition:

After any crash, recovery can select complete G or complete G+1, never a semantic mixture.

---

# 17. TR13 — Create Checkpoint

**Purpose:** Advance the recovery frontier and make older WAL eligible for retirement.

Reference procedure:

```text
1. Choose target WAL/commit frontier C.
2. Materialize all committed state required through C.
3. Synchronize required canonical Segment state.
4. Publish the corresponding valid Manifest generation.
5. Create checkpoint metadata binding Manifest generation to applied WAL/commit frontier.
6. Synchronize checkpoint metadata.
7. Publish checkpoint as current recovery frontier.
8. Recompute minimum WAL retention boundary.
```

Checkpoint MUST never get ahead of durable canonical materialization.

---

# 18. TR14 — Select Recovery State

**Purpose:** Establish the trusted starting point after process or machine failure.

Reference procedure:

```text
1. Validate database identity and format compatibility.
2. Enumerate candidate Manifest generations using explicit metadata rules.
3. Select latest complete valid authoritative Manifest.
4. Select latest valid checkpoint compatible with that Manifest history.
5. Determine required redo-start LSN.
6. Validate that required WAL exists and is continuous enough for recovery.
```

Filesystem modification time MUST NOT be used as authority.

---

# 19. TR15 — Scan WAL for Recovery

**Purpose:** Classify durable transactions after the checkpoint frontier.

Reference procedure:

```text
1. Start at required redo LSN.
2. Parse WAL records in LSN order with bounded lengths.
3. Verify record integrity and continuity.
4. Accumulate transaction mutations by transaction.id.
5. On valid TX_COMMIT, verify required mutation count/content is complete.
6. Mark transaction eligible for redo.
7. At valid incomplete tail, stop safely.
8. On corruption/missing required WAL, fail recovery explicitly.
```

A transaction without valid TX_COMMIT remains uncommitted.

---

# 20. TR16 — Redo Committed History

**Purpose:** Reconstruct committed state not represented by the trusted applied frontier.

Reference procedure:

```text
1. Order redo-eligible transactions by commit.sequence.
2. For each transaction beyond the applied frontier:
   a. validate canonical mutation payloads;
   b. apply to recovery materialization state;
   c. preserve transaction/commit identity;
3. Write recovery output into non-authoritative structures where possible.
4. Verify resulting canonical structures.
5. Publish resulting Manifest atomically.
6. Establish a new checkpoint/applied frontier.
```

Redo MUST be idempotent at the logical database level.

---

# 21. TR17 — Recover Active Segment

**Purpose:** Handle OPEN Segment bytes around the last trusted applied boundary.

Reference procedure:

```text
1. Validate the active Segment up to the trusted applied boundary.
2. Treat bytes beyond the boundary as untrusted transition residue unless separately proven authoritative.
3. Truncate, ignore, or replace untrusted tail according to platform/storage rules.
4. Redo committed history from WAL.
5. Produce a valid OPEN or SEALED replacement Segment.
```

Recovery MUST NOT infer commit from parseable tail bytes.

---

# 22. TR18 — Retire WAL

**Purpose:** Remove WAL no longer needed for authoritative obligations.

Reference procedure:

```text
1. Determine minimum recovery-required LSN from current checkpoint.
2. Incorporate later retention constraints such as backup/replication if present.
3. Identify WAL segments wholly below the minimum required frontier.
4. Verify retained WAL begins at or before every required consumer frontier.
5. Retire eligible WAL atomically/safely.
```

Never retire WAL still required to recover acknowledged commits.

---

# 23. TR19 — Group Commit

**Purpose:** Amortize synchronization cost while preserving individual commit semantics.

Status: `REFERENCE OPTIMIZATION`.

Reference procedure:

```text
1. Serialize a batch of independently validated committing transactions.
2. Assign strictly increasing commit.sequence values in batch order.
3. Append each transaction's complete WAL commit batch in that order.
4. Issue one durable synchronization covering all complete commit records in the batch.
5. Mark each covered transaction COMMITTED.
6. Acknowledge each transaction independently.
```

A transaction whose complete commit record is not covered by the successful durability boundary MUST NOT receive `COMMIT_OK`.

---

# 24. TR20 — Deterministic Failure Injection

**Purpose:** Prove state-transition correctness at every persistence boundary.

Reference harness SHOULD support deterministic crash/failure seeds at least at:

```text
before/after every WAL append
before/after WAL sync
inside WAL record writes
before/after commit state publication
before/after Segment append
before/after Block finalization
before/after Segment sync
before/after Manifest candidate write
before/after Manifest publication
before/after Checkpoint publication
inside recovery replay
```

For each seed, the harness restarts from durable bytes only and compares recovered state with the expected reference history.

---

# 25. Required Properties

Every conforming optimized Layer 2 implementation MUST preserve:

```text
Atomicity
Strict-serializable committed history
Durable commit before acknowledgement
No uncommitted visibility
Redo-only recovery semantics
Deterministic commit order
Manifest authority
Recovery idempotence
Commit-status resolvability
Integrity failure visibility
```

---

# 26. Falsification Properties

The following are direct test or property-testing targets.

## Property A — Acknowledged durability

For every transaction T:

```text
if client_received(COMMIT_OK(T))
then recover(crash_at_any_later_point) contains T exactly once
```

## Property B — No phantom commit

```text
if durable_TX_COMMIT(T) never occurred
then recovered_state does not expose T as committed
```

## Property C — Lost acknowledgement

```text
if durable_TX_COMMIT(T) occurred
and COMMIT_OK was lost
then recovered_state contains T exactly once
```

## Property D — Recovery convergence

```text
recover(recover(state)) == recover(state)
```

at the logical canonical-state level.

## Property E — Commit ordering

For committed transactions A and B:

```text
A.commit.sequence < B.commit.sequence
=> A precedes B in committed serialization history
```

## Property F — Index irrelevance

Deleting all rebuildable indexes before recovery MUST NOT change the recovered canonical result.

---

# 27. Optimization Doctrine

Layer 2 optimizations are welcome, including:

- group commit;
- WAL batching;
- parallel WAL encoding;
- concurrent readers;
- MVCC;
- optimistic validation;
- asynchronous materialization;
- parallel redo;
- incremental checkpointing.

They are valid only when they preserve the reference semantics.

Performance evidence cannot override a failed correctness property.
