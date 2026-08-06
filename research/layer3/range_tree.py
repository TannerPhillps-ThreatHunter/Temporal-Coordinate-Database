from __future__ import annotations

from bisect import bisect_left
from typing import Iterable, List, Optional, Tuple

from .baselines import _start_candidate_stop
from .reference import BoundaryPolicy, Interval, Window, overlaps


class _Node:
    __slots__ = ("lo", "hi", "left", "right", "rows", "ends")

    def __init__(self, lo: int, hi: int, rows_by_start: List[Interval]) -> None:
        self.lo = lo
        self.hi = hi
        self.left: Optional[_Node] = None
        self.right: Optional[_Node] = None

        subset = rows_by_start[lo:hi]
        self.rows = sorted(subset, key=lambda x: (x.end, x.start, x.object_id))
        self.ends = [row.end for row in self.rows]

        if hi - lo > 1:
            mid = (lo + hi) // 2
            self.left = _Node(lo, mid, rows_by_start)
            self.right = _Node(mid, hi, rows_by_start)


class StaticEndpointRangeTree:
    """Static 2D orthogonal range-query baseline over (start, end).

    This is intentionally a research baseline, not a proposed TCDB production
    index. It stores an end-sorted secondary array at each node of a balanced
    tree over start order, producing O(n log n) reference amplification.

    An overlap query decomposes the valid start prefix into canonical nodes and
    applies the end constraint within each node.
    """

    def __init__(self, intervals: Iterable[Interval]) -> None:
        self.rows_by_start = sorted(
            intervals,
            key=lambda x: (x.start, x.end, x.object_id),
        )
        self.starts = [row.start for row in self.rows_by_start]
        self.root = (
            _Node(0, len(self.rows_by_start), self.rows_by_start)
            if self.rows_by_start
            else None
        )

    def query_overlap(
        self,
        window: Window,
        policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
    ) -> Tuple[List[int], int, int]:
        """Return matches, candidate rows, and visited tree nodes."""

        if self.root is None:
            return [], 0, 0

        stop = _start_candidate_stop(self.starts, window, policy)
        candidates: List[Interval] = []
        visited_nodes = 0

        def visit(node: Optional[_Node]) -> None:
            nonlocal visited_nodes

            if node is None or node.lo >= stop:
                return

            visited_nodes += 1

            if node.hi <= stop:
                # end >= query.start is the lossless endpoint-space candidate
                # condition under both experimental policies because point
                # extents at query.start must remain visible.
                first = bisect_left(node.ends, window.start)
                candidates.extend(node.rows[first:])
                return

            visit(node.left)
            visit(node.right)

        visit(self.root)

        matches = [
            row.object_id
            for row in candidates
            if overlaps(row, window, policy)
        ]
        return matches, len(candidates), visited_nodes

    def stored_reference_count(self) -> int:
        """Count interval references stored across all tree-node arrays."""

        def count(node: Optional[_Node]) -> int:
            if node is None:
                return 0
            return len(node.rows) + count(node.left) + count(node.right)

        return count(self.root)
