from __future__ import annotations

import math
from typing import Dict, Iterable, Sequence

import numpy as np

from .synthetic import FAMILIES, _gaps


def leave_one_out_nn_accuracy(X: np.ndarray, labels: np.ndarray, block: int = 200) -> float:
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


def scale_variation_experiment(
    *,
    per_family: int = 300,
    events_per_entity: int = 24,
    seed: int = 4242,
) -> Dict[str, float]:
    """Test trajectory similarity under uniform temporal stretching/compression.

    Each trajectory receives an independent multiplicative time scale sampled
    log-uniformly from approximately 0.35x to 3x.
    """

    rng = np.random.default_rng(seed)
    rows = []
    labels = []

    for family in FAMILIES:
        for _ in range(per_family):
            scale = float(np.exp(rng.uniform(np.log(0.35), np.log(3.0))))
            gaps = _gaps(family, events_per_entity - 1, rng) * scale
            rows.append(gaps)
            labels.append(family)

    X = np.stack(rows)
    y = np.asarray(labels)

    median_normalized = X / np.median(X, axis=1, keepdims=True)
    mean_normalized = X / np.mean(X, axis=1, keepdims=True)
    l2_normalized = X / np.linalg.norm(X, axis=1, keepdims=True)
    log_centered = np.log(X) - np.mean(np.log(X), axis=1, keepdims=True)

    return {
        "raw": leave_one_out_nn_accuracy(X, y),
        "median_normalized": leave_one_out_nn_accuracy(median_normalized, y),
        "mean_normalized": leave_one_out_nn_accuracy(mean_normalized, y),
        "l2_normalized": leave_one_out_nn_accuracy(l2_normalized, y),
        "log_centered": leave_one_out_nn_accuracy(log_centered, y),
    }


