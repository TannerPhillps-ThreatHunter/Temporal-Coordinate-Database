# TCDB Root Algorithms

**Status:** Foundational Registry  
**Layer:** Architecture Layer 0

## 1. Purpose

Root Models describe what exists.

Root Algorithms define how those models are canonically transformed, compared, or reasoned about.

Root Algorithms are semantic algorithms. Storage algorithms, index structures, consensus algorithms, compression algorithms, and transport algorithms belong to later layers.

## 2. Algorithm Classes

### Adopted

Established mathematics or algorithms incorporated into TCDB.

Examples include interval relation classification, exact arithmetic, set operations, and standard cryptographic hashing where required.

TCDB does not claim invention of adopted algorithms.

### TCDB-Native

Algorithms created, derived, specialized, or materially refined for TCDB semantics.

A TCDB-native algorithm may begin as experimental and only become canonical after falsification, reference testing, and prior-art review.

## 3. Algorithm Status

Each registered algorithm SHOULD declare one of:

```text
PROPOSED
EXPERIMENTAL
REFERENCE
ADOPTED
CANONICAL
DEPRECATED
REJECTED
```

Status describes architectural maturity, not implementation performance.

## 4. Algorithm Contract

Each Root Algorithm SHOULD define:

```text
Name
Identifier
Purpose
Class
Status
Inputs
Outputs
Preconditions
Postconditions
Invariants
Complexity
Provenance / Prior Art
Reference Algorithm
Optimized Implementations
Test Vectors
```

## 5. Reference vs Optimized Algorithms

\[
ReferenceAlgorithm \neq OptimizedAlgorithm
\]

The reference algorithm exists to define correctness.

An optimized implementation exists to improve cost while preserving semantic equivalence.

For all valid input \(x\):

\[
Optimized(x)=Reference(x)
\]

Any disagreement is a correctness defect until proven otherwise.

## 6. Root Algorithm Families

### A0 — Temporal Coordinate Canonicalization

Maps source temporal representations into canonical TemporalExtent semantics.

Examples:

\[
(start,end)\rightarrow(s,e)
\]

\[
(start,duration)\rightarrow(s,s+d)
\]

\[
(timestamp,resolution)\rightarrow U\subseteq\mathcal{T}
\]

Canonicalization MUST preserve provenance sufficient to distinguish recorded, observed, derived, estimated, or asserted temporal boundaries where known.

### A1 — Exact Temporal Relation Evaluation

Given exact extents \(T_A,T_B\), evaluate interval relationships from endpoint constraints.

This family may adopt Allen interval relations as an established relation basis.

Examples include:

```text
BEFORE
MEETS
OVERLAPS
STARTS
DURING
FINISHES
EQUALS
FINISHED_BY
CONTAINS
STARTED_BY
OVERLAPPED_BY
MET_BY
AFTER
```

### A2 — Indeterminate Temporal Relation Evaluation

Given feasible temporal regions:

\[
U_A,U_B\subseteq\mathcal{T}
\]

evaluate a relation as:

\[
TRUE|FALSE|UNKNOWN
\]

The algorithm MUST NOT manufacture certainty from incomplete temporal knowledge.

### A3 — Temporal Ordering

Establish ordering only under an explicit ordering relation.

For strict interval precedence:

\[
A\prec B \iff e_A<s_B
\]

Temporal objects MAY remain incomparable.

No Root Algorithm may assume a universal predecessor or total event sequence.

### A4 — Temporal Displacement

For exact coordinates:

\[
P_A=(s_A,e_A)
\]

\[
P_B=(s_B,e_B)
\]

derive:

\[
V_{AB}=P_B-P_A=(\Delta s,\Delta e)
\]

with:

\[
\Delta D=\Delta e-\Delta s
\]

Displacement is relation-dependent derived geometry and MUST NOT replace canonical endpoint coordinates.

### A5 — Coordinate Projection

Transform canonical endpoint geometry into derived coordinate systems appropriate for analysis or indexing.

Examples:

\[
(s,e)\rightarrow(s,D)
\]

\[
(s,e)\rightarrow(M,D)
\]

where:

\[
D=e-s
\]

and:

\[
M=(s+e)/2
\]

Projection MUST preserve a documented relationship to canonical coordinates and MUST NOT silently redefine temporal semantics.

## 7. Research Lifecycle

TCDB-native algorithms SHOULD progress through:

```text
Problem
  ↓
Reference Definition
  ↓
Naive Algorithm
  ↓
Prior-Art Review
  ↓
Falsification
  ↓
Optimization
  ↓
Adversarial Testing
  ↓
Real-Data Testing
  ↓
Canonicalization or Rejection
```

Failed algorithms and rejected hypotheses SHOULD remain documented as research provenance when they materially inform the design.

## 8. Non-Root Algorithms

The following are not Layer 0 Root Algorithms merely because TCDB may use them:

```text
B-trees
LSM compaction
Morton encoding
Bloom filters
compression codecs
WAL algorithms
Raft / Paxos
QUIC congestion control
query join algorithms
vector indexing algorithms
```

These belong to later architecture layers unless a future architectural revision demonstrates that one is semantically foundational.
