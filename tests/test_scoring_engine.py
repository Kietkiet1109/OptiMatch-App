from backend.scoring_engine import calculate_deterministic_score


# Verify that the documented weights produce the expected deterministic total.
def test_calculate_deterministic_score_uses_documented_weights():
    skill_matches = [
        {
            'skill': 'python',
            'requirement_type': 'required',
            'match_status': 'matched',
            'evidence': 'Python appears in the resume skills section.',
        },
        {
            'skill': 'docker',
            'requirement_type': 'required',
            'match_status': 'not_detected',
            'evidence': 'Docker is required by the job description.',
        },
        {
            'skill': 'aws',
            'requirement_type': 'preferred',
            'match_status': 'partially_matched',
            'evidence': 'Cloud deployment experience partially supports AWS.',
        },
    ]

    result = calculate_deterministic_score(
        skill_matches,
        {'score': 80, 'evidence': ['Five years of relevant experience.']},
        {'score': 100, 'evidence': ['Bachelor degree matches the requirement.']},
        20,
        [{'severity': 'medium', 'evidence': 'Inconsistent date formatting.'}]
    )

    assert result['required_skill_coverage'] == 50.0
    assert result['technical_skill_coverage'] == 50.0
    assert result['preferred_skill_coverage'] == 50.0
    assert result['shared_skill_count'] == 2
    assert result['missing_required_skill_count'] == 1
    assert result['missing_preferred_skill_count'] == 0
    assert result['experience_alignment'] == 80.0
    assert result['education_alignment'] == 100.0
    assert result['formatting_risk'] == 20.0
    assert result['overall_score'] == 58.5
    assert result['components']['required_skill_coverage']['contribution'] == 20.0
    assert result['components']['experience_alignment']['evidence'] == [
        'Five years of relevant experience.'
    ]
    assert [skill['skill'] for skill in result['matched_required_skills']] == ['python']
    assert [skill['skill'] for skill in result['matched_preferred_skills']] == ['aws']


# Verify that formatting findings become a capped risk score when no score is supplied.
def test_calculate_deterministic_score_derives_formatting_risk():
    result = calculate_deterministic_score(
        [],
        0,
        0,
        formatting_risks=[
            {'severity': 'high', 'evidence': 'Missing section heading.'},
            {'severity': 'low', 'evidence': 'Long dense paragraph.'},
        ]
    )

    assert result['formatting_risk'] == 45
    assert result['components']['formatting_quality']['score'] == 55.0


# Verify that the analysis result exposes the same Phase 7 metrics publicly.
def test_build_analysis_result_exposes_phase_7_metrics():
    from backend.analysis_schema import build_analysis_result

    result = build_analysis_result(
        {
            'resume_pdf': b'%PDF-1.7 resume',
            'job_description_text': 'python required',
        },
        [
            {
                'skill': 'python',
                'requirement_type': 'required',
                'match_status': 'matched',
            }
        ],
        [],
        [],
        [],
        [],
        {'overall': 'medium'},
        [],
        experience_alignment=70,
        education_alignment=80,
        formatting_risk=10,
    )

    assert result['shared_skill_count'] == 1
    assert result['experience_alignment'] == 70.0
    assert result['education_alignment'] == 80.0
    assert result['formatting_risk'] == 10.0
    assert result['scoring']['weights']['required_skill_coverage'] == 40
