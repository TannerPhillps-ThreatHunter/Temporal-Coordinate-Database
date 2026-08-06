from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from .model import Event


FAMILIES = ("periodic", "alternating", "burst", "accelerating", "random")


def _gaps(family: str, count: int, rng: np.random.Generator) -> np.ndarray:
    if family == "periodic":
        return np.maximum(1.0, 100.0 + rng.normal(0.0, 4.0, count))
    if family == "alternating":
        base = np.asarray([55.0 if i % 2 == 0 else 145.0 for i in range(count)])
        return np.maximum(1.0, base + rng.normal(0.0, 4.0, count))
    if family == "burst":
        pattern = (20.0, 20.0, 260.0)
        base = np.asarray([pattern[i % len(pattern)] for i in range(count)])
        return np.maximum(1.0, base + rng.normal(0.0, 5.0, count))
    if family == "accelerating":
        base = np.linspace(180.0, 40.0, count)
        return np.maximum(1.0, base + rng.normal(0.0, 4.0, count))
    if family == "random":
        return rng.uniform(20.0, 260.0, count)
    raise ValueError(f"unsupported family: {family}")


def generate_population(
    *,
    per_family: int = 300,
    events_per_entity: int = 24,
    seed: int = 20260806,
) -> Tuple[List[Event], Dict[str, str]]:
    """Generate families with randomized absolute temporal translations.

    Family identity is encoded primarily in inter-event spacing, while absolute
    start offsets are intentionally independent of family.
    """

    if per_family <= 0 or events_per_entity < 2:
        raise ValueError("invalid population size")

    rng = np.random.default_rng(seed)
    events: List[Event] = []
    family_by_entity: Dict[str, str] = {}
    event_id = 0

    for family in FAMILIES:
        for i in range(per_family):
            entity_id = f"{family}-{i:04d}"
            family_by_entity[entity_id] = family

            offset = float(rng.uniform(0.0, 10_000_000.0))
            gaps = _gaps(family, events_per_entity - 1, rng)
            starts = np.empty(events_per_entity, dtype=np.float64)
            starts[0] = offset
            starts[1:] = offset + np.cumsum(gaps)
            durations = np.maximum(1.0, rng.normal(15.0, 2.0, events_per_entity))

            for start, duration in zip(starts, durations):
                events.append(
                    Event(
                        event_id=event_id,
                        entity_id=entity_id,
                        event_type="activity",
                        start=float(start),
                        end=float(start + duration),
                    )
                )
                event_id += 1

    return events, family_by_entity
