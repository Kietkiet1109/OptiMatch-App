import joblib
import pandas as pd
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import TfidfVectorizer

# Define input file paths
jobs_file = '../data/processed/jobs_clean.csv'
resumes_file = '../data/processed/resumes_clean.csv'
courses_file = '../data/processed/courses_clean.csv'
split_file = '../data/evaluation/jobs_split.csv'

# Define output folder
output_folder = '../outputs/features'

# Read cleaned datasets
jobs = pd.read_csv(jobs_file)
resumes = pd.read_csv(resumes_file)
courses = pd.read_csv(courses_file)
job_split = pd.read_csv(split_file)

# Convert job IDs to strings
jobs['job_id'] = jobs['job_id'].astype(str)
job_split['job_id'] = job_split['job_id'].astype(str)

# Add development and evaluation labels to jobs
jobs = jobs.merge(job_split[['job_id', 'label']], on='job_id', how='left')

# Check that every job received a split label
if jobs['label'].isna().any():
    raise Exception('Some jobs are missing split labels')

# Separate development and evaluation jobs
development_jobs = jobs[jobs['label'] == 'development'].copy()
evaluation_jobs = jobs[jobs['label'] == 'evaluation'].copy()

# Reset indexes of all datas
development_jobs = development_jobs.reset_index(drop=True)
evaluation_jobs = evaluation_jobs.reset_index(drop=True)
resumes = resumes.reset_index(drop=True)
courses = courses.reset_index(drop=True)

# Fill missing text with empty strings
development_jobs['cleaned_description'] = development_jobs['cleaned_description'].fillna('')
evaluation_jobs['cleaned_description'] = evaluation_jobs['cleaned_description'].fillna('')
resumes['cleaned_resume_text'] = resumes['cleaned_resume_text'].fillna('')
courses['cleaned_description'] = courses['cleaned_description'].fillna('')

# Create the modeling corpus
# Evaluation jobs are not included
model_corpus = pd.concat(
    [
        development_jobs['cleaned_description'],
        resumes['cleaned_resume_text'],
        courses['cleaned_description']
    ],
    ignore_index=True
)

# Create one shared TF-IDF vectorizer
vectorizer = TfidfVectorizer(
    stop_words='english',
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.95,
    sublinear_tf=True,
    token_pattern=r'(?u)(?<!\w)[.\w][\w+#./-]*(?!\w)'
)

# Fit the vectorizer only on the modeling corpus
vectorizer.fit(model_corpus)

# Transform development jobs
development_job_features = vectorizer.transform(development_jobs['cleaned_description'])

# Transform evaluation jobs using the same vectorizer
evaluation_job_features = vectorizer.transform(evaluation_jobs['cleaned_description'])

# Transform resumes using the same vectorizer
resume_features = vectorizer.transform(resumes['cleaned_resume_text'])

# Transform courses using the same vectorizer
course_features = vectorizer.transform(courses['cleaned_description']
)

# Save the fitted TF-IDF vectorizer
joblib.dump(vectorizer, f'{output_folder}/tfidf_vectorizer.pkl')

# Save TF-IDF matrices
save_npz(f'{output_folder}/development_jobs_tfidf.npz', development_job_features)
save_npz(f'{output_folder}/evaluation_jobs_tfidf.npz', evaluation_job_features)
save_npz(f'{output_folder}/resumes_tfidf.npz', resume_features)
save_npz(f'{output_folder}/courses_tfidf.npz', course_features)

# Create metadata for matrix row positions
development_metadata = pd.DataFrame(
    {
        'dataset': 'development_job',
        'row_index': range(len(development_jobs)),
        'record_id': development_jobs['job_id'].astype(str)
    }
)

evaluation_metadata = pd.DataFrame(
    {
        'dataset': 'evaluation_job',
        'row_index': range(len(evaluation_jobs)),
        'record_id': evaluation_jobs['job_id'].astype(str)
    }
)

resume_metadata = pd.DataFrame(
    {
        'dataset': 'resume',
        'row_index': range(len(resumes)),
        'record_id': resumes['resume_id'].astype(str)
    }
)

course_metadata = pd.DataFrame(
    {
        'dataset': 'course',
        'row_index': range(len(courses)),
        'record_id': courses['course_num'].astype(str)
    }
)

# Combine metadata into one table
feature_metadata = pd.concat(
    [
        development_metadata,
        evaluation_metadata,
        resume_metadata,
        course_metadata
    ],
    ignore_index=True
)

# Save matrix row information
feature_metadata.to_csv(f'{output_folder}/feature_metadata.csv', index=False)
