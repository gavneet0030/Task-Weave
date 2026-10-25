"""Thread-based worker pool with bounded submission and graceful shutdown."""

from concurrent.futures import Future
from queue import Full, Queue
from threading import Lock, Thread
from typing import Any, Callable


class WorkerPool:
    """Execute callables using fixed workers and a bounded pending queue."""

    _STOP = object()

    def __init__(self, max_workers: int, queue_capacity: int = 100) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if queue_capacity < 1:
            raise ValueError("queue_capacity must be at least 1")

        self.max_workers = max_workers
        self.queue_capacity = queue_capacity
        self._queue: Queue = Queue(maxsize=queue_capacity)
        self._threads: list[Thread] = []
        self._lock = Lock()
        self._started = False
        self._shutdown = False

    def start(self) -> None:
        """Start all worker threads exactly once."""
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Cannot start a shut-down worker pool")
            if self._started:
                return

            self._started = True
            for index in range(self.max_workers):
                thread = Thread(
                    target=self._worker,
                    name=f"taskweave-worker-{index + 1}",
                    daemon=False,
                )
                self._threads.append(thread)
                thread.start()

    def submit(
        self,
        function: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Future:
        """Submit without blocking; reject if the pending queue is full."""
        with self._lock:
            if not self._started:
                raise RuntimeError("Call start() before submit()")
            if self._shutdown:
                raise RuntimeError("Cannot submit after shutdown")

            future = Future()
            try:
                self._queue.put_nowait((future, function, args, kwargs))
            except Full:
                raise Full(
                    f"Worker queue is full (capacity={self.queue_capacity})"
                ) from None
            return future

    def _worker(self) -> None:
        while True:
            item = self._queue.get()
            try:
                if item is self._STOP:
                    return

                future, function, args, kwargs = item
                if not future.set_running_or_notify_cancel():
                    continue

                try:
                    result = function(*args, **kwargs)
                except BaseException as error:
                    future.set_exception(error)
                else:
                    future.set_result(result)
            finally:
                self._queue.task_done()

    def _finish_shutdown(self) -> None:
        """Drain accepted work, then stop and join every worker."""
        self._queue.join()
        for _ in self._threads:
            self._queue.put(self._STOP)
        self._queue.join()
        for thread in self._threads:
            thread.join()

    def shutdown(self, wait: bool = True) -> None:
        """Reject new submissions; wait only when requested."""
        with self._lock:
            if not self._started:
                self._shutdown = True
                return

            if self._shutdown:
                threads = list(self._threads)
                should_finish = False
            else:
                self._shutdown = True
                threads = list(self._threads)
                should_finish = True

        if should_finish:
            if wait:
                self._finish_shutdown()
            else:
                from threading import Thread

                Thread(
                    target=self._finish_shutdown,
                    name="taskweave-shutdown",
                    daemon=True,
                ).start()
        elif wait:
            for thread in threads:
                thread.join()
