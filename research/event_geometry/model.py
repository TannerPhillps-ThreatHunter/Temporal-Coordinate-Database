from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np


@dataclass(frozen=True, order=True)
class Event:
    event_id: int
    entity_id: str
    event_type: str
    start: float
    end: float

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("event start must be <= end")

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass(frozen=True)
class EventInterval:
    """Derived relation-bound geometry between two canonical events.

    First-class addressability does not imply canonical independence. The
    interval identity is composite: relation + source event + target event.
    """

    relation: str
    source_event_id: int
    target_event_id: int
    entity_id: str
    signed_gap: float
    delta_start: float
    delta_end: float
    duration_delta: float

    @property
    def interval_key(self) -> Tuple[str, int, int]:
        return (self.relation, self.source_event_id, self.target_event_id)


@dataclass(frozen=True)
class Trajectory:
    """A relation-selected ordered path through canonical events."""

    selector: str
    entity_id: str
    event_ids: Tuple[int, ...]
    interval_keys: Tuple[Tuple[str, int, int], ...]

    @property
    def trajectory_key(self) -> Tuple[str, str]:
        return (self.selector, self.entity_id)


def derive_same_entity_geometry(
    events: Iterable[Event],
) -> Tuple[List[EventInterval], List[Trajectory]]:
    """Derive adjacency intervals and trajectories under SAME_ENTITY_NEXT.

    Ordering is by (start, end, event_id). The selector/order is explicit
    because TCDB does not assume a universal predecessor relation.
    """

    grouped: Dict[str, List[Event]] = defaultdict(list)
    for event in events:
        grouped[event.entity_id].append(event)

    intervals: List[EventInterval] = []
    trajectories: List[Trajectory] = []

    for entity_id, rows in grouped.items():
        rows.sort(key=lambda e: (e.start, e.end, e.event_id))
        keys: List[Tuple[str, int, int]] = []

        for source, target in zip(rows, rows[1:]):
            interval = EventInterval(
                relation="same_entity_next",
                source_event_id=source.event_id,
                target_event_id=target.event_id,
                entity_id=entity_id,
                signed_gap=target.start - source.end,
                delta_start=target.start - source.start,
                delta_end=target.end - source.end,
                duration_delta=target.duration - source.duration,
            )
            intervals.append(interval)
            keys.append(interval.interval_key)

        trajectories.append(
            Trajectory(
                selector="same_entity",
                entity_id=entity_id,
                event_ids=tuple(e.event_id for e in rows),
                interval_keys=tuple(keys),
            )
        )

    trajectories.sort(key=lambda t: t.entity_id)
    return intervals, trajectories


class ScalarIntervalIndex:
    """Simple sorted access path over one derived interval coordinate."""

    def __init__(self, intervals: Sequence[EventInterval], field: str = "delta_start") -> None:
        if field not in {"delta_start", "delta_end", "signed_gap", "duration_delta"}:
            raise ValueError(f"unsupported field: {field}")
        self.intervals = list(intervals)
        self.field = field
        values = np.asarray([getattr(i, field) for i in self.intervals], dtype=np.float64)
        self.order = np.argsort(values, kind="stable")
        self.values = values[self.order]

    def range_query(self, lower: float, upper: float) -> np.ndarray:
        if lower > upper:
            raise ValueError("lower must be <= upper")
        left = int(np.searchsorted(self.values, lower, side="left"))
        right = int(np.searchsorted(self.values, upper, side="right"))
        return self.order[left:right]


@dataclass(frozen=True)
class SignatureOccurrence:
    entity_id: str
    position: int
    signature: Tuple[int, ...]


class QuantizedSignatureIndex:
    """Exact hash index over quantized rolling interval signatures.

    This is an experimental baseline for direct interval-pattern lookup, not
    an approximate nearest-neighbor structure.
    """

    def __init__(self, *, width: int, bin_width: float) -> None:
        if width <= 0:
            raise ValueError("width must be positive")
        if bin_width <= 0:
            raise ValueError("bin_width must be positive")
        self.width = width
        self.bin_width = float(bin_width)
        self._index: Dict[Tuple[int, ...], List[SignatureOccurrence]] = defaultdict(list)

    def quantize(self, values: Sequence[float]) -> Tuple[int, ...]:
        arr = np.asarray(values, dtype=np.float64)
        return tuple(np.rint(arr / self.bin_width).astype(np.int64).tolist())

    def add_trajectory(self, entity_id: str, values: Sequence[float]) -> None:
        if len(values) < self.width:
            return
        for position in range(len(values) - self.width + 1):
            signature = self.quantize(values[position:position + self.width])
            self._index[signature].append(
                SignatureOccurrence(entity_id, position, signature)
            )

    def lookup(self, values: Sequence[float]) -> List[SignatureOccurrence]:
        if len(values) != self.width:
            raise ValueError("query length must equal index width")
        return list(self._index.get(self.quantize(values), ()))

    @property
    def distinct_signatures(self) -> int:
        return len(self._index)
