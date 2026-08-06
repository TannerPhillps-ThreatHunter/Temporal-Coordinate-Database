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

Experimental code lives under:

```text
research/layer3/
```

Differential tests live under:

```text
tests/test_layer3_reference.py
```

The reproducible candidate benchmark lives under:

```text
benchmarks/layer3_overlap_baselines.py
```

## Layer 3 Research Status

```text
R3.0  Literature Refresh                    COMPLETE
R3.1  Reference Scan Oracle                 COMPLETE
R3.2  Synthetic Dataset Generator           COMPLETE
R3.3  1D Endpoint Baselines                 COMPLETE
R3.4  2D Endpoint Baseline                  COMPLETE
R3.5  Specialized Prior-Art Index           NEXT
R3.6  Predicate x Distribution Matrix       PENDING
R3.7  Open / Indeterminate Extents          PENDING
R3.8  Multi-Frame Strategies                PENDING
R3.9  Real-Data Reproduction                PENDING
R3.10 Planner Statistics                    PENDING
R3.11 Architecture Decision Record          PENDING
```

Layer 3 remains non-canonical until the experimental program produces reproducible evidence.
