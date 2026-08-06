# Layer 3 Research — Coordinate Access & Indexing

**Status:** RESEARCH / NON-CANONICAL  
**Target Architecture:** Layer 3 — Coordinate Access & Indexing  
**Depends On:** Layer 0 semantic invariants, Layer 1 persistence, Layer 2 transaction/recovery semantics

---

# 1. Research Question

Layer 3 must answer:

> How should TCDB locate temporal objects efficiently while preserving exact Layer 0 semantics across interval predicates, multiple temporal frames, indeterminate extents, append-oriented persistence, and changing workload distributions?

The research goal is **not** to select one universal temporal index.

The research goal is to determine:

1. which access-path families are appropriate for which predicates;
2. which data distributions change the preferred access path;
3. when endpoint-native two-dimensional geometry materially outperforms simpler one-dimensional organization;
4. how multiple named temporal frames should be indexed without collapsing their semantics;
5. how indeterminate temporal regions affect candidate generation and three-valued evaluation;
6. how append-oriented canonical storage should interact with rebuildable secondary structures;
7. what planner statistics are required to choose access paths reliably.

---

# 2. Non-Negotiable Correctness Baseline

Every optimized access path MUST be semantically equivalent to a canonical reference scan.

For query `q` over canonical state `D`:

\[
IndexedQuery(D,q)=ReferenceScan(D,q)
\]

The index MAY return a candidate superset requiring exact predicate evaluation.

It MUST NOT introduce false negatives.

For indeterminate extents, equivalence includes identical:

```text
TRUE
FALSE
UNKNOWN
```

results after exact evaluation.

This is the primary falsification oracle for Layer 3.

---

# 3. Prior-Art Families to Review

The following families are research targets, not TCDB inventions.

## 3.1 One-Dimensional Endpoint Structures

Candidates:

```text
start-sorted arrays / B-trees
end-sorted arrays / B-trees
interval trees
segment trees
augmented balanced trees
```

Questions:

- Which predicates reduce efficiently to one endpoint bound?
- How badly do long/heavy-tailed durations inflate candidate sets?
- Can dual start/end structures outperform multidimensional structures for common workloads?

## 3.2 Multidimensional Endpoint Geometry

Canonical determinate extent:

\[
P=(s,e)
\]

Candidate families:

```text
R-tree / R*-tree
range tree
kd-tree
quadtree variants
GiST-style generalized search trees
space-filling curves
Morton / Z-order
UB-tree-like approaches
```

Research question:

> When does indexing endpoint coordinates as a 2D point materially improve candidate pruning over start-oriented indexing?

## 3.3 Specialized Temporal Interval Indexes

Known literature families to refresh and reproduce include:

```text
HINT / HINT+
RD-index
TIDE
LIT / LIT+
Timeline-oriented interval indexes
other modern interval-overlap structures
```

These names are a research inventory only. Their algorithms, claims, publication status, and current best variants MUST be source-verified before architectural use or novelty comparison.

## 3.4 Database-Native Range Indexing

Research production systems that support interval/range predicates, including generalized range indexes and exclusion/overlap semantics.

Questions:

- What guarantees do mature engines expose?
- What physical structures are used?
- Which workload pathologies are documented?
- Which useful concepts can TCDB adopt without inheriting unrelated relational assumptions?

## 3.5 Bitemporal / Multitemporal Indexing

Two temporal frames produce four endpoint dimensions:

\[
(o_s,o_e,k_s,k_e)
\]

Research historical and modern bitemporal/multidimensional approaches, including 4D point mappings and decomposed indexes.

Core comparison:

```text
Single 2n-dimensional index
vs
one endpoint index per TemporalFrame
vs
selected composite frame indexes
vs
planner intersection of frame-local candidate sets
```

No assumption should be made that a symmetric high-dimensional index is optimal merely because the semantic product space is 2n-dimensional.

## 3.6 Indeterminate / Uncertain Temporal Indexing

For:

\[
U\subseteq\mathcal{T}
\]

research:

```text
bounding-region indexes
uncertain interval indexes
probabilistic/indeterminate temporal databases
constraint databases
region intersection indexes
```

Key requirement:

An approximate bounding representation may be used for candidate generation, but exact TCDB truth semantics must still be evaluated against the actual feasible region representation.

## 3.7 Append / Merge-Oriented Secondary Indexing

Layer 1 canonical persistence is append-oriented and sealed segments are immutable.

Research:

```text
LSM secondary indexes
immutable sorted runs
mergeable temporal indexes
segment-local indexes + global directory
leveled vs tiered merging
write amplification / read amplification tradeoffs
```

The secondary index must remain rebuildable from canonical state.

---

# 4. Existing TCDB Empirical Findings to Reproduce

The following findings were observed during earlier exploratory research and MUST be reproduced in a repository benchmark harness before architectural promotion.

## H1 — No Universal Temporal Index

Observed behavior indicated that access-path quality depends on predicate and temporal distribution.

Examples to reproduce:

- start-oriented access performs well for short-duration populations;
- endpoint 2D locality improves under high duration variance;
- duration-oriented access becomes competitive or superior when duration predicates are present.

