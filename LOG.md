# LOG.md — Temporal Coordinate Database Continuity Log

**Date:** 2026-08-06  
**Status:** CONTINUITY / REFLECTION ARTIFACT  
**Canonical:** No

This file records project context accumulated through research, architecture work, experiments, corrections, and implementation decisions during the current TCDB/TCD development session.

It exists to help future AI agents and human collaborators recover not only **what the repository currently says**, but also **why certain distinctions, boundaries, and priorities exist**.

`LOG.md` does not override:

1. `AGENTS.md`
2. `ARCHITECTURE.md`
3. established files under `docs/architecture/`
4. explicit specification documents under `specs/`

If this log conflicts with canonical architecture, the canonical architecture wins.

---

# 1. Executive Reflection

The project began from a deceptively simple idea:

> A temporal object does not merely possess timestamps. It occupies coordinates in temporal space.

The session progressively tested what that claim actually requires of a database.

The most important outcome is that TCDB has become increasingly defined by **semantic distinctions and authority boundaries**, not by any particular index, protocol, file format, or analogy.

The project repeatedly became stronger when two concepts that initially appeared similar were separated:

```text
TemporalObject        != TemporalExtent
TemporalExtent        != TemporalFrame
OccurrenceTime        != KnowledgeTime
SemanticTime          != CommitOrder
CommitOrder           != WallClockTime
ObjectIdentity        != RelationIdentity
RelationSelection     != TemporalGeometry
Canonical             != Derived
Canonical             != Indexed
Canonical             != Analytical
Observation           != UnderlyingOccurrence
StoragePrecision      != KnowledgePrecision
ReferenceAlgorithm    != OptimizedAlgorithm
```

A recurring lesson of the session is:

> **TCDB advances when it refuses to collapse distinctions that conventional systems often treat as implementation details.**

The project also demonstrated a recurring risk: a productive research branch can become interesting enough to displace the central database question. The Event Geometry branch did exactly this. Its findings remain valuable, but the session explicitly corrected the drift and restored the core research target:

> **Derive the Temporal Coordinate Algebra / Query Algebra of the database itself.**

---

# 2. Explicit Context Acquired

These are decisions or positions explicitly stated, accepted, implemented, or written into repository artifacts during the session.

## 2.1 Project Identity

The primary project remains:

# Temporal Coordinate Database

Working abbreviation:

```text
TCDB / TCD
```

The system is currently best described as a **coordinate-native temporal database architecture**.

The project must not be renamed around Event Geometry, computational spacetime, trajectories, or another research concept without deliberate evidence and an explicit architecture decision.

## 2.2 Core Semantic Spine

The primary semantic model is:

```text
TemporalFrame
      ↓
TemporalExtent
      ↓
TemporalObject
      ↓
TemporalRelation
```

with `Commit` belonging to database-history mechanics rather than semantic time.

### TemporalFrame

Answers:

> Which kind of time is this coordinate in?

Candidate frames already considered include:

```text
occurrence
observation
knowledge
validity
```

Frame names are semantic distinctions, not aliases for storage columns.

### TemporalExtent

Determinate extent:

```text
T = (start, end)
start <= end
```

Canonical determinate temporal domain:

```text
𝒯 = {(s,e) | s <= e}
```

Point extent:

```text
start = end
```

Duration is derived:

```text
D = end - start
```

Indeterminate extent is more generally a feasible region:

```text
U ⊆ 𝒯
```

The session explicitly rejected the idea that all uncertainty can be reduced to independent rectangular endpoint bounds. Exact-duration uncertainty, for example, produces a diagonal feasible region.

### TemporalObject

Conceptually:

```text
TemporalObject
├── object_id
├── temporal_frames
├── type
├── attributes
└── provenance
```

The Event Document remains a useful storage/API envelope, but it is not the foundational object model.

### TemporalRelation

Temporal relations are derived from coordinate comparisons.

For exact intervals, Allen-style relations can be compiled to endpoint constraints.

Examples:

```text
BEFORE      e_A < s_B
MEETS       e_A = s_B
OVERLAPS    s_A < s_B < e_A < e_B
EQUALS      s_A = s_B AND e_A = e_B
```

