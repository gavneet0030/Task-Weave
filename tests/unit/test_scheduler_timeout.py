from threading import Event

import pytest

from taskweave.core.task import Task, TaskState
from taskweave.scheduling.base import Scheduler


def test_task_times_out_while_running():
    scheduler = Scheduler(max_workers=1)
    scheduler.start()
    started = Event()
    release = Event()
    task = Task()

    def slow_work():
        started.set()
        release.wait(timeout=3)
        return "finished"

    try:
        future = scheduler.submit(task, slow_work, timeout=0.1)
        assert started.wait(timeout=2)

        import time
        deadline = time.monotonic() + 2
        while task.state is not TaskState.TIMED_OUT and time.monotonic() < deadline:
            time.sleep(0.01)

        assert task.state is TaskState.TIMED_OUT

        release.set()
        assert future.result(timeout=3) == "finished"
        assert task.state is TaskState.TIMED_OUT
    finally:
        release.set()
        scheduler.shutdown()


def test_non_timed_task_completes_normally():
    scheduler = Scheduler(max_workers=1)
    scheduler.start()
    task = Task()

    try:
        future = scheduler.submit(task, lambda: 123, timeout=2)
        assert future.result(timeout=3) == 123
        assert task.state is TaskState.SUCCEEDED
    finally:
        scheduler.shutdown()


def test_rejects_nonpositive_timeout():
    scheduler = Scheduler(max_workers=1)
    scheduler.start()

    try:
        with pytest.raises(ValueError, match="greater than zero"):
            scheduler.submit(Task(), lambda: None, timeout=0)
    finally:
        scheduler.shutdown()


def test_queued_task_timeout_does_not_deadlock():
    import time

    scheduler = Scheduler(max_workers=1, queue_capacity=2)
    started = Event()
    release = Event()
    blocker = Task()
    queued_task = Task()

    scheduler.start()

    def blocked_work():
        started.set()
        release.wait(timeout=5)
        return "released"

    try:
        blocker_future = scheduler.submit(blocker, blocked_work)
        assert started.wait(timeout=2), "Blocking task did not start"

        queued_future = scheduler.submit(
            queued_task,
            lambda: "should not execute",
            timeout=0.15,
        )

        deadline = time.monotonic() + 2
        while (
            queued_task.state is not TaskState.TIMED_OUT
            and time.monotonic() < deadline
        ):
            time.sleep(0.01)

        assert queued_task.state is TaskState.TIMED_OUT
        assert queued_future.cancelled()

        release.set()
        assert blocker_future.result(timeout=3) == "released"
    finally:
        release.set()
        scheduler.shutdown()
