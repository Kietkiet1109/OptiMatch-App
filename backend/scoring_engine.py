# OptiMatch's transparent model
scoring_weights = {
    'required_skill_coverage': 40,
    'technical_skill_coverage': 25,
    'experience_alignment': 15,
    'preferred_skill_coverage': 10,
    'education_alignment': 5,
    'formatting_quality': 5,
}

# Clamp numeric component scores to the 0-to-100 scale
def clamp_score(value):
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return 0.0
    return round(max(0.0, min(100.0, numeric_value)), 2)


# Read a numeric score and its supporting evidence from a scalar or evidence record
def read_score(value, default_evidence):
    if isinstance(value, dict):
        score = value.get('score', value.get('value', 0))
        evidence = value.get('evidence', default_evidence)
    else:
        score = value
        evidence = default_evidence
    if not isinstance(evidence, list):
        evidence = [evidence] if evidence else []
    return clamp_score(score), evidence


# Calculate skill coverage and retain the exact records used as scoring evidence
def calculate_skill_component(skill_matches, requirement_type=None):
    selected_skills = [
        skill for skill in skill_matches
        if requirement_type is None
        or skill.get('requirement_type') == requirement_type
    ]
    considered_skills = [
        skill for skill in selected_skills
        if skill.get('match_status') != 'unclear'
    ]
    status_weights = {
        'matched': 1.0,
        'partially_matched': 0.5,
        'not_detected': 0.0,
    }
    matched_weight = sum(
        status_weights.get(skill.get('match_status'), 0.0)
        for skill in considered_skills
    )
    coverage = (
        matched_weight / len(considered_skills) * 100
        if considered_skills else 0.0
    )
    return round(coverage, 2), considered_skills


# Convert formatting findings into a reproducible risk score when no explicit score exists
def calculate_formatting_risk(formatting_risks):
    severity_weights = {'low': 10, 'medium': 20, 'high': 35}
    risk = 0
    for formatting_risk in formatting_risks or []:
        if isinstance(formatting_risk, dict):
            risk += severity_weights.get(
                str(formatting_risk.get('severity', 'medium'))
                .casefold(), 20
            )
        else:
            risk += 20
    return round(min(100, risk), 2)


# Produce every metric, its weighted contribution, and its supporting evidence
def calculate_deterministic_score(
        skill_matches,
        experience_alignment=0,
        education_alignment=0,
        formatting_risk=None,
        formatting_risks=None):
    technical_coverage, technical_evidence = calculate_skill_component(skill_matches)
    required_coverage, required_evidence = calculate_skill_component(
        skill_matches, 'required'
    )
    preferred_coverage, preferred_evidence = calculate_skill_component(
        skill_matches, 'preferred'
    )
    experience_score, experience_evidence = read_score(
        experience_alignment, []
    )
    education_score, education_evidence = read_score(
        education_alignment, []
    )
    if formatting_risk is None:
        formatting_risk = calculate_formatting_risk(formatting_risks)
    formatting_risk_score = clamp_score(formatting_risk)
    formatting_quality = round(100 - formatting_risk_score, 2)

    # Store each weighted calculation so the overall result is explainable.
    components = {
        'required_skill_coverage': {
            'score': required_coverage,
            'weight': scoring_weights['required_skill_coverage'],
            'contribution': round(required_coverage * 0.40, 2),
            'evidence': required_evidence,
        },
        'technical_skill_coverage': {
            'score': technical_coverage,
            'weight': scoring_weights['technical_skill_coverage'],
            'contribution': round(technical_coverage * 0.25, 2),
            'evidence': technical_evidence,
        },
        'experience_alignment': {
            'score': experience_score,
            'weight': scoring_weights['experience_alignment'],
            'contribution': round(experience_score * 0.15, 2),
            'evidence': experience_evidence,
        },
        'preferred_skill_coverage': {
            'score': preferred_coverage,
            'weight': scoring_weights['preferred_skill_coverage'],
            'contribution': round(preferred_coverage * 0.10, 2),
            'evidence': preferred_evidence,
        },
        'education_alignment': {
            'score': education_score,
            'weight': scoring_weights['education_alignment'],
            'contribution': round(education_score * 0.05, 2),
            'evidence': education_evidence,
        },
        'formatting_quality': {
            'score': formatting_quality,
            'weight': scoring_weights['formatting_quality'],
            'contribution': round(formatting_quality * 0.05, 2),
            'evidence': formatting_risks or [],
        },
    }

    # Count shared and missing skills from the same records used for coverage
    matching_skills = [
        skill for skill in skill_matches
        if skill.get('match_status') in ('matched', 'partially_matched')
    ]
    missing_required_skills = [
        skill for skill in skill_matches
        if skill.get('requirement_type') == 'required'
        and skill.get('match_status') == 'not_detected'
    ]
    missing_preferred_skills = [
        skill for skill in skill_matches
        if skill.get('requirement_type') == 'preferred'
        and skill.get('match_status') == 'not_detected'
    ]
    overall_score = round(
        sum(component['contribution'] for component in components.values()), 2
    )
    return {
        'required_skill_coverage': required_coverage,
        'preferred_skill_coverage': preferred_coverage,
        'technical_skill_coverage': technical_coverage,
        'shared_skill_count': len(matching_skills),
        'missing_required_skill_count': len(missing_required_skills),
        'missing_preferred_skill_count': len(missing_preferred_skills),
        'experience_alignment': experience_score,
        'education_alignment': education_score,
        'formatting_risk': formatting_risk_score,
        'overall_score': overall_score,
        'components': components,
        'matching_skills': matching_skills,
        'missing_required_skills': missing_required_skills,
        'missing_preferred_skills': missing_preferred_skills,
        'weights': scoring_weights.copy(),
    }
