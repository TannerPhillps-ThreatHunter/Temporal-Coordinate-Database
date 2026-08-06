# TCDB Specification Tracks

TCDB is specification-first.

## TCDB-MODEL

**Temporal Coordinate Data Model**

Defines the formal semantic model derived from Architecture Layer 0:

- TemporalFrame
- TemporalExtent
- TemporalObject
- TemporalRelation
- uncertainty
- temporal truth
- semantic invariants

## TCDP

**Temporal Coordinate Database Protocol**

Defines database application semantics independently of QUIC transport mechanics.

## TCDP-QUIC

**Temporal Coordinate Database Protocol over QUIC**

Defines the mapping of TCDP sessions, queries, transactions, cancellation, shutdown, capability negotiation, and results onto QUIC connections and streams.

Current direction:

```text
TCDP/1
  ↓
QUIC
  ↓
TLS 1.3 integration
  ↓
UDP/IP
```

No TCP mapping is currently planned for TCDP/1.

These begin as project specifications. If sufficiently mature and interoperable, they may later be developed as Internet-Drafts with the long-term possibility of RFC publication.
