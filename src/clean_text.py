from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


PROTECTED_REPLACEMENTS = {
    r"\bc\+\+\b": "cplusplus",
    r"\bc#\b": "csharp",
    r"\bnode\.js\b": "nodejs",
    r"\b\.net\b": "dotnet",
}


def clean_text(text: str) -> str:
    value = html.unescape(str(text))
    value = BeautifulSoup(value, "html.parser").get_text(" ")

    for pattern, replacement in PROTECTED_REPLACEMENTS.items():
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)

    value = value.lower()
    value = re.sub(r"[^a-z0-9+#./\-\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    reverse_replacements = {
        "cplusplus": "c++",
        "csharp": "c#",
        "nodejs": "node.js",
        "dotnet": ".net",
    }

    for temporary, original in reverse_replacements.items():
        value = re.sub(rf"\b{re.escape(temporary)}\b", original, value)

    return value


def process_csv(
    input_path: Path,
    output_path: Path,
    text_column: str,
) -> None:
    dataframe = pd.read_csv(input_path)

    if text_column not in dataframe.columns:
        raise ValueError(
            f"{input_path} does not contain {text_column!r}"
        )

    dataframe["cleaned_text"] = (
        dataframe[text_column]
        .fillna("")
        .astype(str)
        .map(clean_text)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean resume and course text."
    )
    parser.add_argument("--courses")
    parser.add_argument("--resumes")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)

    if args.courses:
        process_csv(
            Path(args.courses),
            output_dir / "courses_clean.csv",
            "course_description",
        )

    if args.resumes:
        process_csv(
            Path(args.resumes),
            output_dir / "resumes_clean.csv",
            "resume_text",
        )

    print(f"Cleaned files saved to {output_dir}")


if __name__ == "__main__":
    main()
