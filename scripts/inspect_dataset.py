import csv
from pathlib import Path

path = Path("data/raw/google_instance_usage.csv")

with path.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    print("COLUMNS:")
    print(reader.fieldnames)

    print("\nFIRST 5 ROWS:")
    for i, row in enumerate(reader):
        print(row)
        if i >= 4:
            break

with path.open("r", encoding="utf-8-sig", newline="") as f:
    total_rows = sum(1 for _ in csv.DictReader(f))

print(f"\nTOTAL DATA ROWS: {total_rows}")
print(f"FILE SIZE: {path.stat().st_size:,} bytes")
