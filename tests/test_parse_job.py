from backend.analysis.parse_job import parse_job_description

# Verify that explicit required and preferred language controls technical weights.
def test_parse_job_description_separates_requirement_weights():
    result = parse_job_description('''
    Job Title: Data Engineer
    Company: Example Labs
    Required Qualifications:
    - Required: Python and SQL
    Preferred Qualifications:
    - Experience with AWS preferred
    Soft Skills:
    - Strong communication skills
    Responsibilities:
    - Build data pipelines.
    3+ years of experience. Bachelor's degree preferred.
    Remote in Vancouver.
    ''')

    skills = {skill['name']: skill for skill in result['technical_skills']}
    assert result['job_title'] == 'Data Engineer'
    assert result['company'] == 'Example Labs'
    assert skills['python']['requirement_type'] == 'required'
    assert skills['python']['score_weight'] == 1.0
    assert skills['aws']['requirement_type'] == 'preferred'
    assert skills['aws']['score_weight'] == 0.5
    assert result['soft_skills'][0]['score_weight'] < skills['python']['score_weight']


# Verify that experience, responsibilities, arrangement, and seniority are extracted.
def test_parse_job_description_extracts_non_skill_fields():
    result = parse_job_description('Senior Software Engineer\n4-6 years experience\nHybrid\n')

    assert result['years_experience'][0]['minimum_years'] == 4
    assert result['years_experience'][0]['maximum_years'] == 6
    assert result['location_work_arrangement'] == ['hybrid']
    assert result['seniority_level'] == 'senior'


# Verify that aliases inherit the requirement section containing their source text.
def test_parse_job_description_classifies_aliases_from_their_detected_line():
    result = parse_job_description('''
    Required Skills:
    - ML and Python
    Preferred Skills:
    - NLP
    ''')

    skills = {skill['name']: skill for skill in result['technical_skills']}
    assert skills['machine learning']['requirement_type'] == 'required'
    assert skills['natural language processing']['requirement_type'] == 'preferred'


# Verify logical connectors create one requirement group instead of separate gaps.
def test_parse_job_description_builds_and_or_requirement_groups():
    result = parse_job_description('''
    Required Skills:
    - Python and SQL
    Preferred Skills:
    - PyTorch, TensorFlow, or scikit-learn
    - Python or Java and SQL
    ''')

    groups = result['requirement_groups']
    assert groups[0]['operator'] == 'and'
    assert groups[0]['alternatives'] == ['python', 'sql']
    assert groups[1]['operator'] == 'or'
    assert groups[1]['alternatives'] == ['pytorch', 'tensorflow', 'scikit-learn']
    assert groups[2]['operator'] == 'ambiguous'
    assert groups[2]['is_ambiguous'] is True


# Verify education alternatives remain separate from technical skill groups.
def test_parse_job_description_builds_education_alternative_groups():
    result = parse_job_description('''
    Required Qualifications:
    - Degree in Computer Science, Machine Learning, or Data Science
    ''')

    group = result['requirement_groups'][0]
    assert group['category'] == 'education'
    assert group['operator'] == 'or'
    assert group['requirement_type'] == 'required'


# Verify experience alternatives are represented as a bounded range.
def test_parse_job_description_handles_or_experience_ranges():
    result = parse_job_description('1 or 2 years of experience required')

    assert result['years_experience'][0]['minimum_years'] == 1
    assert result['years_experience'][0]['maximum_years'] == 2


# Verify and/or is treated as an at-least-one alternative without ambiguity.
def test_parse_job_description_handles_and_or_connector():
    result = parse_job_description('Preferred Skills:\n- Python and/or Java')

    group = result['requirement_groups'][0]
    assert group['operator'] == 'or'
    assert group['is_ambiguous'] is False


# Verify the parser handles nested headings and the supplied multi-style job posting.
def test_parse_job_description_handles_nested_jobright_sections():
    job_description = '''
    ## About the job
    The Machine Learning Engineer Intern will develop machine-learning features,
    support data pipelines and integrations, and improve ML development workflows.

    Responsibilities
    • Prepare datasets and build reproducible machine-learning experiments
    • Train, evaluate, and compare models using appropriate metrics
    • Investigate model errors, bias, latency, and reliability

    Qualification
    Required
    • Currently pursuing a degree in Computer Science, Machine Learning, Artificial Intelligence, or Data Science
    • Strong Python programming skills
    • Understanding of machine-learning fundamentals and model evaluation
    • Familiarity with data structures, software development, and version control
    Preferred
    • Experience with PyTorch, TensorFlow, scikit-learn, or similar frameworks
    • Coursework or projects involving NLP, recommendation systems, search, or ranking
    • Familiarity with SQL, cloud services, APIs, or data pipelines
    \\
    '''

    result = parse_job_description(job_description)
    skills = {skill['name']: skill for skill in result['technical_skills']}

    assert skills['machine learning']['requirement_type'] == 'required'
    assert skills['data science']['requirement_type'] == 'required'
    assert skills['data structures']['requirement_type'] == 'required'
    assert skills['version control']['requirement_type'] == 'required'
    assert skills['pytorch']['requirement_type'] == 'preferred'
    assert skills['natural language processing']['requirement_type'] == 'preferred'
    assert skills['data pipelines']['requirement_type'] == 'preferred'
    assert len(result['responsibility_evidence']) == 3
    assert result['normalized_text'].find('##') == -1
    assert result['normalized_text'].find('\\') == -1