The session repeatedly reinforced:

```text
Selector → TemporalPopulation → TemporalGeometry
```

A relation selector determines which objects are compared. Temporal geometry then describes how those selected objects relate.

## 2.3 Three-Valued Temporal Semantics

For uncertain feasible extent `U` and query-satisfying region `R`:

```text
TRUE     if U ⊆ R
FALSE    if U ∩ R = ∅
UNKNOWN  otherwise
```

`UNKNOWN` is not an implementation inconvenience. It is a semantic result representing insufficient temporal knowledge.

No later layer should manufacture Boolean certainty where the model only supports `UNKNOWN`.

## 2.4 Root Algorithms

The session introduced Root Algorithms as a foundational complement to Root Models.

The governing distinction became:

> Models define what exists. Algorithms define how those models are transformed, compared, and reasoned about.

Initial Layer 0 families:

```text
A0  Temporal Coordinate Canonicalization
A1  Exact Temporal Relation Evaluation
A2  Indeterminate Temporal Relation Evaluation
A3  Temporal Ordering
A4  Temporal Displacement
A5  Coordinate Projection
```

A second important distinction was made:

```text
Adopted Algorithm
TCDB-Native Algorithm
```

and independently:

```text
PROPOSED
EXPERIMENTAL
REFERENCE
ADOPTED
CANONICAL
DEPRECATED
REJECTED
```

The project explicitly adopted:

```text
ReferenceAlgorithm != OptimizedAlgorithm
```

while requiring semantic equivalence:

```text
Optimized(x) == Reference(x)
```

for all valid inputs.

## 2.5 Architecture Layers Established

The repository now treats architecture as layered authority:

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

Current status:

```text
Layer 0  ESTABLISHED
Layer 1  ESTABLISHED
Layer 2  ESTABLISHED
Layer 3+ RESEARCH / NOT CANONICAL
```

### Layer 1 — Persistence

Key decisions:

```text
PersistentDatabase
├── Catalog
├── Manifest
├── Segment
│   └── Block
│       └── Record
└── Rebuildable Structures
```

Important doctrines:

- canonical persistence is append-oriented;
- published canonical Records are not mutated in place;
- OPEN Segments may receive appends;
- SEALED Segments are immutable;
- filesystem presence does not imply database membership;
- the Manifest determines authoritative physical membership;
- secondary indexes and projections are rebuildable;
- canonical serialization must be deterministic, versioned, bounded, platform-independent, and exact.

### Layer 2 — Transactions & Recovery

The session established a deliberately strong transaction/recovery model.

Important doctrines:

- strict-serializable committed history is the baseline target;
- `commit.sequence` defines authoritative database-history order;
- `commit.sequence`, WAL LSN, wall-clock time, and TemporalFrames are different things;
- WAL durability precedes authoritative materialization;
- the durable WAL commit record establishes commit truth;
- `COMMIT_OK` acknowledges an already-existing commit;
- a dropped connection after durable commit causes client uncertainty, not database uncertainty;
- recovery is redo-only for durable committed transactions;
- uncommitted mutations never become authoritative canonical state;
- recovery must be deterministic and idempotent;
- deterministic crash/failure injection should cover every state-transition boundary.

## 2.6 `stored_at` Was Removed From Canonical TemporalObject

A significant cleanup occurred when the question arose whether `stored_at` belonged on every temporal object.

The accepted direction was:

```text
TemporalObject
├── object_id
├── temporal_frames
├── type
├── attributes
└── provenance
```

with database mechanics separated:

```text
Commit
├── commit_id
├── sequence
├── committed_at
└── transaction_id
```

Core distinction:

```text
CommitOrder != CommitTime
TemporalFrame != Commit
```

`commit.sequence` is authoritative order. `committed_at` is descriptive wall-clock metadata.

## 2.7 TCDP and QUIC

The session explicitly chose to invent a native application protocol:

# TCDP — Temporal Coordinate Database Protocol

A key doctrine emerged:

```text
QueryLanguage != WireProtocol
```

The intended stack is:

