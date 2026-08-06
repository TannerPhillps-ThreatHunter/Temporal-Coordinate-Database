# Layer 3 Literature Review — Coordinate Access & Indexing

**Status:** REPRODUCED / SOURCE-BACKED RESEARCH  
**Date:** 2026-08-06  
**Scope:** Prior art relevant to TCDB Layer 3 — Coordinate Access & Indexing

---

# 1. Purpose

This document establishes the current prior-art boundary for TCDB Layer 3 before any indexing architecture is promoted to canonical status.

The objective is not to find an algorithm that appears novel. The objective is to determine:

1. which interval and temporal indexing ideas are already established;
2. which physical projections have already been studied;
3. which workloads existing indexes optimize;
4. which assumptions fail under open intervals, uncertainty, multiple temporal frames, append-oriented persistence, or mixed predicates;
5. where TCDB may still contribute a distinct integration or algorithmic result.

No novelty claim is made by this document.

---

# 2. Core Prior-Art Finding

The mapping

```text
interval [s,e] -> point (s,e)
```

and the use of multidimensional range-query machinery over that mapping are established prior art.

This means TCDB MUST NOT claim novelty for:

- endpoint-plane representation;
- rewriting Allen interval relations as endpoint inequalities;
- using 2D range trees for Allen relations;
- using spatial indexes over interval endpoint coordinates;
- mapping multiple temporal intervals into higher-dimensional point spaces;
- using space-filling curves to linearize multidimensional interval coordinates.

The semantic use of `(start,end)` remains useful to TCDB, but it is not by itself a novel indexing contribution.

---

# 3. Prior-Art Families

## 3.1 2D Endpoint Mapping and Allen Relations

Mao, Eran, and Luo map an interval `[x,y]` directly to the 2D point `(x,y)` and rewrite Allen interval relations into range-query constraints. They implement both a 2D range tree and an augmented range tree with fractional cascading.

Source:

- https://doi.org/10.1038/s41598-019-41451-3
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6434014/

Implication for TCDB:

```text
Allen Relation -> Endpoint Constraints -> 2D Range Query
```

is an adopted prior-art technique, not a TCDB invention.

The paper also demonstrates that different Allen predicates have materially different costs even on the same index. This supports TCDB's hypothesis that query planning must be predicate-aware rather than assuming one uniform interval-query cost model.

---

## 3.2 HINT — Hierarchical Interval Partitioning

HINT is a hierarchical in-memory index for intervals. Its design partitions the temporal domain hierarchically, assigns each interval to at most two partitions per level, and reduces stored information within each partition according to interval placement.

Sources:

- https://doi.org/10.1145/3514221.3517873
- https://doi.org/10.1007/s00778-023-00798-w

The later HINT work supports Allen relationships, making HINT a mandatory Layer 3 comparison baseline for exact interval-relation workloads.

Implication for TCDB:

A hierarchical interval-specific index may outperform generic spatial indexing for some workloads. TCDB must benchmark against HINT rather than compare only against B-trees, interval trees, or R-trees.

---

## 3.3 RD-index — Range + Duration Space

RD-index indexes temporal intervals in a two-dimensional space based on temporal position and duration. The published design uses a distribution-aware grid and targets workloads combining range and duration predicates.

Sources:

- https://doi.org/10.1145/3603719.3603732
- https://doi.org/10.1007/s10619-024-07452-6

The extended publication explicitly evaluates B-tree, Interval Tree, Grid-File, period-index, R*-Tree, and HINT baselines.

Implication for TCDB:

The projection

```text
(start,end) -> (start,duration)
```

is established as an indexing coordinate system. TCDB MUST NOT claim novelty for duration-aware 2D indexing.

However, RD-index reinforces an important TCDB research principle:

```text
No universal temporal projection is optimal for every predicate family.
```

Duration-constrained workloads and pure overlap/position workloads may prefer different physical access paths.

---

## 3.4 TIDE — Duration and Endpoint

TIDE is a disk-based temporal interval index organized by duration and endpoint. It uses a two-level architecture in which a top tree orders intervals by duration and bottom trees order by endpoint. The published design uses append-only B+-trees to improve insertion behavior.

Source:

- https://doi.org/10.1145/3748777.3748785

A 2026 follow-on study also frames multiple interval indexes through a common two-dimensional corner-space representation and studies the increasing-ending-time assumption.

Source:

- https://arxiv.org/abs/2606.22773

Implication for TCDB:

TIDE is particularly important because it combines:

```text
duration-oriented partitioning
+
endpoint ordering
+
append-oriented disk structures
```

which overlaps directly with TCDB's persistent-secondary-index research direction.

Any TCDB proposal for append-friendly duration/endpoint indexing must compare against TIDE rather than treating that combination as unexplored.

---

## 3.5 UB-Tree Dual-Space Interval Indexing

Fenk, Markl, and Bayer describe interval processing by indexing the interval dual space using the UB-Tree.

Source:

- https://research.ibm.com/publications/interval-processing-with-the-ub-tree
- DOI: 10.1109/IDEAS.2002.1029652

