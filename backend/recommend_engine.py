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
    resume_values = [str(value).strip() for value in resume_values if str(value).strip()]
    job_values = [str(value).strip() for value in job_values if str(value).strip()]
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
