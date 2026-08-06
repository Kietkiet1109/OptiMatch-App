import html
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Define input and output files
inputfile = '../data/raw/jobs.csv'
outputfile = '../data/processed/jobs_clean.csv'

# Read the raw job data
jobs = pd.read_csv(inputfile)

# Check that the required columns exist
required_columns = ['job_id', 'job_title', 'company', 'category', 'description']
missing_columns = [column for column in required_columns if column not in jobs.columns]
if len(missing_columns) > 0:
    raise Exception(f'Missing required columns: {missing_columns}')

# Convert job IDs to strings
jobs['job_id'] = jobs['job_id'].astype(str)

# Convert publication dates for sorting
if 'publication_date' in jobs.columns:
    jobs['publication_date_sort'] = pd.to_datetime(jobs['publication_date'])
    jobs = jobs.sort_values(by='publication_date_sort', ascending=False)

# Reset the row indexes
jobs = jobs.reset_index(drop=True)

# Detect exact duplicate job IDs
duplicate_id_rows = jobs[jobs.duplicated(subset='job_id', keep='first')]

# Remove exact duplicate job IDs
jobs = jobs.drop_duplicates(subset='job_id',keep='first').copy()

# Preserve the original job description
jobs['raw_description'] = jobs['description'].fillna('').astype(str)

# Remove jobs with empty raw descriptions
jobs = jobs[jobs['raw_description'].str.strip().ne('')].copy()

# Convert HTML entities such as &amp; and &#39;
jobs['cleaned_description'] = jobs['raw_description'].map(html.unescape)

# Remove HTML tags
jobs['cleaned_description'] = (jobs['cleaned_description']
                               .str.replace(r'<[^>]+>', ' ', regex=True))

# Remove URLs that appear inside descriptions
jobs['cleaned_description'] = (jobs['cleaned_description']
                               .str.replace(r'https?://\S+|www\.\S+', ' ', regex=True))

# Remove common navigation and page artifacts
page_artifacts = [
    r'(?i)\bapply now\b',
    r'(?i)\bapply for this job\b',
    r'(?i)\bback to jobs\b',
    r'(?i)\breturn to job search\b',
    r'(?i)\bshare this job\b',
    r'(?i)\bsave this job\b',
    r'(?i)\bcreate job alert\b',
    r'(?i)\bjob alert\b',
    r'(?i)\bprivacy policy\b',
    r'(?i)\bterms of use\b',
    r'(?i)\bskip to main content\b'
]

for artifact in page_artifacts:
    jobs['cleaned_description'] = (jobs['cleaned_description']
                                   .str.replace(artifact, ' ', regex=True))

# Remove common legal and equal-opportunity boilerplate
legal_boilerplate = [
    r'(?i)\bwe are an equal opportunity employer\b[^.]*\.?',
    r'(?i)\bthe company is an equal opportunity employer\b[^.]*\.?',
    r'(?i)\bequal employment opportunity employer\b[^.]*\.?',
    r'(?i)\bqualified applicants will receive consideration for employment without regard to\b[^.]*\.?',
    r'(?i)\bwe do not discriminate on the basis of\b[^.]*\.?',
    r'(?i)\ball qualified applicants will receive consideration\b[^.]*\.?',
    r'(?i)\breasonable accommodation is available\b[^.]*\.?',
    r'(?i)\bif you require a reasonable accommodation\b[^.]*\.?',
    r'(?i)\bapplicants with disabilities\b[^.]*\.?'
]

for boilerplate in legal_boilerplate:
    jobs['cleaned_description'] = (jobs['cleaned_description']
                                   .str.replace(boilerplate, ' ', regex=True))

# Convert text to lowercase
jobs['cleaned_description'] = jobs['cleaned_description'].str.lower()

# Remove unwanted characters while preserving
# Technical punctuation used in C++, C#, .NET and CI/CD
jobs['cleaned_description'] = jobs['cleaned_description'
].str.replace(r'[^a-z0-9+#./\-\s]', ' ', regex=True)

# Normalize repeated whitespace
jobs['cleaned_description'] = (jobs['cleaned_description']
                               .str.replace(r'\s+', ' ', regex=True).str.strip())

# Remove jobs that became empty after cleaning
jobs = jobs[jobs['cleaned_description'].str.strip().ne('')].copy()

# Standardize category labels
category_map = {
    'computer & it': 'Computer and IT',
    'computer and it': 'Computer and IT',
    'computer it': 'Computer and IT',
    'data & analytics': 'Data and Analytics',
    'data and analytics': 'Data and Analytics',
    'data analytics': 'Data and Analytics',
    'software engineer': 'Software Engineering',
    'software engineering': 'Software Engineering',
    'science & engineering': 'Science and Engineering',
    'science and engineering': 'Science and Engineering'
}
jobs['category'] = jobs['category'].fillna('').astype(str).str.strip().str.lower()
jobs['category'] = jobs['category'].replace(category_map)

# Reset indexes before description duplicate detection
jobs = jobs.reset_index(drop=True)

# Detect exact duplicate cleaned descriptions
exact_description_rows = jobs[jobs.duplicated(subset='cleaned_description', keep='first')]

# Remove exact duplicate descriptions
jobs = jobs.drop_duplicates(subset='cleaned_description', keep='first').copy()

# Reset indexes before near-duplicate detection
jobs = jobs.reset_index(drop=True)

# Create TF-IDF vectors for job descriptions
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=1)
job_vectors = vectorizer.fit_transform(jobs['cleaned_description'])

# Calculate similarity between all job descriptions
similarity_matrix = cosine_similarity(job_vectors)

# Set the near-duplicate similarity threshold
similarity_threshold = 0.90

# Create a set for near-duplicate row indexes
near_duplicate_indexes = set()

# Compare each description with the descriptions after it
for first_index in range(len(jobs)):
    if first_index in near_duplicate_indexes:
        continue

    for second_index in range(first_index + 1, len(jobs)):
        if second_index in near_duplicate_indexes:
            continue

        similarity = similarity_matrix[first_index, second_index]

        if similarity >= similarity_threshold:
            near_duplicate_indexes.add(second_index)

# Remove near-duplicate descriptions
jobs = jobs.drop(index=list(near_duplicate_indexes)).copy()

# Remove the old description column
jobs = jobs.drop(columns=['description'])

# Remove the temporary sorting column
if 'publication_date_sort' in jobs.columns:
    jobs = jobs.drop(columns=['publication_date_sort'])

# Put raw and cleaned descriptions together
column_order = ['job_id', 'job_title', 'company', 'category']
optional_columns = ['job_level', 'location']

for column in optional_columns:
    if column in jobs.columns:
        column_order.append(column)

column_order.extend(['raw_description', 'cleaned_description'])
final_columns = ['publication_date', 'job_url']

for column in final_columns:
    if column in jobs.columns:
        column_order.append(column)

# Keep columns in a clear order
jobs = jobs[column_order]

# Save the cleaned job dataset
jobs.to_csv(outputfile, index=False)
