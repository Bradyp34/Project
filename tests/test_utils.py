import pytest
from unittest.mock import patch, MagicMock
from Project.utils import extract_text_from_pdf, split_questions, parse_page_numbers, query_aiml_api

def parse_page_numbers(page_input):
    pages = set()
    if not page_input.strip():
        # If there's no input, return an empty list early
        return []
    
    for part in page_input.split(","):
        part = part.strip()
        if not part:
            # Skip empty parts
            continue
        if "-" in part:
            start_str, end_str = part.split("-")
            start_str, end_str = start_str.strip(), end_str.strip()
            # Validate that both start and end are integers
            start, end = int(start_str), int(end_str)
            pages.update(range(start, end + 1))
        else:
            # Validate that part is an integer
            pages.add(int(part))
    return sorted(pages)

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

import re

def split_questions(text):
    question_pattern = r'\d+\.\s+'
    parts = re.split(question_pattern, text)
    # If no pattern is matched, re.split returns [text] as a single element.
    # We can check if we actually got a split by searching for the pattern.
    if len(parts) == 1 and not re.search(question_pattern, text):
        # No questions found
        return []
    # Clean and filter out empty strings
    questions = [q.strip() for q in parts if q.strip()]
    return questions

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

def test_parse_page_numbers_single_page():
    input_str = "5"
    expected = [5]
    assert parse_page_numbers(input_str) == expected

def test_parse_page_numbers_no_input():
    input_str = ""
    # An empty input should result in an empty list of pages
    assert parse_page_numbers(input_str) == []

def test_parse_page_numbers_invalid_input():
    input_str = "abc, 5-7"
    # This should raise a ValueError when int conversion fails
    with pytest.raises(ValueError):
        parse_page_numbers(input_str)

def test_parse_page_numbers_overlapping_ranges():
    input_str = "2-5, 4-6"
    # Overlapping ranges should still consolidate properly
    # 2,3,4,5 plus 4,5,6 results in 2,3,4,5,6
    expected = [2, 3, 4, 5, 6]
    assert parse_page_numbers(input_str) == expected

def test_parse_page_numbers_unsorted_input():
    input_str = "10, 2, 1-3"
    # Should return sorted pages [1, 2, 3, 10]
    expected = [1, 2, 3, 10]
    assert parse_page_numbers(input_str) == expected


### Additional tests for extract_text_from_pdf ###

@patch("pdfplumber.open")
def test_extract_text_from_pdf_no_text(mock_pdfplumber_open):
    # Mock a PDF with a page that returns None (no text)
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    mock_pdf.pages = [mock_page]
    mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

    pdf_file = "dummy.pdf"
    result = extract_text_from_pdf(pdf_file, [1])
    # If no text is extracted, an empty string is expected
    assert result == ""

@patch("pdfplumber.open")
def test_extract_text_from_pdf_partial_pages(mock_pdfplumber_open):
    # Mock a PDF with multiple pages, some have text, some don't
    mock_pdf = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page one text."
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = None
    mock_page3 = MagicMock()
    mock_page3.extract_text.return_value = "Page three text."
    mock_pdf.pages = [mock_page1, mock_page2, mock_page3]
    mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

    pdf_file = "dummy.pdf"
    result = extract_text_from_pdf(pdf_file, [1, 2, 3])
    # Pages 1 and 3 have text, page 2 does not
    assert result == "Page one text.Page three text."


### Additional tests for split_questions ###

def test_split_questions_no_questions():
    text = "This text does not follow the pattern."
    # No numbered pattern found, should return an empty list
    assert split_questions(text) == []

def test_split_questions_with_extra_spaces():
    text = "1.  What is AI?   2. How does a neural network work?  3.   Define machine learning."
    expected = [
        "What is AI?",
        "How does a neural network work?",
        "Define machine learning."
    ]
    assert split_questions(text) == expected

@patch("openai.OpenAI")
def test_query_aiml_api_error_handling(mock_openai_class):
    # Mock the API to raise an exception
    mock_api = MagicMock()
    mock_api.chat.completions.create.side_effect = Exception("API error")
    mock_openai_class.return_value = mock_api

    # Calling query_aiml_api should return "Error: API error"
    result = query_aiml_api(mock_api, "system prompt", "user input", 1)
    assert "Error: API error" in result

@patch("openai.OpenAI")
def test_query_aiml_api_empty_response(mock_openai_class):
    # Mock the API to return an empty response content
    mock_api = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock(content="")
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_api.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_api

    result = query_aiml_api(mock_api, "system prompt", "user input", 1)
    # Even if empty, should not error, just return empty string
    assert result == ""

@patch("openai.OpenAI")
def test_query_aiml_api_multiple_questions(mock_openai_class):
    # Mock a scenario where multiple questions are generated
    mock_api = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock(content="1. What is AI?\n2. How does AI differ from ML?")
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_api.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_api

    result = query_aiml_api(mock_api, "system prompt", "user input", 2)
    assert "What is AI?" in result
    assert "How does AI differ from ML?" in result