Implication for TCDB:

Using a multidimensional point representation and then linearizing/indexing it through a multidimensional access method has long-standing prior art.

This also means that any future TCDB Morton/Z-order or other space-filling-curve index must be evaluated as an engineering choice, not presented as a new conceptual transformation.

---

## 3.6 Timeline Index

The Timeline Index was proposed as a unified temporal data structure supporting temporal aggregation, time travel, and temporal joins while remaining independent of the physical order of base data.

Source:

- https://doi.org/10.1145/2463676.2465293

Follow-on work also uses the Timeline Index as an access method for cache-efficient interval joins over Allen-style predicates.

Source:

- https://arxiv.org/abs/2008.12665

Implication for TCDB:

Layer 3 research must distinguish:

```text
selection index
join access method
time-travel/version index
```

rather than assuming one interval index naturally solves all temporal operations.

---

## 3.7 LIT and LIT+

LIT separates current/live record versions from past/dead versions instead of storing all versions in one temporal index. LIT+ extends the model under bounded memory by moving older dead versions to a disk-resident fossil index.

Sources:

- DOI: 10.1145/3639275
- https://doi.org/10.1007/s00778-026-00968-6

Implication for TCDB:

Physical separation by lifecycle state is strongly supported by prior work.

For TCDB, this directly strengthens the existing hypothesis that open/current temporal extents may deserve a separate physical access path from closed historical extents.

However:

```text
open/closed separation
```

is not itself a novel principle.

TCDB must determine whether its named-frame semantics, uncertainty model, append-oriented secondary index plane, and commit/semantic-time separation create a distinct requirement beyond LIT/LIT+.

---

## 3.8 Bitemporal Point Mappings

Bitemporal indexing has previously mapped valid-time and transaction-time intervals into multidimensional points. A 1998 study maps each temporal dimension to a two-coordinate representation, producing a higher-dimensional point for region-search access.

Source:

- https://doi.org/10.1016/S0950-5849(98)00054-8

Related work on now-relative bitemporal data uses spatial/R*-tree approaches and explicitly studies intervals whose ends move with current time.

Source:

- https://www.vldb.org/conf/1998/p345.pdf

Implication for TCDB:

The representation of two interval-valued temporal dimensions as four endpoint coordinates is established prior art.

Therefore:

```text
TemporalFrame_1 x TemporalFrame_2 -> 4D endpoint point
```

is not a novelty claim available to TCDB.

The potentially distinctive TCDB question is broader:

> Can an arbitrary catalog of semantically named temporal frames be indexed without collapsing frame meaning, while allowing the planner to compose independent frame-local and cross-frame constraints?

That remains a research question, not an established contribution.

---

## 3.9 Uncertain / Indeterminate Temporal Intervals

Sekino models an uncertain time interval as a set of possible determinate intervals and derives three retrieval outcomes: reliable, impossible, and possible matches.

Sources:

- https://doi.org/10.2197/ipsjjip.28.91
- https://arxiv.org/abs/1905.04611

This is closely aligned with TCDB's current semantic form:

```text
TRUE
FALSE
UNKNOWN
```

under feasible temporal regions.

Implication for TCDB:

TCDB MUST NOT claim novelty merely for representing uncertain temporal intervals as sets/regions of possible determinate intervals or for deriving a three-way query outcome from uncertainty.

The open research problem for TCDB Layer 3 is physical:

> How should feasible coordinate regions be indexed so that candidate generation is efficient while final TRUE/FALSE/UNKNOWN semantics remain exact?

This remains insufficiently answered by the literature reviewed here and is a high-value TCDB research target.

---

## 3.10 Production Database Baselines — PostgreSQL GiST / SP-GiST

PostgreSQL natively supports range and multirange types. GiST and SP-GiST indexes can accelerate overlap, containment, adjacency, before/after, and related range operators.

Source:

- https://www.postgresql.org/docs/current/rangetypes.html

Implication for TCDB:

A credible Layer 3 benchmark must include a production generalized-index baseline, not only academic structures.

PostgreSQL range GiST is a practical baseline for:

```text
overlap
containment
before/after
adjacency
```

and should be included in real-data benchmarking where feasible.

BRIN also provides a useful baseline for physically correlated append-oriented temporal data because its min/max summaries exploit storage locality at very low index cost.

Source:

- https://www.postgresql.org/docs/current/brin.html

---

# 4. What Is Clearly Not Novel

As of this literature refresh, TCDB MUST treat the following as established prior art:

1. representing an interval by endpoint coordinates `(start,end)`;
2. compiling Allen relations into endpoint inequalities;
3. querying Allen relations through 2D range search;
4. using R-trees / R*-trees for temporal intervals;
5. using `(start,duration)` as an interval-index projection;
6. using duration + endpoint as an interval-index organization;
7. hierarchical domain partitioning for interval indexes;
8. mapping bitemporal intervals to four endpoint dimensions;
9. using multidimensional point indexes for temporal dimensions;
10. dual-space indexing of intervals;
11. using space-filling curves to linearize multidimensional temporal points;
12. separating live/current from historical/dead temporal state;
13. representing uncertain intervals as sets of possible intervals;
14. three-way matching semantics for uncertain periods;
15. generic range GiST/SP-GiST indexing of temporal ranges;
16. unified temporal structures for time travel, joins, and aggregation.

