"""Validation and analysis of Google cluster resource-usage profiles."""

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean


REQUIRED_COLUMNS = (
    "avg_cpu",
    "avg_mem",
    "avg_assigned_mem",
    "avg_cycles_per_instruction",
)


@dataclass(frozen=True)
class ResourceSample:
    avg_cpu: float
    avg_mem: float
    avg_assigned_mem: float
    avg_cycles_per_instruction: float


def load_resource_samples(path: str | Path) -> list[ResourceSample]:
    """Load and validate resource measurements from a CSV file."""
    source = Path(path)
    samples: list[ResourceSample] = []

    with source.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV is empty or has no header.")

        missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        for row_number, row in enumerate(reader, start=2):
            try:
                values = {
                    column: float(row[column])
                    for column in REQUIRED_COLUMNS
                }
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid numeric value on CSV row {row_number}."
                ) from exc

            if not all(math.isfinite(value) for value in values.values()):
                raise ValueError(
                    f"Non-finite numeric value on CSV row {row_number}."
                )

            for column in (
                "avg_cpu",
                "avg_mem",
                "avg_assigned_mem",
            ):
                if not 0.0 <= values[column] <= 1.0:
                    raise ValueError(
                        f"{column} must be between 0 and 1 "
                        f"on CSV row {row_number}."
                    )

            if values["avg_cycles_per_instruction"] <= 0:
                raise ValueError(
                    "avg_cycles_per_instruction must be positive "
                    f"on CSV row {row_number}."
                )

            samples.append(ResourceSample(**values))

    if not samples:
        raise ValueError("CSV contains no resource data rows.")

    return samples


def summarize(samples: list[ResourceSample]) -> dict[str, float | int]:
    """Return basic descriptive statistics for validated samples."""
    if not samples:
        raise ValueError("Cannot summarize an empty sample list.")

    return {
        "row_count": len(samples),
        "mean_cpu": fmean(s.avg_cpu for s in samples),
        "mean_memory": fmean(s.avg_mem for s in samples),
        "mean_assigned_memory": fmean(
            s.avg_assigned_mem for s in samples
        ),
        "mean_cycles_per_instruction": fmean(
            s.avg_cycles_per_instruction for s in samples
        ),
        "max_cpu": max(s.avg_cpu for s in samples),
        "max_memory": max(s.avg_mem for s in samples),
    }
