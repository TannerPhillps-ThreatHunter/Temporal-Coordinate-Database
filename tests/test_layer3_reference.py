import unittest

from research.layer3.baselines import (
    AdaptiveEndpointIndex,
    EndSortedIndex,
    StartSortedIndex,
)
from research.layer3.reference import (
    BoundaryPolicy,
    Interval,
    Window,
    reference_scan_overlap,
)
from research.layer3.synthetic import DISTRIBUTIONS, generate_intervals, generate_windows


class BoundaryPolicyTests(unittest.TestCase):
    def test_half_open_touching_intervals_do_not_overlap(self) -> None:
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

    def test_zero_length_interval_is_empty_under_half_open_overlap(self) -> None:
        rows = [Interval(1, 10, 10)]
        self.assertEqual(
            reference_scan_overlap(rows, Window(9, 11), BoundaryPolicy.HALF_OPEN),
            [],
        )


class DifferentialIndexTests(unittest.TestCase):
    def test_all_1d_baselines_equal_reference_oracle(self) -> None:
        for distribution in DISTRIBUTIONS:
            with self.subTest(distribution=distribution):
                rows = generate_intervals(5_000, distribution, seed=17)
                windows = generate_windows(100, seed=19)

                start_index = StartSortedIndex(rows)
                end_index = EndSortedIndex(rows)
                adaptive_index = AdaptiveEndpointIndex(rows)

                for policy in (BoundaryPolicy.HALF_OPEN, BoundaryPolicy.CLOSED):
                    for window in windows:
                        expected = sorted(reference_scan_overlap(rows, window, policy))

                        start_actual, _ = start_index.query_overlap(window, policy)
                        end_actual, _ = end_index.query_overlap(window, policy)
                        adaptive_actual, _, _ = adaptive_index.query_overlap(window, policy)

                        self.assertEqual(sorted(start_actual), expected)
                        self.assertEqual(sorted(end_actual), expected)
                        self.assertEqual(sorted(adaptive_actual), expected)

    def test_generation_is_deterministic(self) -> None:
        first = generate_intervals(100, "mixed", seed=23)
        second = generate_intervals(100, "mixed", seed=23)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
