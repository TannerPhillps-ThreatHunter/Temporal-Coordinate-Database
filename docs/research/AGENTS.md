# AGENTS.md — Research Documentation

Inherits `docs/AGENTS.md` and repository-root `AGENTS.md`.

## Authority

Everything in `docs/research/` is **non-canonical evidence** unless an architecture/specification document explicitly promotes it.

Research may be:

```text
HYPOTHESIS
PRIOR ART
EXPERIMENTAL
REPRODUCED
REFUTED
SUPERSEDED
PAUSED
PROMOTED
```

Always state status when adding a significant result.

## Research Writing Contract

A useful research document should make it possible to answer:

1. What question was tested?
2. What prior art bounds the claim?
3. What model or dataset was used?
4. What reference/baseline was used?
5. What was measured?
6. What failed?
7. What does the result support?
8. What does it NOT establish?
9. What should happen next?

Preserve negative and ambiguous findings.

## Current Branches

Two major research branches currently exist:

```text
Layer 3 Coordinate Access & Indexing
Event Geometry
```

Both are useful evidence. Neither currently supersedes the primary TCDB architectural focus.

The Event Geometry robustness sequence is paused after E1.2 unless deliberately resumed. Do not auto-continue E1.3 simply because it was the next numbered experiment.

## Novelty Discipline

Do not claim novelty for established temporal databases, Allen relations, interval indexing, HINT/HINT^m, bitemporal mappings, DTW, process mining, temporal motifs, event-sequence similarity, or other prior art merely because TCDB combines them.

A TCDB-native contribution must show a meaningful semantic, operational, or asymptotic advantage.