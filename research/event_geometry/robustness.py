from __future__ import annotations

from typing import Dict

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
