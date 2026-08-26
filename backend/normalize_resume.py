from dataclasses import dataclass
import re
import unicodedata


# Keep section names stable so analysis code can use one vocabulary.
section_names = (
    'summary', 'skills', 'work experience', 'education', 'projects',
    'certifications', 'volunteer experience', 'awards', 'publications',
)


# Map common resume headings to the stable section vocabulary.
section_aliases = {
    'professional summary': 'summary', 'profile': 'summary',
    'technical skills': 'skills', 'experience': 'work experience',
    'professional experience': 'work experience',
    'employment history': 'work experience',
    'academic background': 'education',
    'licenses and certifications': 'certifications',
    'volunteering': 'volunteer experience', 'honors': 'awards',
    'research and publications': 'publications',
}


# Use conservative patterns so technical tokens such as C++ remain unchanged.
email_pattern = re.compile(r'\b[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}\b', re.IGNORECASE)
phone_pattern = re.compile(
    r'(?<!\d)(?:\+?\d{1,3}[\s.\-]*)?(?:\(?\d{3}\)?[\s.\-]*)\d{3}[\s.\-]*\d{4}(?!\d)'
)
bullet_pattern = re.compile(r'^[\s]*(?:[•●▪◦‣⁃∙*]|[-–—])\s*')


# The minimum resume representation required by later analysis.
@dataclass(frozen=True)
class NormalizedResume:
    text: str
    sections: dict[str, str]
    masked_email_count: int
    masked_phone_count: int


# Normalize one extracted resume and return no reference to the source text.
def normalize_resume_text(extracted_text: str, *, mask_contacts: bool = True):
    # Reject invalid extractor output before any text operation.
    if not isinstance(extracted_text, str):
        raise TypeError('extracted_text must be a string')

    # Normalize Unicode, page breaks, line endings, and hidden characters.
    text = unicodedata.normalize('NFKC', extracted_text)
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\x0c', '\n')
    text = text.replace('\u00a0', ' ').replace('\u200b', '')
    text = ''.join(
        character if character == '\n' or not unicodedata.category(character).startswith('C') else ' '
        for character in text
    )

    # Normalize bullets and remove repeated page-edge lines.
    text = re.sub(r'[•●▪◦‣⁃∙]', '-', text)
    pages = [page.split('\n') for page in text.split('\n\n\n')]
    if len(pages) > 1:
        edge_counts: dict[str, int] = {}
        for page in pages:
            for line in set(line.strip() for line in page[:3] + page[-3:] if line.strip()):
                edge_counts[line] = edge_counts.get(line, 0) + 1
        repeated_edges = {line for line, count in edge_counts.items() if count > 1}
        pages = [[line for line in page if line.strip() not in repeated_edges] for page in pages]

    # Remove adjacent duplicate lines and conservatively repair line wrapping.
    lines: list[str] = []
    for page in pages:
        for raw_line in page:
            line = bullet_pattern.sub('- ', raw_line.strip()) if raw_line.strip() else ''
            if line and lines and line.casefold() == lines[-1].casefold():
                continue
            previous_candidate = re.sub(r'[^a-z ]', '', lines[-1].casefold()).strip() if lines else ''
            line_candidate = re.sub(r'[^a-z ]', '', line.casefold()).strip()
            if (
                line and lines and lines[-1] and not line.startswith('- ')
                and previous_candidate not in section_names
                and previous_candidate not in section_aliases
                and line_candidate not in section_names
                and line_candidate not in section_aliases
                and not email_pattern.search(line)
                and not phone_pattern.search(line)
                and not line.endswith(':')
                and not re.search(r'\b(?:19|20)\d{2}\b|\|', line)
                and not re.search(r'[.!?:;]$', lines[-1])
            ):
                lines[-1] = f'{lines[-1]} {line}'
            else:
                lines.append(line)

    # Mask direct contact identifiers before analysis by default.
    value = '\n'.join(lines)
    masked_email_count = len(email_pattern.findall(value))
    masked_phone_count = len(phone_pattern.findall(value))
    if mask_contacts:
        value = email_pattern.sub('[EMAIL]', value)
        value = phone_pattern.sub('[PHONE]', value)
    value = re.sub(r'[ \t]+', ' ', value)
    value = re.sub(r'\n{3,}', '\n\n', value).strip()

    # Detect recognized headings and assign the following lines to each section.
    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    for line in value.splitlines():
        candidate = re.sub(r'[^a-z ]', '', line.casefold()).strip()
        candidate = re.sub(r'\s+', ' ', candidate)
        section = candidate if candidate in section_names else section_aliases.get(candidate)
        if section:
            current_section = section
            sections.setdefault(section, [])
        elif current_section:
            sections[current_section].append(line)

    section_text = {section: '\n'.join(section_lines).strip() for section, section_lines in sections.items()}
    return NormalizedResume(value, section_text, masked_email_count, masked_phone_count)
