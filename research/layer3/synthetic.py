from __future__ import annotations

from random import Random
from typing import List

from .reference import Interval, Window


DISTRIBUTIONS = (
    "uniform",
    "fixed",
    "mixed",
    "clustered",
    "equal_start",
    "long",
)


def generate_intervals(
    count: int,
    distribution: str,
    *,
    seed: int = 0,
    domain: int = 1_000_000,
) -> List[Interval]:
    """Generate deterministic determinate interval populations.

    The generator deliberately includes pathological distributions rather than
    only statistically convenient ones. R3.7 will later add open and uncertain
    extents as separate research populations.
    """

    if count < 0:
        raise ValueError("count must be non-negative")
    if domain <= 0:
        raise ValueError("domain must be positive")
    if distribution not in DISTRIBUTIONS:
        raise ValueError(f"unsupported distribution: {distribution}")

    rng = Random(seed)
    intervals: List[Interval] = []

    for object_id in range(count):
        if distribution == "uniform":
            start = rng.randrange(domain)
            duration = rng.randint(1, 1_000)

        elif distribution == "fixed":
            start = rng.randrange(domain)
            duration = 100

        elif distribution == "mixed":
            start = rng.randrange(domain)
            p = rng.random()
            if p < 0.70:
                duration = rng.randint(1, 100)
            elif p < 0.95:
                duration = rng.randint(101, 10_000)
            else:
                duration = rng.randint(10_001, 200_000)

        elif distribution == "clustered":
            center = rng.choice((domain // 5, domain // 2, (4 * domain) // 5))
            start = int(rng.gauss(center, domain / 100))
            start = max(0, min(domain - 1, start))
            duration = rng.randint(1, 5_000)

        elif distribution == "equal_start":
            bucket_count = max(1, count // 50)
            start = (rng.randrange(bucket_count) * 1_000) % domain
            duration = rng.randint(1, 100_000)

        elif distribution == "long":
            start = rng.randrange(domain)
            duration = rng.randint(max(1, domain // 10), max(1, domain // 2))

        else:  # pragma: no cover - guarded above
            raise AssertionError(distribution)

        intervals.append(
            Interval(
                object_id=object_id,
                start=start,
                end=start + duration,
            )
        )

    return intervals


def generate_windows(
    count: int,
    *,
    seed: int = 1,
    domain: int = 1_000_000,
) -> List[Window]:
    """Generate a reproducible mix of short and broad overlap windows."""

    rng = Random(seed)
    widths = (10, 100, 1_000, 10_000, 100_000)
    windows: List[Window] = []

    for _ in range(count):
        start = rng.randrange(domain)
        width = rng.choice(widths)
        windows.append(Window(start=start, end=start + width))

    return windows
