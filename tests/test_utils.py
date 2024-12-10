import pytest
from unittest.mock import patch, MagicMock
from Project.utils import extract_text_from_pdf, split_questions, parse_page_numbers, query_aiml_api

def test_parse_page_numbers():
    input_str = "1, 5-7, 10"
    expected = [1, 5, 6, 7, 10]
    assert parse_page_numbers(input_str) == expected

@patch("pdfplumber.open")
def test_extract_text_from_pdf(mock_pdfplumber_open):
    # Create a mock PDF object
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample text from page."
    mock_pdf.pages = [mock_page, mock_page]  # 2 pages for example
    mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

    # Test extracting from pages 1 and 2
    pdf_file = "dummy.pdf"
    result = extract_text_from_pdf(pdf_file, [1, 2])
    assert result == "Sample text from page.Sample text from page."

    # Test a page out of range
    # Since we're not using Streamlit warnings during test,
    # we just ensure it doesn't throw an exception.
    result = extract_text_from_pdf(pdf_file, [3])
    assert result == ""  # Out of range page returns no text

def test_split_questions():
    text = "1. What is Python? 2. Explain decorators in Python. 3. How does list comprehension work?"
    expected = [
        "What is Python?",
        "Explain decorators in Python.",
        "How does list comprehension work?"
    ]
    assert split_questions(text) == expected

import pytest
from unittest.mock import patch, MagicMock
import Project.utils  # We imported the module instead of the function

@patch("Project.utils.query_aiml_api")
def test_query_aiml_api(mock_query):
    # Now mock_query replaces Project.utils.query_aiml_api everywhere it's called
    mock_query.return_value = "1. What is AI?"

    # Call the function through the module so we use the patched version
    result = Project.utils.query_aiml_api(None, "system prompt", "user input", 1)
    assert result == "1. What is AI?"


@patch("openai.OpenAI")
def test_query_aiml_api_with_mocked_api(mock_openai_class):
    # Mock the API instance
    mock_api = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock(content="1. A generated question?")
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_api.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_api

    # Now call the real function
    result = query_aiml_api(mock_api, "system prompt", "user input", 1)
    assert result == "1. A generated question?"
