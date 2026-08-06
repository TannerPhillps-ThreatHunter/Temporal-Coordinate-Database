import unittest

from research.event_geometry.model import (
    Event,
    QuantizedSignatureIndex,
    ScalarIntervalIndex,
    derive_same_entity_geometry,
)
from research.event_geometry.robustness import scale_variation_experiment


class EventGeometryTests(unittest.TestCase):
    def test_derived_interval_arithmetic(self) -> None:
        events = [
            Event(1, "x", "a", 10.0, 15.0),
            Event(2, "x", "a", 30.0, 38.0),
        ]
        intervals, trajectories = derive_same_entity_geometry(events)
        self.assertEqual(len(intervals), 1)
        interval = intervals[0]
        self.assertEqual(interval.interval_key, ("same_entity_next", 1, 2))
        self.assertEqual(interval.signed_gap, 15.0)
        self.assertEqual(interval.delta_start, 20.0)
        self.assertEqual(interval.delta_end, 23.0)
        self.assertEqual(interval.duration_delta, 3.0)
        self.assertEqual(trajectories[0].event_ids, (1, 2))

    def test_interval_signature_is_translation_invariant(self) -> None:
        original = [
            Event(1, "x", "a", 10.0, 15.0),
            Event(2, "x", "a", 30.0, 38.0),
            Event(3, "x", "a", 50.0, 55.0),
        ]
        shifted = [
            Event(e.event_id, e.entity_id, e.event_type, e.start + 1000.0, e.end + 1000.0)
            for e in original
        ]
        ints_a, _ = derive_same_entity_geometry(original)
        ints_b, _ = derive_same_entity_geometry(shifted)
        self.assertEqual(
            [i.delta_start for i in ints_a],
            [i.delta_start for i in ints_b],
        )

    def test_scalar_index_matches_scan(self) -> None:
        events = [
            Event(1, "a", "x", 0.0, 1.0),
            Event(2, "a", "x", 10.0, 11.0),
            Event(3, "a", "x", 25.0, 26.0),
            Event(4, "b", "x", 0.0, 1.0),
            Event(5, "b", "x", 20.0, 21.0),
        ]
        intervals, _ = derive_same_entity_geometry(events)
        index = ScalarIntervalIndex(intervals, "delta_start")
        actual = set(index.range_query(9.0, 16.0).tolist())
        values = [i.delta_start for i in intervals]
        expected = {i for i, v in enumerate(values) if 9.0 <= v <= 16.0}
        self.assertEqual(actual, expected)

    def test_quantized_signature_index(self) -> None:
        index = QuantizedSignatureIndex(width=3, bin_width=10.0)
        index.add_trajectory("a", [100.0, 101.0, 99.0, 100.0])
        index.add_trajectory("b", [102.0, 99.0, 101.0, 98.0])
        hits = index.lookup([100.0, 100.0, 100.0])
        self.assertTrue(any(h.entity_id == "a" for h in hits))
        self.assertTrue(any(h.entity_id == "b" for h in hits))

    def test_scale_sensitive_and_scale_invariant_metrics_are_distinct(self) -> None:
        result = scale_variation_experiment(per_family=40, events_per_entity=18, seed=17)
        self.assertGreater(result["log_centered"], result["raw"])
        self.assertGreater(result["log_centered"], 0.90)


if __name__ == "__main__":
    unittest.main()
