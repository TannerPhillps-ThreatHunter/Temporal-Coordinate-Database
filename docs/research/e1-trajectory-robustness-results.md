# E1 — Trajectory Robustness Results

**Status:** EXPERIMENTAL / IN PROGRESS  
**Program:** Event Geometry  
**Canonical:** No

# E1.1 — Temporal Scale Variation

## Question

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

---

# E1.2 — Missing Events

## Question

What happens to relation-selected interval geometry when the underlying behavior continues but one or more observations are absent?

The experiment isolates missing **internal** events. The first and last observations are retained so prefix/suffix truncation is deferred to E1.5.

## Prior-Art Boundary

Missing observations and sequence alignment are established research areas.

Relevant prior art includes:

- Dynamic Time Warping and incomplete-series variants;
- edit-distance measures for event sequences with insertion/deletion operations;
- missing-event recovery and trace alignment in process mining;
- incomplete event-log conformance and reconstruction.

Representative references include:

- Yurtman et al., *Estimating Dynamic Time Warping Distance Between Time Series with Missing Data*, ECML-PKDD 2023;
- Song et al., *Heuristic Recovery of Missing Events in Process Logs*;
- Marwan et al., *Challenges and perspectives in recurrence analyses of event time series*, 2023.

TCDB therefore makes no novelty claim for robust sequence alignment or missing-event recovery.

The narrower question is whether TCDB's relation-selected displacement representation exposes a useful compositional law for incomplete observation.

## Missing-Event Geometry

For three ordered observations:

```text
A --V_AB--> B --V_BC--> C
```

where endpoint displacement is:

```text
V_AB = (Δstart_AB, Δend_AB)
```

if `B` is not observed, the directly observable displacement is:

```text
V_AC = (Δstart_AC, Δend_AC)
```

and exactly:

```text
V_AC = V_AB + V_BC
```

because:

```text
start_C - start_A
    = (start_B - start_A) + (start_C - start_B)

end_C - end_A
    = (end_B - end_A) + (end_C - end_B)
```

Likewise:

```text
Δduration_AC = Δduration_AB + Δduration_BC
```

This is **not** true for every derived interval measure. In particular, the signed boundary gap:

```text
G_AB = start_B - end_A
```

is not generally path-additive.

Therefore:

```text
endpoint displacement is compositional
signed boundary gap is not generally compositional
```

This distinction matters for missing-observation robustness.

## Experimental Methods

Five trajectory families were retained:

```text
periodic
alternating
burst
accelerating
random
```

For each family:

```text
100 clean training trajectories
100 independently generated test trajectories
24 events / clean trajectory
23 clean inter-event displacements
```

A clean family prototype is the component-wise median training trajectory.

Internal events in test trajectories are independently deleted with probabilities:

```text
0%
5%
10%
20%
30%
40%
```

Deleting an event automatically coalesces its adjacent `Δstart` displacements by addition.

Three comparison methods were tested.

### Resampled fixed-length baseline

The shortened observed gap sequence is linearly resampled back to the original length and compared in log-gap space.

This deliberately represents a naïve fixed-vector strategy.

### Ordinary DTW

Dynamic Time Warping is applied to log inter-event displacement.

This provides an elastic prior-art baseline that supports sequences of different length.

### Coalescence-aware alignment

A dynamic program permits one observed displacement to match the **sum of one or more consecutive reference displacements**.

Conceptually:

```text
observed_gap_j
    <->
reference_gap_i + ... + reference_gap_k
```

This directly represents the geometry caused by one or more missing intermediate observations.

The implementation is an experimental research baseline. It is not claimed as novel and has not been optimized.

## Results

| Internal Event Deletion | Mean Observed Gaps | Resampled | DTW | Coalescence-Aware |
|---:|---:|---:|---:|---:|
| 0% | 23.000 | 90.0% | 86.4% | 90.0% |
| 5% | 21.956 | 75.2% | 88.2% | 90.6% |
| 10% | 20.864 | 65.0% | **90.4%** | 90.2% |
| 20% | 18.556 | 48.2% | 79.8% | **90.0%** |
| 30% | 16.582 | 38.4% | 66.0% | **90.4%** |
| 40% | 14.262 | 31.6% | 51.8% | **90.0%** |

