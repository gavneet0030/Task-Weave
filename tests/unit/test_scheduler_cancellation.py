from threading import Event

import pytest

from taskweave.core.task import Task, TaskState
from taskweave.scheduling.base import Scheduler


def test_cancel_unknown_task_raises_key_error():
    scheduler = Scheduler(max_workers=1)
    scheduler.start()

    try:
        with pytest.raises(KeyError, match="Unknown task ID"):
            scheduler.cancel("unknown-task")
    finally:
        scheduler.shutdown()


def test_cancel_queued_task_before_worker_starts_it():
    scheduler = Scheduler(max_workers=1)
    scheduler.start()

    started = Event()
    release = Event()
    blocker = Task()
    cancelled_task = Task()

    try:
        first = scheduler.submit(
            blocker,
            lambda: (started.set(), release.wait(timeout=3)),
        )
        assert started.wait(timeout=3)

        second = scheduler.submit(cancelled_task, lambda: "should not run")

        assert scheduler.cancel(cancelled_task.task_id) is True
        assert cancelled_task.state is TaskState.CANCELLED
        assert second.cancelled()

        release.set()
        first.result(timeout=3)
    finally:
        release.set()
        scheduler.shutdown()


def test_running_task_cannot_be_cancelled():
    scheduler = Scheduler(max_workers=1)
    scheduler.start()

    started = Event()
    release = Event()
    task = Task()

    def work():
        started.set()
        release.wait(timeout=3)
        return "finished"

    try:
        future = scheduler.submit(task, work)
        assert started.wait(timeout=3)

        assert scheduler.cancel(task.task_id) is False
        release.set()

        assert future.result(timeout=3) == "finished"
        assert task.state is TaskState.SUCCEEDED
    finally:
        release.set()
        scheduler.shutdown()
