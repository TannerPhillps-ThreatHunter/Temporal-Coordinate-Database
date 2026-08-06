# AGENTS.md — Benchmarks

Inherits repository-root `AGENTS.md`.

## Purpose

`benchmarks/` contains reproducible measurement harnesses. Benchmarks measure implementations and experiments; they do not define semantics.

## Rules

- Correctness must be established before performance comparison.
- Keep dataset size, seed, distribution, query count, policy, and algorithm parameters explicit.
- Report what is measured: candidate count, wall time, memory, storage amplification, build cost, update cost, etc.
- Do not compare unlike metrics as if they were interchangeable.
- Avoid presenting prototype Python timing as production performance evidence.
- Prefer multiple distributions, including adversarial/pathological cases.
- Preserve strong prior-art baselines.

## Reproducibility

A benchmark should run from repository state without hidden notebook state or manual data mutation where practical.

If a benchmark result is cited in `docs/research/`, keep the harness capable of reproducing the stated configuration.

## Interpretation Boundary

A faster benchmark does not authorize architectural promotion. Performance evidence must be combined with semantic correctness, storage/update cost, operational fit, and prior-art comparison.