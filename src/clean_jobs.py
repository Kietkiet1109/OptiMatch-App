import html
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define input and output files
inputfile = '../data/raw/jobs.csv'
outputfile = '../data/processed/jobs_clean.csv'

# Read raw job data
jobs = pd.read_csv(inputfile)

# Check required columns
required_columns = ['job_id', 'job_title', 'company', 'category', 'description']
missing_columns = [column for column in required_columns if column not in jobs.columns]
if len(missing_columns) > 0:
    raise Exception(f'Missing required columns: {missing_columns}')

# Convert job IDs to strings
jobs['job_id'] = jobs['job_id'].astype(str)

# Convert publication date for sorting
if 'publication_date' in jobs.columns:
    jobs['publication_date_sort'] = pd.to_datetime(jobs['publication_date'])
    jobs = jobs.sort_values(by = 'publication_date_sort', ascending = False)

# Remove duplicate job IDs
jobs = jobs.drop_duplicates(subset = 'job_id', keep = 'first').copy()

# Preserve original description
jobs['raw_description'] = jobs['description'].fillna('').astype(str)

# Remove jobs without descriptions
jobs = jobs[jobs['raw_description'].str.strip().ne('')].copy()

# Convert HTML entities
jobs['cleaned_description'] = jobs['raw_description'].map(html.unescape)

# Remove HTML tags
jobs['cleaned_description'] = (jobs['cleaned_description']
                               .str.replace(r'<[^>]+>', ' ', regex = True))

# Remove URLs
jobs['cleaned_description'] = (jobs['cleaned_description']
                               .str.replace(r'https?://\S+|www\.\S+', ' ', regex = True))

# Define common page artifacts
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

# Remove page artifacts
for artifact in page_artifacts:
    jobs['cleaned_description'] = (jobs['cleaned_description']
                                   .str.replace(artifact, ' ', regex = True))

# Define common legal boilerplate
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

# Remove legal boilerplate
for boilerplate in legal_boilerplate:
    jobs['cleaned_description'] = (jobs['cleaned_description']
                                   .str.replace(boilerplate, ' ', regex = True))

# Convert description to lowercase
jobs['cleaned_description'] = jobs['cleaned_description'].str.lower()

# Remove unwanted characters while preserving technical punctuation
jobs['cleaned_description'] = (jobs['cleaned_description']
                               .str.replace(r'[^a-z0-9+#./\-\s]', ' ', regex = True))

# Normalize repeated whitespace
jobs['cleaned_description'] = (jobs['cleaned_description']
                               .str.replace(r'\s+', ' ', regex = True).str.strip())

# Remove descriptions that became empty
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

# Keep only the categories used by the project
categories = [
    'Computer and IT',
    'Data and Analytics',
    'Software Engineering',
    'Science and Engineering'
]
jobs = jobs[jobs['category'].isin(categories)].copy()

# Remove exact duplicate descriptions
jobs = jobs.drop_duplicates(subset = 'cleaned_description', keep = 'first').copy()

# Reset indexes before near-duplicate detection
jobs = jobs.reset_index(drop = True)

# Create TF-IDF vectors for duplicate detection
vectorizer = TfidfVectorizer(stop_words = 'english', ngram_range = (1, 2), min_df = 1)
job_vectors = vectorizer.fit_transform(jobs['cleaned_description'])

# Calculate similarity between job descriptions
similarity_matrix = cosine_similarity(job_vectors)

# Define near-duplicate threshold
similarity_threshold = 0.90

# Store near-duplicate indexes
near_duplicate_indexes = set()

# Compare job descriptions
for first_index in range(len(jobs)):
    if first_index in near_duplicate_indexes:
        continue

    for second_index in range(first_index + 1, len(jobs)):
        if second_index in near_duplicate_indexes:
            continue

        similarity = similarity_matrix[first_index, second_index]
        if similarity >= similarity_threshold:
            near_duplicate_indexes.add(second_index)

# Remove near-duplicate jobs
jobs = jobs.drop(index = list(near_duplicate_indexes)).copy()

# Reset indexes before CS relevance filtering
jobs = jobs.reset_index(drop = True)

# Define strong CS-related job titles
cs_title_patterns = [
    r'\bsoftware engineer\b',
    r'\bsoftware developer\b',
    r'\bsoftware architect\b',
    r'\bsoftware development\b',
    r'\bfrontend developer\b',
    r'\bfront-end developer\b',
    r'\bfrontend engineer\b',
    r'\bfront-end engineer\b',
    r'\bbackend developer\b',
    r'\bback-end developer\b',
    r'\bbackend engineer\b',
    r'\bback-end engineer\b',
    r'\bfull stack\b',
    r'\bfull-stack\b',
    r'\bweb developer\b',
    r'\bmobile developer\b',
    r'\bmobile engineer\b',
    r'\bdata scientist\b',
    r'\bdata engineer\b',
    r'\bdata analyst\b',
    r'\bdata architect\b',
    r'\bmachine learning engineer\b',
    r'\bml engineer\b',
    r'\bai engineer\b',
    r'\bartificial intelligence engineer\b',
    r'\bcomputer vision engineer\b',
    r'\bdevops\b',
    r'\bsite reliability engineer\b',
    r'\bplatform engineer\b',
    r'\bcloud engineer\b',
    r'\bcloud architect\b',
    r'\bsecurity engineer\b',
    r'\bsecurity analyst\b',
    r'\bcybersecurity\b',
    r'\bnetwork engineer\b',
    r'\bnetwork administrator\b',
    r'\bsystems administrator\b',
    r'\bsystem administrator\b',
    r'\bdatabase administrator\b',
    r'\bit support\b',
    r'\btechnical support engineer\b',
    r'\bhelp desk\b',
    r'\bbusiness intelligence\b',
    r'\bqa engineer\b',
    r'\btest automation\b',
    r'\bfirmware engineer\b',
    r'\bembedded software\b',
    r'\bresearch software engineer\b'
]