def delete_internal_events(
    gaps: Sequence[float],
    deletion_probability: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Delete internal observations and derive the gaps that remain observable.

    The first and last events are retained so this experiment isolates missing
    internal observations rather than prefix/suffix truncation.

    If an intermediate event disappears, adjacent inter-event displacements
    coalesce by addition. For example:

        A --d1--> B --d2--> C

    becomes:

        A --(d1+d2)--> C
    """

    if not 0.0 <= deletion_probability <= 1.0:
        raise ValueError("deletion_probability must be in [0, 1]")

    arr = np.asarray(gaps, dtype=np.float64)
    event_count = len(arr) + 1
    keep = np.ones(event_count, dtype=bool)
    if event_count > 2:
        keep[1:-1] = rng.random(event_count - 2) >= deletion_probability

    retained = np.flatnonzero(keep)
    cumulative = np.concatenate(([0.0], np.cumsum(arr)))
    return np.diff(cumulative[retained])


def _resample(values: np.ndarray, target_length: int) -> np.ndarray:
    if len(values) == target_length:
        return values
    if len(values) == 1:
        return np.full(target_length, values[0], dtype=np.float64)
    source_axis = np.linspace(0.0, 1.0, len(values))
    target_axis = np.linspace(0.0, 1.0, target_length)
    return np.interp(target_axis, source_axis, values)


def resampled_log_distance(observed: Sequence[float], reference: Sequence[float]) -> float:
    """Naive fixed-length baseline for incomplete interval sequences."""

    x = _resample(np.asarray(observed, dtype=np.float64), len(reference))
    y = np.asarray(reference, dtype=np.float64)
    return float(np.mean((np.log(x) - np.log(y)) ** 2))


def dtw_log_distance(observed: Sequence[float], reference: Sequence[float]) -> float:
    """Ordinary DTW baseline over log inter-event displacement."""

    x = np.log(np.asarray(observed, dtype=np.float64))
    y = np.log(np.asarray(reference, dtype=np.float64))
    previous = np.full(len(y) + 1, np.inf)
    previous[0] = 0.0

    for xv in x:
        current = np.full(len(y) + 1, np.inf)
        for j, yv in enumerate(y, start=1):
            cost = float((xv - yv) ** 2)
            current[j] = cost + min(previous[j], current[j - 1], previous[j - 1])
        previous = current

    return float(previous[len(y)] / (len(x) + len(y)))


def coalescence_log_distance(
    observed: Sequence[float],
    reference: Sequence[float],
    *,
    max_merge: int = 5,
    merge_penalty: float = 0.02,
) -> float:
    """Deletion-aware alignment for interval displacement sequences.

    One observed displacement may match the sum of several consecutive
    reference displacements. This directly models the geometry produced when
    one or more intermediate events are missing.

    This is an experimental baseline, not a novelty claim or production metric.
    """

    x = np.asarray(observed, dtype=np.float64)
    y = np.asarray(reference, dtype=np.float64)
    if max_merge <= 0:
        raise ValueError("max_merge must be positive")

    n = len(x)
    m = len(y)
    dp = np.full((n + 1, m + 1), np.inf)
    dp[0, 0] = 0.0
    prefix = np.concatenate(([0.0], np.cumsum(y)))

    for j in range(1, n + 1):
        observed_gap = x[j - 1]
        for i in range(1, m + 1):
            best = np.inf
            for width in range(1, min(max_merge, i) + 1):
                reference_sum = prefix[i] - prefix[i - width]
                cost = (
                    (math.log(observed_gap) - math.log(reference_sum)) ** 2
                    + merge_penalty * (width - 1)
                )
                best = min(best, dp[j - 1, i - width] + cost)
            dp[j, i] = best

    return float(dp[n, m] / max(1, n))


def _nearest_family(
    observed: Sequence[float],
    prototypes: Dict[str, np.ndarray],
    distance,
) -> str:
    return min(FAMILIES, key=lambda family: distance(observed, prototypes[family]))


def missing_event_experiment(
    *,
    train_per_family: int = 100,
    test_per_family: int = 100,
    events_per_entity: int = 24,
    deletion_rates: Iterable[float] = (0.0, 0.05, 0.10, 0.20, 0.30, 0.40),
    seed: int = 12345,
) -> Dict[float, Dict[str, float]]:
    """Measure trajectory recognition as internal observations disappear.

    Clean family prototypes are median interval trajectories. Test trajectories
    are independently generated and then have internal events deleted.

    The absolute accuracies are prototype-classification measurements and are
    not directly comparable to E0's leave-one-out nearest-neighbor score. The
    robustness slope across deletion rates is the intended comparison.
    """

    if train_per_family <= 0 or test_per_family <= 0 or events_per_entity < 3:
        raise ValueError("invalid experiment size")

    rng = np.random.default_rng(seed)
    gap_count = events_per_entity - 1

    training = {
        family: np.stack([_gaps(family, gap_count, rng) for _ in range(train_per_family)])
        for family in FAMILIES
    }
    prototypes = {
        family: np.median(training[family], axis=0)
        for family in FAMILIES
    }
    tests = {
        family: [_gaps(family, gap_count, rng) for _ in range(test_per_family)]
        for family in FAMILIES
    }

    results: Dict[float, Dict[str, float]] = {}

    for rate in deletion_rates:
        rate = float(rate)
        deletion_rng = np.random.default_rng(seed + 1000 + int(round(rate * 10000)))
        correct = {"resampled": 0, "dtw": 0, "coalescence": 0}
        observed_lengths = []
        total = 0

        for family in FAMILIES:
            for clean in tests[family]:
                observed = delete_internal_events(clean, rate, deletion_rng)
                observed_lengths.append(len(observed))
                total += 1

                if _nearest_family(observed, prototypes, resampled_log_distance) == family:
                    correct["resampled"] += 1
                if _nearest_family(observed, prototypes, dtw_log_distance) == family:
                    correct["dtw"] += 1
                if _nearest_family(observed, prototypes, coalescence_log_distance) == family:
                    correct["coalescence"] += 1

        results[rate] = {
            "resampled": correct["resampled"] / total,
            "dtw": correct["dtw"] / total,
            "coalescence": correct["coalescence"] / total,
            "mean_observed_gaps": float(np.mean(observed_lengths)),
        }

    return results
