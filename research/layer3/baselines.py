from __future__ import annotations

from bisect import bisect_left, bisect_right
from typing import Iterable, List, Tuple

from .reference import BoundaryPolicy, Interval, Window, overlaps


class StartSortedIndex:
    """1D baseline ordered by interval start."""

    def __init__(self, intervals: Iterable[Interval]) -> None:
        self.rows = sorted(intervals, key=lambda x: (x.start, x.end, x.object_id))
        self.starts = [row.start for row in self.rows]

    def query_overlap(
        self,
        window: Window,
        policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
    ) -> Tuple[List[int], int]:
        if policy is BoundaryPolicy.HALF_OPEN:
            stop = bisect_left(self.starts, window.end)
        else:
            stop = bisect_right(self.starts, window.end)

        candidates = self.rows[:stop]
        matches = [
            row.object_id for row in candidates if overlaps(row, window, policy)
        ]
        return matches, len(candidates)


class EndSortedIndex:
    """1D baseline ordered by interval end."""

    def __init__(self, intervals: Iterable[Interval]) -> None:
        self.rows = sorted(intervals, key=lambda x: (x.end, x.start, x.object_id))
        self.ends = [row.end for row in self.rows]

    def query_overlap(
        self,
        window: Window,
        policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
    ) -> Tuple[List[int], int]:
        if policy is BoundaryPolicy.HALF_OPEN:
            first = bisect_right(self.ends, window.start)
        else:
            first = bisect_left(self.ends, window.start)

        candidates = self.rows[first:]
        matches = [
            row.object_id for row in candidates if overlaps(row, window, policy)
        ]
        return matches, len(candidates)


class AdaptiveEndpointIndex:
    """Choose the smaller 1D endpoint candidate side per overlap query.

    This is intentionally simple. It provides a planner-aware 1D baseline before
    any 2D or specialized temporal index is allowed to claim improvement.
    """

    def __init__(self, intervals: Iterable[Interval]) -> None:
        rows = list(intervals)
        self.start_index = StartSortedIndex(rows)
        self.end_index = EndSortedIndex(rows)

    def query_overlap(
        self,
        window: Window,
        policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
    ) -> Tuple[List[int], int, str]:
        if policy is BoundaryPolicy.HALF_OPEN:
            start_stop = bisect_left(self.start_index.starts, window.end)
            end_first = bisect_right(self.end_index.ends, window.start)
        else:
            start_stop = bisect_right(self.start_index.starts, window.end)
            end_first = bisect_left(self.end_index.ends, window.start)

        start_count = start_stop
        end_count = len(self.end_index.rows) - end_first

        if start_count <= end_count:
            candidates = self.start_index.rows[:start_stop]
            source = "start"
        else:
            candidates = self.end_index.rows[end_first:]
            source = "end"

        matches = [
            row.object_id for row in candidates if overlaps(row, window, policy)
        ]
        return matches, len(candidates), source


def overlap_region_cardinality(
    intervals: Iterable[Interval],
    window: Window,
    policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
) -> int:
    """Cardinality of the exact 2D endpoint overlap region.

    This is NOT an index implementation. It measures the irreducible qualifying
    endpoint region so later 2D structures can be compared against the amount of
    useful work available in principle.
    """

    return sum(1 for row in intervals if overlaps(row, window, policy))
