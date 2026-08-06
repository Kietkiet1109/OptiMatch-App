# OptiMatch-App

An evolving AI-assisted career application toolkit for measuring resume–job alignment, identifying technical skill gaps, recommending learning paths, and improving resumes and cover letters.

## Overview

OptiMatch-App helps job seekers understand how well their application materials align with a target job description.

The project is developed through three progressive versions:

| Version | Main Purpose | Core Technology |
|---|---|---|
| **OptiMatchv1** | Analyse resume–job skill gaps and recommend relevant SFU CMPT courses | NLP, TF-IDF, cosine similarity, statistical analysis |
| **OptiMatchv2** | Accept user resumes and job descriptions through an interactive LLM application and provide broader technical-skill recommendations | LLM, structured prompting, retrieval, deterministic scoring |
| **OptiMatchv3** | Add detailed resume-improvement guidance and cover-letter analysis | LLM-assisted editing, document analysis, evidence-based recommendations |

OptiMatch-App does not reproduce the confidential logic of commercial Applicant Tracking Systems.

The application provides an **ATS compatibility estimate**, not a guaranteed prediction that a resume will pass or fail a specific ATS.

## Project Vision

The long-term goal of OptiMatch-App is to provide job seekers with a transparent and practical system that can:

- Compare a resume with a target job description.
- Measure technical-skill alignment.
- Identify missing or weakly represented skills.
- Explain why a skill was detected as important.
- Recommend appropriate learning resources.
- Suggest evidence-based resume improvements.
- Evaluate and improve cover letters.
- Avoid fabricated qualifications and misleading keyword stuffing.

## Core Principles

OptiMatch-App follows five principles.

### 1. Transparent Recommendations

The application should explain why it produces each score, skill gap, or recommendation.

### 2. Evidence-Based Analysis

Recommendations should be connected to actual text from the resume and job description.

### 3. No Fabrication

The system must not invent experience, qualifications, achievements, or technical skills for the user.

### 4. Privacy by Design

User resumes, job descriptions, and cover letters must not be committed to the repository or retained unnecessarily.

### 5. Human-Controlled Editing

The user remains responsible for reviewing and approving every suggested change.

---

# Version Roadmap

## OptiMatchv1: Resume–Job Skill Gap Analysis

### Purpose

OptiMatchv1 is the analytical foundation of the OptiMatch-App ecosystem.

It analyses technical skills across:

- Entry-level technology job postings.
- Publicly available sample resumes.
- SFU CMPT course descriptions.

The system compares a resume with a target job posting, identifies technical skills that are missing or weakly represented, and recommends relevant SFU CMPT courses.

### Main Questions

OptiMatchv1 investigates:

1. Which technical skills appear most frequently in entry-level technology job postings?

2. How do technical-skill requirements differ across areas such as:

   - Frontend development.
   - Backend development.
   - Data science.
   - Software engineering.

3. Which important job-related technical skills are absent or weakly represented in a resume?

4. Does a TF-IDF-based skill-gap model perform better than a simple keyword-overlap baseline?

5. Which SFU CMPT courses are most closely related to the detected skill gaps?

6. How do resume–job alignment scores differ across technology job domains?

### Data Sources

#### Technology Job Postings

Job postings may be collected from:

- Publicly accessible Indeed pages.
- Publicly accessible LinkedIn pages.
- Public company career pages.
- Public job-posting datasets with appropriate licences.

The project will not attempt to bypass:

- CAPTCHAs.
- Authentication requirements.
- Rate limits.
- Access controls.
- Other anti-automation systems.

Where available, each job record should contain:

| Field | Description |
|---|---|
| `job_id` | Unique identifier or generated text hash |
| `title` | Job title |
| `company` | Company name |
| `location` | Job location |
| `posting_date` | Original posting date |
| `retrieval_date` | Data-collection date |
| `description` | Complete job-description text |
| `required_qualifications` | Required qualifications |
| `preferred_qualifications` | Preferred qualifications |
| `source` | Source website |
| `source_url` | Original page URL |
| `role_domain` | Assigned job category |
| `text_hash` | Hash used for duplicate detection |

