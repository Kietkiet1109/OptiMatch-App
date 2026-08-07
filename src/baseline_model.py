import os
import re
import pandas as pd
from extract_skills import get_skill_pattern, extract_skills

# Define input and output file paths
jobs_file = '../data/processed/jobs_clean.csv'
resumes_file = '../data/processed/resumes_clean.csv'
outputfile = '../outputs/tables/baseline_results.csv'

# Read cleaned job and resume data
jobs = pd.read_csv(jobs_file)
resumes = pd.read_csv(resumes_file)

# Create regular expression patterns for each skill
skill_patterns = get_skill_pattern()

# Extract technical skills from every job description
job_skills = []
for job_description in jobs['cleaned_description']:
    current_skills = extract_skills(job_description, skill_patterns)
    job_skills.append(current_skills)

# Add extracted skills to job data
jobs['job_skills'] = job_skills

# Extract technical skills from every resume
resume_skills = []
for resume_text in resumes['cleaned_resume_text']:
    current_skills = extract_skills(resume_text, skill_patterns)
    resume_skills.append(current_skills)

# Add extracted skills to resume data
resumes['resume_skills'] = resume_skills

# Create a list for all resume-job comparison results
baseline_results = []

# Compare every resume with every job
for job_index, job in jobs.iterrows():

    for resume_index, resume in resumes.iterrows():

        current_job_skills = job['job_skills']
        current_resume_skills = resume['resume_skills']

        # Find skills appearing in both job and resume
        shared_skills = current_job_skills & current_resume_skills

        # Find job skills missing from the resume
        missing_skills = current_job_skills - current_resume_skills

        # Find all unique skills across job and resume
        union_skills = current_job_skills | current_resume_skills

        # Calculate Jaccard similarity
        if len(union_skills) > 0:
            jaccard_similarity = len(shared_skills) / len(union_skills)
        else:
            jaccard_similarity = 0

        # Calculate job-skill coverage
        if len(current_job_skills) > 0:
            skill_coverage = len(shared_skills) / len(current_job_skills)
        else:
            skill_coverage = 0

        # Store the baseline result
        baseline_results.append(
            {
                'job_id': job['job_id'],
                'job_title': job['job_title'],
                'job_category': job['category'],
                'resume_id': resume['resume_id'],
                'job_skill_count': len(current_job_skills),
                'resume_skill_count': len(current_resume_skills),
                'shared_skill_count': len(shared_skills),
                'missing_skill_count': len(missing_skills),
                'job_skills': ', '.join(sorted(current_job_skills)),
                'resume_skills': ', '.join(sorted(current_resume_skills)),
                'shared_skills': ', '.join(sorted(shared_skills)),
                'missing_skills': ', '.join(sorted(missing_skills)),
                'jaccard_similarity': round(jaccard_similarity, 4),
                'skill_coverage': round(skill_coverage, 4)
            }
        )

# Convert all baseline results to a dataframe
baseline_results = pd.DataFrame(baseline_results)

# Sort results by job and skill coverage
baseline_results = baseline_results.sort_values(
    by=['job_id', 'skill_coverage', 'jaccard_similarity'],
    ascending=[True, False, False]
).reset_index(drop=True)

# Save the baseline results
baseline_results.to_csv(outputfile, index=False)
