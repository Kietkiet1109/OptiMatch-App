from pathlib import Path
import pytest
from backend.analysis import validate_resume as workflow

# Ensure invalid input is rejected before the PDF parser is called.
def test_invalid_resume_is_rejected_before_extraction(monkeypatch):
    def fail_if_called(_):
        raise AssertionError('extraction must not run')

    monkeypatch.setattr(workflow, 'extract_pdf_text', fail_if_called)
    with pytest.raises(workflow.ResumeValidationError):
        workflow.process_temporary_resume(b'not a pdf', lambda normalized_resume: normalized_resume)


# Ensure the analyzer receives normalized text and the temporary file is deleted.
def test_resume_is_extracted_and_deleted(monkeypatch):
    observed_path: list[Path] = []

    def fake_extract(pdf_path: Path) -> str:
        observed_path.append(pdf_path)
        assert pdf_path.exists()
        return 'Skills\nPython\nemail@example.com'

    monkeypatch.setattr(workflow, 'extract_pdf_text', fake_extract)
    result = workflow.process_temporary_resume(
        b'%PDF-1.7 test',
        lambda normalized_resume: normalized_resume.text,
    )
    assert result == 'Skills\nPython\n[EMAIL]'
    assert not observed_path[0].exists()
