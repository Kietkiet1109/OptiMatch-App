import json
from urllib.parse import urlparse

# Keep recommendation wording separate from the evidence classifier so each output is auditable
action_templates = {
    'not_detected': {
        'category': 'learning resources',
        'action': 'Build a small project that uses {skill}, then document the decisions, setup, and results.',
        'learning_level': 'beginner',
        'estimated_effort': '2-4 weeks',
    },
    'weakly_demonstrated': {
        'category': 'learning and evidence building',
        'action': 'Strengthen an existing project by showing how you used {skill}, your individual contribution, and a measurable result.',
        'learning_level': 'intermediate',
        'estimated_effort': '1-2 weeks',
    },
}

# Accept only resource types and difficulty values used by the resource contract
allowed_resource_types = {
    'official_documentation', 'online_course', 'guided_tutorial', 'video',
    'practice_project'
}
allowed_difficulties = {'beginner', 'intermediate'}
allowed_verification_statuses = {'verified', 'needs_verification'}

# Accept providers as established learning sources
recognized_providers = {
    'aws', 'coursera', 'docker', 'edx', 'freecodecamp', 'github',
    'google', 'ibm', 'khan academy', 'linux foundation', 'microsoft learn',
    'mozilla', 'udemy', 'youtube'
}

# Convert legacy and current match labels into the 4 user-facing evidence states
def classify_evidence_status(match_status):
    value = str(match_status or '').casefold().strip()
    status_map = {
        'matched': 'explicitly_demonstrated',
        'explicitly_demonstrated': 'explicitly_demonstrated',
        'partially_matched': 'weakly_demonstrated',
        'weakly_demonstrated': 'weakly_demonstrated',
        'not_detected': 'not_detected',
        'unclear': 'likely_related_uncertain',
        'uncertain': 'likely_related_uncertain',
        'likely_related_uncertain': 'likely_related_uncertain',
    }
    return status_map.get(value, 'likely_related_uncertain')


# Read a skill name from the match formats produced by the existing backend phases
def read_skill_name(skill_match):
    if not isinstance(skill_match, dict):
        return ''
    value = skill_match.get('skill', skill_match.get('name', ''))
    return str(value).strip()


# Select evidence without treating an absent resume excerpt as proof of absent ability
def read_evidence(skill_match, resume_evidence, job_evidence):
    skill_name = read_skill_name(skill_match)
    resume_values = []
    job_values = []
    if isinstance(skill_match, dict):
        resume_values = skill_match.get('resume_evidence', [])
        job_values = skill_match.get('job_evidence', skill_match.get('evidence', []))
    if isinstance(resume_values, str):
        resume_values = [resume_values]
    if isinstance(job_values, str):
        job_values = [job_values]
    if not isinstance(resume_values, list):
        resume_values = []
    if not isinstance(job_values, list):
        job_values = []
    for record in resume_evidence or []:
        if isinstance(record, dict):
            record_skill = str(record.get('skill', record.get('name', ''))).casefold()
            if record_skill == skill_name.casefold():
                resume_values.append(record.get('text_evidence', record.get('evidence', '')))
    for record in job_evidence or []:
        if isinstance(record, dict):
            record_skill = str(record.get('skill', record.get('name', ''))).casefold()
            if record_skill == skill_name.casefold():
                job_values.append(record.get('text_evidence', record.get('evidence', '')))
    # Convert evidence records into plain text before using them in explanations or prompts
    resume_values = [
        str(value.get('text_evidence', value.get('evidence', ''))).strip()
        if isinstance(value, dict) else str(value).strip()
        for value in resume_values
    ]
    job_values = [
        str(value.get('text_evidence', value.get('evidence', ''))).strip()
        if isinstance(value, dict) else str(value).strip()
        for value in job_values
    ]
    resume_values = [value for value in resume_values if value]
    job_values = [value for value in job_values if value]
    return resume_values, job_values


# Keep only required technical gaps so the recommendation layer cannot expand its scope
def is_recommendation_gap(skill_match, evidence_status):
    if not isinstance(skill_match, dict):
        return False
    return (
        skill_match.get('skill_type') == 'technical'
        and skill_match.get('requirement_type') == 'required'
        and evidence_status in {'not_detected', 'weakly_demonstrated'}
    )


