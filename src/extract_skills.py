from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

from src.common import load_json, normalize_skill


DEFAULT_SKILLS = {
    "aws",
    "c",
    "c++",
    "c#",
    "css",
    "docker",
    "git",
    "html",
    "java",
    "javascript",
    "kubernetes",
    "machine learning",
    "node.js",
    "numpy",
    "pandas",
    "postgresql",
    "python",
    "r",
    "react",
    "rest",
    "sql",
    "typescript",
    "unit testing",
}


def contains_skill(text: str, skill: str) -> bool:
    pattern = rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])"
    return bool(re.search(pattern, text.lower()))


def extract_skills(
    text: str,
    aliases: dict[str, str],
) -> list[str]:
    candidates = DEFAULT_SKILLS | set(aliases) | set(aliases.values())
    detected: set[str] = set()

    for candidate in candidates:
        if contains_skill(text, candidate):
            detected.add(normalize_skill(candidate, aliases))

    return sorted(detected)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract normalized technical skills."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--text-column", default="cleaned_text")
    parser.add_argument("--aliases", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataframe = pd.read_csv(args.input)

    if args.text_column not in dataframe.columns:
        raise ValueError(
            f"Missing text column: {args.text_column}"
        )

    aliases = load_json(args.aliases)
    dataframe["detected_skills"] = dataframe[
        args.text_column
    ].fillna("").map(
        lambda text: "|".join(extract_skills(str(text), aliases))
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
