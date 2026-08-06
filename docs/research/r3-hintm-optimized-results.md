# R3.5b HINT^m Optimized Query Reproduction

**Status:** REPRODUCED EXPERIMENTAL RESULT  
**Research Program:** Layer 3 — Coordinate Access & Indexing  
**Prior Art:** HINT / HINT^m by Christodoulou, Bouros, and Mamoulis

## 1. Objective

R3.5b reproduces the duplicate-avoidance access pattern used by HINT^m for generalized overlap queries and compares it with the conservative R3.5a traversal.

The purpose is not to claim HINT^m as TCDB-native work. It is to establish a stronger prior-art baseline before Layer 3 architecture is proposed.

## 2. Source Verification

The authors' published paper and official `pbour/hint` source were used to verify two details before implementation:

1. original/replica classification during canonical-cover assignment;
2. optimized overlap traversal across first, interior, and last relevant partitions.

The official source confirms that each interval has one original reference and that a right-edge cover is only classified as original in the special case where it exhausts the remaining cover before ascending.

For overlap queries, the optimized traversal performs:

```text
first relevant partition:
    originals + replicas

interior relevant partitions:
    originals only

last relevant partition:
    originals only

root:
    originals only
```

This eliminates duplicate result production when the original/replica invariant is correct.

## 3. TCDB Boundary-Semantics Adaptation

Published HINT/HINT^m assumes closed intervals.

TCDB research currently keeps two experimental policies:

```text
CLOSED
HALF_OPEN + first-class point extents
```

For `CLOSED`, interior HINT^m originals can be emitted without an overlap predicate comparison as established by HINT.

For `HALF_OPEN`, the TCDB reproduction conservatively rechecks every scanned reference because TCDB's point-aware half-open semantics are not the semantic model proved by HINT.

Therefore R3.5b separates:

```text
physical reference scans
predicate comparisons
```

A low HINT comparison count under the closed model must not be silently transferred to TCDB's eventual model before boundary semantics are frozen.

## 4. Differential Validation

The corrected optimized traversal was validated against the TCDB reference scan across:

- all six synthetic distributions;
- 10,003 extents per distribution in the extended validation run;
- 153 query windows per distribution;
- HALF_OPEN and CLOSED policies;
- explicit point extents at domain boundaries and midpoint;
- point query windows.

Additional invariants:

```text
original_reference_count == indexed_object_count
optimized_duplicate_emissions == 0
optimized_result == ReferenceScan
```

All tested cases passed.

## 5. Benchmark Configuration

```text
rows:       100,000 per distribution
queries:    200 per distribution
row seed:   7
query seed: 8
m:          10
```

The benchmark measures candidate/reference work, not production latency.

## 6. HALF_OPEN TCDB-Adapted Results

| Distribution | Refs / Row | Matches | Conservative Scans | Optimized Scans | Scan Reduction |
|---|---:|---:|---:|---:|---:|
| uniform | 1.257 | 2,043.8 | 2,657.6 | 2,141.0 | 19.4% |
| fixed | 1.052 | 1,999.5 | 2,201.9 | 2,098.4 | 4.7% |
| mixed | 1.644 | 2,612.1 | 4,008.5 | 2,724.3 | 32.0% |
| clustered | 2.355 | 2,582.3 | 5,709.3 | 2,644.1 | 53.7% |
| equal_start | 5.194 | 6,873.0 | 15,480.2 | 6,975.7 | 54.9% |
| long | 7.559 | 26,939.9 | 38,515.2 | 27,061.2 | 29.7% |

Under the HALF_OPEN research policy, every optimized scan is currently rechecked by the TCDB predicate oracle.

## 7. CLOSED Prior-Art Comparison Behavior

Using the closed-interval model assumed by HINT, the physical optimized scan counts are the same, but many interior results require no predicate comparison.

| Distribution | Optimized Scans | Predicate Comparisons | Comparison-Free Fraction |
|---|---:|---:|---:|
| uniform | 2,141.0 | 217.0 | 89.9% |
| fixed | 2,098.4 | 170.7 | 91.9% |
| mixed | 2,724.3 | 827.2 | 69.6% |
| clustered | 2,644.1 | 455.4 | 82.8% |
| equal_start | 6,975.7 | 5,131.5 | 26.4% |
| long | 27,061.2 | 25,261.5 | 6.7% |

This reproduces the qualitative HINT result that many returned intervals can be emitted without comparisons, but also shows that the benefit depends strongly on interval/query geometry.

## 8. Findings

### O1 — Correct original/replica classification is what makes duplicate-free traversal possible

The optimized evaluator emitted zero duplicates in every differential test after the structural correction.

The earlier failed shortcut was therefore an implementation/reproduction problem plus incomplete HINT^m boundary handling, not evidence against the HINT method.

### O2 — Optimized HINT^m reduces physical reference access, not just semantic candidates

The conservative R3.5a path often examined many replicas that were later deduplicated.

The optimized rule avoids scanning replicas outside the first relevant partition at each level, reducing physical-reference work by roughly:

```text
4.7% to 54.9%
```

across the current workloads.

### O3 — Optimized scans approach result cardinality

At `m=10`, average optimized scanned references were only about:

```text
1.004x to 1.050x
```

actual result cardinality across the six tested distributions.

This makes HINT^m a substantially stronger baseline than candidate cardinality alone suggested.

### O4 — Comparison savings are workload-dependent

Short/fixed/uniform populations allowed most closed-model results to be emitted comparison-free.

Long intervals largely eliminate this benefit because many results remain in boundary partitions that require comparisons.

Therefore planner statistics should eventually describe not only selectivity, but also expected interval replication and boundary-partition pressure.

### O5 — TCDB boundary semantics can materially change physical execution

Under the current HALF_OPEN + point model, TCDB deliberately forfeits HINT's comparison-free interior shortcut until the semantics are proven compatible.

This reinforces a project-wide rule:

```text
Semantic Model -> Physical Algorithm
```

not the reverse.

## 9. What R3.5b Does Not Prove

R3.5b does not prove that:

- HINT^m should become TCDB's canonical index;
- closed intervals should become TCDB's boundary model;
- Python reference counts predict production CPU/cache behavior;
- the current `m=10` setting is optimal;
- HINT's remaining subdivisions, sorting, sparsity, cache, and storage optimizations are unnecessary.

## 10. Next Experiment

R3.5c should reproduce the published bottom-up comparison-minimization state (`foundzero` / `foundone`, corresponding to the paper's boundary-comparison state) and measure whether it further reduces predicate comparisons without changing physical scan correctness.

After R3.5c, the research program can decide whether to reproduce HINT subdivisions/sorting before advancing to the broader R3.6 predicate x distribution matrix.