---

# 5. Strong Remaining TCDB Research Questions

The literature substantially narrows the possible contribution. The strongest remaining Layer 3 questions are now:

## RQ1 — Named-Frame Index Composition

Given an object with independent named frames:

```text
occurrence
knowledge
observation
validity
...
```

should TCDB maintain:

- one index per frame;
- selected compound frame indexes;
- a general multidimensional structure;
- adaptive indexes chosen from workload statistics;
- or a hybrid of these?

The key requirement is semantic independence of frame identity.

## RQ2 — Uncertainty-Aware Candidate Generation

How should general feasible endpoint regions be indexed?

Rectangular endpoint uncertainty is only one special case. Correlated uncertainty may form diagonal segments, polygons, or more general feasible subsets of:

```text
T = {(s,e) | s <= e}
```

A candidate-generation algorithm must not create false negatives and final predicate evaluation must preserve TRUE/FALSE/UNKNOWN.

## RQ3 — Planner Over Projection Families

Can a cost model choose among:

```text
start-oriented
end-oriented
dual endpoint
(start,end)
(start,duration)
(midpoint,duration)
HINT-style partitioning
TIDE-style duration/endpoint
production GiST-like generalized range index
```

based on predicate class, selectivity, endpoint correlation, duration variance, openness, uncertainty, and frame?

## RQ4 — Append-Oriented Secondary Index Plane

TCDB's Layer 1/2 design separates canonical commit-order persistence from rebuildable temporal secondaries.

Research question:

> Which temporal index families can be adapted to immutable/mergeable secondary structures while retaining competitive query performance?

TIDE and LIT+ are mandatory prior-art comparisons here.

## RQ5 — Semantic Time vs Commit Time

TCDB explicitly separates semantic temporal frames from commit sequence.

Research question:

> What physical index composition best supports queries combining semantic-frame predicates with `AS OF COMMIT` visibility constraints without conflating those dimensions?

This combination may be more distinctive than indexing either dimension alone.

## RQ6 — Open-Extent Strategy

Prior art supports physical distinction between live/current and historical intervals.

TCDB must determine whether open semantic extents should be:

- physically isolated;
- normalized against a logical NOW;
- indexed by start only;
- maintained in a live index;
- or handled differently by frame.

## RQ7 — Relation-Key + Temporal-Geometry Access

TCDB separates non-temporal relation selectors from temporal geometry.

Research question:

> Should relation-key selection occur before temporal access, after temporal access, or through compound access structures under different cardinalities?

This is especially relevant for event/entity keys, source keys, Community ID, and other equivalence/correlation domains.

---

# 6. Revised Benchmark Baseline Set

Layer 3 benchmarking should include at minimum:

```text
B0  Full canonical scan
B1  Start-sorted B+-tree-like index
B2  End-sorted B+-tree-like index
B3  Dual start/end indexes
B4  Conventional interval tree
B5  2D endpoint range index
B6  R*-tree / generalized spatial baseline
B7  HINT
B8  RD-index or faithful range-duration reproduction
B9  TIDE or faithful duration/endpoint reproduction
B10 PostgreSQL range GiST/SP-GiST
B11 BRIN-style block summaries where physical ordering is correlated
```

Additional workload-specific baselines:

```text
Timeline Index / sweep-based methods for joins
LIT/LIT+ for evolving/current-vs-history workloads
```

---

# 7. Revised Research Doctrine

The literature supports a stronger principle than simply "no universal index":

```text
Temporal access-path quality is a function of
predicate family
x data distribution
x duration distribution
x endpoint correlation
x temporal-frame count
x uncertainty geometry
x lifecycle state
x physical ordering
x workload mix.
```

Therefore Layer 3 should probably define an **index plane and planner contract**, not one canonical temporal index.

This is a hypothesis to test, not yet architecture.

---

# 8. R3.0 Result

**R3.0 — Literature Refresh: COMPLETE for initial Layer 3 architecture research.**

The review is sufficient to prevent obvious prior-art collisions and to define the benchmark set.

It is not exhaustive enough to support a patentability or formal novelty opinion.

The next research steps are:

```text
R3.1  Reference Scan Oracle
R3.2  Synthetic Dataset Generator
R3.3  1D Endpoint Baselines
R3.4  2D Endpoint Baseline
R3.5  Specialized Prior-Art Index Reproduction
R3.6  Predicate x Distribution Matrix
R3.7  Open / Indeterminate Extents
R3.8  Multi-Frame Strategies
R3.9  Real-Data Reproduction
R3.10 Planner Statistics
R3.11 Architecture Decision Record
```

Layer 3 MUST remain non-canonical until these experiments produce reproducible evidence.
