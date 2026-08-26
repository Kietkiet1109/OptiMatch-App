import re
try:
    from .extract_skills import extract_skill_evidence
except ImportError:
    from extract_skills import extract_skill_evidence

# Store deterministic labels that separate scoring importance from ordinary keywords.
requirement_weights = {
    'required': 1.0,
    'preferred': 0.5,
    'general': 0.25
}

# Detect common section headings without depending on capitalization.
section_patterns = {
    'required_qualifications': re.compile(
        r'^(required qualifications?|minimum qualifications?|must have|requirements?)$', re.I
    ),
    'preferred_qualifications': re.compile(
        r'^(preferred qualifications?|nice to have|bonus qualifications?|desired qualifications?)$', re.I
    ),
    'responsibilities': re.compile(
        r'^(responsibilities|what you will do|what you will be doing|duties)$', re.I
    ),
    'technical_skills': re.compile(
        r'^(technical skills?|technologies|technology stack|tools?)$', re.I
    ),
    'education_requirements': re.compile(
        r'^(education|education requirements?|academic requirements?)$', re.I
    ),
    'certifications': re.compile(r'^(certifications?|licenses?)$', re.I),
    'soft_skills': re.compile(r'^(soft skills?|competencies|core competencies)$', re.I),
    'location_work_arrangement': re.compile(
        r'^(location|work arrangement|work location|remote|about the role)$', re.I
    )
}


# Identify soft skills separately so they cannot receive technical-skill weight.
soft_skill_terms = {
    'communication', 'collaboration', 'teamwork', 'leadership', 'problem solving',
    'time management', 'adaptability', 'attention to detail', 'critical thinking',
    'written communication', 'verbal communication', 'stakeholder management'
}


# Identify domain terms that add context but are not automatically scorable skills.
industry_terms = {
    'fintech', 'financial services', 'healthcare', 'education', 'e-commerce',
    'government', 'telecommunications', 'saas', 'cybersecurity', 'retail',
    'banking', 'insurance', 'machine learning', 'artificial intelligence',
    'cloud computing', 'data analytics'
}


# Clean one line while retaining useful technical punctuation and readable evidence.
def clean_line(value):
    value = re.sub(r'^\s*[-*•▪◦]\s*', '', value)
    return re.sub(r'\s+', ' ', value).strip(' \t:')


# Split the description into heading-based sections and preserve unclassified text.
def split_sections(text):
    sections = {'general': []}
    current_section = 'general'
    for raw_line in str(text).splitlines():
        line = clean_line(raw_line)
        if not line:
            continue
        heading = line.rstrip(':').strip()
        matched_section = next(
            (name for name, pattern in section_patterns.items() if pattern.fullmatch(heading)),
            None
        )
        if matched_section:
            current_section = matched_section
            sections.setdefault(current_section, [])
            continue
        sections.setdefault(current_section, []).append(line)
    return sections


# Classify a sentence using explicit requirement language before using its section.
def classify_requirement(text, section):
    value = text.casefold()
    if re.search(r'\b(required|requiredly|must|required to|minimum|mandatory)\b', value):
        return 'required'
    if re.search(r'\b(preferred|preferably|nice to have|bonus|desired|plus)\b', value):
        return 'preferred'
    if section == 'required_qualifications':
        return 'required'
    if section == 'preferred_qualifications':
        return 'preferred'
    return 'general'


# Return a compact record with explicit scoring weight and source evidence.
def build_classified_record(name, record_type, requirement_type, evidence):
    return {
        'name': name,
        'type': record_type,
        'requirement_type': requirement_type,
        'score_weight': requirement_weights[requirement_type],
        'evidence': evidence
    }


