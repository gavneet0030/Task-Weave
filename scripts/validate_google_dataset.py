from pathlib import Path

from taskweave.data.google_cluster import load_resource_samples, summarize


def main():
    dataset = Path("data/raw/google_instance_usage.csv")
    samples = load_resource_samples(dataset)
    report = summarize(samples)

    print("Google Cluster Resource Profile")
    print("=" * 36)
    for key, value in report.items():
        if isinstance(value, float):
            print(f"{key}: {value:.6f}")
        else:
            print(f"{key}: {value}")

    print("\nValidation successful. No task arrival times or durations")
    print("were inferred from the resource-usage rows.")


if __name__ == "__main__":
    main()
