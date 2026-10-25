"""Task lifecycle states and guarded state transitions."""

from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from uuid import uuid4


class TaskState(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


TERMINAL_STATES = {
    TaskState.SUCCEEDED,
    TaskState.FAILED,
    TaskState.CANCELLED,
    TaskState.TIMED_OUT,
}

_ALLOWED_TRANSITIONS = {
    TaskState.CREATED: {TaskState.QUEUED, TaskState.CANCELLED},
    TaskState.QUEUED: {
        TaskState.RUNNING,
        TaskState.CANCELLED,
        TaskState.TIMED_OUT,
    },
    TaskState.RUNNING: {
        TaskState.SUCCEEDED,
        TaskState.FAILED,
        TaskState.TIMED_OUT,
    },
    TaskState.SUCCEEDED: set(),
    TaskState.FAILED: set(),
    TaskState.CANCELLED: set(),
    TaskState.TIMED_OUT: set(),
}


@dataclass
class Task:
    """Minimal task metadata; execution is added in a later phase."""

    task_id: str = field(default_factory=lambda: str(uuid4()))
    state: TaskState = TaskState.CREATED
    _lock: Lock = field(default_factory=Lock, repr=False, compare=False)

    @property
    def is_terminal(self) -> bool:
        return self.state in TERMINAL_STATES

    def transition_to(self, new_state: TaskState) -> None:
        """Perform one valid state transition atomically."""
        with self._lock:
            if new_state not in _ALLOWED_TRANSITIONS[self.state]:
                raise ValueError(
                    f"Invalid task transition: {self.state.value} -> {new_state.value}"
                )
            self.state = new_state