# Parse a job description into stable fields used by matching and later scoring phases.
def parse_job_description(text, job_title = None, company = None):
    value = '' if text is None else str(text)
    sections = split_sections(value)
    lines = [line for section_lines in sections.values() for line in section_lines]
    sentence_records = [
        (line, section_name)
        for section_name, section_lines in sections.items()
        for line in section_lines
    ]

    # Extract title and company from explicit fields or common metadata lines.
    metadata_text = '\n'.join(lines[:8])
    if not job_title:
        title_match = re.search(r'(?im)^\s*(?:job title|position|role)\s*:\s*(.+)$', metadata_text)
        job_title = clean_line(title_match.group(1)) if title_match else None
    if not company:
        company_match = re.search(r'(?im)^\s*company\s*:\s*(.+)$', metadata_text)
        company = clean_line(company_match.group(1)) if company_match else None

    # Extract structured qualification and responsibility text with requirement classes.
    required_qualifications = sections.get('required_qualifications', [])
    preferred_qualifications = sections.get('preferred_qualifications', [])
    responsibilities = sections.get('responsibilities', [])
    education_requirements = sections.get('education_requirements', [])
    certifications = sections.get('certifications', [])
    location_text = ' '.join(sections.get('location_work_arrangement', []))

    # Detect technical skills and classify each occurrence by its local evidence.
    technical_skills = []
    for evidence in extract_skill_evidence(value, source_document='job_description'):
        line = next((line for line, section in sentence_records
                     if evidence['normalized_skill_name'] in line.casefold()), value)
        requirement_type = classify_requirement(
            line, next((section for line_value, section in sentence_records if line_value == line), 'general')
        )
        technical_skills.append(build_classified_record(
            evidence['normalized_skill_name'], 'technical_skill', requirement_type,
            evidence['text_evidence']
        ))
    technical_skills = list({record['name']: record for record in technical_skills}.values())

    # Detect soft skills and explicitly give them a lower weight than technical skills.
    soft_skills = []
    for term in soft_skill_terms:
        match = re.search(r'(?<![a-z])' + re.escape(term) + r'(?![a-z])', value, re.I)
        if match:
            evidence = value[max(0, match.start() - 60):min(len(value), match.end() + 60)].strip()
            requirement_type = classify_requirement(evidence, 'soft_skills')
            soft_skills.append(build_classified_record(
                term, 'soft_skill', requirement_type, evidence
            ))

    # Extract years, education, certifications, work arrangement, seniority, and domain terms.
    experience_matches = re.findall(
        r'(?i)(\d+)(?:\s*[-to]+\s*(\d+))?\s*\+?\s*years?[^.\n]{0,80}', value
    )
    years_experience = []
    for first_year, second_year in experience_matches:
        years_experience.append({
            'minimum_years': int(first_year),
            'maximum_years': int(second_year) if second_year else None,
            'evidence': next((line for line in lines if first_year in line), value)
        })
    seniority_match = re.search(
        r'(?i)\b(entry[- ]level|junior|intermediate|mid[- ]level|senior|lead|principal|manager|director|intern)\b',
        (job_title or '') + ' ' + value
    )
    location_work_arrangement = [
        term for term in ('remote', 'hybrid', 'on-site', 'onsite', 'in office')
        if re.search(r'(?i)\b' + re.escape(term) + r'\b', location_text or value)
    ]
    industry_domain_terms = [term for term in industry_terms if re.search(
        r'(?<![a-z])' + re.escape(term) + r'(?![a-z])', value, re.I
    )]

    return {
        'schema_version': 'optimatch.job_description',
        'job_title': job_title,
        'company': company,
        'required_qualifications': required_qualifications,
        'preferred_qualifications': preferred_qualifications,
        'technical_skills': technical_skills,
        'soft_skills': soft_skills,
        'years_experience': years_experience,
        'education_requirements': education_requirements,
        'certifications': certifications,
        'responsibilities': responsibilities,
        'industry_domain_terms': industry_domain_terms,
        'location_work_arrangement': location_work_arrangement,
        'location_evidence': location_text or None,
        'seniority_level': seniority_match.group(1).casefold() if seniority_match else None,
        'unclassified_text': sections.get('general', [])
    }
