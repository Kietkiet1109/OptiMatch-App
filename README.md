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

- CS-related technology job postings.
- Publicly available sample resumes.
- SFU CMPT course descriptions.

The system compares a resume with a target job posting, identifies technical skills that are missing or weakly represented, and recommends relevant SFU CMPT courses.

### Main Questions

OptiMatch v1 answers four practical questions:

1. Which technical skills are most frequently requested in CS-related technology jobs?
2. Which important job-related technical skills are missing or weakly represented in a resume?
3. Does a TF-IDF gap model provide useful information beyond a simple keyword-overlap baseline?
4. Which SFU Computing courses are most closely related to the detected skill gaps?

The system is intended as an analytical and educational tool. It does **not** claim to reproduce confidential ATS logic, predict hiring decisions, or prove whether a candidate possesses a skill.

## Key Features

- Collects and cleans public technology job postings.
- Filters broad job categories to retain CS-related roles.
- Uses a curated technical-skill dictionary for interpretable matching.
- Compares resumes and jobs with a simple keyword-overlap baseline.
- Represents jobs, resumes, and courses in one shared TF-IDF feature space.
- Calculates cosine similarity and non-negative resume–job gap vectors.
- Ranks SFU Computing courses by similarity to detected skill gaps.
- Evaluates baseline and TF-IDF outputs against held-out human labels.
- Performs exploratory and statistical analysis in a reproducible notebook.
- Provides a single `main.py` entry point for reproducing the modelling pipeline.

## Project Workflow

```text
Raw jobs + resumes + courses
          |
          v
   Dataset cleaning
          |
          v
 Technical-skill extraction
          |
          +-------------------+
          |                   |
          v                   v
 Keyword baseline       Development/evaluation split
                              |
                              v
                     Shared TF-IDF feature space
                              |
                              v
                    Resume-job gap calculation
                              |
                              v
                    SFU course recommendation
                              |
                              v
                    Held-out human evaluation
                              |
                              v
                  Statistical analysis + figures
```

### Data Sources

## Dataset Summary

| Dataset | Source | Raw Records | Final Records | Main Use |
|---|---|---:|---:|---|
| Jobs | The Muse Jobs API | 300 | 93 | Skill demand, baseline model, TF-IDF gap analysis |
| Resumes | Kaggle Resume Dataset | 2,484 | 100 | Resume skill extraction and resume–job comparison |
| Courses | SFU Academic Calendar | 166 | 93 | Course recommendation |
| Human labels | Manual annotation | 20 pairs | 20 pairs | Held-out model evaluation |

Raw data is kept separate from processed data so the complete workflow can be reproduced.

## 1. Technology Job Postings

### Source

Job postings were collected from the public **The Muse Jobs API**.

The initial candidate set used four broad Muse categories:

- Computer and IT
- Data and Analytics
- Software Engineering
- Science and Engineering

These categories were used only as an initial filter and were **not assumed to contain only CS-related jobs**.

### Job Cleaning

The job-cleaning pipeline:

- Removes duplicate job IDs.
- Removes exact duplicate descriptions.
- Detects and removes near-duplicate descriptions using TF-IDF cosine similarity.
- Removes empty descriptions.
- Converts HTML entities.
- Removes HTML tags, URLs, page artifacts, and repeated boilerplate.
- Normalizes whitespace.
- Preserves technical punctuation such as `C++`, `C#`, `.NET`, and `CI/CD`.
- Standardizes the four Muse category labels.
- Applies title- and description-based CS relevance filtering.

The additional CS relevance filter was necessary because broad categories could include unrelated roles such as retail, banking, mechanical engineering, thermal engineering, and other non-computing jobs.

After cleaning and CS relevance filtering, **93 jobs** remained.

| Category | Final Jobs |
|---|---:|
| Computer and IT | 20 |
| Data and Analytics | 45 |
| Science and Engineering | 9 |
| Software Engineering | 19 |
| **Total** | **93** |

