# E1 — Trajectory Robustness Results

**Status:** EXPERIMENTAL / IN PROGRESS  
**Program:** Event Geometry  
**Canonical:** No

## E1.1 — Temporal Scale Variation

### Question

Does an interval trajectory retain recognizable geometry when the entire temporal pattern is uniformly stretched or compressed?

This distinguishes two different query intents:

```text
cadence-sensitive similarity
shape-sensitive similarity
```

They must not be silently conflated.

## Experiment

The five E0 trajectory families were regenerated with an independent multiplicative time scale for each trajectory.

Scale was sampled approximately log-uniformly from:

```text
0.35x .. 3.0x
```

Each representation was evaluated with leave-one-out nearest-neighbor classification.

## Results

| Representation | Accuracy |
|---|---:|
| raw Δstart vector | 87.40% |
| median-normalized | 93.67% |
| mean-normalized | 94.13% |
| L2-normalized | 95.20% |
| log-centered | 96.33% |

The unscaled E0 experiment achieved 98.27% with raw interval displacement, so multiplicative scale variation materially degraded the naïve representation.

## Finding E1.1-F1 — Translation invariance is not scale invariance

Consecutive displacement automatically removes absolute temporal translation:

```text
(t_1 + c, ..., t_n + c)
    ->
(Δt_1, ..., Δt_(n-1))
```

but scaling remains:

```text
(a t_1, ..., a t_n)
    ->
(a Δt_1, ..., a Δt_(n-1))
```

Therefore an ordinary interval signature is cadence-sensitive.

## Finding E1.1-F2 — Similarity requires an explicit invariance contract

A future TCDB trajectory query should not expose a single ambiguous `SIMILAR` operator.

At minimum, research should distinguish intents resembling:

```text
SIMILAR ABSOLUTE
SIMILAR TRANSLATION_INVARIANT
SIMILAR SCALE_INVARIANT
```

Names are provisional.

The important point is semantic:

> The invariances a similarity metric removes are part of the query meaning.

## Finding E1.1-F3 — Normalization can recover temporal shape

Scale-normalized representations recovered most of the lost classification performance.

The best tested representation was log-centered inter-event displacement:

```text
log(Δt_i) - mean(log(Δt))
```

with 96.33% accuracy.

This is an analytical projection, not a canonical temporal coordinate.

## Finding E1.1-F4 — Cadence remains information

Scale normalization intentionally removes absolute cadence.

That is useful for queries asking for pattern shape, but harmful when the rate itself is semantically meaningful.

Therefore TCDB should preserve both:

```text
canonical interval geometry
        +
query-selected normalization/projection
```

rather than replacing canonical displacement with a normalized signature.

## What E1.1 Does Not Establish

This experiment does not establish that:

- log-centering is the correct production metric;
- scale invariance is desirable for every domain;
- normalized signatures survive missing or duplicate events;
- variable-length trajectories can be compared this way;
- elastic methods such as DTW are inferior or unnecessary;
- a trajectory-similarity index should be persisted.

## Plan

```text
E1.1  Temporal Scale Variation                    COMPLETE
E1.2  Missing Events                              NEXT
E1.3  Duplicate Events                            PENDING
E1.4  Timestamp Jitter / Clock Uncertainty        PENDING
E1.5  Variable Trajectory Length                  PENDING
E1.6  Selector Contamination / Identity Ambiguity PENDING
E1.7  Signature Metric Comparison                 PENDING
E1.8  Real-Data Reproduction                      PENDING
```

E1.2 should determine how rapidly trajectory geometry degrades when observations are incomplete and whether robust comparison requires explicit missing-event semantics rather than ordinary vector distance.