**Status:** HYPOTHESIS / PRIOR EXPERIMENT REQUIRES REPRODUCTION

## H2 — Open Extents Should Be Physically Separated or Special-Cased

Earlier synthetic tests showed that mixing open-ended extents into ordinary closed-interval blocks dramatically inflated overlap candidate counts.

Research alternatives:

```text
separate open-extent index
special open-extent partition
sentinel infinity in shared index
hybrid planner path
```

**Status:** HYPOTHESIS / PRIOR EXPERIMENT REQUIRES REPRODUCTION

## H3 — Endpoint Geometry Matters Most Under Duration Variance

Earlier tests suggested:

```text
short duration population -> start locality often sufficient
heavy-tail duration        -> (start,end) geometry gains value
bimodal duration           -> (start,end) geometry gains value
```

**Status:** HYPOTHESIS / PRIOR EXPERIMENT REQUIRES REPRODUCTION

## H4 — Commit-Ordered Physical Segments Are Not Sufficient as Temporal Index Partitions

Occurrence order may diverge materially from commit/knowledge order.

Permanent commit-order segment boundaries can therefore create poor occurrence-time pruning.

Candidate direction:

```text
immutable commit-ordered canonical payload
+
mergeable occurrence-oriented reference indexes
```

**Status:** STRONG HYPOTHESIS / REQUIRES REPRODUCTION

## H5 — Logical Relation Order Is Not Physical Storage Order

Entity/relation populations may exhibit useful semantic sequence structure while producing worse compression or locality than global occurrence order.

Relation indexes should therefore likely store references rather than physically reorganize canonical payload by every relation.

**Status:** STRONG HYPOTHESIS / REQUIRES REPRODUCTION

---

# 5. Predicate Taxonomy

Layer 3 research must benchmark predicates separately rather than averaging them into one generic "temporal query" workload.

For object extent:

\[
E=(s,e)
\]

and query extent:

\[
Q=(a,b)
\]

include at minimum:

## Point/Bound Predicates

```text
START < t
START BETWEEN a,b
END < t
END BETWEEN a,b
DURATION BETWEEN x,y
```

## Interval Predicates

```text
BEFORE
AFTER
MEETS
OVERLAPS
CONTAINS
DURING
EQUALS
```

Include the full exact Allen relation family where useful.

## ASOF / Point Containment

```text
s <= t <= e
```

with exact boundary semantics frozen by the semantic specification.

## Multi-Frame Predicates

Example:

```text
occurrence OVERLAPS [a,b]
AND
knowledge CONTAINS ASOF c
```

## Mixed Temporal + Domain Selection

Example:

```text
same entity / relation key
AND
occurrence predicate
```

This is essential because relation selection changes candidate populations and observed temporal distributions.

---

# 6. Dataset Distribution Matrix

Synthetic datasets MUST explicitly vary the characteristics that drive index behavior.

## Cardinality

```text
10^4
10^5
10^6
10^7+
```

as feasible for each implementation stage.

## Duration Distribution

```text
point events
fixed short
uniform
log-normal
heavy-tail / Pareto
bimodal short+long
very long spanning intervals
```

## Start Distribution

```text
uniform
bursty
periodic
clustered
monotonic ingestion
out-of-order occurrence
adversarial random occurrence vs commit order
```

## Overlap Density

```text
sparse
moderate
dense
near-global spanning intervals
```

## Open-Extent Fraction

```text
0%
0.1%
1%
5%
10%
20%
```

## Uncertainty Geometry

```text
exact point
bounded rectangle
start chronon + exact duration diagonal segment
independent endpoint uncertainty
large uncertainty region
```

## Frame Count

```text
1 frame
2 frames
3 frames
4+ frames
```

with both correlated and deliberately decorrelated frame values.

---

# 7. Benchmark Metrics

Do not benchmark only wall-clock latency.

Collect:

```text
candidate objects
candidate blocks
bytes read
index bytes
build time
incremental update time
merge time
write amplification
read amplification
memory footprint
p50 latency
p95 latency
p99 latency
false-positive candidate ratio
false-negative count (must be zero)
```

For uncertainty:

```text
TRUE count
FALSE count
UNKNOWN count
candidate-to-exact-evaluation ratio
```

For multi-frame queries:

```text
per-frame candidate cardinality
intersection cardinality
ordering of predicate application
planner estimation error
```

---

# 8. Candidate Access Paths for First Benchmark Harness

The first reproducible harness should deliberately start simple.

## Baseline B0 — Canonical Scan

Authoritative correctness oracle.

Complexity:

\[
O(N)
\]

## Baseline B1 — Start-Sorted

Sorted by:

\[
s
\]

Use binary search to bound start predicates, then exact filter.

## Baseline B2 — End-Sorted

Sorted by:

\[
e
\]

## Baseline B3 — Dual Endpoint

Maintain independent start- and end-oriented structures and intersect candidate sets where useful.

## Candidate C1 — Endpoint 2D

Index:

\[
(s,e)
\]

using one selected multidimensional structure.

The first implementation should favor simplicity and reproducibility over claiming production suitability.

## Candidate C2 — Duration Projection

