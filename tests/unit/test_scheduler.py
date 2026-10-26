import pytest

from taskweave.config import TaskWeaveConfig

from taskweave.core.task import Task, TaskState
from taskweave.scheduling.base import Scheduler


def test_scheduler_executes_task_and_updates_state():
    scheduler = Scheduler(max_workers=2)
    scheduler.start()
    task = Task()

    try:
        future = scheduler.submit(task, lambda x: x * 2, 21)

        assert future.result(timeout=3) == 42
        assert task.state is TaskState.SUCCEEDED
    finally:
        scheduler.shutdown()


def test_scheduler_marks_failed_task():
    scheduler = Scheduler(max_workers=1)
    scheduler.start()
    task = Task()

    def fail():
        raise ValueError("intentional failure")

    try:
        future = scheduler.submit(task, fail)

        with pytest.raises(ValueError, match="intentional failure"):
            future.result(timeout=3)

        assert task.state is TaskState.FAILED
    finally:
        scheduler.shutdown()


def test_scheduler_requires_start_before_submit():
    scheduler = Scheduler(max_workers=1)

    with pytest.raises(RuntimeError, match="start"):
        scheduler.submit(Task(), lambda: 1)


def test_scheduler_rejects_duplicate_task_submission():
    scheduler = Scheduler(max_workers=1)
    scheduler.start()
    task = Task()

    try:
        scheduler.submit(task, lambda: "first")

        with pytest.raises(ValueError, match="CREATED"):
            scheduler.submit(task, lambda: "second")
    finally:
        scheduler.shutdown()


def test_scheduler_rejects_task_when_queue_is_full():
    from queue import Full
    from threading import Event

    scheduler = Scheduler(max_workers=1, queue_capacity=1)
    started = Event()
    release = Event()

    def blocked_task():
        started.set()
        release.wait(timeout=5)
        return "released"

    scheduler.start()
    try:
        first = Task()
        first_future = scheduler.submit(first, blocked_task)
        assert started.wait(timeout=2), "Worker did not start in time"

        second = Task()
        second_future = scheduler.submit(second, lambda: "queued")

        third = Task()
        with pytest.raises(Full, match="queue is full"):
            scheduler.submit(third, lambda: "rejected")

        assert third.state is TaskState.CANCELLED
        assert third.task_id not in scheduler._tasks

        release.set()
        assert first_future.result(timeout=3) == "released"
        assert second_future.result(timeout=3) == "queued"
    finally:
        release.set()
        scheduler.shutdown()


def test_scheduler_accepts_config_object():
    config = TaskWeaveConfig(max_workers=2, queue_capacity=10)
    scheduler = Scheduler(config=config)

    assert scheduler.config is config
    assert scheduler.config.max_workers == 2
    assert scheduler.config.queue_capacity == 10


def test_scheduler_rejects_unimplemented_priority_policy():
    config = TaskWeaveConfig(scheduling_policy="priority")

    with pytest.raises(NotImplementedError, match="FIFO"):
        Scheduler(config=config)


@pytest.mark.parametrize("policy", ["block", "timeout"])
def test_scheduler_rejects_unimplemented_overflow_policies(policy):
    config = TaskWeaveConfig(overflow_policy=policy)

    with pytest.raises(NotImplementedError, match="reject"):
        Scheduler(config=config)


def test_scheduler_rejects_config_with_legacy_arguments():
    config = TaskWeaveConfig()

    with pytest.raises(ValueError, match="either config"):
        Scheduler(max_workers=2, config=config)

def test_shutdown_respects_configured_grace_period():
    import time
    from threading import Event

    config = TaskWeaveConfig(
        max_workers=1,
        queue_capacity=2,
        shutdown_grace_seconds=0.1,
    )
    scheduler = Scheduler(config=config)
    scheduler.start()

    started = Event()
    release = Event()

    def blocked_work():
        started.set()
        release.wait(timeout=3)
        return "finished"

    try:
        future = scheduler.submit(Task(), blocked_work)
        assert started.wait(timeout=2), "Task did not start"

        before = time.monotonic()
        scheduler.shutdown(wait=True)
        elapsed = time.monotonic() - before

        assert elapsed < 1.0, (
            f"Shutdown exceeded the grace period unexpectedly: {elapsed:.2f}s"
        )
        assert not future.done(), "Blocked task should still be running"
    finally:
        release.set()
        scheduler.shutdown(wait=True)

    assert future.result(timeout=2) == "finished"