## 2. Public Resume Dataset

The resume data comes from:

- **Dataset:** Resume Dataset
- **Creator:** Snehaan Bhawal
- **Source:** Kaggle
- **Licence:** CC0: Public Domain
- **Date accessed:** August 4, 2026

The raw dataset contains **2,484 resumes** across multiple categories.

OptiMatch v1:

- Uses the `Resume_str` text field.
- Removes records with missing resume text.
- Removes duplicate resumes.
- Filters to the `INFORMATION-TECHNOLOGY` category.
- Selects a reproducible sample of 100 resumes.
- Assigns stable resume IDs.
- Masks detected email addresses and phone numbers.
- Normalizes whitespace.
- Preserves raw and cleaned text.
- Calculates resume word counts.
- Extracts technical skills using the shared extraction module.

The final resume dataset contains **100 public IT resumes**.

These resumes are sample public records and should not be interpreted as representative of all job seekers or SFU students.

## 3. SFU Computing Course Descriptions

Course descriptions were collected from publicly accessible **SFU Academic Calendar** pages.

The course-cleaning pipeline:

- Removes duplicate course numbers.
- Removes records with missing descriptions.
- Normalizes course codes and whitespace.
- Removes HTML artifacts.
- Preserves official course descriptions.
- Separates prerequisite text when available.
- Removes selected special-topic, project, practicum, co-op, internship, thesis, portfolio, unoffered, and cross-listed records according to documented project rules.

The final course dataset contains **93 SFU Computing courses**.

Course recommendations are based on public course descriptions and should therefore be interpreted as **text-based curriculum matches**, not guarantees that a course teaches every detected skill.

## 4. Human Evaluation Labels

A fixed held-out evaluation sample contains **20 resume–job pairs**.

For each pair, important missing technical skills were manually labelled by comparing:

- the held-out job description; and
- the paired resume text.

The supplied `human_labels.csv` is treated as fixed evaluation ground truth so results can be reproduced consistently.

Human annotation is subjective, so these labels should be interpreted as a practical evaluation reference rather than objective proof of technical competency.

# Technical Approach

## 1. Technical-Skill Dictionary

A curated technical-skill dictionary is stored in:

```text
config/technical_skills.json
```

It contains skills from areas such as:

- Programming languages
- Frameworks
- Databases
- Cloud and DevOps
- Data and machine learning
- Development tools
- Networking and security
- Software-development practices

Examples include Python, Java, JavaScript, SQL, AWS, Azure, GCP, Docker, Kubernetes, Git, CI/CD, machine learning, cybersecurity, and network security.

Shared extraction logic is implemented in:

```text
src/extract_skills.py
```

Rule-based matching is used instead of relying only on general-purpose Named Entity Recognition because technical terms such as `C`, `C++`, `C#`, `R`, `Go`, and `Node.js` require careful handling.

## 2. Keyword-Overlap Baseline

The baseline model compares the normalized technical-skill sets of a job and a resume.

For a job skill set $(J)$ and resume skill set $(R)$:

### Shared skills

$$
J \cap R
$$

### Missing skills

$$
J - R
$$

### Skill coverage

$$
\text{Skill Coverage}=\frac{|J \cap R|}{|J|}
$$

### Jaccard similarity

$$
J(R,J)=\frac{|R \cap J|}{|R \cup J|}
$$

The baseline is intentionally simple and interpretable.

Implementation:

```text
src/baseline_model.py
```

## 3. Development and Evaluation Split

The cleaned job dataset is divided into development and held-out evaluation records using:

```text
src/split_data.py
```

Split metadata is stored in:

```text
data/evaluation/jobs_split.csv
```

The split column is named `label` with values `development` and `evaluation`.

Randomized operations use:

```python
random_seed = 353
```

The final evaluation set contains **20 held-out jobs**.

## 4. Shared TF-IDF Feature Space

Jobs, resumes, and SFU course descriptions are transformed using **one shared TF-IDF vocabulary**.