```text
TCDB
 ↓
TCDP
 ↓
QUIC
 ↓
TLS 1.3 integration
 ↓
UDP/IP
```

Current transport decision:

```text
TCDP/1 runs only over QUIC
```

No TCP fallback is currently planned.

Important TCDP/1 transport rules discussed:

- QUIC-only;
- reliable streams only;
- QUIC DATAGRAM disabled for canonical DB operations;
- application 0-RTT disabled/prohibited initially;
- one primary operation context per QUIC stream;
- one transaction per transaction stream as a starting invariant;
- request IDs remain application-level even though QUIC has stream IDs;
- commit outcome must be recoverable after connection ambiguity.

The session also separated standards tracks conceptually:

```text
TCDB-MODEL
TCDP
TCDP-QUIC
```

These are project specifications, not official RFCs unless they eventually pass through an external standards process.

---

# 3. Implicit Context Learned About How This Project Should Be Worked

These principles were not always introduced as formal architecture, but they became clear through repeated interaction and correction.

## 3.1 Do Not Hand the Project a Finished Answer Too Early

TCDB has repeatedly improved by deriving concepts, testing them, and allowing failures to change the model.

The working method should therefore be:

```text
Primitive
  ↓
Definition
  ↓
Structure
  ↓
Principle
  ↓
Reference Model
  ↓
Experiment
  ↓
Falsification
  ↓
Architecture
```

A polished implementation before semantic clarity is usually premature.

## 3.2 Failed Experiments Are Valuable Project State

The session repeatedly benefited from failed or corrected experiments:

- uncertainty showed arbitrary ordering can invent unsupported facts;
- path signatures underperformed simpler recurrence features;
- a shortcut HINT/HINT^m reproduction produced mismatches and forced a correction;
- Event Geometry became productive enough to reveal project drift;
- raw interval similarity failed under scale variation;
- naïve fixed-length trajectory comparison failed under missing events.

The correct response to failure is not deletion. It is classification:

```text
REJECTED
SUPERSEDED
REFUTED
LIMITED
```

with provenance retained.

## 3.3 Prior Art Is a Boundary Condition, Not a Threat

The session repeatedly tightened novelty claims after literature review.

Established territory includes at least:

- temporal and bitemporal databases;
- Allen interval algebra;
- `(start,end)` endpoint-plane representations;
- 4D mappings for bitemporal intervals;
- temporal uncertainty;
- interval orders and partial orders;
- interval indexing families including HINT/HINT^m, RD-index, TIDE, LIT/LIT+, Timeline Index, UB-tree approaches;
- generic spatial / Morton / space-filling indexing;
- process-mining traces;
- interval-sequence similarity;
- temporal motifs;
- DTW and sequence-alignment approaches.

TCDB should never claim novelty merely because familiar machinery is expressed in TCDB terminology.

The interesting contribution, if one exists, is likely in the **composition of semantic distinctions and database behavior**, not an isolated rediscovery of interval mathematics.

## 3.4 Architecture Must Be Earned by Evidence

A recurring implicit rule became explicit in `AGENTS.md`:

```text
Research != Architecture
Benchmark Result != Semantic Truth
Implementation != Specification
```

A research result should not silently alter established architectural meaning.

Promotion must be deliberate.

## 3.5 Strong Baselines Matter

The project should compare new ideas against the strongest credible alternative, not a deliberately weak baseline.

Examples from this session:

- adaptive endpoint indexing became the real 1D baseline rather than start-only scans;
- HINT^m became the meaningful interval-index baseline after literature reproduction;
- DTW became a reasonable incomplete-sequence baseline for Event Geometry;
- full reference scans remain the semantic oracle even when optimized structures are faster.

## 3.6 The User's "Proceed" Usually Means Continue the Current Program, Not Reopen Fundamentals

The session frequently advanced through concise continuation commands.

A future agent should preserve established context and continue the current plan unless new evidence or an explicit user correction changes direction.

At the same time, continuation should not become inertia: when work begins drifting from the project center, it should be surfaced and corrected.

---

# 4. Experimentally Learned Context

