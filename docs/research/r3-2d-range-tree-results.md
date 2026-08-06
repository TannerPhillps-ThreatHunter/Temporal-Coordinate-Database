# R3.4 Results — Static 2D Endpoint Range Tree

**Status:** REPRODUCED EXPERIMENTAL RESULT  
**Research Program:** Layer 3 — Coordinate Access & Indexing  
**Scope:** R3.4

## 1. Purpose

R3.4 asks whether an actual two-dimensional endpoint access structure can exploit both overlap constraints directly:

```text
start < query.end
AND
end > query.start
```

while preserving the reference-oracle invariant:

```text
IndexedQuery(D, q) == ReferenceScan(D, q)
```

The structure tested here is a static orthogonal range tree over `(start, end)`.

It is established spatial/range-search machinery and is used strictly as a prior-art baseline. It is not a TCDB novelty claim and is not proposed as the production Layer 3 index.

## 2. Structure

The baseline sorts rows by `start` in a balanced tree.

Every tree node stores the rows in its subtree again, sorted by `end`.

An overlap query:

1. finds the lossless start prefix;
2. decomposes that prefix into canonical tree nodes;
3. binary-searches each node's end-sorted array;
4. gathers rows satisfying the end-side candidate constraint;
5. applies the reference overlap predicate for final semantic validation.

Conceptually:

```text
start tree
  |
  +-- node end-array
  +-- node end-array
  +-- node end-array
  ...
```

This is intentionally expensive in memory so that it provides a clean static 2D query baseline.

## 3. Differential Correctness

The 2D range tree was tested against the same oracle matrix as the 1D baselines:

- six synthetic distributions;
- 5,000 generated intervals per distribution;
- 100 generated windows per distribution;
- HALF_OPEN and CLOSED research policies;
- explicit point extents;
- point query windows.

Result:

```text
StaticEndpointRangeTree == ReferenceScan
```

for every tested query.

## 4. Candidate Results

Experimental configuration:

```text
rows:       100,000 per distribution
queries:    200 per distribution
row seed:   7
query seed: 8
policy:     HALF_OPEN with first-class point semantics
```

Average candidates observed:

| Distribution | Actual Matches | Adaptive 1D Candidates | 2D Range Candidates |
|---|---:|---:|---:|
| uniform | 2,043.845 | 26,249.605 | 2,043.950 |
| fixed | 1,999.465 | 26,154.375 | 1,999.570 |
| mixed | 2,612.115 | 26,495.085 | 2,612.220 |
| clustered | 2,582.255 | 22,794.315 | 2,582.335 |
| equal_start | 6,873.030 | 28,692.630 | 6,873.130 |
| long | 26,939.855 | 39,252.190 | 26,939.915 |

The small excess above actual match cardinality comes from conservative endpoint candidate boundaries required to preserve first-class point extents.

## 5. Structural Cost

For 100,000 intervals, the static tree stored:

```text
1,768,928 interval references
```

or approximately:

```text
17.69 stored references per canonical interval
```

This is the expected cost class of a straightforward range tree: strong orthogonal query pruning in exchange for substantial redundant secondary state.

## 6. Findings

### F6 — 2D endpoint constraints contain real pruning power

For the first five distributions, the 2D structure reduced candidate counts from roughly 23-29% of the population under adaptive 1D selection to roughly the actual 2-7% result cardinality.

This confirms that the second endpoint is not merely descriptive metadata for overlap access.

### F7 — Candidate optimality is not storage optimality

The static range tree obtains excellent candidate pruning by duplicating row references across many tree nodes.

Therefore:

```text
minimum candidates != minimum system cost
```

A TCDB production index must account for:

- memory amplification;
- disk amplification;
- index-build cost;
- append cost;
- merge/compaction cost;
- crash/rebuild behavior;
- multi-frame multiplication.

### F8 — Multi-frame TCDB makes O(n log n) duplication especially suspicious

If each named TemporalFrame receives an independent structure with this amplification, index cost scales roughly with both row count and frame count.

That makes the static range tree useful as a query-efficiency upper baseline but unattractive as an obvious default physical design.

### F9 — Long-duration populations reduce available pruning headroom

For the `long` population, actual overlap cardinality is already about 27% of rows.

The 2D structure still avoids extra false candidates, but no indexing method can avoid emitting the actual qualifying rows.

This reinforces the need for selectivity-aware planning rather than unconditional use of the most sophisticated index.

### F10 — Layer 0 point semantics leak into 2D candidate geometry

Under the HALF_OPEN research policy, a point extent at `query.start` must remain visible even though a non-point interval ending at the same coordinate does not overlap.

Thus a pure endpoint inequality can require conservative candidate inclusion followed by semantic filtering.

This suggests a future design choice:

```text
point extents may deserve explicit physical representation or statistics
```

rather than being treated as ordinary zero-duration intervals in every access path.

## 7. Decision

R3.4 does **not** justify promoting a static range tree into Layer 3 architecture.

It establishes two benchmark facts:

1. a structure using both endpoints can dramatically reduce false candidates;
2. naïve 2D range-tree materialization has severe reference amplification.

The target for later TCDB-specific design is therefore not simply "build a 2D index."

It is:

> Preserve most of the two-endpoint pruning benefit while fitting TCDB's append-oriented, rebuildable, multi-frame persistence model at materially lower write and storage amplification.

## 8. Next Research

The next useful experiment is R3.5: reproduce at least one specialized prior-art temporal index or a faithful simplified variant, with preference for a structure designed around temporal interval workloads rather than a generic 2D range tree.

Candidates for reproduction include:

```text
HINT/HINT+
TIDE-style duration + endpoint access
RD-index-style duration/position partitioning
```

The chosen reproduction must be compared against:

```text
ReferenceScan
StartSorted
EndSorted
AdaptiveEndpoint
StaticEndpointRangeTree
```

and must report query pruning and physical amplification separately.
