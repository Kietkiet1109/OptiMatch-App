import pandas as pd

# Define input file paths
jobs_file = '../data/processed/jobs_clean.csv'
resumes_file = '../data/processed/resumes_clean.csv'
split_file = '../data/evaluation/jobs_split.csv'

# Define output file path
outputfile = f'../data/evaluation/human_labels.csv'

# Define random seed
random_seed = 353

# Read cleaned data
jobs = pd.read_csv(jobs_file)
resumes = pd.read_csv(resumes_file)
job_split = pd.read_csv(split_file)

# Convert IDs to strings
jobs['job_id'] = jobs['job_id'].astype(str)
job_split['job_id'] = job_split['job_id'].astype(str)
resumes['resume_id'] = resumes['resume_id'].astype(str)

# Get the held-out evaluation jobs
evaluation_ids = job_split[job_split['label'] == 'evaluation']['job_id']
evaluation_jobs = jobs[jobs['job_id'].isin(evaluation_ids)].copy()

# Sort evaluation jobs for reproducibility
evaluation_jobs = evaluation_jobs.sort_values(by = 'job_id').reset_index(drop = True)

# Select one different resume for each evaluation job
evaluation_resumes = (resumes.sample(n = len(evaluation_jobs), random_state = random_seed)
                      .reset_index(drop = True))

# Create evaluation pairs
evaluation_pairs = pd.DataFrame(
    {
        'job_id': evaluation_jobs['job_id'],
        'job_title': evaluation_jobs['job_title'],
        'category': evaluation_jobs['category'],
        'resume_id': evaluation_resumes['resume_id'],
        'job_description': evaluation_jobs['cleaned_description'],
        'resume_text': evaluation_resumes['cleaned_resume_text']
    }
)

# Create empty column for manual labels
evaluation_pairs['human_missing_skills'] = ''

# Save evaluation pairs for manual annotation
evaluation_pairs.to_csv(outputfile, index = False)
