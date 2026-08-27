from backend.recommendation.recommend_engine import generate_learning_resources
from backend.recommendation.recommend_engine import generate_recommendations

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


# Verify alternatives are recommended as one choice rather than separate missing skills.
def test_generate_recommendations_keeps_or_alternatives_together():
    recommendations = generate_recommendations([
        {
            'skill': 'pytorch',
            'skill_type': 'technical',
            'requirement_type': 'required',
            'match_status': 'not_detected',
            'operator': 'or',
            'alternatives': ['pytorch', 'tensorflow'],
            'job_evidence': [{'text_evidence': 'PyTorch or TensorFlow experience.'}],
        }
    ])

    assert len(recommendations) == 1
    assert recommendations[0]['skill'] == 'pytorch or tensorflow'


# Verify that the chatbot receives only deterministic required technical gaps.
def test_generate_learning_resources_sends_only_gap_data():
    recommendations = generate_recommendations([
        {
            'skill': 'docker',
            'skill_type': 'technical',
            'requirement_type': 'required',
            'match_status': 'not_detected',
            'job_evidence': [{'text_evidence': 'Docker is required.'}],
        },
        {
            'skill': 'python',
            'skill_type': 'technical',
            'requirement_type': 'required',
            'match_status': 'matched',
        }
    ])
    captured_request = {}

    # Return one valid structured resource from the fake chatbot adapter.
    def chatbot_callable(request):
        captured_request.update(request)
        return {
            'recommendations': [{
                'skill': 'docker',
                'resources': [{
                    'title': 'Docker Get Started Guide',
                    'provider': 'Docker',
                    'resource_type': 'official_documentation',
                    'url': 'https://docs.docker.com/get-started/',
                    'difficulty': 'beginner',
                    'estimated_time': '4-6 hours',
                    'reason': 'Introduces containers and Dockerfiles.',
                    'verification_status': 'needs_verification'
                }],
                'practice_task': 'Containerize a small API.',
                'learning_order': 1
            }]
        }

    result = generate_learning_resources(
        recommendations, chatbot_callable, target_role='Backend Developer'
    )

    assert captured_request['uploaded_data']['target_role'] == 'Backend Developer'
    assert captured_request['uploaded_data']['missing_required_technical_skills'] == [{
        'skill': 'docker',
        'job_evidence': 'Docker is required.',
        'resume_status': 'not_detected',
        'priority': 'high'
    }]
    assert result['validation']['status'] == 'accepted'


# Verify that unsupported providers and malformed resources are rejected.
def test_validate_resource_response_rejects_unsafe_resource_data():
    recommendations = generate_recommendations([{
        'skill': 'docker',
        'skill_type': 'technical',
        'requirement_type': 'required',
        'match_status': 'not_detected',
    }])

    result = generate_learning_resources(
        recommendations,
        lambda request: {
            'recommendations': [{
                'skill': 'docker',
                'resources': [{
                    'title': 'Unknown Course',
                    'provider': 'Unknown Provider',
                    'resource_type': 'online_course',
                    'url': 'not-a-url',
                    'difficulty': 'beginner',
                    'estimated_time': '1 hour',
                    'reason': 'Learn Docker.',
                    'verification_status': 'needs_verification'
                }],
                'practice_task': 'Build a container.',
                'learning_order': 1
            }]
        }
    )

    assert result['recommendations'] == []
    assert result['validation']['status'] == 'rejected'
