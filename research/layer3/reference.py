from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List


class BoundaryPolicy(str, Enum):
    """Experimental interval boundary policy.

    Layer 0 has not yet frozen interval boundary semantics. The research oracle
    therefore makes boundary policy explicit instead of silently choosing one.
    """

    HALF_OPEN = "half_open"
    CLOSED = "closed"


@dataclass(frozen=True, order=True)
class Interval:
    object_id: int
    start: int
    end: int
    frame: str = "occurrence"

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("interval start must be <= end")


@dataclass(frozen=True)
class Window:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("window start must be <= end")


def overlaps(
    interval: Interval,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> bool:
    """Reference overlap predicate over determinate intervals.

    HALF_OPEN interprets extents as [start, end).
    CLOSED interprets extents as [start, end].

    The function is intentionally obvious rather than optimized. It is the
    semantic oracle against which candidate-generating indexes are checked.
    """

    if policy is BoundaryPolicy.HALF_OPEN:
        return interval.start < window.end and interval.end > window.start

    if policy is BoundaryPolicy.CLOSED:
        return interval.start <= window.end and interval.end >= window.start

    raise ValueError(f"unsupported boundary policy: {policy}")


def before(
    interval: Interval,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> bool:
    if policy is BoundaryPolicy.HALF_OPEN:
        return interval.end <= window.start
    if policy is BoundaryPolicy.CLOSED:
        return interval.end < window.start
    raise ValueError(f"unsupported boundary policy: {policy}")


def after(
    interval: Interval,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> bool:
    if policy is BoundaryPolicy.HALF_OPEN:
        return interval.start >= window.end
    if policy is BoundaryPolicy.CLOSED:
        return interval.start > window.end
    raise ValueError(f"unsupported boundary policy: {policy}")


def contains(
    interval: Interval,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> bool:
    # Endpoint containment has the same inequality form for these policies;
    # the difference appears at overlap/adjacency boundaries.
    return interval.start <= window.start and interval.end >= window.end


def during(
    interval: Interval,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> bool:
    return interval.start >= window.start and interval.end <= window.end


def reference_scan_overlap(
    intervals: Iterable[Interval],
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> List[int]:
    """Return object IDs satisfying overlap using a full canonical scan."""

    return [
        interval.object_id
        for interval in intervals
        if overlaps(interval, window, policy)
    ]


def reference_scan(
    intervals: Iterable[Interval],
    predicate: str,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> List[int]:
    predicates = {
        "overlaps": overlaps,
        "before": before,
        "after": after,
        "contains": contains,
        "during": during,
    }

    try:
        fn = predicates[predicate]
    except KeyError as exc:
        raise ValueError(f"unsupported predicate: {predicate}") from exc

    return [
        interval.object_id
        for interval in intervals
        if fn(interval, window, policy)
    ]
