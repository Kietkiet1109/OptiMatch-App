import html
import re
import pandas as pd


# Define input and output file paths
inputfile = '../data/raw/resumes.csv'
outputfile = '../data/processed/resumes_clean.csv'

# Define skill aliases and technical skills file path
skill_aliases_file = '../config/skill_aliases.json'
tech_skills_file = '../config/tech_skills.json'

# Define the number of resumes to keep
sample_target = 100

# Read the raw resume data
resumes = pd.read_csv(inputfile)

# Read the skill aliases data
skill_aliases_series = pd.read_json(skill_aliases_file, typ = 'series')
skill_aliases_dict = skill_aliases_series.to_dict()

# Read the technical skills data
tech_skills_series = pd.read_json(tech_skills_file, typ = 'series')
tech_skills_dict = tech_skills_series.to_dict()

# Check that all required columns exist
required_columns = ['ID', 'Resume_str', 'Category']
missing_columns = [column for column in required_columns if column not in resumes.columns]
if len(missing_columns) > 0:
    raise Exception(f'Missing required columns: {missing_columns}')

# Standardize the category column
resumes['Category'] = resumes['Category'].fillna('').astype(str).str.strip().str.upper()

# Keep only Information Technology resumes
resumes = resumes[resumes['Category'] == 'INFORMATION-TECHNOLOGY'].copy()

# Remove records with missing resume text
resumes = resumes[resumes['Resume_str'].notna()].copy()

# Convert resume text to strings
resumes['Resume_str'] = resumes['Resume_str'].astype(str)

# Remove records containing only whitespace
resumes = resumes[resumes['Resume_str'].str.strip().ne('')].copy()

# Create normalized text for duplicate detection
resumes['duplicate_text'] = (resumes['Resume_str']
                             .str.replace(r'\s+', ' ', regex=True)
                             .str.strip())

# Remove duplicate resumes
resumes = resumes.drop_duplicates(subset='duplicate_text', keep='first').copy()

# Remove the temporary duplicate column
resumes = resumes.drop(columns=['duplicate_text'])

# Preserve the original Kaggle ID
resumes['resume_id'] = resumes['ID'].astype(str)

# Preserve the original category
resumes['category'] = resumes['Category']

# Preserve the original resume text
resumes['raw_resume_text'] = resumes['Resume_str']

# Create the cleaned resume text
resumes['cleaned_resume_text'] = resumes['raw_resume_text'].map(html.unescape)

# Remove HTML tags that remain in the text
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(r'<[^>]+>', ' ', regex=True))

# Remove non-breaking spaces and hidden characters
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace('\xa0', ' ', regex=False))
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace('\u200b', ' ', regex=False))

# Mask email addresses
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(r'(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b',
                                               ' email_masked ', regex=True))

# Mask ten-digit phone numbers
ten_digit_phone_patterns = (
    r'(?<!\d)(?:\+?1[\s.-]*)?(?:\(?\d{3}\)?[\s.-]*)'
    r'\d{3}[\s.-]*\d{4}(?!\d)'
)
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(ten_digit_phone_patterns,
                                               ' phone_masked ', regex=True))

# Mask seven-digit phone numbers
seven_digit_phone_pattern = r'(?<!\d)\d{3}[\s.-]\d{4}(?!\d)'
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(seven_digit_phone_pattern,
                                               ' phone_masked ', regex=True))

# Mask common street-address patterns
street_address_patterns = (
    r'(?i)\b\d{1,6}\s+[a-z0-9.#\'-]+'
    r'(?:\s+[a-z0-9.#\'-]+){0,5}\s+'
    r'(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|'
    r'boulevard|blvd|court|ct|way|parkway|pkwy|highway|hwy)'
    r'\b(?:[.,]?\s*(?:apt|suite|unit|#)\s*[a-z0-9-]+)?'
)
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(street_address_patterns,
                                               ' address_masked ', regex=True))

# Mask city, state and postal-code patterns
other_address_patterns = (
    r'(?i)\b[a-z]+(?:\s+[a-z]+){0,2},\s*'
    r'[a-z]{2}\s+\d{5}(?:-\d{4})?\b'
)
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(other_address_patterns,
                                               ' address_masked ', regex=True))

# Replace location placeholders in the Kaggle resumes
location_pattern = r'(?i)\bcity\s*,?\s*state\b'
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(location_pattern,
                                               ' location_masked ', regex=True))


# Replace anonymized company placeholders
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(r'(?i)\bcompany name\b',
                                               ' company_masked ', regex=True))

# Standardize common technical-skill names
for skill_alias, standard_skill in skill_aliases_dict.items():
    resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                      .str.replace(skill_alias, standard_skill,
                                                   regex=True))

# Convert cleaned resume text to lowercase
resumes['cleaned_resume_text'] = resumes['cleaned_resume_text'].str.lower()

# Remove unwanted characters while preserving
# Technical punctuation such as C++, C#, .NET and CI/CD
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(r'[^a-z0-9+#./\-\s_]',
                                               ' ', regex=True))

# Normalize repeated whitespace
resumes['cleaned_resume_text'] = (resumes['cleaned_resume_text']
                                  .str.replace(r'\s+',' ', regex=True)
                                  .str.strip())

# Remove resumes that became empty after cleaning
resumes = resumes[resumes['cleaned_resume_text'].str.strip().ne('')].copy()

# Combine all skill categories into one list
unique_skills = set()
for skill_group in tech_skills_dict.values():
    for skill in skill_group:
        unique_skills.add(skill.lower())

# Sort skills by length
sorted_skills = sorted(unique_skills, key=len, reverse=True)

# Escape special characters
escaped_skills = [re.escape(skill) for skill in sorted_skills]

# Create one regular expression for technical skills
skill_pattern = r'(?<![a-z0-9])(?:' + '|'.join(escaped_skills) + r')(?![a-z0-9])'

# Find technical skills in each resume
resumes['detected_skills'] = (resumes['cleaned_resume_text']
                              .str.findall(skill_pattern, flags=re.IGNORECASE))

# Get the list of unique technical skills
resumes['tech_skills'] = resumes['detected_skills'].map(
    lambda skills: set(skill.lower() for skill in skills) & unique_skills
)

# Remove resumes that have empty skill list
resumes = resumes[resumes['tech_skills'].str.len() > 0].copy()

# Calculate the number of unique technical skills
resumes['num_tech_skills'] = resumes['tech_skills'].apply(lambda l: len(l))

# Remove the temporary detected-skills column
resumes = resumes.drop(columns=['detected_skills'])

# Select 100 resumes using a fixed random seed
if len(resumes) > sample_target:
    resumes = resumes.sample(n = sample_target, random_state=353)

# Sort the selected resumes by their stable ID
resumes = resumes.sort_values(by='resume_id').reset_index(drop=True)

# Keep the final required columns
resumes = resumes[
    [
        'resume_id',
        'category',
        'raw_resume_text',
        'cleaned_resume_text',
        'tech_skills',
        'num_tech_skills'
    ]
]

# Save the cleaned resume dataset
resumes.to_csv(outputfile, index=False)
