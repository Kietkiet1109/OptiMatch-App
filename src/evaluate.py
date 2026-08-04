from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def precision_at_k(
    expected: set[str],
    predicted: list[str],
    k: int,
) -> float:
    selected = predicted[:k]

    if not selected:
        return 0.0

    relevant = sum(skill in expected for skill in selected)
    return relevant / len(selected)


def recall_at_k(
    expected: set[str],
    predicted: list[str],
    k: int,
) -> float:
    if not expected:
        return 0.0

    selected = set(predicted[:k])
    return len(expected & selected) / len(expected)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate skill-gap predictions."
    )
    parser.add_argument("--labels", required=True)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--k", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    labels = pd.read_csv(args.labels)
    predictions = pd.read_csv(args.predictions)

    required_prediction_columns = {
        "job_id",
        "resume_id",
        "predicted_skills",
    }

    missing = required_prediction_columns - set(predictions.columns)

    if missing:
        raise ValueError(
            f"Prediction file is missing columns: {sorted(missing)}"
        )

    expected_groups = (
        labels.groupby(["job_id", "resume_id"])["missing_skill"]
        .apply(lambda values: set(values.astype(str)))
        .to_dict()
    )

    results: list[dict] = []

    for _, row in predictions.iterrows():
        key = (row["job_id"], row["resume_id"])
        expected = expected_groups.get(key, set())
        predicted = [
            item.strip()
            for item in str(row["predicted_skills"]).split("|")
            if item.strip()
        ]

        results.append(
            {
                "job_id": key[0],
                "resume_id": key[1],
                f"precision_at_{args.k}": precision_at_k(
                    expected,
                    predicted,
                    args.k,
                ),
                f"recall_at_{args.k}": recall_at_k(
                    expected,
                    predicted,
                    args.k,
                ),
            }
        )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result_frame = pd.DataFrame(results)
    result_frame.to_csv(
        output_dir / "evaluation_results.csv",
        index=False,
    )

    print(result_frame.mean(numeric_only=True))


if __name__ == "__main__":
    main()
