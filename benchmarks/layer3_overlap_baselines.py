from __future__ import annotations

import argparse
import statistics
from typing import Dict, List

from research.layer3.baselines import (
    AdaptiveEndpointIndex,
    EndSortedIndex,
    StartSortedIndex,
    overlap_region_cardinality,
)
from research.layer3.range_tree import StaticEndpointRangeTree
from research.layer3.reference import BoundaryPolicy, reference_scan_overlap
from research.layer3.synthetic import DISTRIBUTIONS, generate_intervals, generate_windows


def run_distribution(
    distribution: str,
    *,
    rows: int,
    queries: int,
    seed: int,
) -> Dict[str, float]:
    intervals = generate_intervals(rows, distribution, seed=seed)
    windows = generate_windows(queries, seed=seed + 1)

    start_index = StartSortedIndex(intervals)
    end_index = EndSortedIndex(intervals)
    adaptive_index = AdaptiveEndpointIndex(intervals)
    range_tree = StaticEndpointRangeTree(intervals)

    start_candidates: List[int] = []
    end_candidates: List[int] = []
    adaptive_candidates: List[int] = []
    range_candidates: List[int] = []
    range_nodes: List[int] = []
    exact_region: List[int] = []
    match_counts: List[int] = []

    for window in windows:
        expected = sorted(
            reference_scan_overlap(intervals, window, BoundaryPolicy.HALF_OPEN)
        )

        start_actual, start_count = start_index.query_overlap(window)
        end_actual, end_count = end_index.query_overlap(window)
        adaptive_actual, adaptive_count, _ = adaptive_index.query_overlap(window)
        range_actual, range_count, visited_nodes = range_tree.query_overlap(window)

        if sorted(start_actual) != expected:
            raise AssertionError("start-sorted index disagrees with reference oracle")
        if sorted(end_actual) != expected:
            raise AssertionError("end-sorted index disagrees with reference oracle")
        if sorted(adaptive_actual) != expected:
            raise AssertionError("adaptive endpoint index disagrees with reference oracle")
        if sorted(range_actual) != expected:
            raise AssertionError("2D range tree disagrees with reference oracle")

        start_candidates.append(start_count)
        end_candidates.append(end_count)
        adaptive_candidates.append(adaptive_count)
        range_candidates.append(range_count)
        range_nodes.append(visited_nodes)
        match_counts.append(len(expected))
        exact_region.append(overlap_region_cardinality(intervals, window))

    return {
        "rows": float(rows),
        "queries": float(queries),
        "avg_matches": statistics.mean(match_counts),
        "avg_start_candidates": statistics.mean(start_candidates),
        "avg_end_candidates": statistics.mean(end_candidates),
        "avg_adaptive_candidates": statistics.mean(adaptive_candidates),
        "avg_range_candidates": statistics.mean(range_candidates),
        "avg_range_nodes": statistics.mean(range_nodes),
        "avg_exact_region": statistics.mean(exact_region),
        "range_stored_references": float(range_tree.stored_reference_count()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--queries", type=int, default=200)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    header = (
        "distribution,rows,queries,avg_matches,avg_start_candidates,"
        "avg_end_candidates,avg_adaptive_candidates,avg_range_candidates,"
        "avg_range_nodes,avg_exact_region,range_stored_references"
    )
    print(header)

    for distribution in DISTRIBUTIONS:
        result = run_distribution(
            distribution,
            rows=args.rows,
            queries=args.queries,
            seed=args.seed,
        )
        print(
            f"{distribution},{args.rows},{args.queries},"
            f"{result['avg_matches']:.3f},"
            f"{result['avg_start_candidates']:.3f},"
            f"{result['avg_end_candidates']:.3f},"
            f"{result['avg_adaptive_candidates']:.3f},"
            f"{result['avg_range_candidates']:.3f},"
            f"{result['avg_range_nodes']:.3f},"
            f"{result['avg_exact_region']:.3f},"
            f"{result['range_stored_references']:.0f}"
        )


if __name__ == "__main__":
    main()