The vectorizer is fitted on the approved modelling corpus and then used to transform:

- Development jobs
- Held-out evaluation jobs
- Resumes
- Courses

Held-out evaluation jobs are transformed using the fitted vectorizer but are not used to fit the vocabulary.

Using one vectorizer ensures that every dataset is represented in the same feature dimensions.

Implementation:

```text
src/build_features.py
```

## 5. Resume–Job Similarity and Gap Calculation

Cosine similarity is calculated for every resume–job pair:

$$
\operatorname{similarity}(R,J)=
\frac{R \cdot J}{\|R\|\|J\|}
$$

A non-negative TF-IDF gap vector is calculated as:

$$
G_i=\max(J_i-R_i,0)
$$

where:

- $(J_i)$ is the job TF-IDF weight for feature $(i)$.
- $(R_i)$ is the resume TF-IDF weight for feature $(i)$.
- $(G_i)$ measures how much more strongly the feature appears in the job than in the resume.

Only technical-skill features are presented as actionable skill gaps.

Implementation:

```text
src/calculate_gaps.py
```

## 6. Course Recommendation

Each resume–job gap vector is compared with every SFU course vector:

$$
\operatorname{course\_match}(G,C)=
\frac{G \cdot C}{\|G\|\|C\|}
$$

Courses are ranked by cosine similarity.

Recommendation output includes:

- Course number
- Course title
- Similarity score
- Matching terms
- Course description
- Prerequisites when available

Implementation:

```text
src/recommend_courses.py
```

## 7. Held-Out Evaluation

The keyword baseline and TF-IDF model are evaluated against the same 20 manually labelled held-out resume–job pairs.

Evaluation metrics include:

- Precision
- Recall
- Jaccard overlap
- Precision@3
- Recall@3
- Precision@5
- Recall@5
- Jaccard@5

Implementation:

```text
src/evaluate.py
```

Evaluation pairs are prepared using:

```text
src/label_skills.py
```

# Results

## Job-Market Skill Demand

The most frequently requested technical skills in the final 93-job dataset were:

| Skill | Job Postings |
|---|---:|
| Python | 44 |
| SQL | 32 |
| Agile | 31 |
| Azure | 29 |
| Machine learning | 27 |
| AWS | 23 |
| GCP | 20 |
| Cybersecurity | 19 |
| Java | 19 |
| CI/CD | 15 |

Skill demand differed across categories:

- **Data and Analytics** showed particularly high demand for Python, SQL, and machine learning.
- **Software Engineering** emphasized Python, Java, Agile, and CI/CD.
- **Computer and IT** showed stronger emphasis on Azure, AWS, and cybersecurity.

## Resume Skill Profile

The 100 sampled resumes contained an average of approximately **6.5 detected technical skills per resume**.

Frequently observed skills included Windows, Active Directory, SQL, Cisco, Linux, LAN, SharePoint, Oracle, WAN, and VMware.

The sampled resumes were therefore more infrastructure- and IT-oriented than the job dataset, which placed more emphasis on programming, cloud platforms, machine learning, and modern software-development practices.

## Baseline Evaluation

On the 20 held-out evaluation pairs, the keyword baseline achieved approximately:

| Metric | Score |
|---|---:|
| Mean precision | 0.3637 |
| Mean recall | 0.3375 |
| Mean Jaccard overlap | 0.2086 |

## TF-IDF Evaluation

The TF-IDF model achieved approximately:

| Metric | Score |
|---|---:|
| Precision@3 | 0.3583 |
| Recall@3 | 0.1875 |
| Precision@5 | 0.3858 |
| Recall@5 | 0.2775 |
| Jaccard@5 | 0.2142 |

TF-IDF produced slightly higher Precision@5 and Jaccard overlap than the baseline, while the baseline achieved higher recall.

The mean Jaccard improvement was approximately **0.0055**, so the TF-IDF model did **not clearly dominate** the simpler keyword-overlap baseline.