#### SFU CMPT Course Descriptions

Public SFU course pages will be used to collect:

| Field | Description |
|---|---|
| `course_code` | Official course code |
| `course_title` | Official course title |
| `course_description` | Public course description |
| `prerequisites` | Listed prerequisites |
| `source_url` | Original SFU page |
| `retrieval_date` | Data-collection date |

Course recommendations are text-based matches.

A recommendation does not guarantee that the course teaches every detected skill or that taking the course guarantees job readiness.

#### Public Resume Dataset

The initial public resume data source is:

- **Dataset:** Resume Dataset
- **Dataset creator:** Snehaan Bhawal
- **Source:** Kaggle
- **Licence:** CC0: Public Domain
- **Date accessed:** August 4, 2026

Expected fields include:

| Field | Description |
|---|---|
| `resume_id` | Anonymous resume identifier |
| `resume_text` | Extracted resume text |
| `category` | Resume category |
| `source` | Dataset source |
| `word_count` | Resume word count |
| `cleaned_text` | Normalized text used by the model |

The public resume records are not assumed to represent SFU students or the entire technology-job applicant population.

### Data Processing

The OptiMatchv1 pipeline performs:

1. Data acquisition.
2. Data validation.
3. Text extraction.
4. Personal-information removal.
5. Text normalization.
6. Duplicate detection.
7. Job-domain classification.
8. Technical-skill extraction.
9. TF-IDF feature construction.
10. Resume–job comparison.
11. Course recommendation.
12. Statistical evaluation.
13. Visualization.

### Text Cleaning Requirements

The cleaning process should:

- Remove HTML and navigation content.
- Normalize whitespace and character encoding.
- Remove duplicated job postings.
- Remove repeated corporate boilerplate.
- Normalize common skill aliases.
- Preserve meaningful technical punctuation.
- Preserve important multiword technical expressions.
- Retain raw and cleaned text for auditing.

The pipeline must preserve technical terms such as:

- C
- C++
- C#
- R
- Go
- .NET
- Node.js
- React
- REST
- AWS
- SQL

It should also preserve phrases such as:

- Machine learning.
- Data structures.
- Unit testing.
- Software engineering.
- Cloud computing.
- Version control.
- Continuous integration.

### Technical-Skill Extraction

OptiMatchv1 uses a hybrid skill-extraction approach combining:

- A curated technical-skill dictionary.
- Skill-alias normalization.
- Rule-based phrase matching.
- Unigram features.
- Bigram features.
- TF-IDF weights.

Example alias mappings:

```json
{
  "js": "javascript",
  "javascript": "javascript",
  "node": "node.js",
  "nodejs": "node.js",
  "node.js": "node.js",
  "amazon web services": "aws",
  "postgres": "postgresql",
  "reactjs": "react"
}
```

Generic Named Entity Recognition should not be treated as the only skill-extraction method because general-language models may not recognize technical frameworks, tools, and programming languages accurately.

### Baseline Model

The baseline compares normalized technical-skill sets.

For a resume $(R)$ and job description $(J)$, it calculates:

- Shared technical skills.
- Job skills absent from the resume.
- Jaccard similarity.
- Unweighted skill coverage.
- Weighted skill coverage.

The baseline is intentionally simple and interpretable.

### TF-IDF Model

All resumes, job descriptions, and course descriptions must be transformed using the same fitted feature space.

Cosine similarity is calculated as:

$$
\operatorname{similarity}(R,J)
=
\frac{R \cdot J}{\|R\|\|J\|}
$$

A non-negative skill-gap vector is defined as:

$$
G_i=\max(J_i-R_i,0)
$$

where:

- $(J_i)$ is the job-description weight for feature $(i)$.
- $(R_i)$ is the resume weight for feature $(i)$.
- $(G_i)$ represents the amount by which the job feature exceeds the resume feature.

For each resume–job pair, OptiMatchv1 produces:

- Resume–job similarity score.
- Technical-skill coverage score.
- Shared technical skills.
- Missing or underrepresented technical skills.
- Evidence from the job description.
- Ranked SFU CMPT course recommendations.

### Course Recommendation

