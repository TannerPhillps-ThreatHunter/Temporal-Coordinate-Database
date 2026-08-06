# R3.5a HINT^m Structural Reproduction

**Status:** REPRODUCED STRUCTURAL BASELINE — CORRECTED  
**Research Program:** Layer 3 — Coordinate Access & Indexing  
**Prior Art:** HINT / HINT^m by Christodoulou, Bouros, and Mamoulis

## 1. Scope

This experiment reproduces the structural core of HINT^m as a prior-art baseline for TCDB research.

It is **not** a claim that TCDB invented hierarchical interval partitioning, canonical-cover assignment, original/replica classification, or HINT^m query processing.

Primary references:

- Christodoulou, Bouros, Mamoulis, *HINT: a hierarchical interval index for Allen relationships*, VLDB Journal 33, 73-100 (2024).
- Official source repository: `https://github.com/pbour/hint`

## 2. Reproduced Mechanics

The corrected R3.5a baseline implements:

1. linear endpoint normalization into `[0, 2^m-1]`;
2. bottom-up hierarchical decomposition;
3. canonical-cover interval assignment;
4. at most two assignments per level;
5. exactly one `original` reference per indexed interval;
6. zero or more `replica` references;
7. configurable hierarchy depth `m`.

### Correction discovered during R3.5b

The first R3.5a implementation classified the first emitted canonical-cover partition as `original` too aggressively.

The official HINT^m source contains a more precise right-edge rule. If the left edge has not yet produced an original, an even right-edge partition is classified as original **only when removing that right edge exhausts the remaining cover**. Otherwise that right-edge entry is a replica and the original may occur at a coarser parent level.

Example for an exact `[0,15]` mapped domain:

```text
interval [4,6]

bottom partition 6 -> replica
parent partition 2 -> original
```

The repository implementation and tests were corrected before R3.5b was accepted.

This correction does not change total reference amplification, but it is essential for HINT's duplicate-avoidance query rules.

## 3. Conservative TCDB Query Evaluator

The R3.5a query evaluator remains intentionally more conservative than the optimized HINT^m algorithms.

For every level it:

1. maps the query boundaries into the hierarchy;
2. visits every partition between the mapped query boundaries;
3. collects both originals and replicas;
4. deduplicates object ids;
5. applies the TCDB reference overlap predicate.

This establishes a simple differential-correctness baseline before optimized traversal.

The index measures separately:

```text
unique_candidates
scanned_references
```

## 4. Correctness

Randomized differential testing compared the conservative HINT^m evaluator against the full reference oracle across:

- all six synthetic distributions;
- HALF_OPEN and CLOSED experimental boundary policies;
- explicit point extents;
- point query windows;
- multiple hierarchy depths.

After the original/replica correction, an additional invariant is asserted:

```text
original_reference_count == indexed_object_count
```

Result:

```text
HintMIndex.query_overlap == ReferenceScan
```

for the tested workloads.

## 5. Parameter Sweep

Experimental configuration:

```text
rows:       100,000 per distribution
queries:    200 per distribution
row seed:   7
query seed: 8
m values:   8, 10, 12
policy:     HALF_OPEN with first-class point semantics
```

These are research-harness measurements, not production latency claims.

### m = 8

| Distribution | Refs / Row | Matches | Unique Candidates | Scanned References |
|---|---:|---:|---:|---:|
| uniform | 1.06 | 2,043.8 | 2,435.9 | 2,563.4 |
| fixed | 1.01 | 1,999.5 | 2,396.9 | 2,422.6 |
| mixed | 1.31 | 2,612.1 | 3,088.9 | 3,695.8 |
| clustered | 1.47 | 2,582.3 | 2,837.8 | 3,919.8 |
| equal_start | 3.47 | 6,873.0 | 7,277.0 | 12,225.0 |
| long | 5.59 | 26,939.9 | 27,429.7 | 35,479.4 |

### m = 10

