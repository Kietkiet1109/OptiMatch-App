from backend.recommend_engine import generate_recommendations


# Verify that only missing required technical skills become learning recommendations.
def test_generate_recommendations_filters_to_required_technical_gaps():
    skill_matches = [
        {
            'skill': 'docker',
            'skill_type': 'technical',
            'requirement_type': 'required',
            'match_status': 'not_detected',
            'job_evidence': [{'text_evidence': 'Docker is required.'}],
        },
        {
            'skill': 'aws',
            'skill_type': 'technical',
            'requirement_type': 'preferred',
            'match_status': 'not_detected',
        },
        {
            'skill': 'communication',
            'skill_type': 'soft',
            'requirement_type': 'required',
            'match_status': 'not_detected',
        },
        {
            'skill': 'python',
            'skill_type': 'technical',
            'requirement_type': 'required',
            'match_status': 'matched',
        },
    ]

    recommendations = generate_recommendations(skill_matches)

    assert [recommendation['skill'] for recommendation in recommendations] == ['docker']
    assert recommendations[0]['recommendation_type'] == 'learning'


# Verify that weak evidence receives learning and evidence-building guidance.
def test_generate_recommendations_handles_weak_required_technical_evidence():
    recommendations = generate_recommendations([
        {
            'skill': 'postgresql',
            'skill_type': 'technical',
            'requirement_type': 'required',
            'match_status': 'partially_matched',
            'resume_evidence': ['Used PostgreSQL in one project.'],
            'job_evidence': [{'text_evidence': 'Strong PostgreSQL experience is required.'}],
        }
    ])

    assert recommendations[0]['recommendation_type'] == 'learning_and_evidence'
    assert 'limited evidence' in recommendations[0]['why_it_matters']