# Build the smallest possible chatbot request from deterministic recommendations
def build_resource_request(recommendations, target_role=None):
    if not isinstance(recommendations, list):
        raise TypeError('recommendations must be a list')

    missing_skills = []
    for recommendation in recommendations:
        if not isinstance(recommendation, dict):
            continue
        if recommendation.get('recommendation_type') not in {
                'learning', 'learning_and_evidence'}:
            continue
        if recommendation.get('evidence_status') not in {
                'not_detected', 'weakly_demonstrated'}:
            continue
        skill_name = str(recommendation.get('skill', '')).strip()
        if not skill_name:
            continue
        job_evidence = recommendation.get('job_evidence', [])
        missing_skills.append({
            'skill': skill_name,
            'job_evidence': job_evidence[0] if job_evidence else '',
            'resume_status': recommendation['evidence_status'],
            'priority': recommendation.get('priority', 'high')
        })

    # Instruct the chatbot to generate resources without making deterministic decisions
    instructions = (
        'Generate learning resources only for the skills in missing_required_technical_skills. '
        'Do not add skills, claim that a user lacks a skill, or use the resume to invent a gap. '
        'Return JSON only. Do not fabricate URLs, course names, instructors, prices, '
        'certifications, or completion times. Use recognized providers and include one '
        'practical exercise for every skill. Use only these resource_type values: '
        'official_documentation, online_course, guided_tutorial, video, practice_project.'
    )
    return {
        'system': instructions,
        'uploaded_data': {
            'target_role': target_role or 'unspecified role',
            'missing_required_technical_skills': missing_skills
        }
    }


# Validate the chatbot response
def validate_resource_response(model_response, requested_skills):
    if isinstance(model_response, str):
        try:
            model_response = json.loads(model_response)
        except json.JSONDecodeError:
            model_response = None
    if isinstance(model_response, dict):
        model_recommendations = model_response.get('recommendations')
    else:
        model_recommendations = model_response

    requested_names = {
        str(skill).casefold().strip() for skill in requested_skills or []
        if str(skill).strip()
    }
    issues = []
    safe_recommendations = []
    seen_skills = set()
    if not isinstance(model_recommendations, list):
        return {
            'recommendations': [],
            'validation': {'status': 'rejected', 'issues': ['recommendations must be a list']}
        }

    for recommendation in model_recommendations:
        if not isinstance(recommendation, dict):
            issues.append('invalid recommendation record')
            continue
        skill_name = recommendation.get('skill')
        skill_key = str(skill_name or '').casefold().strip()
        resources = recommendation.get('resources')
        practice_task = recommendation.get('practice_task')
        learning_order = recommendation.get('learning_order')
        if skill_key not in requested_names or skill_key in seen_skills:
            issues.append('recommendation skill is not requested or is duplicated')
            continue
        if not isinstance(resources, list) or not resources:
            issues.append('recommendation resources must be a non-empty list')
            continue
        if not isinstance(practice_task, str) or not practice_task.strip():
            issues.append('practice_task must be a non-empty string')
            continue
        if not isinstance(learning_order, int) or isinstance(learning_order, bool) or learning_order < 1:
            issues.append('learning_order must be a positive integer')
            continue

        safe_resources = []
        seen_urls = set()
        for resource in resources:
            if not isinstance(resource, dict):
                issues.append('invalid resource record')
                continue
            title = resource.get('title')
            provider = resource.get('provider')
            resource_type = resource.get('resource_type')
            url = resource.get('url')
            difficulty = resource.get('difficulty')
            estimated_time = resource.get('estimated_time')
            reason = resource.get('reason')
            verification_status = resource.get('verification_status')
            parsed_url = urlparse(str(url or ''))
            provider_key = str(provider or '').casefold().strip()
            if not all(isinstance(value, str) and value.strip() for value in (
                    title, provider, resource_type, url, estimated_time, reason,
                    verification_status)):
                issues.append('resource contains a missing text field')
                continue
            if provider_key not in recognized_providers:
                issues.append('resource provider is not recognized')
                continue
            if resource_type not in allowed_resource_types:
                issues.append('resource type is not supported')
                continue
            if difficulty not in allowed_difficulties:
                issues.append('resource difficulty is not supported')
                continue
            if verification_status not in allowed_verification_statuses:
                issues.append('resource verification status is not supported')
                continue
            if parsed_url.scheme not in {'http', 'https'} or not parsed_url.netloc:
                issues.append('resource URL is invalid')
                continue
            if str(url).casefold() in seen_urls:
                issues.append('duplicate resource URL')
                continue
            seen_urls.add(str(url).casefold())
            safe_resources.append({
                'title': title.strip(),
                'provider': provider.strip(),
                'resource_type': resource_type,
                'url': url.strip(),
                'difficulty': difficulty,
                'estimated_time': estimated_time.strip(),
                'reason': reason.strip(),
                'verification_status': verification_status
            })
        if not safe_resources:
            issues.append('recommendation has no valid resources')
            continue
        seen_skills.add(skill_key)
        safe_recommendations.append({
            'skill': str(skill_name).strip(),
            'resources': safe_resources,
            'practice_task': practice_task.strip(),
            'learning_order': learning_order
        })

    # Reject the response when the chatbot produced no usable structured record
    status = 'accepted' if safe_recommendations and not issues else (
        'repaired' if safe_recommendations else 'rejected'
    )
    return {
        'recommendations': safe_recommendations,
        'validation': {'status': status, 'issues': issues}
    }


