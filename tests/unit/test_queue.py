import pytest
from queue import Empty, Full

from taskweave.core.queue import BoundedTaskQueue


def test_queue_is_fifo():
    queue = BoundedTaskQueue[int](2)
    queue.put_nowait(10)
    queue.put_nowait(20)
    assert queue.get_nowait() == 10
    assert queue.get_nowait() == 20


def test_queue_rejects_when_full():
    queue = BoundedTaskQueue[int](1)
    queue.put_nowait(1)
    with pytest.raises(Full):
        queue.put_nowait(2)


def test_queue_rejects_when_empty():
    queue = BoundedTaskQueue[int](1)
    with pytest.raises(Empty):
        queue.get_nowait()


def test_capacity_must_be_positive():
    with pytest.raises(ValueError):
        BoundedTaskQueue[int](0)