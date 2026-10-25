import pytest

from taskweave.core.task import Task, TaskState


def test_task_starts_created():
    assert Task().state is TaskState.CREATED


def test_valid_task_lifecycle():
    task = Task()
    task.transition_to(TaskState.QUEUED)
    task.transition_to(TaskState.RUNNING)
    task.transition_to(TaskState.SUCCEEDED)
    assert task.is_terminal


def test_invalid_transition_is_rejected():
    task = Task()
    with pytest.raises(ValueError):
        task.transition_to(TaskState.SUCCEEDED)


def test_terminal_state_cannot_transition_again():
    task = Task()
    task.transition_to(TaskState.CANCELLED)
    with pytest.raises(ValueError):
        task.transition_to(TaskState.QUEUED)