from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List


class BoundaryPolicy(str, Enum):
    """Experimental boundary policy for non-point extents.

    TCDB defines s=e as an instantaneous point extent. Therefore a point is not
    interpreted as an empty half-open interval. Point semantics are handled
    explicitly by the reference oracle.
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

    @property
    def is_point(self) -> bool:
        return self.start == self.end


@dataclass(frozen=True)
class Window:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("window start must be <= end")

    @property
    def is_point(self) -> bool:
        return self.start == self.end


def overlaps(
    interval: Interval,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> bool:
    """Reference overlap predicate over determinate temporal extents.

    Under HALF_OPEN, non-point extents use [start, end), while s=e remains a
    first-class instantaneous point rather than becoming the empty set.
    """

    if policy is BoundaryPolicy.CLOSED:
        return interval.start <= window.end and interval.end >= window.start

    if policy is not BoundaryPolicy.HALF_OPEN:
        raise ValueError(f"unsupported boundary policy: {policy}")

    if interval.is_point and window.is_point:
        return interval.start == window.start

    if interval.is_point:
        return window.start <= interval.start < window.end

    if window.is_point:
        return interval.start <= window.start < interval.end

    return interval.start < window.end and interval.end > window.start


def before(
    interval: Interval,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> bool:
    if policy is BoundaryPolicy.HALF_OPEN:
        if interval.is_point:
            return interval.start < window.start
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
        if interval.is_point:
            return interval.start >= window.end if not window.is_point else interval.start > window.start
        return interval.start >= window.end if not window.is_point else interval.start > window.start
    if policy is BoundaryPolicy.CLOSED:
        return interval.start > window.end
    raise ValueError(f"unsupported boundary policy: {policy}")


def contains(
    interval: Interval,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> bool:
    if policy is BoundaryPolicy.HALF_OPEN:
        if interval.is_point:
            return window.is_point and interval.start == window.start
        if window.is_point:
            return interval.start <= window.start < interval.end
    return interval.start <= window.start and interval.end >= window.end


def during(
    interval: Interval,
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> bool:
    if policy is BoundaryPolicy.HALF_OPEN:
        if interval.is_point:
            if window.is_point:
                return interval.start == window.start
            return window.start <= interval.start < window.end
        if window.is_point:
            return False
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
