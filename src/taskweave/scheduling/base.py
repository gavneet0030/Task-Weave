"""FIFO scheduler with cancellation and task execution timeouts."""

from concurrent.futures import Future
from threading import Lock, Timer
from typing import Any, Callable

from taskweave.config import TaskWeaveConfig
from taskweave.core.task import Task, TaskState
from taskweave.workers.pool import WorkerPool


class Scheduler:
    """Submit tasks in FIFO order and track their execution lifecycle."""

    def __init__(
        self,
        max_workers: int | None = None,
        queue_capacity: int | None = None,
        *,
        config: TaskWeaveConfig | None = None,
    ) -> None:
        if config is not None and (
            max_workers is not None or queue_capacity is not None
        ):
            raise ValueError(
                "Pass either config or max_workers/queue_capacity, not both"
            )

        if config is None:
            config = TaskWeaveConfig(
                max_workers=2 if max_workers is None else max_workers,
                queue_capacity=100 if queue_capacity is None else queue_capacity,
            )

        if config.scheduling_policy != "fifo":
            raise NotImplementedError(
                "Only FIFO scheduling is implemented currently"
            )
        if config.overflow_policy != "reject":
            raise NotImplementedError(
                "Only reject overflow handling is implemented currently"
            )

        self.config = config
        self._pool = WorkerPool(
            max_workers=config.max_workers,
            queue_capacity=config.queue_capacity,
        )
        self._lock = Lock()
        self._started = False
        self._shutdown = False
        self._futures: dict[str, Future] = {}
        self._tasks: dict[str, Task] = {}
        self._timers: dict[str, Timer] = {}

    def start(self) -> None:
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Cannot start a shut-down scheduler")
            if self._started:
                return
            self._pool.start()
            self._started = True

    def submit(
        self,
        task: Task,
        function: Callable[..., Any],
        *args: Any,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Future:
        if timeout is not None and timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        with self._lock:
            if not self._started:
                raise RuntimeError("Call start() before submit()")
            if self._shutdown:
                raise RuntimeError("Cannot submit after shutdown")
            if task.state is not TaskState.CREATED:
                raise ValueError("Only CREATED tasks can be submitted")

            task.transition_to(TaskState.QUEUED)
            self._tasks[task.task_id] = task

            try:
                future = self._pool.submit(
                    self._execute_task, task, function, args, kwargs
                )
            except Exception:
                task.transition_to(TaskState.CANCELLED)
                self._tasks.pop(task.task_id, None)
                raise

            self._futures[task.task_id] = future

            if timeout is not None:
                timer = Timer(timeout, self._on_timeout, args=(task.task_id,))
                timer.daemon = True
                self._timers[task.task_id] = timer
                timer.start()

            future.add_done_callback(
                lambda completed, task_id=task.task_id:
                self._on_future_done(task_id, completed)
            )
            return future

    def _execute_task(
        self,
        task: Task,
        function: Callable[..., Any],
        args: tuple,
        kwargs: dict,
    ) -> Any:
        with self._lock:
            if task.state is TaskState.TIMED_OUT:
                raise TimeoutError(
                    f"Task {task.task_id} timed out before execution"
                )
            if task.state is TaskState.CANCELLED:
                raise RuntimeError(f"Task {task.task_id} was cancelled")
            task.transition_to(TaskState.RUNNING)

        try:
            result = function(*args, **kwargs)
        except Exception:
            with self._lock:
                if task.state is TaskState.RUNNING:
                    task.transition_to(TaskState.FAILED)
            raise
        else:
            with self._lock:
                if task.state is TaskState.RUNNING:
                    task.transition_to(TaskState.SUCCEEDED)
            return result

    def _on_timeout(self, task_id: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            future = self._futures.get(task_id)

            if task is None or future is None or task.is_terminal:
                return
            if task.state not in {TaskState.QUEUED, TaskState.RUNNING}:
                return

        if future.cancel():
            with self._lock:
                if task.state in {TaskState.QUEUED, TaskState.RUNNING}:
                    task.transition_to(TaskState.TIMED_OUT)
            return

        with self._lock:
            if task.state in {TaskState.QUEUED, TaskState.RUNNING}:
                task.transition_to(TaskState.TIMED_OUT)

    def _on_future_done(self, task_id: str, future: Future) -> None:
        with self._lock:
            timer = self._timers.pop(task_id, None)
        if timer is not None:
            timer.cancel()

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            future = self._futures.get(task_id)

            if task is None or future is None:
                raise KeyError(f"Unknown task ID: {task_id}")
            if task.state is not TaskState.QUEUED:
                return False

        if not future.cancel():
            return False

        with self._lock:
            if task.state is TaskState.QUEUED:
                task.transition_to(TaskState.CANCELLED)
            timer = self._timers.pop(task_id, None)

        if timer is not None:
            timer.cancel()

        return task.state is TaskState.CANCELLED

    def get_future(self, task_id: str) -> Future:
        with self._lock:
            try:
                return self._futures[task_id]
            except KeyError:
                raise KeyError(f"Unknown task ID: {task_id}") from None

    def shutdown(self, wait: bool = True) -> None:
        with self._lock:
            if self._shutdown:
                return
            self._shutdown = True
            timers = list(self._timers.values())
            self._timers.clear()

        for timer in timers:
            timer.cancel()

        self._pool.shutdown(wait=wait)