This result is important because it shows that a more complex text representation does not automatically provide a large improvement over an interpretable rule-based approach.

## Job-Category Gap Scores

Mean job-level gap scores were approximately:

| Category | Mean Gap Score |
|---|---:|
| Computer and IT | 0.9739 |
| Data and Analytics | 0.9768 |
| Science and Engineering | 0.9718 |
| Software Engineering | 0.9733 |

A standard one-way ANOVA produced evidence of category differences under the standard ANOVA assumptions, but the equal-variance assumption was not satisfied. The result should therefore be interpreted cautiously.

## Course Recommendations

The most frequently top-ranked SFU courses were:

1. **CMPT 732 - Big Data Lab I**
2. **CMPT 410 - Machine Learning**
3. **CMPT 733 - Big Data Lab II**
4. **CMPT 372 - Web II - Server-side Development**
5. **CMPT 473 - Software Testing, Reliability and Security**

The highest-ranked recommendations therefore tended to emphasize big data, machine learning, server-side development, software testing, and security/privacy.

Recommendation similarity scores were generally low, which is expected because short course descriptions contain less detail than full job descriptions.

# Analysis and Visualizations

Exploratory analysis, statistical analysis, and visualizations are contained in:

```text
notebooks/analysis.ipynb
```

The notebook includes job-market skill frequencies, technical-skill differences by category, resume skill distributions, course coverage, baseline-versus-TF-IDF evaluation performance, gap-score distributions, and course recommendation analysis.

# Repository Structure

```text
OptiMatch-v1/
├── README.md
├── requirements.txt
├── .gitignore
│
├── config/
│   └── technical_skills.json
│
├── data/
│   ├── raw/
│   │   ├── jobs.csv
│   │   ├── resumes.csv
│   │   └── courses.csv
│   ├── processed/
│   │   ├── jobs_clean.csv
│   │   ├── resumes_clean.csv
│   │   └── courses_clean.csv
│   └── evaluation/
│       ├── jobs_split.csv
│       └── human_labels.csv
│
├── src/
│   ├── main.py
│   ├── collect_jobs.py
│   ├── collect_courses.py
│   ├── clean_jobs.py
│   ├── clean_resumes.py
│   ├── clean_courses.py
│   ├── extract_skills.py
│   ├── baseline_model.py
│   ├── split_data.py
│   ├── build_features.py
│   ├── calculate_gaps.py
│   ├── recommend_courses.py
│   ├── label_skills.py
│   └── evaluate.py
│
├── notebooks/
│   └── analysis.ipynb
│
└── outputs/
    ├── tables/
    ├── features/
    ├── gaps/
    ├── recommendations/
    └── evaluation/
```

# Installation

## 1. Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd OptiMatch-v1
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate on Linux or macOS:

```bash
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Spark is not required because the final datasets are small enough to process efficiently with pandas and scikit-learn.

# Reproducing the Final Results

For exact reproduction of the reported results, use the supplied fixed data files:

```text
data/raw/jobs.csv
data/raw/resumes.csv
data/raw/courses.csv
data/evaluation/human_labels.csv
```

`collect_jobs.py` and `collect_courses.py` remain available for new data collection, but rerunning them at a later date may produce different raw datasets.

Run the complete modelling pipeline with:

```bash
python src/main.py
```

`main.py` executes:

```text
clean_jobs.py
    ↓
clean_resumes.py
    ↓
clean_courses.py
    ↓
baseline_model.py
    ↓
split_data.py
    ↓
build_features.py
    ↓
calculate_gaps.py
    ↓
recommend_courses.py
    ↓
evaluate.py
```

Then run the analysis notebook:

```bash
jupyter notebook notebooks/analysis.ipynb
```

Use **Run All** to reproduce the exploratory analysis, statistical analysis, figures, and final findings.

Randomized operations use:

```python
random_seed = 353
```

# Main Outputs

The pipeline produces:

```text
outputs/tables/baseline_results.csv

