# AGENTS.md — Tests

Inherits repository-root `AGENTS.md`.

## Purpose

`tests/` protects semantic correctness, research invariants, and regression behavior.

## Testing Priority

Use this order:

```text
semantic correctness
invariant preservation
differential equivalence
failure/recovery behavior
performance regression
```

Do not weaken a correctness test to accommodate an optimized implementation unless the underlying semantic contract has been deliberately revised.

## Differential Testing

Where a reference evaluator exists, compare candidates against it directly.

Examples:

```text
Optimized(x) == Reference(x)
IndexedQuery(D,q) == ReferenceScan(D,q)
```

## Edge Cases

Prefer explicit tests for:

- point extents (`start == end`);
- boundary semantics;
- equal timestamps;
- uncertainty / UNKNOWN when introduced;
- partial orders and incomparability;
- crash/recovery boundaries;
- missing or contradictory observations in research models;
- deterministic generation from fixed seeds.

## Research Tests

Research tests may protect experimental findings without making those findings canonical. Name and document them so their scope is clear.

If a research branch is paused, keep its tests unless the experiment is intentionally retired; paused does not mean invalid.