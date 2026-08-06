# R3.5 HINT^m Structural Reproduction

**Status:** REPRODUCED STRUCTURAL BASELINE  
**Research Program:** Layer 3 — Coordinate Access & Indexing  
**Prior Art:** HINT / HINT^m by Christodoulou, Bouros, and Mamoulis

## 1. Scope

This experiment reproduces the structural core of HINT^m as a prior-art baseline for TCDB research.

It is **not** a claim that TCDB invented hierarchical interval partitioning, canonical-cover assignment, original/replica classification, or HINT^m query processing.

Primary references:

- Christodoulou, Bouros, Mamoulis, *HINT: a hierarchical interval index for Allen relationships*, VLDB Journal 33, 73-100 (2024).
- Official source repository: `https://github.com/pbour/hint`

## 2. Reproduced Mechanics

The R3.5 baseline implements:

1. linear endpoint normalization into `[0, 2^m-1]`;
2. bottom-up hierarchical decomposition;
3. canonical-cover interval assignment;
4. at most two assignments per level;
5. first assignment classified as `original`;
6. subsequent assignments classified as `replica`;
7. configurable hierarchy depth `m`.

The assignment is based on the HINT/HINT^m procedure described in the paper: at a level, an odd left boundary and/or even right boundary is assigned to a partition, the covered boundary is removed, and both boundaries are shifted to the parent level.

## 3. Conservative TCDB Query Evaluator

For this first reproduction, query evaluation is intentionally more conservative than the optimized HINT^m algorithms.

For every level:

1. map the query boundaries into the hierarchy;
2. visit every partition between the mapped query boundaries;
3. collect both originals and replicas;
4. deduplicate object ids;
5. apply the TCDB reference overlap predicate.

This sacrifices some of HINT^m's published query efficiency in exchange for a simple differential-correctness boundary.

The index therefore measures two separate costs:

```text
unique_candidates
scanned_references
```

The first measures semantic over-selection after hierarchy pruning.
The second exposes physical duplicate/reference work caused by replication across levels.

## 4. Correctness

Randomized differential testing compared HINT^m results against the full reference oracle across:

- all six existing synthetic distributions;
- HALF_OPEN and CLOSED experimental boundary policies;
- explicit point extents;
- point query windows;
- hierarchy depths used in the experiment.

Result:

```text
HintMIndex == ReferenceScan
```

for the conservative evaluator in the tested workloads.

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

The static 2D range-tree baseline previously required about 17.7 stored references per row at 100k rows.

Therefore HINT^m demonstrates a much more favorable pruning/space tradeoff for these workloads.

### H2 — `m` is a genuine physical planning parameter

Increasing `m` generally reduces unique candidate over-selection but increases stored-reference amplification and, in the conservative evaluator, scanned-reference work.

This confirms that hierarchy depth should not be treated as a fixed semantic constant.

### H3 — Long and equal-start distributions remain adversarial

The `long` and `equal_start` populations produce substantially higher replication than uniform/fixed populations.

At `m=10`:

```text
equal_start: ~5.19 references/row
long:        ~7.56 references/row
```

This reinforces the research requirement for workload-aware index planning and statistics.

### H4 — Unique candidates and physical references are different costs

At finer hierarchies, semantic over-selection becomes tiny while scanned-reference work can continue increasing because intervals appear in several hierarchy partitions.

Therefore Layer 3 benchmarking must keep separate metrics for:

```text
result cardinality
unique candidate cardinality
physical reference accesses
storage amplification
```

### H5 — Published HINT^m optimizations matter

The paper's original/replica query rules, subdivisions, sorting, sparsity/skew handling, and storage optimizations are not optional details if the goal is to reproduce published HINT^m performance.

The current TCDB reproduction establishes the hierarchy and correctness baseline, not final HINT^m performance.

## 7. Failed Optimization Attempt

A direct shortcut was tested using the comparison-free HINT duplicate-avoidance rule:

```text
first relevant partition -> originals + replicas
later relevant partitions -> originals only
```

Applying this shortcut directly to the discretized HINT^m baseline with TCDB's experimental point semantics produced duplicate and/or mismatch cases on mixed, clustered, equal-start, and long populations.

This result does **not** refute HINT or HINT^m.

It shows that TCDB must reproduce the full HINT^m boundary-comparison logic rather than mixing the comparison-free HINT query rule with the discretized HINT^m structure.

The failed shortcut is retained as research provenance.

## 8. Comparison With Earlier Baselines

For `m=10`, HINT^m reduces candidate cardinality far below the adaptive 1D baseline:

```text
uniform:
  Adaptive 1D ~26,250 candidates
  HINT^m      ~2,141 candidates
  matches     ~2,044

mixed:
  Adaptive 1D ~26,495 candidates
  HINT^m      ~2,724 candidates
  matches     ~2,612
```

It approaches the pruning quality of the static 2D range tree while using dramatically fewer stored references.

This makes HINT^m the strongest current prior-art baseline in the TCDB Layer 3 research program.

## 9. Current Interpretation

R3.5 does not justify inventing a TCDB-native interval index yet.

Instead, it raises the bar:

> Any TCDB-native access method must demonstrate a meaningful advantage over a tuned HINT^m-class baseline under a workload TCDB specifically requires, such as named multi-frame composition, uncertain feasible regions, commit-time composition, or relation-key + temporal-geometry planning.

## 10. Next Work

R3.5b should reproduce more of the published HINT^m query algorithm, including boundary comparisons and original/replica duplicate avoidance.

After that, R3.6 should broaden benchmarking from overlap-only queries into a predicate x distribution matrix.
