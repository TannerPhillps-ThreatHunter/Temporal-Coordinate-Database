from __future__ import annotations

import argparse
import statistics
from typing import Dict, Iterable, List

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
) -> Dict[str, float]:
    intervals = generate_intervals(rows, distribution, seed=seed)
    windows = generate_windows(queries, seed=seed + 1)
    index = HintMIndex(intervals, m=m)

    unique_candidates: List[int] = []
    scanned_references: List[int] = []
    match_counts: List[int] = []

    for window in windows:
        expected = sorted(
            reference_scan_overlap(intervals, window, BoundaryPolicy.HALF_OPEN)
        )
        actual, stats = index.query_overlap(window, BoundaryPolicy.HALF_OPEN)

        if sorted(actual) != expected:
            raise AssertionError(
                f"HINT^m disagrees with reference oracle: {distribution=} {m=}"
            )

        unique_candidates.append(stats.unique_candidates)
        scanned_references.append(stats.scanned_references)
        match_counts.append(len(expected))

    return {
        "rows": float(rows),
        "queries": float(queries),
        "m": float(m),
        "reference_amplification": index.reference_amplification,
        "avg_matches": statistics.mean(match_counts),
        "avg_unique_candidates": statistics.mean(unique_candidates),
        "avg_scanned_references": statistics.mean(scanned_references),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--queries", type=int, default=200)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--m", type=int, nargs="+", default=[8, 10, 12])
    args = parser.parse_args()

    print(
        "distribution,m,rows,queries,reference_amplification,avg_matches,"
        "avg_unique_candidates,avg_scanned_references"
    )

    for m in args.m:
        for distribution in DISTRIBUTIONS:
            result = run_distribution(
                distribution,
                rows=args.rows,
                queries=args.queries,
                seed=args.seed,
                m=m,
            )
            print(
                f"{distribution},{m},{args.rows},{args.queries},"
                f"{result['reference_amplification']:.6f},"
                f"{result['avg_matches']:.3f},"
                f"{result['avg_unique_candidates']:.3f},"
                f"{result['avg_scanned_references']:.3f}"
            )


if __name__ == "__main__":
    main()