The skill-gap vector is compared with each SFU CMPT course vector.

For course $(C)$:

$$
\operatorname{course\_match}(G,C)
=
\frac{G \cdot C}{\|G\|\|C\|}
$$

Each result may include:

- Course code.
- Course title.
- Course-match score.
- Matching technical terms.
- Course description.
- Prerequisites.

### OptiMatchv1 Evaluation

The model should be evaluated using a held-out set of manually labelled job postings.

Potential metrics include:

- Precision at $(k)$.
- Recall at $(k)$.
- Jaccard similarity.
- Mean number of relevant skills retrieved.
- Human inter-rater agreement.
- Baseline-versus-TF-IDF comparison.
- Qualitative error analysis.

Possible statistical tests include:

- One-way ANOVA.
- Welch’s ANOVA.
- Kruskal–Wallis test.
- Appropriate post-hoc comparisons.

The statistical test must be selected only after inspecting the sample sizes, distributions, and variance assumptions.

---

## OptiMatchv2: Interactive LLM Resume Matcher

### Purpose

OptiMatchv2 transforms the analytical pipeline into an interactive LLM-powered application.

Users provide:

- A resume.
- A target job description.

The application then estimates the resume’s ATS compatibility and provides technical-skill recommendations.

Unlike OptiMatchv1, learning recommendations are not limited to SFU courses.

### Main User Flow

1. The user pastes or uploads a resume.
2. The user pastes a target job description.
3. The application extracts structured resume information.
4. The application extracts required and preferred job qualifications.
5. A deterministic scoring engine calculates measurable alignment.
6. The LLM interprets the structured comparison.
7. The application returns an ATS compatibility assessment.
8. The application identifies missing or weakly represented skills.
9. The application recommends technical learning actions.
10. The application displays supporting evidence.

### ATS Compatibility Output

OptiMatchv2 must not return an unsupported statement such as:

> This resume will bypass the ATS.

Instead, it should return an assessment such as:

- **Strong alignment**
- **Moderate alignment**
- **Needs improvement**
- **Low alignment**

The output may include:

| Component | Example |
|---|---|
| Overall compatibility | 72/100 |
| Technical-skill coverage | 78% |
| Required-skill coverage | 80% |
| Preferred-skill coverage | 55% |
| Experience alignment | Moderate |
| Education alignment | Strong |
| Formatting risk | Low |
| Missing technical skills | Docker, AWS, CI/CD |
| Recommendation confidence | Medium |

The score must be presented as an OptiMatch estimate, not as an official ATS score.

### Hybrid Analysis Architecture

OptiMatchv2 should combine deterministic analysis with LLM interpretation.

#### Deterministic Components

- Resume parsing.
- Job-description parsing.
- Technical-skill extraction.
- Exact and normalized skill matching.
- Keyword coverage.
- TF-IDF or embedding similarity.
- Required-versus-preferred skill weighting.
- Resume section detection.
- Formatting checks.

#### LLM Components

- Contextual interpretation.
- Skill relationship reasoning.
- Explanation generation.
- Recommendation prioritization.
- Career-path suggestions.
- User-friendly summaries.

The LLM should receive structured data whenever possible rather than being asked to calculate every score from raw text.

### Technical-Skill Recommendations

Recommendations may include:

- Official documentation.
- Online courses.
- University courses.
- Certifications.
- Practice projects.
- Open-source contributions.
- Technical interview topics.
- Portfolio project ideas.
- Books or tutorials.
- Related tools and frameworks.

Each recommendation should identify:

- The missing skill.
- Why the skill matters for the target role.
- Evidence from the job description.
- Suggested learning level.
- Estimated priority.
- One or more learning actions.

Example:

```json
{
  "skill": "docker",
  "priority": "high",
  "reason": "Docker appears in the required qualifications and is not detected in the resume.",
  "recommended_actions": [
    "Complete an introductory Docker course",
    "Containerize an existing application",
    "Add a Dockerfile and deployment instructions to a portfolio project"
  ]
}
```

### LLM Output Requirements

LLM responses should use a validated structured format.

Example:

