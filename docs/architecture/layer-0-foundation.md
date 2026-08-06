# Architecture Layer 0 — Foundation

**Status:** Canonical Foundation  
**System:** Temporal Coordinate Database (TCDB)

## 1. System Identity

A Temporal Coordinate Database models temporal extent as a coordinate-space primitive rather than treating time merely as auxiliary attributes attached to records.

For determinate extent:

\[
P=(s,e), \quad s\le e
\]

with canonical domain:

\[
\mathcal{T}=\{(s,e)\mid s\le e\}
\]

## 2. Root Models

```text
Temporal Semantic Plane
├── TemporalFrame
├── TemporalExtent
├── TemporalObject
└── TemporalRelation

Database History Plane
└── Commit
```

### TemporalFrame

Defines the semantic meaning of a temporal coordinate system.

Examples may include occurrence, observation, knowledge, and validity.

Distinct frames MUST remain semantically distinguishable.

### TemporalExtent

Defines where an object exists within a TemporalFrame.

Determinate:

\[
T=(s,e)
\]

Indeterminate:

\[
U\subseteq\mathcal{T}
\]

Duration is derived:

\[
D=e-s
\]

Storage precision MUST NOT be interpreted as source or epistemic precision.

### TemporalObject

An identifiable object associated with one or more named temporal frames:

\[
O=(id,\{F_i:T_i\},attributes,provenance)
\]

Object identity is independent of relation keys and coordinates.

### TemporalRelation

Describes temporal geometry or domain/object relationships.

Coordinate-derived relations include BEFORE, AFTER, MEETS, OVERLAPS, CONTAINS, DURING, and EQUALS.

Domain relations select which objects should be compared.

Selection semantics and temporal geometry MUST remain separate.

### Commit

Commit belongs to database mechanics, not the temporal ontology.

\[
C=(sequence,transaction,metadata)
\]

`commit.sequence` establishes authoritative database order.

`committed_at`, when present, is descriptive metadata.

TCDB does not define canonical `stored_at` on TemporalObject.

## 3. Three-Valued Temporal Truth

For feasible extent region \(U\) and predicate-satisfying region \(R\):

TRUE:

\[
U\subseteq R
\]

FALSE:

\[
U\cap R=\varnothing
\]

UNKNOWN otherwise.

TCDB MUST preserve UNKNOWN when evidence cannot establish TRUE or FALSE.

## 4. Information Doctrine

```text
Canonical
Derived
Indexed
Analytical
```

Canonical information is authoritative.

Derived information is deterministically computed from canonical state.

Indexed information is redundant physical acceleration state.

Analytical information is higher-order interpretation.

\[
Canonical \neq Derived \neq Indexed \neq Analytical
\]

Rebuildable structures MUST be reconstructible from authoritative state and explicit derivation rules.

## 5. Root Algorithms

Layer 0 also defines semantic Root Algorithms. Root Models provide the nouns of TCDB; Root Algorithms provide its semantic verbs.

See `root-algorithms.md`.

## 6. Explicit Non-Collapses

\[
TemporalObject \neq TemporalExtent
\]

\[
TemporalExtent \neq TemporalFrame
\]

\[
ObjectIdentity \neq RelationIdentity
\]

\[
OccurrenceTime \neq KnowledgeTime
\]

\[
SemanticTime \neq CommitOrder
\]

\[
CommitOrder \neq WallClockTime
\]

\[
RelationSelection \neq TemporalGeometry
\]

\[
TotalOrder \neq PartialOrder
\]

\[
StoragePrecision \neq KnowledgePrecision
\]

\[
Observation \neq UnderlyingOccurrence
\]

## 7. Production Time Requirement

Canonical production time MUST support exact deterministic ordering and MUST NOT depend on floating-point comparison semantics.

The physical width, epoch, time scale, and encoding are delegated to later specifications.

## 8. Protocol Boundary

Current direction:

```text
TCDP
  ↓
QUIC
  ↓
TLS 1.3 integration
  ↓
UDP/IP
```

TCDP/1 is intended to be QUIC-native. No TCP mapping is currently planned.

## 9. Dependency Rules

- Later layers MAY depend on Layer 0.
- Layer 0 MUST NOT depend on later implementation details.
- Physical optimization MUST NOT change semantic results.
- Query shorthand MUST lower to explicit Layer 0 semantics.
- Protocol encoding MUST preserve Layer 0 distinctions.
- Distribution MUST NOT redefine temporal semantics.
