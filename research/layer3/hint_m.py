from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Set, Tuple

from .reference import BoundaryPolicy, Interval, Window, overlaps


@dataclass(frozen=True)
class HintQueryStats:
    unique_candidates: int
    scanned_references: int


class HintMIndex:
    """Conservative research implementation of the HINT^m hierarchy.

    This is a prior-art reproduction baseline, not a TCDB-native index claim.

    Structural behavior follows HINT^m's hierarchical canonical-cover assignment:
    endpoints are mapped into [0, 2^m-1], and an interval is assigned to at most
    two partitions per level. The first assignment is classified as an original;
    subsequent assignments are replicas.

    Query processing is intentionally conservative for R3.5: it visits all
    hierarchy partitions whose mapped spans intersect the query, deduplicates
    object ids, and applies the TCDB reference predicate. This preserves a clear
    correctness boundary before reproducing HINT^m's more advanced duplicate-
    avoidance, subdivision, sorting, sparsity, and cache optimizations.
    """

    def __init__(self, intervals: Iterable[Interval], *, m: int = 10) -> None:
        if m < 0 or m > 30:
            raise ValueError("m must be between 0 and 30 for this research baseline")

        rows = list(intervals)
        self.rows: Dict[int, Interval] = {row.object_id: row for row in rows}
        if len(self.rows) != len(rows):
            raise ValueError("object_id values must be unique")

        self.m = m
        self.max_code = (1 << m) - 1

        self.min_endpoint = min((row.start for row in rows), default=0)
        self.max_endpoint = max((row.end for row in rows), default=1)
        if self.max_endpoint <= self.min_endpoint:
            self.max_endpoint = self.min_endpoint + 1

        self.partitions: DefaultDict[
            Tuple[int, int], Dict[str, List[int]]
        ] = defaultdict(lambda: {"original": [], "replica": []})

        self.stored_references = 0
        for row in rows:
            self._assign(row)

    @property
    def reference_amplification(self) -> float:
        if not self.rows:
            return 0.0
        return self.stored_references / len(self.rows)

    def _map_endpoint(self, value: int) -> int:
        if self.max_code == 0:
            return 0
        if value <= self.min_endpoint:
            return 0
        if value >= self.max_endpoint:
            return self.max_code

        numerator = (value - self.min_endpoint) * self.max_code
        denominator = self.max_endpoint - self.min_endpoint
        return numerator // denominator

    def _store(self, level: int, partition: int, object_id: int, *, original: bool) -> None:
        group = "original" if original else "replica"
        self.partitions[(level, partition)][group].append(object_id)
        self.stored_references += 1

    def _assign(self, row: Interval) -> None:
        """Assign one interval using the HINT/HINT^m canonical-cover procedure."""

        a = self._map_endpoint(row.start)
        b = self._map_endpoint(row.end)
        level = self.m
        first_assignment = True

        while level >= 0 and a <= b:
            if a & 1:
                self._store(
                    level,
                    a,
                    row.object_id,
                    original=first_assignment,
                )
                first_assignment = False
                a += 1

            if a <= b and (b & 1) == 0:
                self._store(
                    level,
                    b,
                    row.object_id,
                    original=first_assignment,
                )
                first_assignment = False
                b -= 1

            a >>= 1
            b >>= 1
            level -= 1

    def query_overlap(
        self,
        window: Window,
        policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
    ) -> Tuple[List[int], HintQueryStats]:
        """Return overlap matches and conservative HINT^m access statistics."""

        q_start = self._map_endpoint(window.start)
        q_end = self._map_endpoint(window.end)

        candidates: Set[int] = set()
        scanned_references = 0

        for level in range(self.m, -1, -1):
            shift = self.m - level
            first = q_start >> shift
            last = q_end >> shift

            for partition in range(first, last + 1):
                groups = self.partitions.get((level, partition))
                if groups is None:
                    continue

                for group in ("original", "replica"):
                    values = groups[group]
                    scanned_references += len(values)
                    candidates.update(values)

        matches = [
            object_id
            for object_id in candidates
            if overlaps(self.rows[object_id], window, policy)
        ]

        return matches, HintQueryStats(
            unique_candidates=len(candidates),
            scanned_references=scanned_references,
        )
