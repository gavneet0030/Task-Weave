import pytest

from taskweave.workers.pool import WorkerPool


def test_worker_executes_task_and_returns_result():
    pool = WorkerPool(max_workers=2)
    pool.start()

    try:
        future = pool.submit(lambda a, b: a + b, 10, 20)
        assert future.result(timeout=3) == 30
    finally:
        pool.shutdown()


def test_worker_captures_task_exception():
    pool = WorkerPool(max_workers=1)
    pool.start()

    def fail():
        raise ValueError("expected test failure")

    try:
        future = pool.submit(fail)

        with pytest.raises(ValueError, match="expected test failure"):
            future.result(timeout=3)

        assert pool.submit(lambda: "still works").result(timeout=3) == "still works"
    finally:
        pool.shutdown()


def test_pool_rejects_submission_before_start():
    pool = WorkerPool(max_workers=1)

    with pytest.raises(RuntimeError, match="start"):
        pool.submit(lambda: 1)


def test_pool_rejects_submission_after_shutdown():
    pool = WorkerPool(max_workers=1)
    pool.start()
    pool.shutdown()

    with pytest.raises(RuntimeError, match="shutdown"):
        pool.submit(lambda: 1)


def test_shutdown_waits_for_queued_tasks():
    pool = WorkerPool(max_workers=2)
    pool.start()

    futures = [pool.submit(lambda value=i: value) for i in range(10)]
    pool.shutdown(wait=True)

    assert [future.result(timeout=3) for future in futures] == list(range(10))

def test_pool_rejects_submission_when_queue_is_full():
    from threading import Event
    from queue import Full

    pool = WorkerPool(max_workers=1, queue_capacity=1)
    started = Event()
    release = Event()

    def blocked_task():
        started.set()
        release.wait(timeout=5)
        return "released"

    pool.start()
    try:
        running = pool.submit(blocked_task)
        assert started.wait(timeout=2), "Worker did not start in time"

        queued = pool.submit(lambda: "queued")

        with pytest.raises(Full, match="queue is full"):
            pool.submit(lambda: "should be rejected")

        release.set()
        assert running.result(timeout=3) == "released"
        assert queued.result(timeout=3) == "queued"
    finally:
        release.set()
        pool.shutdown()



def test_shutdown_wait_false_returns_while_task_is_blocked():
    from threading import Event

    pool = WorkerPool(max_workers=1, queue_capacity=2)
    started = Event()
    release = Event()

    def blocked_task():
        started.set()
        release.wait(timeout=5)
        return "finished"

    pool.start()
    future = pool.submit(blocked_task)

    try:
        assert started.wait(timeout=2), "Worker did not start in time"
        pool.submit(lambda: "queued")

        pool.shutdown(wait=False)

        with pytest.raises(RuntimeError, match="shutdown"):
            pool.submit(lambda: "rejected")
    finally:
        release.set()

    assert future.result(timeout=3) == "finished"


def test_shutdown_wait_false_drains_accepted_tasks():
    from threading import Event

    pool = WorkerPool(max_workers=1, queue_capacity=3)
    started = Event()
    release = Event()

    def blocked_task():
        started.set()
        release.wait(timeout=5)
        return "first"

    pool.start()
    first = pool.submit(blocked_task)
    second = pool.submit(lambda: "second")

    try:
        assert started.wait(timeout=2), "Worker did not start in time"
        pool.shutdown(wait=False)
    finally:
        release.set()

    assert first.result(timeout=3) == "first"
    assert second.result(timeout=3) == "second"
    pool.shutdown(wait=True)
