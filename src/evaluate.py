import pandas as pd

# Define input file paths
labels_file = '../data/evaluation/human_labels.csv'
baseline_file = '../outputs/tables/baseline_results.csv'
gap_file = '../outputs/gaps/gap_results.csv'

# Define output file path
outputfile = f'../outputs/evaluation/evaluation_results.csv'

# Read human labels and model results
human_labels = pd.read_csv(labels_file)
baseline_results = pd.read_csv(baseline_file)
gap_results = pd.read_csv(gap_file)

# Convert IDs to strings
human_labels['job_id'] = human_labels['job_id'].astype(str)
human_labels['resume_id'] = human_labels['resume_id'].astype(str)
baseline_results['job_id'] = baseline_results['job_id'].astype(str)
baseline_results['resume_id'] = baseline_results['resume_id'].astype(str)
gap_results['job_id'] = gap_results['job_id'].astype(str)
gap_results['resume_id'] = gap_results['resume_id'].astype(str)

# Check that all human labels were completed
if human_labels['human_missing_skills'].isna().any():
    raise Exception('Some human labels are missing')

# Keep baseline predictions needed for evaluation
baseline_predictions = baseline_results[['job_id', 'resume_id', 'missing_skills']].copy()

# Rename baseline prediction column
baseline_predictions = baseline_predictions.rename(
    columns={'missing_skills': 'baseline_missing_skills'}
)

# Keep TF-IDF predictions needed for evaluation
tfidf_predictions = gap_results[['job_id', 'resume_id', 'top_gap_skills']].copy()

# Merge human labels with baseline predictions
evaluation = human_labels.merge(
    baseline_predictions,
    on=['job_id', 'resume_id'],
    how='left',
)

# Treat empty baseline predictions as no missing skills
evaluation['baseline_missing_skills'] = evaluation['baseline_missing_skills'].fillna('')

# Merge TF-IDF predictions
evaluation = evaluation.merge(
    tfidf_predictions,
    on=['job_id', 'resume_id'],
    how='left'
)

# Check that predictions were found
if evaluation['baseline_missing_skills'].isna().any():
    raise Exception('Some baseline predictions are missing')

if evaluation['top_gap_skills'].isna().any():
    evaluation['top_gap_skills'] = evaluation['top_gap_skills'].fillna('')

# Create lists for evaluation metrics
baseline_precision = []
baseline_recall = []
baseline_jaccard = []

tfidf_precision_3 = []
tfidf_recall_3 = []
tfidf_precision_5 = []
tfidf_recall_5 = []
tfidf_jaccard_5 = []

baseline_relevant_count = []
tfidf_relevant_count = []

# Evaluate each held-out resume-job pair
for index, row in evaluation.iterrows():

    # Convert human labels to a normalized set
    human_skills = set()
    for skill in str(row['human_missing_skills']).split(','):
        if skill.strip() != '':
            human_skills.add(skill.strip().lower())

    # Convert baseline predictions to a set
    baseline_skills = set()
    for skill in str(row['baseline_missing_skills']).split(','):
        if skill.strip() != '':
            baseline_skills.add(skill.strip().lower())

    # Convert ranked TF-IDF predictions to a list
    tfidf_skills = list()
    for skill in str(row['top_gap_skills']).split(','):
        if skill.strip() != '':
            tfidf_skills.append(skill.strip().lower())

    # Get top 3 and top 5 TF-IDF skills
    tfidf_top_3 = tfidf_skills[:3]
    tfidf_top_5 = tfidf_skills[:5]

    # Find correct baseline predictions
    baseline_correct = baseline_skills & human_skills

    # Calculate baseline precision
    if len(baseline_skills) > 0:
        current_precision = len(baseline_correct) / len(baseline_skills)
    else:
        current_precision = 0

    # Calculate baseline recall
    if len(human_skills) > 0:
        current_recall = len(baseline_correct) / len(human_skills)
    else:
        current_recall = 0

    # Calculate baseline Jaccard similarity
    baseline_union = baseline_skills | human_skills

    if len(baseline_union) > 0:
        current_jaccard = len(baseline_correct) / len(baseline_union)
    else:
        current_jaccard = 0

    baseline_precision.append(current_precision)
    baseline_recall.append(current_recall)
    baseline_jaccard.append(current_jaccard)
    baseline_relevant_count.append(len(baseline_correct))

    # Find correct TF-IDF top 3 predictions
    tfidf_correct_3 = set(tfidf_top_3) & human_skills

    # Calculate TF-IDF Precision@3
    if len(tfidf_top_3) > 0:
        current_precision_3 = len(tfidf_correct_3) / len(tfidf_top_3)
    else:
        current_precision_3 = 0

    # Calculate TF-IDF Recall@3
    if len(human_skills) > 0:
        current_recall_3 = len(tfidf_correct_3) / len(human_skills)
    else:
        current_recall_3 = 0

    tfidf_precision_3.append(current_precision_3)
    tfidf_recall_3.append(current_recall_3)

    # Find correct TF-IDF top 5 predictions
    tfidf_correct_5 = set(tfidf_top_5) & human_skills

    # Calculate TF-IDF Precision@5
    if len(tfidf_top_5) > 0:
        current_precision_5 = len(tfidf_correct_5) / len(tfidf_top_5)
    else:
        current_precision_5 = 0

    # Calculate TF-IDF Recall@5
    if len(human_skills) > 0:
        current_recall_5 = len(tfidf_correct_5) / len(human_skills)
    else:
        current_recall_5 = 0

    # Calculate TF-IDF Jaccard@5
    tfidf_union_5 = set(tfidf_top_5) | human_skills

    if len(tfidf_union_5) > 0:
        current_jaccard_5 = len(tfidf_correct_5) / len(tfidf_union_5)
    else:
        current_jaccard_5 = 0

    tfidf_precision_5.append(current_precision_5)
    tfidf_recall_5.append(current_recall_5)
    tfidf_jaccard_5.append(current_jaccard_5)
    tfidf_relevant_count.append(len(tfidf_correct_5))

# Add evaluation metrics to dataframe
evaluation['baseline_precision'] = baseline_precision
evaluation['baseline_recall'] = baseline_recall
evaluation['baseline_jaccard'] = baseline_jaccard
evaluation['baseline_relevant_count'] = baseline_relevant_count
evaluation['tfidf_precision_3'] = tfidf_precision_3
evaluation['tfidf_recall_3'] = tfidf_recall_3
evaluation['tfidf_precision_5'] = tfidf_precision_5
evaluation['tfidf_recall_5'] = tfidf_recall_5
evaluation['tfidf_jaccard_5'] = tfidf_jaccard_5
evaluation['tfidf_relevant_count'] = tfidf_relevant_count

# Save detailed evaluation results
evaluation.to_csv(outputfile, index = False)