These findings arose from concrete tests or source-backed reproductions during the session.

## 4.1 Endpoint Geometry Is Useful, But Not Novel by Itself

Mapping a determinate interval to:

```text
(start, end)
```

produces a useful coordinate space.

The valid region is triangular:

```text
start <= end
```

Three important line families appear:

```text
start = constant       vertical
end = constant         horizontal
duration = constant    diagonal
```

No ordinary 2D affine coordinate system aligns all three simultaneously.

The canonical semantic coordinate remains `(start,end)`.

Alternative projections such as `(start,duration)` or `(midpoint,duration)` may be useful physically or analytically, but they are derived projections.

## 4.2 Temporal Relations Compile to Coordinate Constraints

Exhaustive exact-interval testing showed the 13 Allen relations can be derived from endpoint comparisons.

This strongly supports the compiler model:

```text
TemporalPredicate
      ↓
CoordinateConstraintSet
```

This compiler idea is likely central to the future Temporal Coordinate Algebra / Query Algebra.

## 4.3 Multi-Frame Semantics Survived Coordinate Compilation

Synthetic tests over occurrence and knowledge frames showed direct semantic evaluation agreed with equivalent coordinate half-space constraints.

This supports treating named temporal frames as independent semantic coordinate spaces that may compose through product spaces without being semantically collapsed.

## 4.4 Occurrence Order and Knowledge/Entry Order Are Different

Real-data testing using NYC Film Permits showed strong global rank correlation between entry time and occurrence start while still producing many local inversions.

This reinforced:

```text
OccurrenceOrder != KnowledgeOrder
```

A strong global correlation is not semantic equivalence.

## 4.5 No Universal Temporal Index Emerged

Testing showed different predicates and distributions favor different structures.

Examples:

- start-oriented access can be strong without duration predicates;
- duration-aware access can improve duration-constrained queries;
- endpoint geometry helps under high duration variance;
- open intervals can cause severe candidate inflation;
- physical grouping by commit order can be poor for occurrence-time search;
- workload-aware planning matters.

The project therefore learned:

> **There is no universal temporal index.**

Layer 3 must eventually be planner- and statistics-aware.

## 4.6 HINT^m Became the Strongest Current Prior-Art Interval Baseline

A reference/structural HINT^m reproduction was implemented and corrected against source material.

The important practical result was that HINT^m approached 2D pruning quality with dramatically lower reference amplification than the static 2D range-tree baseline.

At the same time, adversarial long/equal-start distributions produced significantly higher replication.

This reinforced:

```text
index quality = f(predicate, distribution, parameterization, maintenance cost)
```

not merely query latency on uniform synthetic data.

## 4.7 Static 2D Range Trees Proved Pruning Value but Exposed Storage Cost

The static endpoint range-tree baseline drove overlap candidates close to result cardinality, demonstrating how valuable both endpoint constraints can be.

But reference amplification was roughly 17.7x at 100k rows in the tested implementation.

Important lesson:

```text
Excellent Pruning != Excellent Database Index
```

## 4.8 Relation Selection Determines Observability

Across recurrence and security/network experiments, changing the predecessor/selector relation changed the geometry and what behavior could be observed.

This is one of the more important cross-cutting findings:

> **There is no universal "previous event." The relation is part of the temporal question.**

## 4.9 Identifiers Such as 5-Tuple and Community ID Are Relation Keys, Not Event Identity

Real security telemetry showed repeated 5-tuples associated with temporally distinct events.

Community ID was validated as useful for flow-equivalence/candidate selection, but not as temporal occurrence identity.

Therefore:

```text
EventID != 5Tuple
EventID != CommunityID
```

and more generally:

```text
RelationKey != EventIdentity
```

## 4.10 Observation Resolution Is Not Physical Truth

Coarse security telemetry exposed pairs that shared recorded timestamps but could not be safely ordered.

The session reinforced:

```text
StoragePrecision != ObservationResolution != PhysicalReality
```

A database may preserve the first two. It cannot manufacture the third.

## 4.11 Event Geometry Produced Useful Derived Behavior

The Event Geometry branch tested whether relation-selected intervals and trajectories could become independently useful structures.