Index derived projection:

\[
(s,D)
\]

for duration-sensitive workloads.

## Candidate C3 — Midpoint/Duration Projection

Index:

\[
(M,D)
\]

as an explicitly derived analytical/index projection.

## Candidate C4 — Hierarchical / Specialized Interval Index

Implement one well-documented specialized interval algorithm from prior art after its exact reference description is re-verified.

---

# 9. Multi-Frame Research Experiments

Test at least these strategies.

## MF1 — Independent Frame Indexes

```text
occurrence index
knowledge index
observation index
...
```

Query each relevant frame independently and intersect references.

## MF2 — Composite Selected Frames

Build explicit indexes only for common frame combinations.

Example:

\[
(o_s,o_e,k_s,k_e)
\]

## MF3 — Generic Product-Space Index

Evaluate direct 2n-dimensional indexing.

## MF4 — Adaptive Planner

Choose between frame-local and composite access based on statistics.

Research question:

> At what dimensionality and selectivity does product-space indexing lose to decomposed candidate intersection?

---

# 10. Uncertainty Research Experiments

The central problem is that index geometry and semantic geometry may differ.

For a feasible region `U`, an index may store a conservative bounding region `B(U)`.

Require:

\[
U\subseteq B(U)
\]

so candidate generation cannot exclude a possible match.

Benchmark:

```text
bounding boxes
specialized correlated-region encodings
region class partitioning
exact-vs-uncertain physical separation
```

Measure the candidate inflation introduced by each approximation.

---

# 11. Planner Research

Assume no universal index until disproven.

Planner inputs may eventually require statistics such as:

```text
start distribution
end distribution
duration distribution
start/end correlation
overlap density
open-extent fraction
uncertainty class distribution
frame correlation
relation-key density
```

A major research question is whether independent histograms are sufficient or whether TCDB needs explicit endpoint-correlation statistics.

Because:

\[
e=s+D
\]

start and end are structurally correlated in many datasets.

---

# 12. Adversarial Workloads

Any proposed index should be tested against inputs designed to defeat its assumptions.

Include:

```text
all intervals same start
all intervals same end
all intervals contain query
all intervals span nearly entire time domain
alternating very-short / very-long intervals
monotonic commit order with random occurrence order
large clusters of equal timestamps
pathological open extents
high-dimensional sparse multi-frame predicates
uncertainty regions covering broad endpoint space
```

An architecture choice should not be based only on friendly random data.

---

# 13. Real-Data Validation

Synthetic tests reveal mechanisms; real data reveals whether those mechanisms matter.

Reuse or reacquire representative interval datasets from at least:

```text
transport / mobility intervals
administrative / permit intervals
network/security flow intervals
system/application telemetry where available
```

Real-data tests should preserve provenance and clearly distinguish recorded vs derived endpoints.

---

# 14. Novelty Discipline

TCDB MUST NOT claim novelty for established concepts such as:

```text
interval trees
segment trees
R-trees
GiST
endpoint transformation [s,e] -> (s,e)
space-filling curve indexing
bitemporal multidimensional indexes
LSM secondary indexes
uncertain temporal intervals
```

Potentially distinctive contributions must be isolated precisely and compared against prior art.

Candidate areas worth investigating, without current novelty claims:

```text
named-frame-aware access planning
three-valued uncertainty-aware candidate planning
adaptive selection among endpoint/projection indexes
coordinate + relation selector planning
mergeable temporal-reference hierarchy specialized for TCDB persistence
statistics that explicitly model endpoint and frame correlation
```

Any future novelty claim requires a refreshed literature search and reproducible comparison.

---

# 15. Research Gates Before Layer 3 Architecture

Layer 3 architecture SHOULD NOT be canonized until at least:

- [ ] current literature/prior-art review is source-verified;
- [ ] canonical scan oracle exists;
- [ ] start-sorted baseline implemented;
- [ ] end-sorted baseline implemented;
- [ ] dual-endpoint baseline implemented;
- [ ] at least one 2D endpoint index implemented;
- [ ] at least one specialized interval index reproduced from prior art;
- [ ] workload distribution matrix tested;
- [ ] open-extent behavior reproduced;
- [ ] uncertainty candidate semantics tested;
- [ ] at least two multi-frame strategies compared;
- [ ] all optimized results match reference scan exactly;
- [ ] real datasets validate or refute synthetic conclusions;
- [ ] planner-relevant statistics are identified;
- [ ] rejected hypotheses are recorded.

---

# 16. Immediate Research Sequence

```text
R3.0  Literature Refresh
R3.1  Reference Scan Oracle
R3.2  Synthetic Dataset Generator
R3.3  1D Endpoint Baselines
R3.4  2D Endpoint Baseline
R3.5  Specialized Prior-Art Index
R3.6  Predicate × Distribution Matrix
R3.7  Open / Indeterminate Extents
R3.8  Multi-Frame Strategies
R3.9  Real-Data Reproduction
R3.10 Planner Statistics
R3.11 Architecture Decision Record
```

Only after these stages should findings be promoted into `layer-3-coordinate-access-indexing.md` under `docs/architecture/`.
