import pytest

from taskweave.config import TaskWeaveConfig


def test_default_config():
    config = TaskWeaveConfig()
    assert config.max_workers == 2
    assert config.queue_capacity == 100


def test_config_rejects_invalid_worker_count():
    with pytest.raises(ValueError):
        TaskWeaveConfig(max_workers=0)