import unittest

from research.layer3.baselines import (
    AdaptiveEndpointIndex,
    EndSortedIndex,
    StartSortedIndex,
)
from research.layer3.range_tree import StaticEndpointRangeTree
from research.layer3.reference import (
    BoundaryPolicy,
    Interval,
    Window,
    reference_scan_overlap,
)
from research.layer3.synthetic import DISTRIBUTIONS, generate_intervals, generate_windows


class BoundaryPolicyTests(unittest.TestCase):
    def test_half_open_touching_nonpoint_intervals_do_not_overlap(self) -> None:
        rows = [Interval(1, 10, 20)]
        self.assertEqual(
            reference_scan_overlap(rows, Window(20, 30), BoundaryPolicy.HALF_OPEN),
            [],
        )

    def test_closed_touching_intervals_overlap_at_boundary(self) -> None:
        rows = [Interval(1, 10, 20)]
        self.assertEqual(
            reference_scan_overlap(rows, Window(20, 30), BoundaryPolicy.CLOSED),
            [1],
        )

    def test_point_extent_survives_half_open_policy(self) -> None:
        rows = [Interval(1, 10, 10)]
        self.assertEqual(
            reference_scan_overlap(rows, Window(9, 11), BoundaryPolicy.HALF_OPEN),
            [1],
        )

    def test_point_at_half_open_window_start_matches(self) -> None:
        rows = [Interval(1, 10, 10)]
        self.assertEqual(
            reference_scan_overlap(rows, Window(10, 20), BoundaryPolicy.HALF_OPEN),
            [1],
        )

    def test_point_at_half_open_window_end_does_not_match(self) -> None:
        rows = [Interval(1, 20, 20)]
        self.assertEqual(
            reference_scan_overlap(rows, Window(10, 20), BoundaryPolicy.HALF_OPEN),
            [],
        )

    def test_equal_points_overlap(self) -> None:
        rows = [Interval(1, 20, 20)]
        self.assertEqual(
            reference_scan_overlap(rows, Window(20, 20), BoundaryPolicy.HALF_OPEN),
            [1],
        )


class DifferentialIndexTests(unittest.TestCase):
    def test_all_baselines_equal_reference_oracle(self) -> None:
        for distribution in DISTRIBUTIONS:
            with self.subTest(distribution=distribution):
                rows = generate_intervals(5_000, distribution, seed=17)
                rows.extend(
                    [
                        Interval(10_001, 0, 0),
                        Interval(10_002, 500_000, 500_000),
                        Interval(10_003, 1_000_000, 1_000_000),
                    ]
                )
                windows = generate_windows(100, seed=19)
                windows.extend(
                    [
                        Window(0, 0),
                        Window(500_000, 500_000),
                        Window(1_000_000, 1_000_000),
                    ]
                )

                start_index = StartSortedIndex(rows)
                end_index = EndSortedIndex(rows)
                adaptive_index = AdaptiveEndpointIndex(rows)
                range_tree = StaticEndpointRangeTree(rows)

                for policy in (BoundaryPolicy.HALF_OPEN, BoundaryPolicy.CLOSED):
                    for window in windows:
                        expected = sorted(reference_scan_overlap(rows, window, policy))

                        start_actual, _ = start_index.query_overlap(window, policy)
                        end_actual, _ = end_index.query_overlap(window, policy)
                        adaptive_actual, _, _ = adaptive_index.query_overlap(window, policy)
                        range_actual, _, _ = range_tree.query_overlap(window, policy)

                        self.assertEqual(sorted(start_actual), expected)
                        self.assertEqual(sorted(end_actual), expected)
                        self.assertEqual(sorted(adaptive_actual), expected)
                        self.assertEqual(sorted(range_actual), expected)

    def test_generation_is_deterministic(self) -> None:
        first = generate_intervals(100, "mixed", seed=23)
        second = generate_intervals(100, "mixed", seed=23)
        self.assertEqual(first, second)

    def test_range_tree_reports_reference_amplification(self) -> None:
        rows = generate_intervals(1_000, "uniform", seed=31)
        tree = StaticEndpointRangeTree(rows)
        self.assertGreater(tree.stored_reference_count(), len(rows))


if __name__ == "__main__":
    unittest.main()
