import csv

import pytest

from taskweave.data.google_cluster import (
    load_resource_samples,
    summarize,
)


FIELDS = [
    "avg_cpu",
    "avg_mem",
    "avg_assigned_mem",
    "avg_cycles_per_instruction",
]


def write_csv(path, rows, fields=FIELDS):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_loads_valid_resource_samples(tmp_path):
    path = tmp_path / "sample.csv"
    write_csv(path, [
        dict(avg_cpu="0.4", avg_mem="0.3",
             avg_assigned_mem="0.6",
             avg_cycles_per_instruction="150"),
        dict(avg_cpu="0.6", avg_mem="0.5",
             avg_assigned_mem="0.7",
             avg_cycles_per_instruction="160"),
    ])

    samples = load_resource_samples(path)

    assert len(samples) == 2
    assert samples[0].avg_cpu == pytest.approx(0.4)


def test_summary_calculates_means_and_maxima(tmp_path):
    path = tmp_path / "sample.csv"
    write_csv(path, [
        dict(avg_cpu="0.4", avg_mem="0.3",
             avg_assigned_mem="0.6",
             avg_cycles_per_instruction="150"),
        dict(avg_cpu="0.6", avg_mem="0.5",
             avg_assigned_mem="0.8",
             avg_cycles_per_instruction="170"),
    ])

    result = summarize(load_resource_samples(path))

    assert result["row_count"] == 2
    assert result["mean_cpu"] == pytest.approx(0.5)
    assert result["mean_memory"] == pytest.approx(0.4)
    assert result["max_cpu"] == pytest.approx(0.6)


def test_rejects_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    write_csv(path, [], fields=["avg_cpu"])

    with pytest.raises(ValueError, match="Missing required columns"):
        load_resource_samples(path)


def test_rejects_cpu_outside_valid_range(tmp_path):
    path = tmp_path / "bad.csv"
    write_csv(path, [
        dict(avg_cpu="1.5", avg_mem="0.3",
             avg_assigned_mem="0.6",
             avg_cycles_per_instruction="150"),
    ])

    with pytest.raises(ValueError, match="avg_cpu"):
        load_resource_samples(path)


def test_rejects_non_numeric_values(tmp_path):
    path = tmp_path / "bad.csv"
    write_csv(path, [
        dict(avg_cpu="unknown", avg_mem="0.3",
             avg_assigned_mem="0.6",
             avg_cycles_per_instruction="150"),
    ])

    with pytest.raises(ValueError, match="Invalid numeric value"):
        load_resource_samples(path)


def test_rejects_empty_data_file(tmp_path):
    path = tmp_path / "empty.csv"
    write_csv(path, [])

    with pytest.raises(ValueError, match="no resource data rows"):
        load_resource_samples(path)


def test_rejects_non_positive_cycles(tmp_path):
    path = tmp_path / "bad.csv"
    write_csv(path, [
        dict(avg_cpu="0.4", avg_mem="0.3",
             avg_assigned_mem="0.6",
             avg_cycles_per_instruction="0"),
    ])

    with pytest.raises(ValueError, match="must be positive"):
        load_resource_samples(path)
