from backend.parse_job import parse_job_description

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
