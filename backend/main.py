import json
import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .analysis.analysis_schema import build_analysis_result
from .analysis.extract_skills import extract_skill_evidence
from .analysis.parse_job import parse_job_description
from .analysis.validate_resume import ResumeValidationError, process_temporary_resume
from .recommendation.recommend_engine import (
    generate_learning_resources,
    generate_recommendations,
)

# Load local environment settings without exposing secrets to the frontend
load_dotenv()
chatbot_api_url = os.getenv('CHATBOT_API_URL').strip()
chatbot_api_key = os.getenv('CHATBOT_API_KEY').strip()
model = os.getenv('MODEL', 'openai/gpt-oss-20b').strip()

# Define the strict JSON contract requested
resource_response_schema = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'recommendations': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'skill': {'type': 'string'},
                    'resources': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {
                                'title': {'type': 'string'},
                                'provider': {'type': 'string'},
                                'resource_type': {
                                    'type': 'string',
                                    'enum': [
                                        'official_documentation', 'online_course',
                                        'guided_tutorial', 'video', 'practice_project'
                                    ]
                                },
                                'url': {'type': 'string'},
                                'difficulty': {
                                    'type': 'string',
                                    'enum': ['beginner', 'intermediate']
                                },
                                'estimated_time': {'type': 'string'},
                                'reason': {'type': 'string'},
                                'verification_status': {
                                    'type': 'string',
                                    'enum': ['verified', 'needs_verification']
                                }
                            },
                            'required': [
                                'title', 'provider', 'resource_type', 'url',
                                'difficulty', 'estimated_time', 'reason',
                                'verification_status'
                            ]
                        }
                    },
                    'practice_task': {'type': 'string'},
                    'learning_order': {'type': 'integer'}
                },
                'required': [
                    'skill', 'resources', 'practice_task', 'learning_order'
                ]
            }
        }
    },
    'required': ['recommendations']
}

# Send the gap-only request to Groq and return its generated JSON content
def request_chatbot(chatbot_request):
    headers = {'Content-Type': 'application/json'}
    if chatbot_api_key:
        headers['Authorization'] = f'Bearer {chatbot_api_key}'
    groq_request = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': chatbot_request['system']},
            {
                'role': 'user',
                'content': json.dumps(chatbot_request['uploaded_data'])
            }
        ],
        'temperature': 0,
        'response_format': {
            'type': 'json_schema',
            'json_schema': {
                'name': 'resource_recommendation_response',
                'strict': True,
                'schema': resource_response_schema
            }
        }
    }
    response = requests.post(
        chatbot_api_url,
        json=groq_request,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

# Create the HTTP surface
app = FastAPI(title='OptiMatch API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
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

    # Keep the job skills visible so the result can distinguish extraction from matching.
    detected_job_skills = []
    skill_matches = []
    requirement_groups = parsed_job.get('requirement_groups', [])
    grouped_line_indexes = {
        group['line_index'] for group in requirement_groups
        if group.get('category') == 'technical_skill'
    }
    for group in requirement_groups:
        if group.get('category') != 'technical_skill':
            continue
        alternatives = group['alternatives']
        detected_job_skills.extend({
            'skill': skill,
            'requirement_type': group['requirement_type'],
            'evidence': group['source_text'],
        } for skill in alternatives)
        matched_alternatives = [
            skill for skill in alternatives if resume_by_skill.get(skill, [])
        ]
        if group['operator'] == 'or':
            match_status = 'matched' if matched_alternatives else 'not_detected'
        elif group['operator'] == 'and':
            match_status = (
                'matched' if len(matched_alternatives) == len(alternatives)
                else 'partially_matched' if matched_alternatives
                else 'not_detected'
            )
        else:
            match_status = 'unclear'
        resume_group_evidence = [
            evidence
            for skill in matched_alternatives
            for evidence in resume_by_skill.get(skill, [])
        ]
        skill_matches.append({
            'skill': matched_alternatives[0] if matched_alternatives else alternatives[0],
            'normalized_skill_name': alternatives[0],
            'skill_type': 'technical',
            'requirement_type': group['requirement_type'],
            'match_status': match_status,
            'resume_evidence': resume_group_evidence,
            'job_evidence': [{'text_evidence': group['source_text']}],
            'requirement_group_id': group['group_id'],
            'operator': group['operator'],
            'alternatives': alternatives,
            'matched_alternatives': matched_alternatives,
            'alternative_evidence': group['evidence'],
        })
    for group_name in ('technical_skills', 'soft_skills'):
        for job_skill in parsed_job.get(group_name, []):
            if job_skill.get('line_index') in grouped_line_indexes:
                continue
            skill_name = job_skill['name']
            matched_evidence = resume_by_skill.get(skill_name.casefold(), [])
            detected_job_skills.append({
                'skill': skill_name,
                'requirement_type': job_skill['requirement_type'],
                'evidence': job_skill['evidence'],
            })
            skill_matches.append({
                'skill': skill_name,
                'normalized_skill_name': skill_name.casefold(),
                'skill_type': 'technical' if group_name == 'technical_skills' else 'soft',
                'requirement_type': job_skill['requirement_type'],
                'match_status': 'matched' if matched_evidence else 'not_detected',
                'resume_evidence': matched_evidence,
                'job_evidence': [{'text_evidence': job_skill['evidence']}],
            })
    return skill_matches, resume_evidence, detected_job_skills


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
        skill_matches, resume_evidence, detected_job_skills = build_skill_matches(
            normalized_resume.text,
            parsed_job
        )
        job_evidence = [
            {'skill': skill['skill'], 'text_evidence': skill['job_evidence'][0]['text_evidence']}
            for skill in skill_matches
        ]
        recommendations = generate_recommendations(
            skill_matches,
            resume_evidence=resume_evidence,
            job_evidence=job_evidence
        )
        resource_recommendations = None
        if chatbot_api_url and recommendations:
            try:
                resource_recommendations = generate_learning_resources(
                    recommendations,
                    request_chatbot,
                    target_role=parsed_job.get('job_title')
                )
            except (requests.RequestException, ValueError, TypeError, KeyError, IndexError):
                resource_recommendations = {
                    'recommendations': [],
                    'validation': {
                        'status': 'rejected',
                        'issues': ['chatbot resource generation failed']
                    }
                }
        return build_analysis_result(
            {
                'resume_pdf': resume,
                'job_description_text': job_description_text,
            },
            skill_matches,
            resume_evidence,
            job_evidence,
            build_formatting_risks(normalized_resume),
            recommendations,
            {'overall': 'deterministic'},
            [],
            detected_job_skills=detected_job_skills,
            resource_recommendations=resource_recommendations
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