```json
{
  "compatibility_band": "moderate_alignment",
  "overall_score": 72,
  "shared_skills": [
    "python",
    "sql",
    "git"
  ],
  "missing_required_skills": [
    "docker"
  ],
  "missing_preferred_skills": [
    "aws"
  ],
  "recommendations": [],
  "limitations": []
}
```

The application must handle:

- Invalid model output.
- Missing fields.
- Unsupported claims.
- Empty documents.
- Very long documents.
- Prompt-injection text inside uploaded documents.
- API errors.
- Timeouts.
- Rate limits.

### OptiMatchv2 Evaluation

OptiMatchv2 should be evaluated on:

- Agreement with human reviewers.
- Skill-extraction accuracy.
- Structured-output validity.
- Unsupported recommendation rate.
- Hallucination rate.
- Explanation quality.
- Response latency.
- Cost per analysis.
- Stability across repeated runs.
- User usefulness ratings.

---

## OptiMatchv3: Resume and Cover-Letter Optimizer

### Purpose

OptiMatchv3 extends the interactive matching system with detailed resume and cover-letter support.

It includes all OptiMatchv2 capabilities and adds:

- Resume-fixing recommendations.
- Resume bullet-point analysis.
- Section-level feedback.
- Cover-letter compatibility analysis.
- Cover-letter improvement suggestions.
- Application-package consistency checks.

### Resume Analysis Features

OptiMatchv3 may analyse:

- Contact-information completeness.
- Professional summary relevance.
- Technical-skill placement.
- Experience-section relevance.
- Bullet-point quality.
- Use of measurable outcomes.
- Action verbs.
- Repetition.
- Verb tense consistency.
- Resume length.
- Section ordering.
- ATS-unfriendly formatting.
- Missing evidence for claimed skills.
- Alignment with required qualifications.
- Alignment with preferred qualifications.

### Resume-Fixing Tips

Suggestions may include:

- Moving important skills into relevant experience bullets.
- Replacing vague claims with specific evidence.
- Adding measurable impact where truthful.
- Removing irrelevant or repeated information.
- Improving bullet-point clarity.
- Reordering sections.
- Standardizing technical-skill names.
- Adding missing portfolio links.
- Clarifying project contributions.
- Improving consistency between summary, skills, and experience.

OptiMatchv3 must not encourage users to insert skills they do not possess.

### Resume Bullet Analysis

Each bullet may be evaluated for:

| Criterion | Description |
|---|---|
| Action | Does the bullet begin with a clear action? |
| Task | Does it explain what was done? |
| Technology | Does it identify relevant tools or methods? |
| Result | Does it show a measurable or meaningful outcome? |
| Relevance | Does it connect to the target role? |
| Credibility | Is the statement supported by the user’s experience? |

Example output:

```json
{
  "original_bullet": "Worked on a website using React.",
  "issues": [
    "The action is vague",
    "No contribution is specified",
    "No result is provided"
  ],
  "suggested_structure": "Built [feature] using React and [technology], resulting in [truthful outcome].",
  "requires_user_input": [
    "What feature did you build?",
    "What was your individual contribution?",
    "Was there a measurable result?"
  ]
}
```

The application should request missing facts instead of inventing them.

### Cover-Letter Analysis

OptiMatchv3 can accept:

- Resume.
- Job description.
- Cover letter.

It may evaluate:

- Employer and role specificity.
- Opening strength.
- Connection between experience and job requirements.
- Evidence supporting key claims.
- Technical-skill relevance.
- Repetition of resume content.
- Paragraph organization.
- Professional tone.
- Grammar and clarity.
- Closing strength.
- Consistency with the resume.
- Unsupported or contradictory claims.

### Cover-Letter Improvement

The application may suggest:

- A stronger opening.
- Better employer-specific reasoning.
- More relevant experience examples.
- Clearer connections to job requirements.
- Removal of generic statements.
- Stronger paragraph transitions.
- A more concise closing.
- Correction of contradictions between documents.

The application should not generate false enthusiasm, false employer knowledge, or fabricated professional experience.

### Application Consistency Check

OptiMatchv3 may compare the resume and cover letter to identify:

