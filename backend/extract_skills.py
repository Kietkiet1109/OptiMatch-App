import json
import re


# Define configuration paths
tech_skills_file = '../config/tech_skills.json'
skill_aliases_file = '../config/skill_aliases.json'
role_domains_file = '../config/role_domains.json'


# Read the configuration files and flatten the categorized skill dictionary.
def load_configuration():
    with tech_skills_file.open(encoding='utf-8') as file:
        technical_skills = json.load(file)
    with skill_aliases_file.open(encoding='utf-8') as file:
        skill_aliases = json.load(file)
    with role_domains_file.open(encoding='utf-8') as file:
        role_domains = json.load(file)
    skill_names = {normalize_term(skill) for group in technical_skills.values() for skill in group}
    canonical_names = {skill: skill for skill in skill_names}
    for alias, canonical_name in skill_aliases.items():
        canonical_names[normalize_term(alias)] = canonical_name.casefold()
    return canonical_names, role_domains


# Normalize case and punctuation while preserving word boundaries for regex matching.
def normalize_term(value):
    value = value.casefold().strip()
    value = value.replace('&', ' and ')
    value = re.sub(r'[._/\\-]+', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()


# Build a pattern that supports punctuation, abbreviations, and multi-word terms.
def build_pattern(canonical_names):
    terms = sorted(canonical_names, key=lambda term: len(normalize_term(term)), reverse=True)
    patterns = []
    for term in terms:
        normalized_term = normalize_term(term)
        if normalized_term in {'c', 'r', 'go'}:
            continue
        term_pattern = re.escape(normalized_term).replace(r'\ ', r'[\s._/\\-]+')
        patterns.append(r'(?<![a-z0-9])' + term_pattern + r'(?![a-z0-9])')
    return re.compile('|'.join(patterns), re.IGNORECASE)


# Return canonical skill names for existing callers.
def get_skill_set():
    canonical_names, _ = load_configuration()
    return set(canonical_names.values())


# Return the compatibility regex used by the original baseline model.
def get_skill_pattern():
    canonical_names, _ = load_configuration()
    return build_pattern(canonical_names).pattern


# Extract canonical names without changing the original set-based API.
def extract_skills(text, skill_pattern=None):
    detections = extract_skill_evidence(text)
    return {detection['normalized_skill_name'] for detection in detections}


# Extract every detected skill with source, section, evidence, location, and confidence.
def extract_skill_evidence(text, source_document='document', section=None, page=None):
    value = '' if text is None else str(text)
    canonical_names, role_domains = load_configuration()
    pattern = build_pattern(canonical_names)
    detections = []
    matched_spans = set()

    # Match configured aliases and canonical names, then resolve context-sensitive short terms.
    for match in pattern.finditer(value):
        matched_text = match.group(0)
        normalized_match = normalize_term(matched_text)
        canonical_name = canonical_names.get(normalized_match)
        if canonical_name is None:
            canonical_name = canonical_names.get(matched_text.casefold(), normalized_match)
        matched_spans.add((match.start(), match.end()))
        detections.append({
            'skill_name': matched_text,
            'normalized_skill_name': canonical_name,
            'source_document': source_document,
            'section': section,
            'text_evidence': value[max(0, match.start() - 80):min(len(value), match.end() + 80)].strip(),
            'character_start': match.start(),
            'character_end': match.end(),
            'page': page,
            'confidence': 'high',
        })

    # Apply conservative context rules for ambiguous one-letter and short language names.
    context_pattern = re.compile(r'(?<![a-z0-9])(?:c|r|go)(?![a-z0-9])', re.IGNORECASE)
    context_terms = {
        normalize_term(term) for terms in role_domains.values() for term in terms
    }
    for match in context_pattern.finditer(value):
        if (match.start(), match.end()) in matched_spans:
            continue
        surrounding_text = value[max(0, match.start() - 45):min(len(value), match.end() + 45)].casefold()
        context_cues = ('programming', 'language', 'code')
        if any(term in surrounding_text for term in context_cues) or (
            any(term in surrounding_text for term in context_terms)
            and any(term in surrounding_text for term in ('skill', 'experience', 'proficient'))
        ):
            matched_text = match.group(0)
            detections.append({
                'skill_name': matched_text,
                'normalized_skill_name': matched_text.casefold(),
                'source_document': source_document,
                'section': section,
                'text_evidence': surrounding_text.strip(),
                'character_start': match.start(),
                'character_end': match.end(),
                'page': page,
                'confidence': 'medium',
            })

    # Sort by source position and remove duplicate detections at the same location.
    detections.sort(key=lambda detection: (detection['character_start'], detection['character_end']))
    unique_detections = []
    seen_skills = set()
    for detection in detections:
        key = (detection['normalized_skill_name'], detection['character_start'])
        if key not in seen_skills:
            unique_detections.append(detection)
            seen_skills.add(key)
    return unique_detections
