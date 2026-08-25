from backend.analysis_schema import build_analysis_result
from backend.analysis_schema import calculate_coverage
from backend.analysis_schema import validate_analysis_input


# Verify that a valid PDF and job description pass input validation.
def test_validate_analysis_input_accepts_pdf_and_job_text():
    analysis_input = {
        'resume_pdf': b'%PDF-1.7 resume',
        'job_description_text': 'python and docker required',
        'target_role_title': 'software engineer',
        'user_preferences': {'career_level': 'entry_level'}
    }

    assert validate_analysis_input(analysis_input) == []


# Verify that a partial skill match receives half credit.
def test_calculate_coverage_counts_partial_matches_as_half():
    skill_matches = [
        {'requirement_type': 'required', 'match_status': 'matched'},
        {'requirement_type': 'required', 'match_status': 'partially_matched'},
        {'requirement_type': 'required', 'match_status': 'not_detected'}
    ]

    assert calculate_coverage(skill_matches, 'required') == 50.0


# Verify that the completed result contains the required Phase 0 fields.
def test_build_analysis_result_returns_required_phase0_fields():
    analysis_input = {
        'resume_pdf': b'%PDF-1.7 resume',
        'job_description_text': 'python and docker required'
    }
    skill_matches = [
        {
            'skill': 'python',
            'requirement_type': 'required',
            'match_status': 'matched'
        },
        {
            'skill': 'docker',
            'requirement_type': 'required',
            'match_status': 'not_detected'
        }
    ]

    # Build a result from the normalized input and skill-match records.
    result = build_analysis_result(
        analysis_input,
        skill_matches,
        [],
        [],
        [],
        [],
        {'overall': 'medium'},
        []
    )

    # Check the result status, label, score scale, and missing skill.
    assert result['status'] == 'completed'
    assert result['label'] == 'OptiMatch compatibility estimate'
    assert result['overall_score']['scale'] == 100
    assert result['missing_required_skills'][0]['skill'] == 'docker'
