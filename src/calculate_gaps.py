import joblib
import pandas as pd
from scipy.sparse import load_npz
from scipy.sparse import save_npz
from scipy.sparse import vstack
from sklearn.metrics.pairwise import cosine_similarity
from extract_skills import get_skill_set

# Define input file paths
jobs_file = '../data/processed/jobs_clean.csv'
baseline_file = '../outputs/tables/baseline_results.csv'
metadata_file = '../outputs/features/feature_metadata.csv'
tech_skills_file = '../config/technical_skills.json'
vectorizer_file = '../outputs/features/tfidf_vectorizer.pkl'
development_file = '../outputs/features/development_jobs_tfidf.npz'
evaluation_file = '../outputs/features/evaluation_jobs_tfidf.npz'
resumes_file = '../outputs/features/resumes_tfidf.npz'

# Define output file paths
output_folder = '../outputs/gaps'
result_file = f'{output_folder}/gap_results.csv'
gap_file = f'{output_folder}/gap_vectors.npz'

# Define number of gap skills to display
top_k = 5

# Read cleaned job data
jobs = pd.read_csv(jobs_file)

# Convert job IDs to strings
jobs['job_id'] = jobs['job_id'].astype(str)

# Create job lookup table
jobs_lookup = jobs.set_index('job_id')

# Read baseline results
baseline_results = pd.read_csv(baseline_file)

# Convert baseline IDs to strings
baseline_results['job_id'] = baseline_results['job_id'].astype(str)
baseline_results['resume_id'] = baseline_results['resume_id'].astype(str)

# Read feature metadata
feature_metadata = pd.read_csv(metadata_file)

# Convert record IDs to strings
feature_metadata['record_id'] = feature_metadata['record_id'].astype(str)

# Get development job metadata
development_metadata = feature_metadata[feature_metadata['dataset'] == 'development_job']
development_metadata = development_metadata.sort_values(by = 'row_index').reset_index(drop = True)

# Add development label
development_metadata['split'] = 'development'

# Get evaluation job metadata
evaluation_metadata = feature_metadata[feature_metadata['dataset'] == 'evaluation_job']
evaluation_metadata = evaluation_metadata.sort_values(by = 'row_index').reset_index(drop = True)

# Add evaluation label
evaluation_metadata['split'] = 'evaluation'

# Get resume metadata
resume_metadata = feature_metadata[feature_metadata['dataset'] == 'resume']
resume_metadata = resume_metadata.sort_values(by = 'row_index').reset_index(drop = True)

# Load the fitted TF-IDF vectorizer
vectorizer = joblib.load(vectorizer_file)

# Get TF-IDF feature names
feature_names = vectorizer.get_feature_names_out()

# Load TF-IDF matrices
development_features = load_npz(development_file)
evaluation_features = load_npz(evaluation_file)
resume_features = load_npz(resumes_file)

# Combine development and evaluation job matrices
job_features = vstack([development_features, evaluation_features]).tocsr()

# Combine job metadata in the same order
job_metadata = pd.concat([development_metadata, evaluation_metadata], ignore_index=True)

# Check that matrix rows match metadata rows
if job_features.shape[0] != len(job_metadata):
    raise Exception('Job feature rows do not match job metadata')

if resume_features.shape[0] != len(resume_metadata):
    raise Exception('Resume feature rows do not match resume metadata')

# Get technical skills set
technical_skills = get_skill_set()

# Calculate cosine similarity for every job-resume pair
similarity_matrix = cosine_similarity(job_features, resume_features)

# Create lists for gap results and vectors
gap_results = []
gap_vectors = []

