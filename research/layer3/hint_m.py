from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Set, Tuple

from .reference import BoundaryPolicy, Interval, Window, overlaps


@dataclass(frozen=True)
class HintQueryStats:
    unique_candidates: int
    scanned_references: int
    predicate_comparisons: int = 0
    duplicate_emissions: int = 0


class HintMIndex:
    """Research reproduction of the HINT^m hierarchy.

    This is a prior-art baseline, not a TCDB-native index claim.

    Structural behavior follows HINT^m's hierarchical canonical-cover
    assignment. Endpoints are mapped into ``[0, 2^m-1]`` and each interval is
    assigned to at most two partitions per level.

    The original/replica classification mirrors the authors' reference source:
    the left cover partition is the original when it is selected first; a
    right-edge partition is original only when it is the sole remaining cover
    before ascending. Every indexed interval therefore has exactly one original
    reference and zero or more replicas.

    Two overlap paths are retained:

    * ``query_overlap`` is the conservative R3.5a evaluator. It visits every
      relevant originals/replicas division, deduplicates ids, then applies the
      TCDB reference predicate.
    * ``query_overlap_optimized`` reproduces HINT^m's duplicate-avoidance access
      rule: first relevant partition -> originals + replicas; later relevant
      partitions -> originals only. Boundary partitions are predicate-checked.
      For TCDB's experimental HALF_OPEN policy, interior emissions are also
      rechecked because HINT's published proofs assume closed intervals.
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

    @property
    def original_reference_count(self) -> int:
        return sum(len(groups["original"]) for groups in self.partitions.values())

    @property
    def replica_reference_count(self) -> int:
        return sum(len(groups["replica"]) for groups in self.partitions.values())

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

    def _store(
        self,
        level: int,
        partition: int,
        object_id: int,
        *,
        original: bool,
    ) -> None:
        group = "original" if original else "replica"
        self.partitions[(level, partition)][group].append(object_id)
        self.stored_references += 1

    def _assign(self, row: Interval) -> None:
        """Assign one interval using the HINT/HINT^m canonical-cover procedure.

        Levels are represented as ``m`` at the bottom (finest) level down to
        ``0`` at the root. ``first_found`` follows the original implementation's
        classification logic rather than simply labeling the first emitted
        right-edge cover as an original.
        """

        a = self._map_endpoint(row.start)
        b = self._map_endpoint(row.end)
        level = self.m
        first_found = False

        while level >= 0 and a <= b:
            if a & 1:
                self._store(
                    level,
                    a,
                    row.object_id,
                    original=not first_found,
                )
                first_found = True
                a += 1

            if a <= b and (b & 1) == 0:
                previous_b = b
                b -= 1

                # This is the subtle branch used by the official HINT^m source.
                # A right-edge cover is original only if no earlier cover was
                # found and removing it exhausts the remaining interval cover.
                if (not first_found) and b < a:
                    self._store(
                        level,
                        previous_b,
                        row.object_id,
                        original=True,
                    )
                else:
                    self._store(
                        level,
                        previous_b,
                        row.object_id,
                        original=False,
                    )

            a >>= 1
            b >>= 1
            level -= 1

    def query_overlap(
        self,
        window: Window,
        policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
    ) -> Tuple[List[int], HintQueryStats]:
        """Conservative R3.5a overlap evaluator.

        This intentionally over-accesses replicas and deduplicates candidates so
        that structural correctness remains separable from optimized traversal.
        """

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
            predicate_comparisons=len(candidates),
        )

    def query_overlap_optimized(
        self,
        window: Window,
        policy: BoundaryPolicy = BoundaryPolicy.HALF_OPEN,
    ) -> Tuple[List[int], HintQueryStats]:
        """Duplicate-free HINT^m overlap traversal.

        The physical access pattern follows the published/reference HINT^m
        top-down G-OVERLAPS implementation:

        * first relevant partition at a level: originals + replicas;
        * interior relevant partitions: originals only;
        * last relevant partition: originals only;
        * root: originals only.

        In the CLOSED policy, interior originals can be emitted without an
        overlap comparison, as in HINT^m. HALF_OPEN is a TCDB adaptation, so all
        scanned references are rechecked against TCDB's point-aware oracle until
        the boundary semantics are formally frozen.
        """

        a = self._map_endpoint(window.start)
        b = self._map_endpoint(window.end)

        emitted: List[int] = []
        scanned_references = 0
        predicate_comparisons = 0

        # Fine levels, bottom-up in the paper's numbering but represented here
        # from m down to 1. Root (level 0) is handled separately.
        for level in range(self.m, 0, -1):
            first_groups = self.partitions.get((level, a))
            if first_groups is not None:
                for group in ("original", "replica"):
                    values = first_groups[group]
                    scanned_references += len(values)
                    for object_id in values:
                        predicate_comparisons += 1
                        if overlaps(self.rows[object_id], window, policy):
                            emitted.append(object_id)

            if a < b:
                for partition in range(a + 1, b):
                    groups = self.partitions.get((level, partition))
                    if groups is None:
                        continue

                    values = groups["original"]
                    scanned_references += len(values)

                    if policy is BoundaryPolicy.CLOSED:
                        # HINT^m guarantees these are results under its closed
                        # interval model; no predicate comparison is required.
                        emitted.extend(values)
                    else:
                        # TCDB's experimental half-open + point model is not the
                        # model proved by HINT, so preserve correctness by
                        # rechecking until TCDB-MODEL freezes boundary semantics.
                        for object_id in values:
                            predicate_comparisons += 1
                            if overlaps(self.rows[object_id], window, policy):
                                emitted.append(object_id)

                last_groups = self.partitions.get((level, b))
                if last_groups is not None:
                    values = last_groups["original"]
                    scanned_references += len(values)
                    for object_id in values:
                        predicate_comparisons += 1
                        if overlaps(self.rows[object_id], window, policy):
                            emitted.append(object_id)

            a >>= 1
            b >>= 1

        root_groups = self.partitions.get((0, 0))
        if root_groups is not None:
            values = root_groups["original"]
            scanned_references += len(values)
            for object_id in values:
                predicate_comparisons += 1
                if overlaps(self.rows[object_id], window, policy):
                    emitted.append(object_id)

        unique = set(emitted)
        return list(unique), HintQueryStats(
            unique_candidates=len(unique),
            scanned_references=scanned_references,
            predicate_comparisons=predicate_comparisons,
            duplicate_emissions=len(emitted) - len(unique),
        )
