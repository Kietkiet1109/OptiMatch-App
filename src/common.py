from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()


def normalize_skill(skill: str, aliases: dict[str, str]) -> str:
    normalized = normalize_whitespace(skill).lower()
    return aliases.get(normalized, normalized)


def safe_cosine_similarity(
    vector_a: np.ndarray,
    vector_b: np.ndarray,
) -> float:
    a = np.asarray(vector_a, dtype=float)
    b = np.asarray(vector_b, dtype=float)

    if a.shape != b.shape:
        raise ValueError(
            f"Vector shapes must match: {a.shape} != {b.shape}"
        )

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def calculate_gap_vector(
    resume_vector: np.ndarray,
    job_vector: np.ndarray,
) -> np.ndarray:
    resume = np.asarray(resume_vector, dtype=float)
    job = np.asarray(job_vector, dtype=float)

    if resume.shape != job.shape:
        raise ValueError(
            f"Vector shapes must match: {resume.shape} != {job.shape}"
        )

    return np.maximum(job - resume, 0.0)