outputs/features/tfidf_vectorizer.pkl
outputs/features/development_jobs_tfidf.npz
outputs/features/evaluation_jobs_tfidf.npz
outputs/features/resumes_tfidf.npz
outputs/features/courses_tfidf.npz

outputs/gaps/gap_results.csv
outputs/gaps/gap_vectors.npz

outputs/recommendations/course_recommendations.csv

outputs/evaluation/evaluation_results.csv
```

# Responsible Use

OptiMatch v1 is designed to help users understand text-based resume–job alignment.

It must not be interpreted as:

- An official ATS score.
- A hiring recommendation.
- Proof that a candidate does or does not possess a skill.
- A guarantee that a recommended course teaches every detected skill.
- A guarantee of an interview or job offer.

A skill that is not detected in resume text may still be possessed by the candidate.

The project should therefore be used as a transparent analytical aid rather than an automated hiring decision system.

# Data Privacy

The project may process career-related text and should therefore follow basic privacy principles:

- Do not commit private resumes to a public repository.
- Remove or mask personal information when practical.
- Do not store user-provided career documents unnecessarily.
- Do not use resume content to infer protected personal characteristics.
- Do not train models on private user documents without explicit permission.

The public repository should contain only legally redistributable, sanitized, or synthetic data.

# Limitations

OptiMatch v1 has several important limitations:

- The Muse job sample does not represent the entire technology labour market.
- Broad source categories originally included non-CS jobs and required additional relevance filtering.
- Final job-category sizes are unbalanced.
- Most sampled jobs are mid- or senior-level roles.
- The Kaggle resume dataset may not reflect current applicants.
- Resume text does not directly measure practical technical ability.
- A missing keyword does not necessarily indicate a missing competency.
- Skill extraction depends on the curated technical-skill dictionary.
- TF-IDF measures textual importance rather than semantic mastery.
- Repeated terms may receive excessive importance.
- Only 20 resume–job pairs were manually labelled for final evaluation.
- Human labels are subjective.
- Course descriptions contain much less detail than complete syllabi or learning outcomes.
- Low course similarity may reflect limited course-description detail rather than poor curricular relevance.
- Course similarity does not prove that a course fully addresses a skill gap.
- The model does not reproduce the private ranking logic of commercial ATS products.

# Future Work

OptiMatch v1 provides the analytical foundation for future versions.

Possible extensions include:

- Larger and more balanced technology-job datasets.
- More detailed job-domain classification.
- Larger human-labelled evaluation sets.
- Multiple independent human annotators.
- Contextual embeddings.
- Technical-skill ontologies.
- Required-versus-preferred qualification extraction.
- Broader learning-resource recommendations.
- Interactive resume and job-description input.
- LLM-assisted explanations.
- Resume improvement suggestions.
- Cover-letter analysis.
- A web interface.
- Privacy-focused local document processing.

# Project Highlights

- Built an end-to-end Python/NLP pipeline across **93 CS-related technology jobs, 100 public IT resumes, and 93 SFU Computing courses**.
- Designed an interpretable technical-skill extraction system using a curated skill dictionary and rule-based phrase matching.
- Implemented and compared a keyword-overlap baseline with a shared TF-IDF gap model.
- Evaluated both approaches using **20 manually labelled held-out resume–job pairs**.
- Converted resume–job gap vectors into ranked course recommendations.
- Built reproducible exploratory, statistical, and visualization workflows using pandas, NumPy, SciPy, scikit-learn, Matplotlib, and Seaborn.
- Added a single `main.py` entry point for reproducible end-to-end execution.

# Resume Project Summary

**OptiMatch v1 — Resume–Job Skill Gap Analyzer**

Built a reproducible Python/NLP skill-gap analysis pipeline across **93 CS-related technology jobs, 100 public IT resumes, and 93 SFU Computing courses**, evaluating keyword-overlap and TF-IDF models on **20 manually labelled held-out resume–job pairs** and translating detected skill gaps into ranked learning recommendations.
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