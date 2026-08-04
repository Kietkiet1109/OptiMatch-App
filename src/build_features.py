from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build one shared TF-IDF feature space."
    )
    parser.add_argument(
        "--engine",
        choices=["sklearn", "spark"],
        default="sklearn",
    )
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def load_documents(input_dir: Path) -> tuple[list[str], list[dict]]:
    specifications = [
        ("resumes_clean.csv", "resume_id", "resume"),
        ("courses_clean.csv", "course_code", "course"),
    ]

    documents: list[str] = []
    metadata: list[dict] = []

    for filename, identifier_column, document_type in specifications:
        path = input_dir / filename

        if not path.exists():
            continue

        dataframe = pd.read_csv(path)

        for _, row in dataframe.iterrows():
            documents.append(str(row.get("cleaned_text", "")))
            metadata.append(
                {
                    "document_type": document_type,
                    "document_id": str(row.get(identifier_column, "")),
                }
            )

    return documents, metadata


def main() -> None:
    args = parse_args()

    if args.engine == "spark":
        raise SystemExit(
            "Spark pipeline is not implemented. "
            "Use it only when the corpus size justifies it."
        )

    documents, metadata = load_documents(Path(args.input_dir))

    if not documents:
        raise ValueError("No cleaned documents were found")

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.98,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(documents)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sparse.save_npz(output_dir / "tfidf_matrix.npz", matrix)
    joblib.dump(vectorizer, output_dir / "vectorizer.joblib")

    with (output_dir / "metadata.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metadata, file, indent=2)

    print(f"Created feature matrix with shape {matrix.shape}")


if __name__ == "__main__":
    main()
