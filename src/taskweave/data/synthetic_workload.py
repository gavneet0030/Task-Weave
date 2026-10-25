"""Create reproducible synthetic tasks from resource-usage samples.

The source measurements are real dataset values. Task arrival offsets,
service durations, and priorities generated here are simulated, not
observed values from Google's cluster.
"""

import csv
import random
from pathlib import Path

from taskweave.data.google_cluster import load_resource_samples


def generate_synthetic_tasks(
    samples,
    *,
    seed: int = 42,
    max_tasks_per_sample: int = 10,
    base_service_ms: int = 20,
    bucket_width_ms: int = 1000,
):
    if max_tasks_per_sample < 1:
        raise ValueError("max_tasks_per_sample must be positive.")
    if base_service_ms < 1:
        raise ValueError("base_service_ms must be positive.")
    if bucket_width_ms < 1:
        raise ValueError("bucket_width_ms must be positive.")

    rng = random.Random(seed)
    tasks = []

    for bucket, sample in enumerate(samples):
        # This scaling rule is an experimental assumption, not a property
        # measured directly by the source dataset.
        task_count = 1 + round(
            sample.avg_cpu * (max_tasks_per_sample - 1)
        )

        for _ in range(task_count):
            arrival_offset_ms = (
                bucket * bucket_width_ms
                + rng.randrange(bucket_width_ms)
            )

            # Memory usage influences simulated service duration only.
            # It does not estimate the true execution time of a real task.
            service_time_ms = max(
                1,
                round(base_service_ms * (1 + sample.avg_mem)),
            )

            tasks.append({
                "task_id": f"synthetic-{len(tasks) + 1:07d}",
                "source_sample_index": bucket,
                "arrival_offset_ms": arrival_offset_ms,
                "service_time_ms": service_time_ms,
                "priority": rng.randint(1, 5),
                "source_avg_cpu": sample.avg_cpu,
                "source_avg_mem": sample.avg_mem,
                "is_synthetic": True,
            })

    tasks.sort(key=lambda task: (
        task["arrival_offset_ms"], task["task_id"]
    ))
    return tasks


def main():
    source = Path("data/raw/google_instance_usage.csv")
    output = Path("data/processed/synthetic_workload.csv")

    samples = load_resource_samples(source)
    tasks = generate_synthetic_tasks(samples)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(tasks[0].keys()))
        writer.writeheader()
        writer.writerows(tasks)

    print("Synthetic workload generated.")
    print(f"Source samples: {len(samples)}")
    print(f"Generated tasks: {len(tasks)}")
    print(f"Output file: {output}")
    print("Random seed: 42")
    print("All generated tasks are simulated, not real recorded tasks.")


if __name__ == "__main__":
    main()
