from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate project figures."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataframe = pd.read_csv(args.input)

    if "role_domain" not in dataframe.columns:
        raise ValueError("Input must contain role_domain")

    counts = dataframe["role_domain"].value_counts()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots()
    counts.plot(kind="bar", ax=axis)
    axis.set_title("Job Postings by Role Domain")
    axis.set_xlabel("Role domain")
    axis.set_ylabel("Number of postings")
    figure.tight_layout()
    figure.savefig(output_dir / "jobs_by_domain.png", dpi=200)
    plt.close(figure)


if __name__ == "__main__":
    main()