# Combine CS title patterns
cs_title_pattern = '|'.join(cs_title_patterns)

# Detect strong CS-related titles
jobs['cs_title_match'] = (jobs['job_title'].fillna('')
                          .str.contains(cs_title_pattern,
                                        case = False, regex = True))

# Define clearly non-CS job titles
non_cs_title_patterns = [
    r'\bproduce associate\b',
    r'\bretail\b',
    r'\bbanker\b',
    r'\bteller\b',
    r'\btire\b',
    r'\bbattery service\b',
    r'\bsales associate\b',
    r'\bstore manager\b',
    r'\bmechanical engineer\b',
    r'\bthermal engineer\b',
    r'\bcivil engineer\b',
    r'\bchemical engineer\b',
    r'\bmanufacturing engineer\b',
    r'\bstructural engineer\b',
    r'\bgeotechnical\b',
    r'\bsubstation\b',
    r'\bpower systems engineer\b',
    r'\belectrical field engineer\b',
    r'\bconstruction engineer\b',
    r'\bhvac\b',
    r'\bmagnetics\b'
]

# Combine non-CS title patterns
non_cs_title_pattern = '|'.join(non_cs_title_patterns)

# Detect clearly non-CS titles
jobs['non_cs_title_match'] = (jobs['job_title'].fillna('')
                              .str.contains(non_cs_title_pattern,
                                            case = False, regex = True))

# Define CS-related description concepts
cs_description_patterns = [
    r'\bsoftware development\b',
    r'\bsoftware engineering\b',
    r'\bprogramming\b',
    r'\bsource code\b',
    r'\bcoding\b',
    r'\bfrontend\b',
    r'\bbackend\b',
    r'\bfull stack\b',
    r'\bweb application\b',
    r'\bmobile application\b',
    r'\bapi\b',
    r'\bmicroservices\b',
    r'\bdatabase\b',
    r'\bsql\b',
    r'\bdata analysis\b',
    r'\bdata analytics\b',
    r'\bdata engineering\b',
    r'\bdata pipeline\b',
    r'\betl\b',
    r'\bmachine learning\b',
    r'\bartificial intelligence\b',
    r'\bdeep learning\b',
    r'\bcloud computing\b',
    r'\bcloud infrastructure\b',
    r'\bdevops\b',
    r'\bci/cd\b',
    r'\bdocker\b',
    r'\bkubernetes\b',
    r'\bcybersecurity\b',
    r'\bnetwork security\b',
    r'\bnetwork administration\b',
    r'\bsystem administration\b',
    r'\bversion control\b',
    r'\bgit\b',
    r'\bunit testing\b',
    r'\btest automation\b',
    r'\bdistributed systems\b',
    r'\bbusiness intelligence\b',
    r'\bdata visualization\b'
]

# Count CS-related concepts in each description
jobs['cs_description_count'] = 0
for pattern in cs_description_patterns:
    jobs['cs_description_count'] += (jobs['cleaned_description']
                                     .str.contains(pattern, case = False, regex = True)
                                     .astype(int))

# Define common non-CS description concepts
non_cs_description_patterns = [
    r'\bthermal design\b',
    r'\bheat transfer\b',
    r'\bmechanical design\b',
    r'\bfinite element\b',
    r'\bmanufacturing process\b',
    r'\bproduction line\b',
    r'\bsubstation\b',
    r'\btransformer\b',
    r'\bhigh voltage\b',
    r'\bpower distribution\b',
    r'\bhvac\b',
    r'\bcivil engineering\b',
    r'\bconstruction management\b',
    r'\bstructural design\b',
    r'\bretail sales\b',
    r'\bcustomer service\b',
    r'\bbanking services\b',
    r'\bprocurement\b',
    r'\bsupply chain\b'
]

# Count non-CS concepts in each description
jobs['non_cs_description_count'] = 0
for pattern in non_cs_description_patterns:
    jobs['non_cs_description_count'] += (jobs['cleaned_description']
                                         .str.contains(pattern, case = False, regex = True)
                                         .astype(int))

# Identify ambiguous titles with strong CS description evidence
cs_description_match = (jobs['cs_description_count'].ge(2)
                        & jobs['cs_description_count']
                        .gt(jobs['non_cs_description_count']))

# Allow very strong CS descriptions to override a broad non-CS title
strong_cs_description_match = (jobs['cs_description_count'].ge(4)
                               & jobs['cs_description_count']
                               .ge(jobs['non_cs_description_count'] + 2))

# Keep jobs that are reasonably CS-related
jobs['cs_related'] = (jobs['cs_title_match']
                      | (~jobs['non_cs_title_match'] & cs_description_match)
                      | (jobs['non_cs_title_match'] & strong_cs_description_match))

# Keep only CS-related jobs
jobs = jobs[jobs['cs_related']].copy()

# Remove temporary columns
temporary_columns = [
    'description',
    'publication_date_sort',
    'cs_title_match',
    'non_cs_title_match',
    'cs_description_count',
    'non_cs_description_count',
    'cs_related'
]
temporary_columns = [column for column in temporary_columns if column in jobs.columns]
jobs = jobs.drop(columns = temporary_columns)

# Define final column order
column_order = [
    'job_id',
    'job_title',
    'company',
    'category',
    'job_level',
    'location',
    'raw_description',
    'cleaned_description',
    'publication_date',
    'job_url'
]

# Keep final columns
jobs = jobs[column_order]

# Reset final indexes
jobs = jobs.reset_index(drop = True)

# Save the cleaned jobs data
jobs.to_csv(outputfile, index = False)
