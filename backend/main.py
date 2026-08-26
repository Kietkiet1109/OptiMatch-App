from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .analysis_schema import build_analysis_result
from .extract_skills import extract_skill_evidence
from .parse_job import parse_job_description
from .validate_resume import ResumeValidationError, process_temporary_resume

# Create the HTTP surface
app = FastAPI(title='OptiMatch API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)


# Convert the parser output into the records used by the scoring engine
def build_skill_matches(resume_text, parsed_job):
    resume_evidence = extract_skill_evidence(
        resume_text,
        source_document='resume'
    )
    resume_by_skill = {}
    for evidence in resume_evidence:
        resume_by_skill.setdefault(
            evidence['normalized_skill_name'], []
        ).append(evidence)

    skill_matches = []
    for group_name in ('technical_skills', 'soft_skills'):
        for job_skill in parsed_job.get(group_name, []):
            skill_name = job_skill['name']
            matched_evidence = resume_by_skill.get(skill_name.casefold(), [])
            skill_matches.append({
                'skill': skill_name,
                'requirement_type': job_skill['requirement_type'],
                'match_status': 'matched' if matched_evidence else 'not_detected',
                'resume_evidence': matched_evidence,
                'job_evidence': [{'text_evidence': job_skill['evidence']}],
            })
    return skill_matches, resume_evidence


# Add transparent formatting findings without treating them as hiring decisions
def build_formatting_risks(normalized_resume):
    formatting_risks = []
    if not normalized_resume.sections:
        formatting_risks.append({
            'issue': 'No recognizable resume section headings were detected.',
            'severity': 'medium',
        })
    if normalized_resume.masked_email_count or normalized_resume.masked_phone_count:
        formatting_risks.append({
            'issue': 'Contact details were detected and temporarily masked during analysis.',
            'severity': 'low',
        })
    return formatting_risks


# Run the deterministic analysis while the uploaded PDF remains temporary
def analyze_resume(resume, job_description_text):
    parsed_job = parse_job_description(job_description_text)

    def analyze_normalized_resume(normalized_resume):
        skill_matches, resume_evidence = build_skill_matches(
            normalized_resume.text,
            parsed_job
        )
        job_evidence = [
            {'skill': skill['skill'], 'text_evidence': skill['job_evidence'][0]['text_evidence']}
            for skill in skill_matches
        ]
        return build_analysis_result(
            {
                'resume_pdf': resume,
                'job_description_text': job_description_text,
            },
            skill_matches,
            resume_evidence,
            job_evidence,
            build_formatting_risks(normalized_resume),
            [],
            {'overall': 'deterministic'},
            []
        )

    return process_temporary_resume(
        resume,
        analyze_normalized_resume,
        content_type='application/pdf'
    )


# Provide a simple readiness check for the frontend and local development
@app.get('/api/health')
def health_check():
    return {'status': 'ok'}


# Accept one PDF and one job description, then return the explainable result
@app.post('/api/analyze')
async def analyze_endpoint(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    if not resume.filename or not resume.filename.casefold().endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDF files are accepted.')
    if len(job_description.strip()) < 80:
        raise HTTPException(status_code=400, detail='The job description must contain at least 80 characters.')

    try:
        result = analyze_resume(await resume.read(), job_description)
    except ResumeValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail='The analysis could not be completed.') from error
    return result
