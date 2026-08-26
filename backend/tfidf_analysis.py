import html
import re
import joblib
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
try:
    from .extract_skills import get_skill_set, normalize_term
    from .normalize_resume import normalize_resume_text
except ImportError:
    from extract_skills import get_skill_set, normalize_term
    from normalize_resume import normalize_resume_text

# Point to the approved vocabulary
default_vectorizer_file = (
    Path(__file__).resolve().parent.parent
    / 'outputs'
    / 'features'
    / 'tfidf_vectorizer.pkl'
)

# Clean request text while preserving technical punctuation
def clean_job_text(job_description_text):
    value = '' if job_description_text is None else str(job_description_text)
    value = html.unescape(value)
    value = re.sub(r'https?://\S+|www\.\S+', ' ', value, flags=re.IGNORECASE)
    value = re.sub(r'<[^>]+>', ' ', value)
    value = re.sub(r'[^a-z0-9+#./\-\s]', ' ', value.casefold())
    return re.sub(r'\s+', ' ', value).strip()


# Return a short job-description excerpt that supports one ranked technical gap
def build_job_evidence(job_text, skill_name):
    value = job_text.casefold()
    skill = skill_name.casefold()
    position = value.find(skill)
    if position < 0:
        return ''
    evidence_start = max(0, position - 80)
    evidence_end = min(len(job_text), position + len(skill) + 80)
    return job_text[evidence_start:evidence_end].strip()


# Analyze 1 cleaned resume against 1 cleaned job with a persisted approved vectorizer
def analyze_resume_job(
        resume_text,
        job_description_text,
        vectorizer=None,
        vectorizer_file=default_vectorizer_file,
        top_k=5):

    # Validate the request-specific inputs before vectorization
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError('resume_text must be a non-empty string')
    if not isinstance(job_description_text, str) or not job_description_text.strip():
        raise ValueError('job_description_text must be a non-empty string')
    if top_k < 1:
        raise ValueError('top_k must be at least 1')

    # Normalize the uploaded resume and clean the supplied job description separately
    cleaned_resume_text = normalize_resume_text(resume_text).text
    cleaned_job_text = clean_job_text(job_description_text)
    if not cleaned_job_text:
        raise ValueError('job_description_text has no usable text')

    # Load the approved vocabulary
    if vectorizer is None:
        vectorizer = joblib.load(vectorizer_file)
    if not hasattr(vectorizer, 'transform') or not hasattr(vectorizer, 'get_feature_names_out'):
        raise TypeError('vectorizer must be a fitted TF-IDF vectorizer')

    # Transform both documents using exactly the same persisted feature space
    resume_features = vectorizer.transform([cleaned_resume_text])
    job_features = vectorizer.transform([cleaned_job_text])
    similarity = float(cosine_similarity(job_features, resume_features)[0, 0])
    gap_vector = (job_features - resume_features).tocsr()
    gap_vector.data[gap_vector.data < 0] = 0
    gap_vector.eliminate_zeros()

    # Keep only positive gap features that are known technical skills
    feature_names = vectorizer.get_feature_names_out()
    technical_skills = {normalize_term(skill) for skill in get_skill_set()}
    technical_gaps = []
    for feature_index, gap_weight in zip(gap_vector.indices, gap_vector.data):
        feature_name = str(feature_names[feature_index])
        if normalize_term(feature_name) in technical_skills:
            technical_gaps.append((feature_name, float(gap_weight)))
    technical_gaps = sorted(
        technical_gaps,
        key=lambda item: (-item[1], item[0])
    )

    # Rank the strongest gaps and attach evidence from the supplied job description
    ranked_gaps = [
        {
            'skill': skill,
            'weight': round(weight, 6),
            'evidence': build_job_evidence(cleaned_job_text, skill)
        }
        for skill, weight in technical_gaps[:top_k]
    ]

    # Return TF-IDF as a supporting, inspectable signal for the broader scoring system
    return {
        'schema_version': 'optimatch.tfidf',
        'vectorizer_source': 'approved_persisted_vectorizer',
        'cosine_similarity': round(similarity, 6),
        'technical_gap_count': len(technical_gaps),
        'ranked_gaps': ranked_gaps,
        'cleaned_resume_text': cleaned_resume_text,
        'cleaned_job_description': cleaned_job_text
    }
