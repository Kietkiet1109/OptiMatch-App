import pandas as pd

# Define input and output file paths
inputfile = '../data/processed/jobs_clean.csv'
outputfile = '../data/evaluation/jobs_split.csv'

# Define random seed and evaluation size
random_seed = 353
evaluation_per_category = 5

# Read cleaned job data
jobs = pd.read_csv(inputfile)

# Check that required columns exist
required_columns = ['job_id', 'job_title', 'category']
missing_columns = [column for column in required_columns if column not in jobs.columns]
if len(missing_columns) > 0:
    raise Exception(f'Missing required columns: {missing_columns}')

# Get the number of jobs in each category
category_counts = jobs['category'].value_counts()

# Make sure every category has at least 5 jobs
if (category_counts < evaluation_per_category).any():
    raise Exception('Not enough jobs in one or more categories')

# Randomly select 5 evaluation jobs from each category
evaluation_jobs = (jobs.groupby('category', group_keys = False)
                   .sample(n = evaluation_per_category, random_state = random_seed))

# Create development and evaluation labels
jobs['split'] = 'development'
jobs.loc[jobs['job_id'].isin(evaluation_jobs['job_id']), 'label'] = 'evaluation'

# Keep only information needed for the split
job_split = jobs[['job_id', 'job_title', 'category', 'label']].copy()

# Sort the split file for easier inspection
job_split = job_split.sort_values(by = ['category', 'label', 'job_id']).reset_index(drop=True)

# Save only the split information
job_split.to_csv(outputfile, index=False)