Results included:

- absolute timestamp nearest-neighbor classification near chance across synthetic families;
- inter-event displacement retained strong family structure under arbitrary temporal translation;
- derived EventIntervals could be independently indexed while remaining reconstructible;
- all-pairs interval materialization is combinatorially unacceptable;
- relation selection determines which interval population exists;
- scale normalization changes the meaning of trajectory similarity;
- missing observations contract additive displacement paths.

These results are worth preserving.

They do **not** currently justify replacing TCDB with an Event Geometry or computational-spacetime project.

---

# 5. Drift and Correction Log

This section records where the session changed direction because the current path was becoming misleading or overextended.

## 5.1 Event Document Was Demoted From Foundation

Early representations naturally centered Event Documents.

The project corrected this by recognizing that an Event Document is a representation/envelope rather than the foundational abstraction.

The deeper root is `TemporalObject` occupying one or more `TemporalExtent`s in named `TemporalFrame`s.

## 5.2 `stored_at` Was Removed From TemporalObject

`stored_at` initially appeared to belong alongside other temporal information.

The project corrected this by separating semantic time from database mechanics.

Commit mechanics now carry system-history information.

## 5.3 Uncertainty Was Generalized Beyond Rectangles

Independent endpoint uncertainty was initially a natural representation.

The project learned that constraints such as fixed duration create non-rectangular feasible regions.

Therefore uncertainty should eventually be modeled as general feasible coordinate regions with rectangular bounds as a special case.

## 5.4 HINT^m Reproduction Was Corrected Against Official Source

An early structural reproduction misclassified some cover assignments and an attempted duplicate-avoidance shortcut produced mismatches.

The implementation was corrected rather than defended.

This is exactly the desired research behavior.

## 5.5 Event Geometry Became a Drift From the Main Project

The Event Geometry branch produced interesting results and then began driving the roadmap toward trajectory robustness, missing events, duplicates, and similarity metrics.

The user explicitly identified that this had drifted from the main focus.

The project response was to preserve the research but demote it to a derived/paused branch.

This correction should be remembered.

Future agents should not resume Event Geometry simply because those files exist.

---

# 6. Current Repository Operating Model

The repository now contains scoped `AGENTS.md` files.

The hierarchy is:

```text
root AGENTS.md
    ↓
nearest child AGENTS.md
    ↓
files in that subtree
```

Current meaningful scopes include:

```text
/
/docs/
/docs/architecture/
/docs/research/
/research/
/research/layer3/
/research/event_geometry/
/benchmarks/
/tests/
/specs/
```

A child `AGENTS.md` may narrow parent guidance but must not contradict it.

This session explicitly prepared the repository for AI interaction so future work is less dependent on conversational memory.

---

# 7. Current Research Position

The project should currently be understood as:

```text
Temporal Coordinate Database
│
├── Established Architecture
│   ├── Layer 0 Foundation
│   ├── Layer 1 Persistence
│   └── Layer 2 Transactions & Recovery
│
├── Active Core Research
│   └── Temporal Coordinate / Query Algebra
│
└── Paused / Derived Research
    ├── Layer 3 indexing experiments
    └── Event Geometry experiments
```

Layer 3 indexing research is valuable and fairly mature experimentally, but should not be canonized until the query algebra tells us precisely what access paths the database must support.

This ordering is important.

The session originally approached Layer 3 before the query algebra was sufficiently formalized. The later reflection suggests the better dependency is:

```text
Temporal Semantics
      ↓
Temporal Coordinate Algebra
      ↓
Query Compilation
      ↓
Access Planning
      ↓
Index Selection
```

rather than allowing an index structure to imply the query model.

---

# 8. Immediate Next Core Problem

The next central problem is:

# Temporal Coordinate Algebra / Query Algebra

Primary question:

> **What is the smallest precise algebra over TemporalFrame, TemporalExtent, TemporalObject, TemporalRelation, and uncertainty from which useful TCDB queries can be composed?**

The algebra should eventually make queries lower into coordinate constraints.

Conceptual example:

```text
FRAME occurrence
| OVERLAPS [10,20]
| FRAME knowledge
| ASOF 35
```

could lower to constraints resembling:

```text
occurrence.start < 20
occurrence.end   > 10
knowledge.start <= 35
knowledge.end   >= 35
```

The important architecture path is:

```text
Temporal Query
      ↓
Temporal Coordinate Algebra
      ↓
Coordinate Constraint Set
      ↓
Logical Plan
      ↓
Physical Access Plan
```

This should be derived carefully rather than copied from SQL vocabulary.

---

# 9. Open Questions Worth Carrying Forward

## Semantic / Algebra

- What are the primitive algebraic operations?
- Which operations are closed over TemporalExtent and which require TemporalObject populations?
- How should named frame switching/composition work?
- Should relation selection be an algebraic operator or an orthogonal population-selection phase?
- How should TRUE/FALSE/UNKNOWN propagate through conjunction, disjunction, negation, and joins?
- How should point extents interact with boundary semantics?
- What interval-boundary convention should become canonical?

## Multi-Frame

- How should product spaces across frames be represented logically?
- When can frames be planned independently?
- When do compound access paths become justified?
- How should semantic time compose with `AS OF COMMIT` without conflation?

## Uncertainty

- What representation should define general feasible coordinate regions?
- What operations preserve exactness versus introduce approximation?
- Which uncertainty predicates can be indexed without losing three-valued correctness?

## Query / Planner

- What constraint normal form should the algebra compile into?
- Which statistics are required for planner decisions?
- How should endpoint correlation be estimated?
- How should open extents be isolated or specialized?
- How should planner correctness be proven against the reference evaluator?

## Persistence / Implementation

- What exact integer time representation should production use?
- What binary canonical encoding should Layer 1 adopt?
- How should catalogs version TemporalFrames and their semantics?
- When should Layer 3 become physical architecture rather than research?

## Protocol

- What is the minimal TCDP/1 message grammar?
- How should TemporalExtent and uncertainty be encoded?
- How should transactions and query streams map to QUIC exactly?
- What stable error and capability registries are necessary?

---

# 10. Guidance to the Next AI Agent

Before continuing TCDB work:

1. read `AGENTS.md`;
2. read `README.md` and `ARCHITECTURE.md`;
3. read the nearest child `AGENTS.md` for the subtree you will modify;
4. inspect existing repository state before assuming this log is current;
5. preserve established layers unless new evidence justifies revision;
6. treat Event Geometry and Layer 3 indexing as paused research unless explicitly resumed;
7. do not confuse research evidence with canonical architecture;
8. use prior-art review before novelty claims;
9. build reference semantics before optimized implementations;
10. keep failed experiments and corrections as provenance.

Most importantly:

> **Do not let implementation convenience define TCDB semantics.**

The repository should evolve from semantic necessity outward:

```text
Meaning
  ↓
Model
  ↓
Algebra
  ↓
Reference Semantics
  ↓
Architecture
  ↓
Optimization
  ↓
Protocol / Distribution
```

---

# 11. Session-Level Synthesis

The most valuable learned context from this session is not a single algorithm or data structure.

It is a way of thinking about TCDB:

### TCDB is not "a database with better timestamps."

It is an attempt to make temporal distinctions explicit enough that the database can reason about them without silently collapsing occurrence, observation, knowledge, commit order, uncertainty, identity, relation, and physical storage into one timeline.

### Coordinate representation is necessary but not sufficient.

The `(start,end)` plane is useful and established prior art. TCDB only becomes distinct if the coordinate representation is connected to meaningful semantic frames, uncertainty, relation selection, algebra, transactions, and query planning in a coherent database model.

### The project should remain falsifiable.

If PostgreSQL ranges, a graph database, a temporal DB, an event store, or existing temporal indexes already express a proposed capability cleanly and efficiently, TCDB should acknowledge that rather than count terminology as novelty.

### The core question remains open.

> **What does a database become when time is treated as a first-class coordinate system rather than incidental metadata?**

That remains the project’s central research question.

The next serious attempt to answer it should begin with the Temporal Coordinate Algebra.
