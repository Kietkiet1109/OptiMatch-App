from src.clean_text import clean_text


def test_html_is_removed() -> None:
    result = clean_text("<p>Python and SQL</p>")
    assert result == "python and sql"


def test_technical_tokens_are_preserved() -> None:
    result = clean_text("C++ C# Node.js .NET")
    assert "c++" in result
    assert "c#" in result
    assert "node.js" in result
    assert ".net" in result


def test_whitespace_is_normalized() -> None:
    result = clean_text("Python\n\n   SQL")
    assert result == "python sql"
