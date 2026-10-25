"""Dependency-free descriptive statistics for benchmark samples."""

import math
from collections.abc import Iterable


def percentile(values: Iterable[float], p: float) -> float:
    """Calculate an interpolated percentile, with p in the range 0..100."""
    data = sorted(values)
    if not data:
        raise ValueError("at least one measurement is required")
    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")
    if len(data) == 1:
        return data[0]

    position = (len(data) - 1) * p / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return data[lower]
    fraction = position - lower
    return data[lower] + fraction * (data[upper] - data[lower])


def throughput(completed_tasks: int, elapsed_seconds: float) -> float:
    """Return completed tasks per second."""
    if completed_tasks < 0:
        raise ValueError("completed_tasks cannot be negative")
    if elapsed_seconds <= 0:
        raise ValueError("elapsed_seconds must be positive")
    return completed_tasks / elapsed_seconds