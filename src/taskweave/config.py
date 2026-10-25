"""Validated runtime configuration and TOML loading."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class TaskWeaveConfig:
    max_workers: int = 2
    queue_capacity: int = 100
    scheduling_policy: str = "fifo"
    overflow_policy: str = "reject"
    shutdown_grace_seconds: float = 5.0

    def __post_init__(self) -> None:
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if self.queue_capacity < 1:
            raise ValueError("queue_capacity must be at least 1")
        if self.scheduling_policy not in {"fifo", "priority"}:
            raise ValueError("scheduling_policy must be fifo or priority")
        if self.overflow_policy not in {"reject", "block", "timeout"}:
            raise ValueError("unsupported overflow_policy")
        if self.shutdown_grace_seconds < 0:
            raise ValueError("shutdown_grace_seconds must be non-negative")


def load_config(path: str | Path = "configs/default.toml") -> TaskWeaveConfig:
    """Load and validate TaskWeave runtime settings from a TOML file."""
    config_path = Path(path)

    with config_path.open("rb") as file:
        document = tomllib.load(file)

    section = document.get("taskweave", {})
    if not isinstance(section, dict):
        raise ValueError("The [taskweave] section must be a TOML table")

    allowed_keys = {
        "max_workers",
        "queue_capacity",
        "scheduling_policy",
        "overflow_policy",
        "shutdown_grace_seconds",
    }
    unknown_keys = set(section) - allowed_keys
    if unknown_keys:
        names = ", ".join(sorted(unknown_keys))
        raise ValueError(f"Unknown [taskweave] setting(s): {names}")

    try:
        return TaskWeaveConfig(**section)
    except TypeError as exc:
        raise ValueError(f"Invalid [taskweave] configuration: {exc}") from exc
