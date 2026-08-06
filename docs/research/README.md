# TCDB Research

Research documents are **non-canonical evidence artifacts**.

They exist to test assumptions before architectural promotion.

A research result may be:

```text
HYPOTHESIS
EXPERIMENTAL
REPRODUCED
REFUTED
SUPERSEDED
PROMOTED
```

Research findings MUST NOT silently become architecture. Promotion requires an explicit architecture revision or specification change.

# Research Program A — Layer 3 Coordinate Access & Indexing

Current evidence artifacts:

- `layer-3-coordinate-access-indexing.md` — hypotheses, experiments, and benchmark plan.
- `layer-3-literature-review.md` — source-backed prior-art review and novelty boundary.
- `r3-baseline-results.md` — R3.1-R3.3 reference-oracle, synthetic-population, and 1D endpoint results.
- `r3-2d-range-tree-results.md` — R3.4 static 2D endpoint range-tree results.
- `r3-hintm-results.md` — corrected R3.5a HINT^m structural reproduction.
- `r3-hintm-optimized-results.md` — R3.5b duplicate-free HINT^m query reproduction.

Experimental code:

```text
research/layer3/
```

Status:

```text
R3.0   Literature Refresh                       COMPLETE
R3.1   Reference Scan Oracle                    COMPLETE
R3.2   Synthetic Dataset Generator              COMPLETE
R3.3   1D Endpoint Baselines                    COMPLETE
R3.4   2D Endpoint Baseline                     COMPLETE
R3.5a  HINT^m Structural Baseline               COMPLETE
R3.5b  HINT^m Duplicate-Free Query Reproduction COMPLETE
R3.5c  HINT^m Bottom-Up Comparison Minimization PAUSED
R3.6   Predicate x Distribution Matrix          PENDING
R3.7   Open / Indeterminate Extents             PENDING
R3.8   Multi-Frame Strategies                   PENDING
R3.9   Real-Data Reproduction                   PENDING
R3.10  Planner Statistics                       PENDING
R3.11  Architecture Decision Record             PENDING
```

R3.5c is paused, not abandoned, while the Event Geometry hypothesis is tested.

The strongest current interval-index prior-art baseline remains corrected, optimized HINT^m.

# Research Program B — Event Geometry

Working hypothesis:

> TCDB may be the temporal projection of a more general event geometry, but that interpretation must earn its place through falsifiable behavior rather than analogy.

Evidence artifacts:

- `event-geometry-literature-review.md` — prior-art boundary around interval sequences, process mining, temporal motifs, and inter-event models.
- `e0-temporal-event-geometry-results.md` — first temporal-only interval/trajectory experiment.

Experimental code:

```text
research/event_geometry/
```

Differential/unit tests:

```text
tests/test_event_geometry.py
```

Status:

```text
E0.0  Prior-Art Boundary                         COMPLETE
E0.1  Relation-Bound EventInterval Model         COMPLETE
E0.2  Relation-Selected Trajectory Model         COMPLETE
E0.3  Translation-Invariant Interval Retrieval   COMPLETE
E0.4  Independent Scalar Interval Index          COMPLETE
E0.5  Rolling Interval-Signature Index           COMPLETE
E0.6  Primitive / Persistence Necessity Test     COMPLETE

E1.1  Temporal Scale Variation                   NEXT
E1.2  Missing Events                             PENDING
E1.3  Duplicate Events                           PENDING
E1.4  Timestamp Jitter / Clock Uncertainty       PENDING
E1.5  Variable Trajectory Length                 PENDING
E1.6  Selector Contamination / Identity Ambiguity PENDING
E1.7  Signature Metric Comparison                PENDING
E1.8  Real-Data Reproduction                     PENDING

E2    Multi-Frame Event Geometry                 DEFERRED
E3    Computational Position X                   DEFERRED
E4    Causal / Topological Geometry              DEFERRED
```

## Current E0 Evidence

The first temporal-only experiment supports three narrow findings:

1. relation-selected interval displacement can preserve behavior under arbitrary absolute temporal translation;
2. derived EventIntervals can be independently indexed without becoming canonical state;
3. all-pairs interval materialization is combinatorially unacceptable, so relation selection is part of the geometry definition.

Current research interpretation:

```text
Event             Canonical candidate
EventInterval     Derived + independently addressable/indexable
Trajectory        Derived + independently addressable/indexable
IntervalSignature Derived/indexed analytical projection
```

This is not yet architecture doctrine.

# Shared Evidence Boundary

TCDB MUST NOT claim novelty for established machinery merely because it is composed into the project.

Known prior-art territory includes:

```text
interval relations
interval indexing
interval-sequence mining
inter-event time modeling
trace / process sequence analysis
object-centric event logs
temporal motifs
event-interval sequence similarity
```

A TCDB-native contribution must demonstrate a meaningful semantic, operational, or asymptotic advantage for a requirement that current systems handle poorly or unnaturally.

Potential differentiating requirements remain:

```text
named temporal-frame composition
uncertain feasible regions
semantic-time + commit-time composition
relation-key + temporal-geometry planning
append-oriented rebuildable index maintenance
relation-bound event geometry under incomplete observation
future computational-position + temporal composition
```

No new architecture layer will be promoted from these programs until experiments are reproducible and an explicit architecture decision records the evidence.
