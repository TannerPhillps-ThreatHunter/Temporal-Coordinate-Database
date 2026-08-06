from __future__ import annotations

from research.event_geometry.robustness import missing_event_experiment


def main() -> None:
    results = missing_event_experiment()
    print("deletion_rate,mean_observed_gaps,resampled,dtw,coalescence")
    for rate, row in results.items():
        print(
            f"{rate:.2f},"
            f"{row['mean_observed_gaps']:.3f},"
            f"{row['resampled']:.6f},"
            f"{row['dtw']:.6f},"
            f"{row['coalescence']:.6f}"
        )


if __name__ == "__main__":
    main()
