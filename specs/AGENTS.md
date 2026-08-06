# AGENTS.md — Specifications

Inherits repository-root `AGENTS.md`.

## Purpose

`specs/` contains formal specification-track work for TCDB semantics and protocols.

Current intended tracks include:

```text
TCDB-MODEL
TCDP
TCDP-QUIC
```

A project specification is not an IETF RFC merely because it is written in RFC style.

## Authority

Specifications must conform to established Layer 0-2 architecture unless an explicit architecture revision accompanies the change.

Do not use a specification draft to silently override architecture.

## Normative Writing

When drafting specification text:

- define terms before normative use;
- distinguish MUST/SHOULD/MAY requirements from explanatory prose;
- keep wire/protocol semantics separate from query-language syntax;
- keep temporal-frame semantics separate from commit/database mechanics;
- preserve TRUE/FALSE/UNKNOWN where uncertainty semantics require it;
- define versioning and extensibility deliberately;
- identify external standards and prior art accurately.

## Protocol Boundary

Current direction:

```text
TCDP -> QUIC -> TLS 1.3 integration -> UDP/IP
```

TCDP/1 is intended to be QUIC-native. Do not introduce a TCP fallback or QUIC DATAGRAM use for canonical database operations without a deliberate protocol decision.

Transport identity is not application identity; request/transaction/commit identifiers remain application-level concepts.

## Standards Discipline

Do not squat IANA-managed values or present provisional identifiers as registered assignments.

If preparing an Internet-Draft, clearly label it as a draft and preserve the distinction:

```text
Project Specification -> Internet-Draft -> possible standards process -> RFC
```