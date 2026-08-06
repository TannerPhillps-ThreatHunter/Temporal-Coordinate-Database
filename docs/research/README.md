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

## Current Research Programs

- `layer-3-coordinate-access-indexing.md` — hypotheses, experiments, and benchmark plan for Coordinate Access & Indexing.
- `layer-3-literature-review.md` — source-backed prior-art review and novelty boundary for Layer 3.
- `r3-baseline-results.md` — R3.1-R3.3 reference-oracle, synthetic-population, and 1D endpoint results.
- `r3-2d-range-tree-results.md` — R3.4 static 2D endpoint range-tree results and amplification analysis.
- `r3-hintm-results.md` — corrected R3.5a HINT^m structural reproduction and parameter sweep.
- `r3-hintm-optimized-results.md` — R3.5b duplicate-free HINT^m query reproduction and scan/comparison results.

Experimental code lives under:

```text
research/layer3/
```

Current access-path implementations include:

```text
reference.py
synthetic.py
baselines.py
range_tree.py
hint_m.py
```

Differential tests live under:

```text
tests/test_layer3_reference.py
```

Reproducible candidate benchmarks live under:

```text
benchmarks/layer3_overlap_baselines.py
benchmarks/layer3_hint_m.py
```

## Layer 3 Research Status

```text
R3.0   Literature Refresh                       COMPLETE
R3.1   Reference Scan Oracle                    COMPLETE
R3.2   Synthetic Dataset Generator              COMPLETE
R3.3   1D Endpoint Baselines                    COMPLETE
R3.4   2D Endpoint Baseline                     COMPLETE
R3.5a  HINT^m Structural Baseline               COMPLETE
R3.5b  HINT^m Duplicate-Free Query Reproduction COMPLETE
R3.5c  HINT^m Bottom-Up Comparison Minimization NEXT
R3.6   Predicate x Distribution Matrix          PENDING
R3.7   Open / Indeterminate Extents             PENDING
R3.8   Multi-Frame Strategies                   PENDING
R3.9   Real-Data Reproduction                   PENDING
R3.10  Planner Statistics                       PENDING
R3.11  Architecture Decision Record             PENDING
```

## Current Evidence Boundary

The strongest current prior-art baseline is corrected, optimized HINT^m.

At `m=10`, the duplicate-free query path reduces physical reference scans to roughly 1.004x-1.050x actual result cardinality in the current synthetic overlap workloads, while reference amplification ranges from roughly 1.05x on fixed short intervals to 7.56x on the adversarial long-interval population.

The TCDB research program MUST NOT propose a new interval index merely because it outperforms a full scan, a single endpoint index, or the static range-tree baseline.

A TCDB-native access method would need to demonstrate a meaningful advantage over tuned prior art for a TCDB-specific requirement such as:

```text
named multi-frame composition
uncertain feasible regions
semantic-time + commit-time composition
relation-key + temporal-geometry planning
append-oriented rebuildable index maintenance
```

Layer 3 remains non-canonical until the experimental program produces reproducible evidence and R3.11 records an explicit architecture decision.
