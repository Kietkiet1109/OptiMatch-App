# Store the minimum score, machine value, and display label for each band.
compatibility_bands = [
    (80, 'strong_alignment', 'Strong alignment'),
    (60, 'moderate_alignment', 'Moderate alignment'),
    (40, 'needs_improvement', 'Needs improvement'),
    (0, 'low_alignment', 'Low alignment')
]


# Function to return validation errors for one analysis input
def validate_analysis_input(analysis_input):

    # Reject values that are not objects before reading their fields.
    if not isinstance(analysis_input, dict):
        return ['analysis_input must be an object']

    # Read the required and optional fields from the submitted input.
    errors = []
    resume_pdf = analysis_input.get('resume_pdf')
    job_description_text = analysis_input.get('job_description_text')
    target_role_title = analysis_input.get('target_role_title')
    user_preferences = analysis_input.get('user_preferences')

    # Confirm that the resume begins with the PDF file signature.
    if not isinstance(resume_pdf, bytes) or not resume_pdf.startswith(b'%PDF-'):
        errors.append('resume_pdf must contain readable PDF bytes')

    # Confirm that the job description contains usable text.
    if not isinstance(job_description_text, str) or not job_description_text.strip():
        errors.append('job_description_text must be a non-empty string')

    # Validate the optional target role title when the user provides it.
    if target_role_title is not None and not isinstance(target_role_title, str):
        errors.append('target_role_title must be a string or null')

    # Validate the optional user preferences when the user provides them.
    if user_preferences is not None and not isinstance(user_preferences, dict):
        errors.append('user_preferences must be an object or null')

    # Return every validation error so the caller can report them together.
    return errors


# Function to return weighted skill coverage from normalized match records
def calculate_coverage(skill_matches, requirement_type=None):

    # Keep only skills for the requested requirement group.
    selected_skills = [
        skill for skill in skill_matches
        if requirement_type is None
        or skill.get('requirement_type') == requirement_type
    ]
    # Exclude unclear matches because they cannot be scored reliably.
    considered_skills = [
        skill for skill in selected_skills
        if skill.get('match_status') != 'unclear'
    ]

    # Return null when there are no scorable skills in the group.
    if not considered_skills:
        return None

    # Assign full, half, or zero credit to each supported match status.
    status_weights = {
        'matched': 1.0,
        'partially_matched': 0.5,
        'not_detected': 0.0
    }
    # Add the weighted match credit and convert it to a percentage.
    matched_weight = sum(
        status_weights.get(skill.get('match_status'), 0.0)
        for skill in considered_skills
    )
    # Round the result to keep the output readable and stable.
    coverage = matched_weight / len(considered_skills) * 100
    return round(coverage, 2)


# Build one validated analysis result.
def build_analysis_result(
        analysis_input,
        skill_matches,
        resume_evidence,
        job_description_evidence,
        formatting_risks,
        recommendations,
        confidence,
        limitations,
        evidence_strength=50,
        formatting_quality=100):

    # Stop before scoring when the submitted input is invalid.
    validation_errors = validate_analysis_input(analysis_input)
    if validation_errors:
        return {
            'schema_version': 'optimatch.v2.analysis.0',
            'status': 'invalid_input',
            'errors': validation_errors
        }

    # Calculate overall, required, and preferred skill coverage.
    technical_skill_coverage = calculate_coverage(skill_matches)
    required_skill_coverage = calculate_coverage(
        skill_matches, 'required'
    )
    preferred_skill_coverage = calculate_coverage(
        skill_matches, 'preferred'
    )

    # Add each available score component using the Phase 0 weights.
    score_parts = []
    if required_skill_coverage is not None:
        score_parts.append((required_skill_coverage, 40))
    if technical_skill_coverage is not None:
        score_parts.append((technical_skill_coverage, 25))
    if preferred_skill_coverage is not None:
        score_parts.append((preferred_skill_coverage, 15))
    score_parts.append((max(0, min(100, evidence_strength)), 10))
    score_parts.append((max(0, min(100, formatting_quality)), 10))

    # Normalize the score when a category, such as preferred skills, is absent.
    total_weight = sum(weight for value, weight in score_parts)
    overall_score = round(
        sum(value * weight for value, weight in score_parts) / total_weight,
        2
    )

    # Select the first compatibility band whose threshold is satisfied.
    compatibility_band = compatibility_bands[-1]
    for band in compatibility_bands:
        if overall_score >= band[0]:
            compatibility_band = band
            break

    # Separate skills that are explicitly missing from required qualifications.
    missing_required_skills = [
        skill for skill in skill_matches
        if skill.get('requirement_type') == 'required'
        and skill.get('match_status') == 'not_detected'
    ]
    # Separate skills that are explicitly missing from preferred qualifications.
    missing_preferred_skills = [
        skill for skill in skill_matches
        if skill.get('requirement_type') == 'preferred'
        and skill.get('match_status') == 'not_detected'
    ]
    # Keep both complete and partial matches as matching skills.
    matching_skills = [
        skill for skill in skill_matches
        if skill.get('match_status') in ('matched', 'partially_matched')
    ]

    # Return the stable Phase 0 result schema for the user interface or API.
    return {
        'schema_version': 'optimatch.v2.analysis.0',
        'status': 'completed',
        'label': 'OptiMatch compatibility estimate',
        'overall_score': {
            'value': overall_score,
            'scale': 100,
            'band': compatibility_band[1]
        },
        'compatibility_band': {
            'value': compatibility_band[1],
            'label': compatibility_band[2]
        },
        'coverage': {
            'technical_skill_coverage': technical_skill_coverage,
            'required_skill_coverage': required_skill_coverage,
            'preferred_skill_coverage': preferred_skill_coverage
        },
        'matching_skills': matching_skills,
        'missing_required_skills': missing_required_skills,
        'missing_preferred_skills': missing_preferred_skills,
        'resume_evidence': resume_evidence,
        'job_description_evidence': job_description_evidence,
        'formatting_risks': formatting_risks,
        'recommendations': recommendations,
        'confidence': confidence,
        'limitations': limitations + [
            'This result is an OptiMatch compatibility estimate, not an official ATS score.',
            'A skill not detected in the resume may still be possessed by the applicant.'
        ],
        'input_quality': {
            'resume_pdf_bytes': len(analysis_input['resume_pdf']),
            'job_description_characters': len(
                analysis_input['job_description_text'].strip()
            )
        }
    }
