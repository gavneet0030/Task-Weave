"""Open-loop arrival timing helpers."""

import random


def poisson_interarrival_seconds(rate_per_second: float) -> float:
    """Sample an exponential interarrival time for a Poisson arrival process."""
    if rate_per_second <= 0:
        raise ValueError("rate_per_second must be positive")
    return random.expovariate(rate_per_second)