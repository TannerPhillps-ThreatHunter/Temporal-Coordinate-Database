from __future__ import annotations

import argparse
import time
from collections import defaultdict
from typing import Dict, List, Sequence

import numpy as np

from .model import (
    Event,
    QuantizedSignatureIndex,
    ScalarIntervalIndex,
    derive_same_entity_geometry,
)
from .synthetic import generate_population


def _group_events(events: Sequence[Event]) -> Dict[str, List[Event]]:
    grouped: Dict[str, List[Event]] = defaultdict(list)
    for event in events:
        grouped[event.entity_id].append(event)
    for rows in grouped.values():
        rows.sort(key=lambda e: (e.start, e.end, e.event_id))
    return grouped


def _leave_one_out_nn_accuracy(X: np.ndarray, labels: np.ndarray, block: int = 200) -> float:
    correct = 0
    n = len(X)
    for start in range(0, n, block):
        A = X[start:start + block]
        distances = ((A[:, None, :] - X[None, :, :]) ** 2).sum(axis=2)
        for local in range(len(A)):
            distances[local, start + local] = np.inf
        nearest = distances.argmin(axis=1)
        correct += int(np.count_nonzero(labels[nearest] == labels[start:start + len(A)]))
    return correct / n


def run(
    *,
    per_family: int = 300,
    events_per_entity: int = 24,
    seed: int = 20260806,
    signature_width: int = 4,
) -> Dict[str, object]:
    events, family_by_entity = generate_population(
        per_family=per_family,
        events_per_entity=events_per_entity,
        seed=seed,
    )
    intervals, trajectories = derive_same_entity_geometry(events)
    interval_by_key = {i.interval_key: i for i in intervals}

    grouped = _group_events(events)
    entity_order = sorted(grouped)
    labels = np.asarray([family_by_entity[e] for e in entity_order])
    trajectory_by_entity = {t.entity_id: t for t in trajectories}

    absolute = np.stack(
        [np.asarray([row.start for row in grouped[e]], dtype=np.float64) for e in entity_order]
    )
    delta_start = np.stack(
        [
            np.asarray(
                [interval_by_key[k].delta_start for k in trajectory_by_entity[e].interval_keys],
                dtype=np.float64,
            )
            for e in entity_order
        ]
    )

    abs_accuracy = _leave_one_out_nn_accuracy(absolute, labels)
    interval_accuracy = _leave_one_out_nn_accuracy(delta_start, labels)

    scalar_index = ScalarIntervalIndex(intervals, "delta_start")
    values = np.asarray([i.delta_start for i in intervals], dtype=np.float64)
    rng = np.random.default_rng(seed + 1)
    range_queries = [
        (float(center - 5.0), float(center + 5.0))
        for center in rng.uniform(10.0, 280.0, 1000)
    ]

    t0 = time.perf_counter()
    full_counts = []
    for lower, upper in range_queries:
        full_counts.append(int(np.count_nonzero((values >= lower) & (values <= upper))))
    full_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    index_counts = []
    for lower, upper in range_queries:
        index_counts.append(len(scalar_index.range_query(lower, upper)))
    index_seconds = time.perf_counter() - t0

    if full_counts != index_counts:
        raise AssertionError("scalar interval index disagrees with full scan")

    trajectory_values: Dict[str, np.ndarray] = {}
    for trajectory in trajectories:
        trajectory_values[trajectory.entity_id] = np.asarray(
            [interval_by_key[k].delta_start for k in trajectory.interval_keys],
            dtype=np.float64,
        )

    signature_results = {}
    for bin_width in (5.0, 10.0, 20.0):
        index = QuantizedSignatureIndex(width=signature_width, bin_width=bin_width)
        for entity_id, vals in trajectory_values.items():
            index.add_trajectory(entity_id, vals)

        covered = 0
        purity_sum = 0.0
        candidate_sum = 0
        total_windows = 0

        for entity_id, vals in trajectory_values.items():
            family = family_by_entity[entity_id]
            for position in range(len(vals) - signature_width + 1):
                total_windows += 1
                query = vals[position:position + signature_width]
                hits = [h for h in index.lookup(query) if h.entity_id != entity_id]
                if not hits:
                    continue
                covered += 1
                purity_sum += sum(
                    family_by_entity[h.entity_id] == family for h in hits
                ) / len(hits)
                candidate_sum += len(hits)

        signature_results[str(int(bin_width))] = {
            "distinct_signatures": index.distinct_signatures,
            "coverage": covered / total_windows,
            "mean_family_purity": purity_sum / covered if covered else 0.0,
            "mean_candidates_when_covered": candidate_sum / covered if covered else 0.0,
        }

    all_pair_count = len(events) * (len(events) - 1) // 2

    return {
        "events": len(events),
        "derived_event_intervals": len(intervals),
        "all_unordered_event_pairs": all_pair_count,
        "all_pairs_to_selected_intervals_ratio": all_pair_count / len(intervals),
        "trajectories": len(trajectories),
        "absolute_timestamp_nn_accuracy": abs_accuracy,
        "interval_signature_nn_accuracy": interval_accuracy,
        "scalar_range_queries": len(range_queries),
        "scalar_full_scan_examined_per_query": len(intervals),
        "scalar_mean_results_per_query": float(np.mean(full_counts)),
        "scalar_full_scan_seconds": full_seconds,
        "scalar_index_seconds": index_seconds,
        "signature_index": signature_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-family", type=int, default=300)
    parser.add_argument("--events-per-entity", type=int, default=24)
    parser.add_argument("--seed", type=int, default=20260806)
    args = parser.parse_args()

    result = run(
        per_family=args.per_family,
        events_per_entity=args.events_per_entity,
        seed=args.seed,
    )

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
