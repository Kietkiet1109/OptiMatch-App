import joblib
import numpy as np
import pandas as pd
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

# Define input file paths
courses_file = '../data/processed/courses_clean.csv'
metadata_file = '../outputs/features/feature_metadata.csv'
vectorizer_file = '../outputs/features/tfidf_vectorizer.pkl'
course_features_file = '../outputs/features/courses_tfidf.npz'
gap_results_file = '../outputs/gaps/gap_results.csv'
gap_vectors_file = '../outputs/gaps/gap_vectors.npz'

# Define output file path
outputfile = f'../outputs/recommendations/course_recommendations.csv'

# Define recommendation settings
top_k = 5
minimum_similarity = 0.01
matching_term_count = 5

# Read cleaned course data
courses = pd.read_csv(courses_file)

# Convert course numbers to strings
courses['course_num'] = courses['course_num'].astype(str)

# Fill missing course information
courses['course_name'] = courses['course_name'].fillna('')
courses['cleaned_description'] = courses['cleaned_description'].fillna('')
courses['prerequisites'] = courses['prerequisites'].fillna('')

# Create course lookup table
courses_lookup = courses.set_index('course_num')

# Read feature metadata
feature_metadata = pd.read_csv(metadata_file)

# Convert record IDs to strings
feature_metadata['record_id'] = feature_metadata['record_id'].astype(str)

# Get course metadata in matrix row order
course_metadata = (feature_metadata[feature_metadata['dataset'] == 'course']
                   .sort_values(by = 'row_index').reset_index(drop = True))

# Read gap result information
gap_results = pd.read_csv(gap_results_file)

# Sort gap results to match gap vector rows
gap_results = gap_results.sort_values(by = 'gap_row_index').reset_index(drop = True)

# Load the fitted TF-IDF vectorizer
vectorizer = joblib.load(vectorizer_file)

# Get shared TF-IDF feature names
feature_names = vectorizer.get_feature_names_out()

# Load course and gap feature matrices
course_features = load_npz(course_features_file)
gap_vectors = load_npz(gap_vectors_file)

# Check course matrix alignment
if course_features.shape[0] != len(course_metadata):
    raise Exception('Course feature rows do not match course metadata')

# Check gap matrix alignment
if gap_vectors.shape[0] != len(gap_results):
    raise Exception('Gap vector rows do not match gap results')

# Check that course and gap features use the same vocabulary
if course_features.shape[1] != gap_vectors.shape[1]:
    raise Exception('Course and gap feature dimensions do not match')

# Calculate similarity between every gap and every course
course_similarity = cosine_similarity(gap_vectors, course_features)

# Create list for recommendation results
recommendations = []

# Process every resume-job gap
for gap_index in range(gap_vectors.shape[0]):

    # Get current resume-job information
    job_id = gap_results.loc[gap_index, 'job_id']
    resume_id = gap_results.loc[gap_index, 'resume_id']
    job_title = gap_results.loc[gap_index, 'job_title']
    job_category = gap_results.loc[gap_index, 'category']
    split = gap_results.loc[gap_index, 'split']
    top_gap_skills = gap_results.loc[gap_index, 'top_gap_skills']

    # Rank courses by similarity
    ranked_courses = np.argsort(course_similarity[gap_index])[::-1]

    # Count valid recommendations
    recommendation_rank = 0

    # Check courses from highest to lowest similarity
    for course_index in ranked_courses:

        similarity = course_similarity[gap_index, course_index]

        # Skip courses with negligible overlap
        if similarity < minimum_similarity:
            continue

        # Stop after reaching the top k courses
        if recommendation_rank >= top_k:
            break

        # Get current course number
        course_num = course_metadata.loc[course_index, 'record_id']

        # Skip course if metadata cannot be found
        if course_num not in courses_lookup.index:
            continue

        # Get current course information
        course_name = courses_lookup.loc[course_num, 'course_name']
        course_description = courses_lookup.loc[course_num, 'cleaned_description']
        prerequisites = courses_lookup.loc[course_num, 'prerequisites']

        # Find features contributing to the similarity
        matching_vector = gap_vectors[gap_index].multiply(course_features[course_index])

        # Create matching term list
        matching_terms = []

        # Keep highest contribution terms
        if matching_vector.nnz > 0:

            term_order = np.argsort(matching_vector.data)[::-1]
            term_order = term_order[:matching_term_count]

            for term_position in term_order:

                feature_index = matching_vector.indices[term_position]

                matching_terms.append(feature_names[feature_index])

        # Increase recommendation rank
        recommendation_rank += 1

        # Store recommendation
        recommendations.append(
            {
                'job_id': job_id,
                'job_title': job_title,
                'job_category': job_category,
                'resume_id': resume_id,
                'split': split,
                'top_gap_skills': top_gap_skills,
                'rank': recommendation_rank,
                'course_num': course_num,
                'course_name': course_name,
                'course_similarity': round(similarity, 4),
                'matching_terms': ', '.join(matching_terms),
                'course_description': course_description,
                'prerequisites': prerequisites
            }
        )

# Convert recommendations to dataframe
recommendations = pd.DataFrame(recommendations)

# Sort recommendations
recommendations = (recommendations.sort_values(by = ['job_id', 'resume_id', 'rank'])
                   .reset_index(drop = True))

# Save course recommendations
recommendations.to_csv(outputfile, index = False)
