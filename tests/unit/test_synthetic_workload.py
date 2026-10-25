import pytest

from taskweave.data.google_cluster import ResourceSample
from taskweave.data.synthetic_workload import generate_synthetic_tasks


def sample(cpu=0.5, memory=0.3):
    return ResourceSample(
        avg_cpu=cpu,
        avg_mem=memory,
        avg_assigned_mem=0.6,
        avg_cycles_per_instruction=150.0,
    )


def test_generates_tasks_from_resource_samples():
    tasks = generate_synthetic_tasks([sample()])

    assert len(tasks) >= 1
    assert all(task["is_synthetic"] is True for task in tasks)
    assert all(task["task_id"].startswith("synthetic-") for task in tasks)


def test_same_seed_produces_same_workload():
    samples = [sample(0.2, 0.3), sample(0.8, 0.5)]

    first = generate_synthetic_tasks(samples, seed=123)
    second = generate_synthetic_tasks(samples, seed=123)

    assert first == second


def test_output_is_sorted_by_arrival_offset():
    tasks = generate_synthetic_tasks(
        [sample(), sample(0.7, 0.4)], seed=8
    )
    offsets = [task["arrival_offset_ms"] for task in tasks]

    assert offsets == sorted(offsets)


def test_rejects_invalid_generation_parameters():
    with pytest.raises(ValueError):
        generate_synthetic_tasks([sample()], max_tasks_per_sample=0)


def test_service_duration_is_positive():
    tasks = generate_synthetic_tasks([sample(memory=0.0)])

    assert all(task["service_time_ms"] > 0 for task in tasks)
