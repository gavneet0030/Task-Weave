import pytest

from taskweave.config import TaskWeaveConfig, load_config


def test_default_config():
    config = TaskWeaveConfig()
    assert config.max_workers == 2
    assert config.queue_capacity == 100
    assert config.scheduling_policy == "fifo"
    assert config.overflow_policy == "reject"
    assert config.shutdown_grace_seconds == 5.0


def test_config_rejects_invalid_worker_count():
    with pytest.raises(ValueError):
        TaskWeaveConfig(max_workers=0)


def test_config_loads_project_default_toml():
    config = load_config()
    assert config.max_workers == 2
    assert config.queue_capacity == 100
    assert config.scheduling_policy == "fifo"
    assert config.overflow_policy == "reject"
    assert config.shutdown_grace_seconds == 5.0


def test_config_loads_custom_toml(tmp_path):
    path = tmp_path / "custom.toml"
    path.write_text(
        '[taskweave]\n'
        'max_workers = 4\n'
        'queue_capacity = 25\n'
        'scheduling_policy = "fifo"\n'
        'overflow_policy = "reject"\n'
        'shutdown_grace_seconds = 2.5\n',
        encoding="utf-8",
    )

    config = load_config(path)
    assert config.max_workers == 4
    assert config.queue_capacity == 25
    assert config.shutdown_grace_seconds == 2.5


def test_config_rejects_unknown_setting(tmp_path):
    path = tmp_path / "invalid.toml"
    path.write_text(
        '[taskweave]\n'
        'max_workers = 2\n'
        'unknown_setting = true\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown"):
        load_config(path)


def test_config_rejects_invalid_policy_from_toml(tmp_path):
    path = tmp_path / "invalid.toml"
    path.write_text(
        '[taskweave]\n'
        'overflow_policy = "magic"\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="overflow_policy"):
        load_config(path)


def test_config_rejects_negative_shutdown_grace():
    with pytest.raises(ValueError, match="shutdown_grace_seconds"):
        TaskWeaveConfig(shutdown_grace_seconds=-1)
