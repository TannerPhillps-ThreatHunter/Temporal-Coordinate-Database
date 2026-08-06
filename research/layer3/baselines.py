from __future__ import annotations

from bisect import bisect_left, bisect_right
from typing import Iterable, List, Tuple

from .reference import BoundaryPolicy, Interval, Window, overlaps


def _start_candidate_stop(
    starts: List[int],
    window: Window,
    policy: BoundaryPolicy,
) -> int:
    if policy is BoundaryPolicy.CLOSED:
        return bisect_right(starts, window.end)

    # For a non-point [a,b) query, candidates require start < b.
    # For a point query t, an interval or point may match when start <= t.
    if window.is_point:
        return bisect_right(starts, window.start)
    return bisect_left(starts, window.end)


def _end_candidate_first(
    ends: List[int],
    window: Window,
    policy: BoundaryPolicy,
) -> int:
    # end >= query.start is the lossless candidate condition for CLOSED.
    # It is also required for HALF_OPEN because a point extent exactly at
    # query.start must remain a candidate. Non-point intervals ending exactly
    # there become harmless false positives removed by the oracle predicate.
    return bisect_left(ends, window.start)


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
        stop = _start_candidate_stop(self.starts, window, policy)
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
        first = _end_candidate_first(self.ends, window, policy)
        candidates = self.rows[first:]
        matches = [
            row.object_id for row in candidates if overlaps(row, window, policy)
        ]
        return matches, len(candidates)


class AdaptiveEndpointIndex:
    """Choose the smaller lossless 1D endpoint candidate side per query."""

    def __init__(self, intervals: Iterable[Interval]) -> None:
        rows = list(intervals)
        self.start_index = StartSortedIndex(rows)
        self.end_index = EndSortedIndex(rows)

    def query_overlap(
        self,
        window: Window,
        policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
    ) -> Tuple[List[int], int, str]:
        start_stop = _start_candidate_stop(
            self.start_index.starts,
            window,
            policy,
        )
        end_first = _end_candidate_first(
            self.end_index.ends,
            window,
            policy,
        )

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
    """Cardinality of the exact endpoint-space overlap result region.

    This is NOT an index implementation. It measures the qualifying region so
    future 2D structures can be compared with the useful result cardinality.
    """

    return sum(1 for row in intervals if overlaps(row, window, policy))
