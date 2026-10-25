"""Validated runtime configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskWeaveConfig:
    max_workers: int = 2
    queue_capacity: int = 100
    scheduling_policy: str = "fifo"
    overflow_policy: str = "reject"

    def __post_init__(self) -> None:
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if self.queue_capacity < 1:
            raise ValueError("queue_capacity must be at least 1")
        if self.scheduling_policy not in {"fifo", "priority"}:
            raise ValueError("scheduling_policy must be fifo or priority")
        if self.overflow_policy not in {"reject", "block", "timeout"}:
            raise ValueError("unsupported overflow_policy")