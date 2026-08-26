# Keep recommendation wording separate from the evidence classifier so each output is auditable
action_templates = {
    'not_detected': {
        'category': 'practice projects',
        'action': 'Build a small project that uses {skill}, then document the decisions, setup, and results.',
        'learning_level': 'beginner',
        'estimated_effort': '2-4 weeks',
    },
    'weakly_demonstrated': {
        'category': 'portfolio improvements',
        'action': 'Strengthen an existing project by showing how you used {skill}, your individual contribution, and a measurable result.',
        'learning_level': 'intermediate',
        'estimated_effort': '1-2 weeks',
    },
    'explicitly_demonstrated': {
        'category': 'interview preparation topics',
        'action': 'Prepare to explain one real example of {skill}, including trade-offs, debugging, testing, and limitations.',
        'learning_level': 'intermediate',
        'estimated_effort': '3-5 days',
    },
    'likely_related_uncertain': {
        'category': 'official documentation',
        'action': 'Review the official documentation for {skill} and complete one small validation exercise before claiming direct experience.',
        'learning_level': 'beginner to intermediate',
        'estimated_effort': '3-7 days',
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


# Build ranked recommendations with transparent status-specific actions and explanations
def generate_recommendations(skill_matches, resume_evidence=None, job_evidence=None,
                             max_recommendations=10):
    if not isinstance(skill_matches, list):
        raise TypeError('skill_matches must be a list')
    if max_recommendations < 1:
        raise ValueError('max_recommendations must be at least 1')

    recommendations = []
    status_priority = {
        'not_detected': {'required': 'high', 'preferred': 'medium', 'general': 'low'},
        'weakly_demonstrated': {'required': 'high', 'preferred': 'medium', 'general': 'low'},
        'likely_related_uncertain': {'required': 'high', 'preferred': 'medium', 'general': 'low'},
        'explicitly_demonstrated': {'required': 'medium', 'preferred': 'low', 'general': 'low'},
    }
    status_confidence = {
        'not_detected': 0.65,
        'weakly_demonstrated': 0.75,
        'likely_related_uncertain': 0.45,
        'explicitly_demonstrated': 0.9,
    }

    # Convert every supported match into one stable, explainable recommendation record
    for skill_match in skill_matches:
        skill_name = read_skill_name(skill_match)
        if not skill_name:
            continue
        evidence_status = classify_evidence_status(
            skill_match.get('match_status') if isinstance(skill_match, dict) else None
        )
        template = action_templates[evidence_status]
        requirement_type = (
            skill_match.get('requirement_type', 'general')
            if isinstance(skill_match, dict) else 'general'
        )
        requirement_type = requirement_type if requirement_type in status_priority[evidence_status] else 'general'
        current_resume_evidence, current_job_evidence = read_evidence(
            skill_match, resume_evidence, job_evidence
        )
        evidence_note = 'The job description identifies this skill as relevant.'
        if current_job_evidence:
            evidence_note = current_job_evidence[0]
        if evidence_status == 'not_detected':
            why_it_matters = (
                f'{skill_name} is relevant to the target role, but it was not detected in the supplied resume text. '
                'This is a document-evidence gap, not proof that you lack the skill.'
            )
        elif evidence_status == 'weakly_demonstrated':
            why_it_matters = f'{skill_name} appears related to the target role, but the resume gives limited evidence of depth or results.'
        elif evidence_status == 'explicitly_demonstrated':
            why_it_matters = f'{skill_name} is explicitly demonstrated, so interview-ready explanation and evidence quality are the next priorities.'
        else:
            why_it_matters = f'{skill_name} may be related to the target role, but the available evidence is too ambiguous for a firm conclusion.'
        recommendations.append({
            'skill': skill_name,
            'priority': status_priority[evidence_status][requirement_type],
            'why_it_matters': why_it_matters,
            'job_evidence': current_job_evidence or [evidence_note],
            'current_resume_evidence': current_resume_evidence,
            'learning_level': template['learning_level'],
            'recommended_action': template['action'].format(skill=skill_name),
            'category': template['category'],
            'estimated_effort': template['estimated_effort'],
            'confidence': status_confidence[evidence_status],
            'evidence_status': evidence_status,
        })

    # Rank required gaps first, then weaker evidence, while preserving deterministic output
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda recommendation: (
        priority_order[recommendation['priority']],
        -recommendation['confidence'],
        recommendation['skill'].casefold(),
    ))
    return recommendations[:max_recommendations]