- Conflicting employment dates.
- Different job titles.
- Inconsistent technical skills.
- Contradictory claims.
- Missing evidence.
- Repeated content.
- Different career objectives.
- Skills claimed in one document but unsupported in the other.

### OptiMatchv3 Evaluation

OptiMatchv3 should be evaluated using:

- Human helpfulness ratings.
- Factual-consistency checks.
- Unsupported-edit rate.
- Grammar and clarity improvement.
- Resume–job alignment improvement.
- Cover-letter relevance improvement.
- User acceptance rate for suggestions.
- Comparison between original and revised documents.
- Privacy and security testing.

---

# System Architecture

A possible high-level architecture is:

```text
User Interface
      |
      v
Document Upload and Parsing
      |
      v
Text Cleaning and PII Protection
      |
      v
Structured Resume and Job Extraction
      |
      +--------------------------+
      |                          |
      v                          v
Deterministic Scoring       LLM Analysis Layer
      |                          |
      +-------------+------------+
                    |
                    v
        Recommendation Engine
                    |
                    v
       Evidence and Explanation Layer
                    |
                    v
              User Results
```

## Main Components

### Frontend

Responsible for:

- Resume input.
- Job-description input.
- Cover-letter input in OptiMatchv3.
- Score visualization.
- Recommendation display.
- User approval of suggested edits.

Possible technologies:

- React.
- Next.js.
- Streamlit.
- Gradio.

### Backend API

Responsible for:

- File validation.
- Document parsing.
- Analysis requests.
- Score calculation.
- LLM orchestration.
- Recommendation generation.
- Error handling.

Possible technologies:

- Python.
- FastAPI.
- Pydantic.
- Celery or background queues for longer document-processing tasks.

### Analysis Engine

Responsible for:

- Text normalization.
- Skill extraction.
- Skill matching.
- TF-IDF or embedding similarity.
- Gap calculation.
- Course or learning-resource ranking.

### LLM Layer

Responsible for:

- Contextual explanation.
- Structured recommendations.
- Resume improvement guidance.
- Cover-letter analysis.
- User-facing summaries.

The LLM layer should not replace deterministic validation.

### Recommendation Catalogue

OptiMatchv2 and OptiMatchv3 may use a structured recommendation catalogue containing:

- Skill name.
- Skill category.
- Difficulty.
- Prerequisites.
- Learning resources.
- Project suggestions.
- Related occupations.
- Source information.
- Last review date.

---

# Repository Structure

```text
OptiMatch-App/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── evaluation.md
│   ├── privacy.md
│   └── roadmap.md
├── versions/
│   ├── OptiMatchv1/
│   │   ├── README.md
│   │   ├── config/
│   │   ├── data/
│   │   ├── notebooks/
│   │   ├── src/
│   │   ├── tests/
│   │   └── outputs/
│   ├── OptiMatchv2/
│   │   ├── README.md
│   │   ├── frontend/
│   │   ├── backend/
│   │   ├── prompts/
│   │   ├── schemas/
│   │   ├── tests/
│   │   └── evaluation/
│   └── OptiMatchv3/
│       ├── README.md
│       ├── frontend/
│       ├── backend/
│       ├── prompts/
│       ├── schemas/
│       ├── tests/
│       └── evaluation/
├── shared/
│   ├── document_parsing/
│   ├── skill_extraction/
│   ├── scoring/
│   ├── security/
│   └── utilities/
├── sample_data/
│   ├── synthetic_resume.txt
│   ├── synthetic_job_description.txt
│   └── synthetic_cover_letter.txt
└── tests/
```

Alternatively, each version may be maintained in a separate Git branch or release tag.

Using separate version directories is recommended when the versions have significantly different architectures.

---

# Installation

## Requirements

The exact requirements depend on the version being used.

Possible requirements include:

- Python 3.11 or later.
- Node.js 20 or later for a JavaScript frontend.
- Java and PySpark for optional distributed processing.
- An API key for the selected LLM provider.
- A local model runtime when using an open-source model.

## Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd OptiMatch-App
```

## Create a Python Environment

```bash
python3 -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

Version-specific dependencies may be installed from the relevant directory:

```bash
pip install -r versions/OptiMatchv1/requirements.txt
```

## Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Example configuration:

```env
LLM_PROVIDER=<provider>
LLM_MODEL=<model>
LLM_API_KEY=<api-key>
DATABASE_URL=<database-url>
MAX_UPLOAD_SIZE_MB=5
DELETE_USER_FILES_AFTER_ANALYSIS=true
LOG_DOCUMENT_CONTENT=false
```

Never commit `.env` files or API keys.

---

# Planned Usage

## Run OptiMatchv1

```bash
python versions/OptiMatchv1/src/calculate_gaps.py \
  --resume sample_data/synthetic_resume.txt \
  --job sample_data/synthetic_job_description.txt
```

Generate SFU course recommendations:

```bash
python versions/OptiMatchv1/src/recommend_courses.py \
  --gap-file outputs/gap_result.json \
  --top-k 5
```

## Run OptiMatchv2

Start the backend:

```bash
uvicorn versions.OptiMatchv2.backend.main:app --reload
```

Start the frontend:

```bash
cd versions/OptiMatchv2/frontend
npm install
npm run dev
```

## Run OptiMatchv3

```bash
uvicorn versions.OptiMatchv3.backend.main:app --reload
```

The actual commands must be updated when the implementation is finalized.

---

# Example OptiMatchv2 Result

```json
{
  "compatibility_band": "moderate_alignment",
  "overall_score": 72,
  "technical_skill_coverage": 78,
  "required_skill_coverage": 80,
  "preferred_skill_coverage": 55,
  "shared_skills": [
    "python",
    "sql",
    "git"
  ],
  "missing_required_skills": [
    "docker"
  ],
  "missing_preferred_skills": [
    "aws",
    "kubernetes"
  ],
  "recommendations": [
    {
      "skill": "docker",
      "priority": "high",
      "reason": "Docker is listed as a required qualification but is not detected in the resume.",
      "actions": [
        "Complete an introductory Docker course",
        "Containerize an existing portfolio project",
        "Add deployment instructions to the project README"
      ]
    }
  ],
  "limitations": [
    "The result is an OptiMatch estimate and not an official ATS score.",
    "A skill not detected in the resume may still be possessed by the user."
  ]
}
```

---

# Data Privacy and Security

OptiMatch-App may process personal career documents.

The project must therefore:

- Avoid storing user files longer than necessary.
- Avoid logging raw resume and cover-letter text.
- Remove temporary files after analysis.
- Encrypt stored documents when persistence is required.
- Prevent uploaded documents from being treated as system instructions.
- Validate file extensions and content types.
- Enforce upload-size limits.
- Reject executable or unsupported files.
- Protect API keys and secrets.
- Provide a clear data-retention policy.
- Allow users to delete their data.
- Avoid training models on user documents without explicit consent.

The public repository should contain only:

- Synthetic documents.
- Sanitized examples.
- Legally redistributable data.
- Configuration templates without secrets.

---

# Responsible Use

OptiMatch-App should help users communicate their real qualifications more clearly.

It must not:

- Fabricate work experience.
- Invent technical skills.
- Generate false achievements.
- Encourage keyword stuffing.
- Claim guaranteed ATS success.
- Impersonate recruiters.
- Make final hiring decisions.
- Infer protected personal characteristics.
- Rank candidates for employers without appropriate review.
- conceal major inconsistencies between documents.

The system should clearly distinguish among:

- A skill that is missing from the resume text.
- A skill that the user confirms they possess.
- A skill that the user needs to learn.
- A skill that is optional for the target role.

---

# Testing Strategy

## Shared Tests

Tests should cover:

- HTML removal.
- Resume parsing.
- Job-description parsing.
- Personal-information detection.
- Skill-alias normalization.
- Technical-token preservation.
- Empty-document handling.
- Duplicate detection.
- Cosine-similarity calculation.
- Gap-vector calculation.
- Score-range validation.
- Invalid file handling.

## OptiMatchv2 Tests

Additional tests should cover:

- LLM structured-output validation.
- Prompt-injection resistance.
- Missing output fields.
- Hallucinated skills.
- Unsupported recommendations.
- API timeouts.
- Model-provider failures.
- Repeated-run stability.

