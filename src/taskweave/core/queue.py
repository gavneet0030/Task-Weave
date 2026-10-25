"""A small bounded FIFO queue used as an initial building block."""

from queue import Empty, Full, Queue
from typing import Generic, TypeVar

T = TypeVar("T")


class BoundedTaskQueue(Generic[T]):
    """Thread-safe bounded FIFO storage.

    This wrapper does not yet implement scheduler lifecycle semantics.
    A queue.Full exception indicates overload when a non-blocking put is used.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be greater than zero")
        self._queue: Queue[T] = Queue(maxsize=capacity)

    @property
    def capacity(self) -> int:
        return self._queue.maxsize

    def put_nowait(self, item: T) -> None:
        self._queue.put_nowait(item)

    def get_nowait(self) -> T:
        return self._queue.get_nowait()

    def task_done(self) -> None:
        self._queue.task_done()

    def qsize(self) -> int:
        return self._queue.qsize()

    @staticmethod
    def is_empty_error(error: Exception) -> bool:
        return isinstance(error, Empty)

    @staticmethod
    def is_full_error(error: Exception) -> bool:
        return isinstance(error, Full)