# Compare every job with every resume
for job_index in range(job_features.shape[0]):

    # Get current job information
    job_id = job_metadata.loc[job_index, 'record_id']
    job_split = job_metadata.loc[job_index, 'split']
    job_description = jobs_lookup.loc[job_id, 'cleaned_description']
    job_description = str(job_description)

    # Compare current job with every resume
    for resume_index in range(resume_features.shape[0]):

        # Get current resume ID
        resume_id = resume_metadata.loc[resume_index, 'record_id']

        # Calculate non-negative gap vector
        gap_vector = (job_features[job_index] - resume_features[resume_index]).tocsr()

        # Replace negative gap values with zero
        gap_vector.data[gap_vector.data < 0] = 0

        # Remove stored zero values
        gap_vector.eliminate_zeros()

        # Save gap vector for Stage 10
        gap_row_index = len(gap_vectors)
        gap_vectors.append(gap_vector)

        # Find technical features with positive gaps
        technical_gaps = []

        for feature_index, gap_weight in zip(gap_vector.indices, gap_vector.data):
            feature_name = feature_names[feature_index]
            if feature_name in technical_skills:
                technical_gaps.append((feature_name, float(gap_weight)))

        # Sort technical gaps by TF-IDF gap weight
        technical_gaps = sorted(technical_gaps, key=lambda item: item[1], reverse=True)

        # Count all technical gap skills
        technical_gap_count = len(technical_gaps)

        # Keep only the highest-weight gap skills
        top_gaps = technical_gaps[:top_k]

        # Create readable skill list
        top_gap_skills = [skill for skill, weight in top_gaps]

        # Create readable skill-weight list
        top_gap_weights = [f'{skill}:{weight:.4f}' for skill, weight in top_gaps]

        # Find evidence around each gap skill
        evidence = []

        for skill, weight in top_gaps:
            skill_position = job_description.lower().find(skill)

            if skill_position >= 0:
                evidence_start = max(0, skill_position - 60)

                evidence_end = min(len(job_description), skill_position + len(skill) + 60)

                evidence_text = job_description[evidence_start:evidence_end].strip()

                evidence.append(f'{skill}: {evidence_text}')

        # Store gap result
        gap_results.append(
            {
                'gap_row_index': gap_row_index,
                'job_id': job_id,
                'resume_id': resume_id,
                'split': job_split,
                'cosine_similarity': round(similarity_matrix[job_index, resume_index], 4),
                'technical_gap_count': technical_gap_count,
                'top_gap_skills': ', '.join(top_gap_skills),
                'top_gap_weights': ', '.join(top_gap_weights),
                'job_evidence': ' | '.join(evidence)
            }
        )

# Combine all gap vectors into one sparse matrix
gap_vectors = vstack(gap_vectors).tocsr()

# Convert gap results to dataframe
gap_results = pd.DataFrame(gap_results)

# Keep baseline information needed for comparison
baseline_summary = baseline_results[
    [
        'job_id',
        'resume_id',
        'jaccard_similarity',
        'skill_coverage',
        'shared_skills',
        'missing_skills'
    ]
].copy()

# Rename baseline columns clearly
baseline_summary = baseline_summary.rename(
    columns={
        'jaccard_similarity': 'baseline_jaccard',
        'skill_coverage': 'baseline_skill_coverage',
        'shared_skills': 'baseline_shared_skills',
        'missing_skills':'baseline_missing_skills'
    }
)

# Add baseline information to TF-IDF results
gap_results = gap_results.merge(baseline_summary, on=['job_id', 'resume_id'], how='left')

# Add job title and category
job_information = jobs[
    [
        'job_id',
        'job_title',
        'category'
    ]
].copy()

gap_results = gap_results.merge(job_information, on='job_id', how='left')

# Put important columns first
gap_results = gap_results[
    [
        'gap_row_index',
        'job_id',
        'job_title',
        'category',
        'resume_id',
        'split',
        'cosine_similarity',
        'baseline_jaccard',
        'baseline_skill_coverage',
        'baseline_shared_skills',
        'baseline_missing_skills',
        'technical_gap_count',
        'top_gap_skills',
        'top_gap_weights',
        'job_evidence'
    ]
]

# Save gap results
gap_results.to_csv(result_file, index=False)

# Save full gap vectors
save_npz(gap_file, gap_vectors)