## OptiMatchv3 Tests

Additional tests should cover:

- Factual consistency of rewritten bullets.
- Resume and cover-letter contradiction detection.
- Preservation of dates, titles, and employer names.
- Unsupported achievement generation.
- Grammar corrections.
- User approval before applying edits.

Run tests with:

```bash
pytest
```

---

# Success Criteria

| Version | Minimum Success Criteria |
|---|---|
| **OptiMatchv1** | Produces reproducible skill-gap scores, explains missing skills, and ranks relevant SFU CMPT courses |
| **OptiMatchv2** | Accepts user resume and job-description input, returns valid structured analysis, and produces evidence-based technical recommendations |
| **OptiMatchv3** | Produces factual resume and cover-letter suggestions without fabricating user experience |

Additional measurable criteria may include:

- Precision and recall of technical-skill extraction.
- Human agreement with identified skill gaps.
- Percentage of valid structured LLM outputs.
- Hallucination rate.
- Average analysis latency.
- User usefulness rating.
- Percentage of suggestions accepted by users.

---

# Current Development Status

| Version | Status |
|---|---|
| **OptiMatchv1** | In development |
| **OptiMatchv2** | Planned |
| **OptiMatchv3** | Planned |

## Development Sequence

### Phase 1: Complete OptiMatchv1

- [ ] Collect job-posting data.
- [ ] Collect SFU course descriptions.
- [ ] Import and inspect the public resume dataset.
- [ ] Build the cleaning pipeline.
- [ ] Build the skill dictionary.
- [ ] Implement the baseline model.
- [ ] Implement TF-IDF matching.
- [ ] Implement course recommendation.
- [ ] Evaluate the model.
- [ ] Publish reproducible results.

### Phase 2: Build OptiMatchv2

- [ ] Create resume and job-description input interfaces.
- [ ] Add document parsing.
- [ ] Define structured LLM output schemas.
- [ ] Integrate deterministic scores with LLM explanations.
- [ ] Build a general technical-learning recommendation catalogue.
- [ ] Add privacy controls.
- [ ] Add evaluation and monitoring.
- [ ] Deploy the application.

### Phase 3: Build OptiMatchv3

- [ ] Add resume-section analysis.
- [ ] Add bullet-point feedback.
- [ ] Add factual rewrite workflows.
- [ ] Add cover-letter input.
- [ ] Add cover-letter analysis.
- [ ] Add cross-document consistency checking.
- [ ] Add user approval for edits.
- [ ] Conduct user testing.

---

# Known Limitations

- Commercial ATS systems use private and varying ranking logic.
- A high OptiMatch score cannot guarantee an interview.
- A low score does not prove that a candidate is unqualified.
- Resume text does not directly measure practical ability.
- Job descriptions may contain unrealistic or inconsistent requirements.
- Public job-posting data may not represent the complete labour market.
- Public resume datasets may contain noisy or outdated records.
- TF-IDF measures textual similarity rather than semantic mastery.
- LLM outputs may be inconsistent or unsupported.
- Course descriptions contain less information than complete syllabi.
- Learning recommendations may vary in quality and availability.
- Human review remains necessary.

---

# Future Directions

Potential future extensions include:

- Multilingual resume analysis.
- Local open-source LLM support.
- Contextual embedding models.
- Skill ontologies.
- Interview-question recommendations.
- Portfolio project recommendations.
- GitHub profile analysis with user permission.
- Role-specific resume templates.
- Recruiter-feedback integration.
- Application tracking.
- Job recommendation.
- Career-path planning.
- Browser extension support.
- Mobile application support.
- Private on-device document analysis.

---

# Summary

**OptiMatch-App — AI-Assisted Resume and Job Alignment Platform**

Designed a multi-version career application platform that combines NLP, technical-skill extraction, similarity modelling, and large language models to analyse resume–job alignment. The initial version identifies technical skill gaps and recommends relevant SFU computing courses, while later versions provide interactive ATS compatibility assessments, broader learning recommendations, resume-improvement guidance, and cover-letter analysis.

---