# OptiMatch Phase 3 and Phase 4 implementation

## What is implemented

- `backend/temporary_resume_workflow.py` owns the temporary-document lifecycle.
- `backend/resume_normalizer.py` owns normalization and section detection.
- `tests/test_temporary_resume_workflow.py` verifies validation-before-extraction and cleanup.
- `tests/test_resume_normalizer.py` verifies privacy masking, technical punctuation, duplicate text, and sections.
- `pypdf` is the only new extraction dependency.

The existing `backend/clean_resumes.py` remains the public CSV-dataset cleaner. Do not call it for an uploaded PDF: it expects `ID`, `Resume_str`, and `Category` columns and writes a durable CSV.

## Phase 3 request flow

Implement the HTTP route in this order:

1. Read the multipart upload into bytes, enforce the 5 MB limit, and require `application/pdf` when the client supplies a content type.
2. Call `validate_resume_upload` before invoking any PDF parser or LLM.
3. Call `process_temporary_resume(upload_bytes, analyzer)`. It creates a random temporary directory and a generic `upload.pdf`; the original filename is not used.
4. Inside `analyzer`, pass only the returned `NormalizedResume` and the separately validated job-description text to deterministic skill extraction and/or the LLM.
5. Return the structured analysis result. Never return raw resume text, extracted text, the temporary path, or the original filename.
6. Let the workflow exit normally. Its `finally` block drops text references and `TemporaryDirectory` removes the uploaded file on success and failure.
7. Log only metadata such as byte count, event name, error type, and retention status. Do not log request bodies, filenames, extracted text, prompts, or exception strings that may contain document content.

A route adapter should look conceptually like this:

```python
validate_job_description(job_description)
result = process_temporary_resume(
    upload_bytes,
    lambda resume: analyze_normalized_resume(resume, job_description),
    content_type=content_type,
)
return result
```

The client should state the retention rule before submission: “Your resume is used for this analysis only. The uploaded PDF and extracted text are deleted when processing finishes, including after an error. Results are not saved.”

## Phase 4 normalization contract

`normalize_resume_text` performs these transformations in a deterministic order:

1. Unicode NFKC normalization, line-ending normalization, non-breaking-space and hidden-character cleanup.
2. Bullet normalization to `-`.
3. Repeated top/bottom page-margin removal and adjacent duplicate-line removal.
4. Conservative broken-line joining without joining section headings or likely new entries.
5. Optional email and phone masking, enabled by default.
6. Whitespace compaction while preserving technical punctuation such as `C++`, `C#`, `.NET`, `CI/CD`, and `Node.js`.
7. Detection of Summary, Skills, Work experience, Education, Projects, Certifications, Volunteer experience, Awards, and Publications, including common aliases.

The result contains normalized text and section text only. The original extracted text is not stored in the result and should go out of scope immediately after normalization. For production, keep the analyzer callback synchronous or explicitly clear any queued payload before the request ends.

## Verification checklist

- Invalid bytes fail before PDF extraction.
- Oversized files fail before temporary storage.
- Invalid PDFs return a generic error with no filename or raw content.
- Temporary files disappear after both success and failure.
- Logs contain no resume text, job text, filenames, prompts, or raw exception messages.
- Uploaded PDFs and extracted text are absent from repository status and deployment artifacts.
- The UI does not display the filename after analysis completes.
