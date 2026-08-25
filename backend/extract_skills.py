import pandas as pd
import re

# Define technical skills file
tech_skills_file = '../config/tech_skills.json'

# Read technical skills and create one skills set
def get_skill_set():
    # Read technical skills from JSON
    tech_skills_series = pd.read_json(tech_skills_file, typ='series')
    tech_skills_dict = tech_skills_series.to_dict()

    # Combine all technical skill categories
    tech_skills = set()
    for skill_group in tech_skills_dict.values():
        for skill in skill_group:
            tech_skills.add(skill.lower())

    return tech_skills


# Create one regex pattern from skills set
def get_skill_pattern():

    # Get the skills set
    tech_skills = get_skill_set()

    # Sort longer skills first
    sorted_skills = sorted(tech_skills, key=len, reverse=True)

    # Remove ambiguous short skills
    normal_skills = [skill for skill in sorted_skills
                     if skill not in ['c', 'r', 'go']]

    # Escape special characters
    escaped_skills = [re.escape(skill) for skill in normal_skills]


    # Create the main technical skill pattern
    skill_pattern = (
        r'(?<![a-z0-9])(?:'
        + '|'.join(escaped_skills)
        + r')(?![a-z0-9])'
    )

    # Add special patterns for C, R and Go
    special_pattern = (
        r'|\bc programming\b'
        r'|\bprogramming in c\b'
        r'|\bc language\b'
        r'|\br programming\b'
        r'|\bprogramming in r\b'
        r'|\br language\b'
        r'|\bgolang\b'
        r'|\bgo programming\b'
        r'|\bprogramming in go\b'
        r'|\bgo language\b'
    )

    # Combine normal and special patterns
    skill_pattern = skill_pattern + special_pattern

    return skill_pattern


# Extract technical skills from text
def extract_skills(text, skill_pattern):

    # Convert missing text to empty string
    if text is None:
        text = ''

    # Find all technical skills
    detected_skills = re.findall(skill_pattern, str(text).lower(), flags=re.IGNORECASE)

    # Remove empty results
    detected_skills = [skill for skill in detected_skills if skill != '']

    # Remove duplicates
    detected_skills = set(detected_skills)

    return detected_skills