# Call a provider adapter and return only validated learning resources
def generate_learning_resources(recommendations, chatbot_callable, target_role=None):
    if not callable(chatbot_callable):
        raise TypeError('chatbot_callable must be callable')
    request = build_resource_request(recommendations, target_role)
    requested_skills = [
        item['skill'] for item in request['uploaded_data']['missing_required_technical_skills']
    ]
    model_response = chatbot_callable(request)
    return validate_resource_response(model_response, requested_skills)


# Build ranked recommendations with transparent status-specific actions and explanations
def generate_recommendations(skill_matches, resume_evidence=None, job_evidence=None,
                             max_recommendations=10):
    if not isinstance(skill_matches, list):
        raise TypeError('skill_matches must be a list')
    if max_recommendations < 1:
        raise ValueError('max_recommendations must be at least 1')

    recommendations = []
    status_confidence = {
        'not_detected': 0.65,
        'weakly_demonstrated': 0.75,
    }

    # Convert only required technical gaps into stable recommendation records
    for skill_match in skill_matches:
        skill_name = read_skill_name(skill_match)
        alternatives = skill_match.get('alternatives', []) if isinstance(skill_match, dict) else []
        if alternatives and skill_match.get('operator') == 'or':
            skill_name = ' or '.join(alternatives)
        if not skill_name:
            continue
        evidence_status = classify_evidence_status(
            skill_match.get('match_status') if isinstance(skill_match, dict) else None
        )
        if not is_recommendation_gap(skill_match, evidence_status):
            continue
        template = action_templates[evidence_status]
        current_resume_evidence, current_job_evidence = read_evidence(
            skill_match, resume_evidence, job_evidence
        )
        evidence_note = 'The job description identifies this required technical skill.'
        if current_job_evidence:
            evidence_note = current_job_evidence[0]
        if evidence_status == 'not_detected':
            why_it_matters = (
                f'{skill_name} is relevant to the target role, but it was not detected in the supplied resume text. '
                'This is a document-evidence gap, not proof that you lack the skill.'
            )
        elif evidence_status == 'weakly_demonstrated':
            why_it_matters = f'{skill_name} is required for the target role, but the resume provides limited evidence of depth or results.'
        recommendations.append({
            'skill': skill_name,
            'priority': 'high',
            'why_it_matters': why_it_matters,
            'job_evidence': current_job_evidence or [evidence_note],
            'current_resume_evidence': current_resume_evidence,
            'recommendation_type': 'learning' if evidence_status == 'not_detected' else 'learning_and_evidence',
            'learning_level': template['learning_level'],
            'recommended_action': template['action'].format(skill=skill_name),
            'category': template['category'],
            'estimated_effort': template['estimated_effort'],
            'confidence': status_confidence[evidence_status],
            'evidence_status': evidence_status,
        })

    # Rank missing skills before weakly demonstrated skills with deterministic output
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda recommendation: (
        priority_order[recommendation['priority']],
        0 if recommendation['evidence_status'] == 'not_detected' else 1,
        recommendation['skill'].casefold(),
    ))
    return recommendations[:max_recommendations]
