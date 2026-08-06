# E0 — Temporal Event Geometry Results

**Status:** REPRODUCED EXPERIMENTAL RESULT  
**Program:** Event Geometry  
**Canonical:** No

## 1. Question

Can relation-selected intervals and trajectory signatures become independently addressable and indexable computational structures while remaining derived from canonical temporal events?

This experiment intentionally excludes computational position `X` and causality.

## 2. Experimental Model

Canonical event:

```text
Event
├── event_id
├── entity_id
├── event_type
├── start
└── end
```

Derived relation-bound interval:

```text
EventInterval
├── relation
├── source_event_id
├── target_event_id
├── entity_id
├── signed_gap
├── delta_start
├── delta_end
└── duration_delta
```

Composite address:

```text
(relation, source_event_id, target_event_id)
```

Derived trajectory:

```text
Trajectory
├── selector
├── entity_id
├── ordered event_ids
└── ordered interval_keys
```

Composite address:

```text
(selector, entity_id)
```

The initial relation is:

```text
same_entity_next
```

and ordering is explicit by `(start, end, event_id)`.

## 3. Synthetic Population

The experiment generated:

```text
5 trajectory families
300 entities per family
24 events per entity
1,500 trajectories
36,000 events
34,500 selected consecutive EventIntervals
```

Families:

```text
periodic
alternating
burst
accelerating
random
```

Absolute trajectory offsets are randomized independently of family.

The experiment therefore tests whether relative temporal geometry retains behavioral structure after absolute temporal translation.

## 4. E0.1 — Translation-Invariant Trajectory Retrieval

Two leave-one-out nearest-neighbor representations were compared.

### Absolute temporal representation

```text
[start_1, start_2, ..., start_n]
```

Accuracy:

```text
20.07%
```

Five equally populated classes imply a 20% chance baseline.

### Interval-displacement representation

```text
[Δstart_1, Δstart_2, ..., Δstart_(n-1)]
```

Accuracy:

```text
98.27%
```

### Interpretation

The experiment demonstrates that a trajectory's inter-event geometry can preserve structure that is obscured by arbitrary absolute temporal translation.

It does NOT establish that interval signatures are novel; event-sequence and interval-sequence similarity have substantial prior art.

It DOES establish a useful TCDB property to continue testing:

```text
Absolute temporal position can vary
while
relation-selected temporal geometry remains stable.
```

## 5. E0.2 — Independent Scalar Interval Index

A sorted access path was built directly over the derived `delta_start` coordinate.

Workload:

```text
34,500 EventIntervals
1,000 range queries
```

Correctness:

```text
IntervalIndex(query) == FullIntervalScan(query)
```

for every generated range query.

Average result cardinality:

```text
~1,267 intervals/query
```

A full scan examines:

```text
34,500 intervals/query
```

while the sorted index performs logarithmic boundary lookup plus result-range access.

In the current NumPy research harness, the indexed query loop was also faster than vector full scans, but wall-clock timings are implementation-specific and are not treated as architecture evidence.

### Interpretation

A derived EventInterval can be queried independently without becoming canonical information.

This supports the distinction:

```text
First-Class Addressability != Canonical Primitive
```

## 6. E0.3 — Rolling Interval-Signature Index

A simple exact hash index was built over quantized rolling 4-interval signatures.

This is not an approximate-nearest-neighbor structure and is not proposed as a production index.

Results:

| Quantization Bin | Distinct Signatures | Query Coverage | Mean Same-Family Purity | Mean Candidates When Covered |
|---:|---:|---:|---:|---:|
| 5 | 10,597 | 73.68% | 99.16% | 33.87 |
| 10 | 6,910 | 79.61% | 98.56% | 355.74 |
| 20 | 5,537 | 84.05% | 98.25% | 2,020.54 |

### Interpretation

Quantized interval signatures expose a familiar indexing tradeoff:

```text
finer quantization
    -> fewer matches / smaller candidate sets
    -> lower coverage

coarser quantization
    -> higher coverage
    -> larger candidate sets
```

The high family purity is expected because the synthetic families were deliberately defined by temporal spacing patterns.

This validates the harness, not novelty.

## 7. E0.4 — All-Pairs Explosion

For 36,000 events, the number of unordered event pairs is:

```text
647,982,000
```

The explicit `same_entity_next` relation selects only:

```text
34,500
```

EventIntervals.

Ratio:

```text
~18,782 : 1
```

### Finding

An event geometry cannot practically mean "materialize the interval between every event pair."

Relation selection is therefore foundational to useful interval geometry:

```text
Relation Selector
      ↓
Event Pair Population
      ↓
EventInterval Geometry
```

This reinforces the existing TCDB doctrine:

```text
Relation selection determines observability.
```

## 8. Primitive Test

The experiment does not justify promoting either `EventInterval` or `Trajectory` to a new canonical primitive.

For the tested semantics:

```text
EventInterval = f(Canonical Events, Relation Selector)
Trajectory    = g(Canonical Events, Selector, Ordering)
```

Both are losslessly reconstructible.

The current strongest interpretation is therefore:

```text
Event             Canonical candidate
EventInterval     Derived, addressable, indexable
Trajectory        Derived, addressable, indexable
IntervalSignature Derived/indexed analytical projection
```

This remains a research conclusion, not Layer 0 doctrine.

## 9. What E0 Does Not Establish

E0 does NOT show that:

- TCDB is a computational spacetime system;
- event geometry is a novel field;
- trajectories should be persisted canonically;
- entity identity can be reconstructed from temporal continuity alone;
- interval signatures remain robust under missing/duplicate events;
- interval signatures remain useful under temporal scaling;
- interval geometry implies causality;
- the same model works for multiple temporal frames;
- computational position `X` is necessary.

## 10. Next Falsification Phase — E1

E1 should attack the positive E0 result with operational messiness.

Planned tests:

```text
E1.1  Temporal scale variation
E1.2  Missing events
E1.3  Duplicate events
E1.4  Timestamp jitter / clock uncertainty
E1.5  Variable trajectory length
E1.6  Selector contamination / identity ambiguity
E1.7  Signature metric comparison
E1.8  Real-data reproduction
```

Only if useful geometry survives these tests should the program consider persistence architecture or introduce computational position `X`.
