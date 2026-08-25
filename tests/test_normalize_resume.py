from backend.normalize_resume import normalize_resume_text


# Ensure privacy masking, section detection, and technical punctuation preservation.
def test_resume_normalizer_preserves_technical_terms():
    result = normalize_resume_text(
        'Skills\nC++, C#, .NET, CI/CD, Node.js\n\n'
        'Education\nSimon Fraser University\n\n'
        'alex@example.com\n+1 (604) 555-0199'
    )
    assert 'C++' in result.text
    assert 'C#' in result.text
    assert '.NET' in result.text
    assert 'CI/CD' in result.text
    assert 'Node.js' in result.text
    assert '[EMAIL]' in result.text
    assert '[PHONE]' in result.text
    assert result.sections['skills'] == 'C++, C#, .NET, CI/CD, Node.js'
