import html
import pandas as pd


# Define input and output file paths
inputfile = '../data/raw/courses.csv'
outputfile = '../data/processed/courses_clean.csv'

# Read the raw course data
courses = pd.read_csv(inputfile)

# Check that all required columns exist
required_columns = ['course_num', 'course_name', 'description']
missing_columns = [column for column in required_columns if column not in courses.columns]
if len(missing_columns) > 0:
    raise Exception(f'Missing required columns: {missing_columns}')

# Normalize course numbers
courses['course_num'] = courses['course_num'].fillna('').astype(str)
courses['course_num'] = courses['course_num'].str.upper()
courses['course_num'] = (courses['course_num']
                         .str.replace(r'\s+', ' ', regex=True)
                         .str.strip())

# Convert HTML entities in course names
courses['course_name'] = courses['course_name'].fillna('').astype(str).map(html.unescape)

# Remove HTML tags from course names
courses['course_name'] = (courses['course_name']
                          .str.replace(r'<[^>]+>', ' ', regex=True))

# Remove the credit value from course names
courses['course_name'] = (courses['course_name']
                          .str.replace(r'\s*\(\d+\)\s*$', '', regex=True))

# Normalize whitespace in course names
courses['course_name'] = (courses['course_name']
                          .str.replace(r'\s+', ' ', regex=True)
                          .str.strip())

# Preserve the original course description
courses['raw_description'] = courses['description']

# Remove rows without course descriptions
courses = courses[courses['raw_description'].notna()].copy()
courses['raw_description'] = courses['raw_description'].astype(str)
courses = courses[courses['raw_description'].str.strip().ne('')].copy()

# Convert HTML entities in course descriptions
courses['cleaned_description'] = courses['raw_description'].map(html.unescape)

# Remove HTML tags from course descriptions
courses['cleaned_description'] = (courses['cleaned_description']
                                  .str.replace(r'<[^>]+>', ' ', regex=True))

# Remove common HTML whitespace artifacts
courses['cleaned_description'] = (courses['cleaned_description']
                                  .str.replace(r'&nbsp;',' ', regex=True))

# Normalize whitespace in course descriptions
courses['cleaned_description'] = (courses['cleaned_description']
                                  .str.replace(r'\s+', ' ', regex=True).str.strip())

# Extract prerequisites into a separate column
courses['prerequisites'] = (courses['cleaned_description']
                            .str.extract(r'(?i)\bprerequisite:\s*([^.]*)'))
courses['prerequisites'] = courses['prerequisites'].fillna('').str.strip()

# Remove duplicate course numbers
courses = courses.drop_duplicates(subset='course_num', keep='first').copy()

# Define special course title words
special_pattern = (
    r'\b(?:special topics|project|projects|practicum|'
    r'co-op|internship|thesis|portfolio|directed|extended)\b'
)

# Remove special courses unavailable to normal students
courses = courses[~courses['course_name'].str.contains(
    special_pattern, case=False, regex=True, na=False)].copy()

# Define courses not offered during the last two years
unoffered_courses = [
    'CMPT 102',
    'CMPT 106',
    'CMPT 110',
    'CMPT 115',
    'CMPT 128',
    'CMPT 129',
    'CMPT 165',
    'CMPT 166',
    'CMPT 275',
    'CMPT 300',
    'CMPT 320'
]

# Remove unoffered courses
courses = courses[~courses['course_num'].isin(unoffered_courses)].copy()

# Define graduate courses cross-listed with undergraduate courses
cross_listed_courses = [
    'CMPT 710',
    'CMPT 713',
    'CMPT 721',
    'CMPT 726',
    'CMPT 728',
    'CMPT 750',
    'CMPT 762',
    'CMPT 764',
    'CMPT 766',
    'CMPT 767',
    'CMPT 769',
    'CMPT 776',
    'CMPT 777',
    'CMPT 800',
    'CMPT 827'
]

# Remove cross-listed graduate courses
courses = courses[~courses['course_num'].isin(cross_listed_courses)].copy()

# Remove rows that became empty after cleaning
courses = courses[courses['cleaned_description'].str.strip().ne('')].copy()

# Remove the original description column
courses = courses.drop(columns=['description'])

# Keep the final columns in a clear order
courses = courses[
    [
        'course_num',
        'course_name',
        'raw_description',
        'cleaned_description',
        'prerequisites'
    ]
]


# Sort courses by course number
courses = courses.sort_values(by='course_num').reset_index(drop=True)

# Save the cleaned course dataset
courses.to_csv(outputfile, index=False)
