import pytest

from taskweave.workloads.open_loop import poisson_interarrival_seconds


def test_interarrival_is_positive():
    assert poisson_interarrival_seconds(10.0) > 0


def test_interarrival_rejects_nonpositive_rate():
    with pytest.raises(ValueError):
        poisson_interarrival_seconds(0)