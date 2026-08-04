from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"resume_text"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and import the external resume dataset."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    dataframe = pd.read_csv(input_path)
    missing = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing:
        raise ValueError(
            f"Resume dataset is missing columns: {sorted(missing)}"
        )

    if "resume_id" not in dataframe.columns:
        dataframe.insert(
            0,
            "resume_id",
            [f"resume_{index:05d}" for index in range(len(dataframe))],
        )

    dataframe = dataframe.dropna(subset=["resume_text"]).copy()
    dataframe["resume_text"] = dataframe["resume_text"].astype(str)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)

    print(f"Imported {len(dataframe)} resume records to {output_path}")


if __name__ == "__main__":
    main()
