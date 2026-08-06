# AGENTS.md — Documentation

Inherits repository-root `AGENTS.md`.

## Purpose

`docs/` records human-readable architectural authority and non-canonical research evidence.

Its two current subtrees have different authority:

```text
docs/architecture/  -> established architectural contracts
docs/research/      -> non-canonical evidence and hypotheses
```

Never blur those roles.

## Documentation Rules

- Preserve explicit status labels.
- Prefer definitions before conclusions.
- Separate semantic rules from implementation examples.
- Use mathematics where it removes ambiguity.
- Preserve failed experiments and contradictory results in research documents.
- Do not promote research language into architecture merely by moving or copying text.

## Cross-Document Consistency

If a documentation change affects project-wide architecture, check `README.md`, `ARCHITECTURE.md`, and affected child documents for consistency.

When documents disagree, do not silently choose one. Identify the conflict and resolve authority explicitly.