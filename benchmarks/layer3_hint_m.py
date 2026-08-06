from __future__ import annotations

import argparse
import statistics
from typing import Dict, List

from research.layer3.hint_m import HintMIndex
from research.layer3.reference import BoundaryPolicy, reference_scan_overlap
from research.layer3.synthetic import DISTRIBUTIONS, generate_intervals, generate_windows


def run_distribution(
    distribution: str,
    *,
    rows: int,
    queries: int,
    seed: int,
    m: int,
    policy: BoundaryPolicy,
) -> Dict[str, float]:
    intervals = generate_intervals(rows, distribution, seed=seed)
    windows = generate_windows(queries, seed=seed + 1)
    index = HintMIndex(intervals, m=m)

    match_counts: List[int] = []
    conservative_candidates: List[int] = []
    conservative_scans: List[int] = []
    optimized_candidates: List[int] = []
    optimized_scans: List[int] = []
    optimized_comparisons: List[int] = []
    optimized_duplicates: List[int] = []

    for window in windows:
        expected = sorted(reference_scan_overlap(intervals, window, policy))

        conservative, conservative_stats = index.query_overlap(window, policy)
        optimized, optimized_stats = index.query_overlap_optimized(window, policy)

        if sorted(conservative) != expected:
            raise AssertionError(
                f"conservative HINT^m disagrees with oracle: {distribution=} {m=}"
            )
        if sorted(optimized) != expected:
            raise AssertionError(
                f"optimized HINT^m disagrees with oracle: {distribution=} {m=}"
            )
        if optimized_stats.duplicate_emissions:
            raise AssertionError(
                f"optimized HINT^m emitted duplicates: {distribution=} {m=}"
            )

        match_counts.append(len(expected))
        conservative_candidates.append(conservative_stats.unique_candidates)
        conservative_scans.append(conservative_stats.scanned_references)
        optimized_candidates.append(optimized_stats.unique_candidates)
        optimized_scans.append(optimized_stats.scanned_references)
        optimized_comparisons.append(optimized_stats.predicate_comparisons)
        optimized_duplicates.append(optimized_stats.duplicate_emissions)

    return {
        "rows": float(rows),
        "queries": float(queries),
        "m": float(m),
        "reference_amplification": index.reference_amplification,
        "avg_matches": statistics.mean(match_counts),
        "avg_conservative_candidates": statistics.mean(conservative_candidates),
        "avg_conservative_scans": statistics.mean(conservative_scans),
        "avg_optimized_candidates": statistics.mean(optimized_candidates),
        "avg_optimized_scans": statistics.mean(optimized_scans),
        "avg_optimized_comparisons": statistics.mean(optimized_comparisons),
        "avg_optimized_duplicates": statistics.mean(optimized_duplicates),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--queries", type=int, default=200)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--m", type=int, nargs="+", default=[8, 10, 12])
    parser.add_argument(
        "--policy",
        choices=[policy.value for policy in BoundaryPolicy],
        default=BoundaryPolicy.HALF_OPEN.value,
    )
    args = parser.parse_args()
    policy = BoundaryPolicy(args.policy)

    print(
        "distribution,m,policy,rows,queries,reference_amplification,avg_matches,"
        "avg_conservative_candidates,avg_conservative_scans,"
        "avg_optimized_candidates,avg_optimized_scans,"
        "avg_optimized_comparisons,avg_optimized_duplicates"
    )

    for m in args.m:
        for distribution in DISTRIBUTIONS:
            result = run_distribution(
                distribution,
                rows=args.rows,
                queries=args.queries,
                seed=args.seed,
                m=m,
                policy=policy,
            )
            print(
                f"{distribution},{m},{policy.value},{args.rows},{args.queries},"
                f"{result['reference_amplification']:.6f},"
                f"{result['avg_matches']:.3f},"
                f"{result['avg_conservative_candidates']:.3f},"
                f"{result['avg_conservative_scans']:.3f},"
                f"{result['avg_optimized_candidates']:.3f},"
                f"{result['avg_optimized_scans']:.3f},"
                f"{result['avg_optimized_comparisons']:.3f},"
                f"{result['avg_optimized_duplicates']:.3f}"
            )


if __name__ == "__main__":
    main()
