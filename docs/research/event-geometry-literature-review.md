# Event Geometry — Prior-Art Boundary

**Status:** SOURCE-BACKED RESEARCH NOTE  
**Program:** Event Geometry  
**Canonical:** No

## 1. Purpose

This note bounds the hypothesis that TCDB may be a temporal projection of a more general event geometry.

The goal is not to establish novelty by terminology. It is to identify which component ideas are already well developed and therefore must be treated as prior art.

## 2. Established Prior Art

### 2.1 Interval relations

Allen-style interval reasoning already treats time intervals as endpoint-defined objects with a finite relation algebra. TCDB must continue to adopt or compile established interval mathematics where appropriate rather than claiming interval relations as novel.

### 2.2 Interval-based sequence mining

Chen, Peng, and Lee's work on mining temporal patterns in time-interval-based data explicitly studies sequences of events that persist for durations and introduces endpoint/endtime representations for discovering temporal patterns.

Therefore the following are not novel by themselves:

```text
interval-valued events
interval sequence mining
endpoint representations for temporal patterns
frequent interval patterns
```

Reference:

- Yi-Cheng Chen, Wen-Chih Peng, Suh-Yin Lee, *Mining Temporal Patterns in Time Interval-Based Data*, IEEE TKDE 27(12), 2015, DOI `10.1109/TKDE.2015.2454515`.

### 2.3 Event-interval sequence similarity

ARTEMIS directly studies similarity between event-interval sequences and motivates searching, indexing, and mining such sequences.

Therefore "compare event trajectories by interval structure" is not itself a novelty claim.

Reference:

- Orestis Kostakis, Panagiotis Papapetrou, Jaakko Hollmén, *ARTEMIS: Assessing the Similarity of Event-Interval Sequences*, ECML PKDD 2011, DOI `10.1007/978-3-642-23783-6_15`.

### 2.4 Process-mining traces and object-centric event logs

Process mining already treats an event log as collections of traces/sequences associated with process cases. Object-centric process mining goes further: events may relate to multiple objects, objects have identity, and object/object as well as event/object relationships can be explicit.

OCEL 2.0 therefore occupies important prior-art territory around:

```text
events
objects
object continuity
event-object relationships
object-object relationships
dynamic object attributes
```

References:

- ProcessMining.org, *Event Data*.
- OCEL 2.0 specification and standard, `https://ocel-standard.org/`.

### 2.5 Inter-event times

Temporal point-process literature treats asynchronous events in continuous time and explicitly models inter-event times/gaps. Thus, the fact that gaps contain statistical or behavioral information is established.

TCDB must distinguish its database/addressability hypothesis from stochastic temporal point-process modeling.

### 2.6 Temporal motifs

Temporal-network research combines event order with graph/topological structure. Temporal motifs can encode ordered timestamped interactions subject to timing constraints, and prior work explicitly investigates temporal causality/topology patterns.

Therefore a future `(X,T)` model cannot claim novelty merely because it combines topology and time.

References include:

- Kovanen et al., *Temporal Motifs in Time-Dependent Networks*.
- Paranjape, Benson, Leskovec, *Motifs in Temporal Networks*.

## 3. Current Novelty Boundary

The following broad ideas are already occupied by prior art:

```text
interval events
interval relations
inter-event times
sequence/trace representations
interval-sequence similarity
temporal pattern mining
temporal motifs
object-centric event logs
topology + temporal ordering
```

Therefore the Event Geometry program must test narrower claims.

Potentially differentiating questions include whether TCDB can provide a coherent database model in which:

1. canonical events remain coordinate-native across named temporal frames;
2. relation-selected event intervals are independently addressable and indexable without becoming canonical duplicates;
3. trajectories are derived from explicit selector/order semantics rather than one global case notion;
4. interval-pattern indexes coexist with ordinary event access paths and commit-history semantics;
5. uncertainty, observation/knowledge frames, and incomplete ordering survive into trajectory queries;
6. later `(X,T)` queries compose computational position with temporal geometry without collapsing into an ordinary graph edge model.

None of these are novelty claims yet.

## 4. Research Rule

The Event Geometry program adopts this rule:

> First-class queryability does not imply primitive or canonical storage.

An EventInterval or Trajectory may become a first-class query object while remaining a deterministic, rebuildable projection of canonical events and explicit relation semantics.

Whether that distinction is useful is an empirical question.

## 5. Immediate Experiment

E0 tests only temporal geometry:

```text
Canonical Events
      ↓ explicit selector/order
Derived EventIntervals
      ↓
Derived Trajectories
      ↓
Interval Signatures
      ↓
Independent Index / Similarity Search
```

Computational position `X`, causal reachability, topology, and distributed-system clocks remain deferred until the temporal-only model demonstrates useful behavior.
