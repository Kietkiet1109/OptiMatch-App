import numpy as np
import pytest

from src.common import calculate_gap_vector, safe_cosine_similarity


def test_identical_vectors_have_similarity_one() -> None:
    vector = np.array([1.0, 2.0, 3.0])
    assert safe_cosine_similarity(vector, vector) == pytest.approx(1.0)


def test_zero_vector_returns_zero_similarity() -> None:
    assert safe_cosine_similarity(
        np.array([0.0, 0.0]),
        np.array([1.0, 1.0]),
    ) == 0.0


def test_gap_vector_keeps_only_positive_job_difference() -> None:
    resume = np.array([0.8, 0.1, 0.5])
    job = np.array([0.4, 0.7, 0.5])

    result = calculate_gap_vector(resume, job)

    assert np.allclose(result, np.array([0.0, 0.6, 0.0]))
