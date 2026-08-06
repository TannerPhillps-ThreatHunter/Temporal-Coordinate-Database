# R3 Baseline Results — Reference Oracle and 1D Endpoint Access

**Status:** REPRODUCED EXPERIMENTAL RESULT  
**Research Program:** Layer 3 — Coordinate Access & Indexing  
**Scope:** R3.1, R3.2, R3.3

## 1. Purpose

This experiment establishes a correctness oracle and simple one-dimensional access baselines before evaluating 2D or specialized temporal indexes.

The governing correctness invariant is:

```text
IndexedQuery(D, q) == ReferenceScan(D, q)
```

Candidate-generating structures may over-select, but they MUST NOT lose valid results.

## 2. Reference Oracle

The research harness now defines an obvious full-scan evaluator for determinate temporal extents.

Two boundary policies remain experimental:

```text
HALF_OPEN
CLOSED
```

An important semantic correction emerged during testing:

> TCDB point extents (`start == end`) cannot be modeled as empty half-open intervals.

Under the HALF_OPEN research policy, non-point extents use `[start, end)`, while point extents remain first-class instantaneous coordinates.

Examples:

```text
point t overlaps [a,b) iff a <= t < b
point t overlaps point u iff t == u
```

This preserves the Layer 0 doctrine that `s=e` represents a point event.

## 3. Synthetic Populations

R3.2 currently generates six deterministic determinate populations:

```text
uniform
fixed
mixed
clustered
equal_start
long
```

They intentionally vary duration variance, endpoint correlation, clustering, and coarse/equal start behavior.

Open and uncertain extents remain deferred to R3.7.

## 4. 1D Baselines

Three baseline access paths were implemented:

### Start-Sorted

Sort by `start`, select the lossless start-side candidate prefix, then apply the reference overlap predicate.

### End-Sorted

Sort by `end`, select the lossless end-side candidate suffix, then apply the reference overlap predicate.

### Adaptive Endpoint

For each query, estimate the candidate cardinality of both 1D sides and scan whichever side is smaller.

This provides a deliberately strong 1D baseline for later planner and 2D comparisons.

## 5. Differential Correctness

Randomized differential testing was performed across:

- all six distributions;
- 5,000 generated intervals per distribution;
- 100 generated windows per distribution;
- HALF_OPEN and CLOSED policies;
- explicit point extents at multiple coordinates;
- point query windows.

Result:

```text
StartSorted == ReferenceScan
EndSorted == ReferenceScan
AdaptiveEndpoint == ReferenceScan
```

for every tested query.

No Layer 3 access path should be benchmarked for speed before satisfying this equivalence property.

## 6. Candidate Benchmark

Experimental configuration:

```text
rows:       100,000 per distribution
queries:    200 per distribution
row seed:   7
query seed: 8
policy:     HALF_OPEN with first-class point semantics
query widths: 10, 100, 1,000, 10,000, 100,000
```

The following values are average candidate counts, not production latency claims.

| Distribution | Actual Matches | Start Candidates | End Candidates | Adaptive 1D Candidates |
|---|---:|---:|---:|---:|
| uniform | 2,043.845 | 51,591.655 | 50,452.295 | 26,249.605 |
| fixed | 1,999.465 | 51,599.830 | 50,399.740 | 26,154.375 |
| mixed | 2,612.115 | 51,555.410 | 51,056.810 | 26,495.085 |
| clustered | 2,582.255 | 52,666.720 | 49,915.615 | 22,794.315 |
| equal_start | 6,873.030 | 51,640.520 | 55,232.610 | 28,692.630 |
| long | 26,939.855 | 51,638.945 | 75,300.970 | 39,252.190 |

## 7. Initial Findings

### F1 — Single-endpoint overlap access is weak for centered/random queries

Across these workloads, a start-only or end-only overlap access path often admits roughly half the population before exact filtering.

This is expected from the overlap geometry:

```text
start < query.end
AND
end > query.start
```

A one-dimensional index exploits only one half-plane at a time.

### F2 — Planner choice already matters before specialized indexes

Choosing the smaller of the start-side and end-side candidate sets materially reduces work.

The adaptive 1D baseline reduced average candidate counts to approximately:

```text
22.8% - 39.3% of the population
```

across the tested distributions.

Therefore a future specialized index MUST be compared against adaptive endpoint selection, not merely against a full scan or a single start-sorted baseline.

### F3 — Duration distribution changes the useful access side

Long-duration populations strongly inflate the end-side candidate suffix.

For the `long` distribution:

```text
start candidates: ~51.6%
end candidates:   ~75.3%
adaptive:         ~39.3%
```

This supports the existing research hypothesis that there is no universal endpoint access path independent of workload distribution.

### F4 — The exact overlap region can be much smaller than either 1D candidate region

For the first five populations, actual result cardinality averaged only about 2-7% of rows while the adaptive 1D baseline still examined about 23-29%.

This is the primary motivation for R3.4:

> Can a 2D endpoint structure exploit both inequalities directly without paying the cost of scanning or intersecting two large 1D candidate sets?

The `long` distribution is an important counterweight: actual overlap selectivity rises to roughly 27%, reducing the theoretical room for improvement.

### F5 — Point semantics affect index candidate boundaries

Preserving `s=e` point extents changes lossless candidate-generation rules.

For example, under the HALF_OPEN research policy, an end-sorted overlap baseline cannot blindly discard `end == query.start`, because a point extent exactly at `query.start` is a valid match even though a non-point interval ending there is not.

Therefore:

```text
Semantic point model -> physical candidate boundary
```

This is a concrete example of Layer 0 semantics constraining Layer 3 index design.

## 8. What This Does Not Prove

These results do NOT establish that:

- 2D indexing is always superior;
- endpoint geometry is novel;
- the current boundary policy should become canonical;
- candidate count directly predicts wall-clock latency;
- the current synthetic distributions represent production workloads;
- a single Layer 3 index should serve every predicate.

## 9. Next Experiment

R3.4 should implement at least one actual two-dimensional endpoint access structure and compare it against:

```text
ReferenceScan
StartSorted
EndSorted
AdaptiveEndpoint
```

The comparison must measure separately:

```text
correctness
candidate cardinality
index build cost
memory footprint
query CPU cost
update / merge cost
```

A 2D structure should not be promoted merely because its candidate cardinality is lower if its maintenance or memory costs make it inferior for TCDB's append-oriented architecture.
