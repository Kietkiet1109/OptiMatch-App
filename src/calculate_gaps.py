from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
from scipy import sparse

from src.common import calculate_gap_vector, safe_cosine_similarity


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate a resume-job TF-IDF gap."
    )
    parser.add_argument("--resume-index", type=int, required=True)
    parser.add_argument("--job-index", type=int, required=True)
    parser.add_argument("--features-dir", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    features_dir = Path(args.features_dir)

    matrix = sparse.load_npz(
        features_dir / "tfidf_matrix.npz"
    )
    vectorizer = joblib.load(
        features_dir / "vectorizer.joblib"
    )

    resume = matrix[args.resume_index].toarray().ravel()
    job = matrix[args.job_index].toarray().ravel()

    similarity = safe_cosine_similarity(resume, job)
    gap = calculate_gap_vector(resume, job)
    feature_names = vectorizer.get_feature_names_out()

    ranked_indices = gap.argsort()[::-1]
    top_missing = [
        {
            "feature": feature_names[index],
            "weight": float(gap[index]),
        }
        for index in ranked_indices[:20]
        if gap[index] > 0
    ]

    result = {
        "similarity": similarity,
        "top_missing_features": top_missing,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