These are prototype-classification results and are not directly comparable to E0's 98.27% leave-one-out nearest-neighbor score.

The relevant measurement is degradation under increasing observation loss.

## Finding E1.2-F1 — Event deletion contracts trajectory edges

Missing an intermediate event does not simply create an absent vector component.

It changes observed geometry by path contraction:

```text
V_AB, V_BC
    ->
V_AC = V_AB + V_BC
```

This is a precise computational effect of incomplete observation.

## Finding E1.2-F2 — Ordinary fixed-vector comparison fails quickly

The resampled baseline dropped from 90.0% to 31.6% as internal deletion increased from 0% to 40%.

Therefore ordinary fixed-position vector similarity is unsuitable when observations may disappear.

## Finding E1.2-F3 — DTW helps, but does not encode the deletion law directly

DTW remained strong at low deletion rates and slightly outperformed the experimental coalescence metric at 10% deletion:

```text
DTW:         90.4%
coalescence: 90.2%
```

However, DTW degraded materially under heavier loss:

```text
20% deletion -> 79.8%
30% deletion -> 66.0%
40% deletion -> 51.8%
```

This is evidence against claiming that the coalescence-aware method is universally superior.

It instead suggests that explicitly modeling event deletion becomes valuable as observation incompleteness grows.

## Finding E1.2-F4 — Coalescence-aware matching remained stable under heavy loss

The experimental deletion-aware metric remained approximately flat near 90% from 0% through 40% internal event deletion.

This supports the hypothesis:

> Missing-event robustness may be better modeled as geometry-preserving path contraction than as generic vector corruption.

The result must still survive duplicates, jitter, variable trajectory length, and real data.

## Finding E1.2-F5 — Observation completeness is part of interpretation

The same underlying trajectory can produce different observed interval sequences depending on which events were captured.

Therefore:

```text
Underlying Trajectory != Observed Trajectory
```

and:

```text
Observed Geometry = Projection(Underlying Geometry, Observation Process)
```

The second expression is a research hypothesis, not architecture doctrine.

It becomes especially relevant when TCDB later revisits separate occurrence and observation frames.

## What E1.2 Does Not Establish

This experiment does not establish that:

- the coalescence dynamic program is novel;
- the current cost function is optimal;
- every missing event should be inferred;
- an unobserved event can be reconstructed uniquely;
- additive displacement proves causality;
- the same method will handle duplicate observations;
- event deletion is distinguishable from a genuine long interval without additional evidence;
- endpoint displacement should become canonical state;
- a trajectory must be persisted.

Most importantly:

```text
long observed displacement
```

can mean either:

```text
a genuinely long interval
```

or:

```text
one or more unobserved intermediate events
```

Temporal geometry alone cannot necessarily distinguish them.

That ambiguity must be preserved rather than guessed away.

---

# Current Robustness Interpretation

E1 now supports the following experimental distinctions:

```text
translation invariance
scale invariance
observation completeness
```

These are independent dimensions of trajectory-query semantics.

A useful trajectory representation therefore cannot be reduced to a single universal normalized vector.

The most structurally interesting E1.2 result is:

```text
Endpoint displacement composes across a path.
Observation loss contracts that path by vector addition.
```

This is mathematically simple and not itself novel, but it gives TCDB a precise way to reason about how incomplete observation changes derived event geometry.

# Plan

```text
E1.1  Temporal Scale Variation                    COMPLETE
E1.2  Missing Events                              COMPLETE
E1.3  Duplicate Events                            NEXT
E1.4  Timestamp Jitter / Clock Uncertainty        PENDING
E1.5  Variable Trajectory Length                  PENDING
E1.6  Selector Contamination / Identity Ambiguity PENDING
E1.7  Signature Metric Comparison                 PENDING
E1.8  Real-Data Reproduction                      PENDING
```

E1.3 should test the inverse observational pathology: duplicated observations introduce extra trajectory vertices and split or nearly repeat displacement structure rather than contracting it.
