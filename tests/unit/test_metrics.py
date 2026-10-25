import pytest

from taskweave.metrics.statistics import percentile, throughput


def test_percentiles():
    assert percentile([10, 20, 30], 50) == 20
    assert percentile([10, 20, 30], 0) == 10
    assert percentile([10, 20, 30], 100) == 30


def test_percentile_rejects_empty_samples():
    with pytest.raises(ValueError):
        percentile([], 50)


def test_throughput():
    assert throughput(100, 2.0) == 50.0