| Distribution | Refs / Row | Matches | Unique Candidates | Scanned References |
|---|---:|---:|---:|---:|
| uniform | 1.26 | 2,043.8 | 2,141.0 | 2,657.6 |
| fixed | 1.05 | 1,999.5 | 2,098.4 | 2,201.9 |
| mixed | 1.64 | 2,612.1 | 2,724.2 | 4,008.5 |
| clustered | 2.35 | 2,582.3 | 2,644.1 | 5,709.3 |
| equal_start | 5.19 | 6,873.0 | 6,975.7 | 15,480.2 |
| long | 7.56 | 26,939.9 | 27,061.2 | 38,515.2 |

### m = 12

| Distribution | Refs / Row | Matches | Unique Candidates | Scanned References |
|---|---:|---:|---:|---:|
| uniform | 1.89 | 2,043.8 | 2,067.9 | 3,843.4 |
| fixed | 1.20 | 1,999.5 | 2,023.9 | 2,430.8 |
| mixed | 2.15 | 2,612.1 | 2,641.3 | 4,942.1 |
| clustered | 3.77 | 2,582.3 | 2,601.0 | 8,968.3 |
| equal_start | 7.11 | 6,873.0 | 6,901.8 | 19,262.9 |
| long | 9.55 | 26,939.9 | 26,970.8 | 41,934.2 |

## 6. Findings

### H1 — HINT^m captures most of the 2D pruning benefit with much lower reference amplification

For ordinary distributions at `m=10`, unique candidate counts are close to true result cardinality while reference amplification remains approximately 1.05-2.35x.

The static 2D range-tree baseline required about 17.7 stored references per row at 100k rows.

### H2 — `m` is a genuine physical planning parameter

Increasing `m` generally reduces unique candidate over-selection while increasing stored-reference amplification.

Hierarchy depth is therefore a physical tuning parameter, not a semantic constant.

### H3 — Long and equal-start distributions remain adversarial

At `m=10`:

```text
equal_start: ~5.19 references/row
long:        ~7.56 references/row
```

This reinforces the requirement for workload-aware planning and statistics.

### H4 — Unique candidates and physical references are different costs

Layer 3 benchmarking must keep separate metrics for:

```text
result cardinality
unique candidate cardinality
physical reference accesses
storage amplification
predicate comparisons
```

### H5 — Correct originals/replicas classification is semantically important to the physical algorithm

The structural index could remain lossless under conservative deduplication even with the earlier classification mistake, which made the error easy to miss.

The optimized HINT traversal depends on the stronger invariant:

```text
exactly one original per interval
```

This is an example of why a conservative oracle-backed path should precede optimization.

## 7. Superseded Failed Shortcut Interpretation

An earlier experiment applied:

```text
first relevant partition -> originals + replicas
later relevant partitions -> originals only
```

and observed duplicates/mismatches.

That experiment is now understood to have mixed two problems:

1. the initial reproduction contained the original/replica classification error described above;
2. HINT^m discretization still requires boundary comparisons, unlike comparison-free HINT.

The failure remains useful provenance, but it is **not** evidence that the published HINT^m duplicate-avoidance rule fails.

R3.5b reproduces the corrected rule directly against the authors' reference source.

## 8. Current Interpretation

HINT^m remains the strongest current prior-art interval-index baseline for TCDB Layer 3 research.

Any TCDB-native access method must demonstrate a meaningful advantage for a TCDB-specific requirement such as:

```text
named multi-frame composition
uncertain feasible regions
semantic-time + commit-time composition
relation-key + temporal-geometry planning
append-oriented rebuildable index maintenance
```

## 9. Next Work

R3.5b reproduces the duplicate-free optimized query path and measures physical-reference and predicate-comparison savings.

A subsequent R3.5c should reproduce the published bottom-up comparison-minimization flags and then the partition subdivisions/sorting optimizations before R3.6 broadens the predicate matrix.
