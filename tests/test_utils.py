# test_utils.py

import pytest
from unittest.mock import patch, MagicMock
from Project.utils import (
    extract_text_from_pdf,
    split_questions,
    parse_page_numbers,
    query_aiml_api
)

import re

### Tests for `extract_text_from_pdf` ###

@patch("pdfplumber.open")
def test_extract_text_from_pdf(mock_pdfplumber_open):
    """
    Test extracting text from specified pages in a PDF.
    Ensures that text from multiple pages is concatenated with newline characters.
    """
    # Create a mock PDF object
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample text from page."
    mock_pdf.pages = [mock_page, mock_page]  # 2 pages for example
    mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

    # Test extracting from pages 1 and 2
    pdf_file = "dummy.pdf"
    result = extract_text_from_pdf(pdf_file, [1, 2])
    assert result == "Sample text from page.\nSample text from page.\n"

    # Test a page out of range
    result = extract_text_from_pdf(pdf_file, [3])
    assert result == ""  # Out of range page returns no text

@patch("pdfplumber.open")
def test_extract_text_from_pdf_no_text(mock_pdfplumber_open):
    """
    Test extracting text from a PDF page that returns None (no text).
    """
    # Mock a PDF with a page that returns None (no text)
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    mock_pdf.pages = [mock_page]
    mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

    pdf_file = "dummy.pdf"
    result = extract_text_from_pdf(pdf_file, [1])
    assert result == ""  # No text extracted

@patch("pdfplumber.open")
def test_extract_text_from_pdf_partial_pages(mock_pdfplumber_open):
    """
    Test extracting text from multiple pages where some pages have text and others do not.
    """
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
    assert result == "Page one text.\nPage three text.\n"

### Tests for `split_questions` ###

def test_split_questions_with_newlines():
    """
    Test splitting text where questions are separated by newlines.
    """
    text = "1. What is AI?\n2. How does it work?\n3. Explain machine learning."
    expected = [
        "What is AI?",
        "How does it work?",
        "Explain machine learning."
    ]
    assert split_questions(text) == expected

### Tests for `parse_page_numbers` ###

def test_parse_page_numbers_single_page():
    """
    Test parsing a single page number.
    """
    input_str = "5"
    expected = [5]
    assert parse_page_numbers(input_str) == expected

def test_parse_page_numbers_no_input():
    """
    Test parsing when no input is provided.
    """
    input_str = ""
    assert parse_page_numbers(input_str) == []

def test_parse_page_numbers_invalid_input():
    """
    Test parsing with invalid input containing non-integer values.
    Should raise a ValueError.
    """
    input_str = "abc, 5-7"
    with pytest.raises(ValueError):
        parse_page_numbers(input_str)

def test_parse_page_numbers_overlapping_ranges():
    """
    Test parsing with overlapping page ranges.
    """
    input_str = "2-5, 4-6"
    expected = [2, 3, 4, 5, 6]
    assert parse_page_numbers(input_str) == expected

def test_parse_page_numbers_unsorted_input():
    """
    Test parsing with unsorted page numbers and ranges.
    """
    input_str = "10, 2, 1-3"
    expected = [1, 2, 3, 10]
    assert parse_page_numbers(input_str) == expected

def test_parse_page_numbers_large_range():
    """
    Test parsing with large page ranges.
    """
    input_str = "1-3, 100-102"
    expected = [1, 2, 3, 100, 101, 102]
    assert parse_page_numbers(input_str) == expected

def test_parse_page_numbers_extra_spaces():
    """
    Test parsing with extra spaces around numbers and ranges.
    """
    input_str = "  4 - 6  ,  10 ,   12 -15 "
    expected = [4, 5, 6, 10, 12, 13, 14, 15]
    assert parse_page_numbers(input_str) == expected

def test_parse_page_numbers_invalid_range():
    """
    Test parsing with an invalid range where the start is greater than the end.
    Should raise a ValueError.
    """
    input_str = "10-8"
    with pytest.raises(ValueError):
        parse_page_numbers(input_str)

### Tests for `query_aiml_api` ###

@patch("openai.OpenAI")
def test_query_aiml_api_with_mocked_api(mock_openai_class):
    """
    Test `query_aiml_api` by mocking the OpenAI API's response.
    """
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

@patch("openai.OpenAI")
def test_query_aiml_api_error_handling(mock_openai_class):
    """
    Test `query_aiml_api` handling when the API raises an exception.
    """
    # Mock the API to raise an exception
    mock_api = MagicMock()
    mock_api.chat.completions.create.side_effect = Exception("API error")
    mock_openai_class.return_value = mock_api

    # Calling query_aiml_api should return "Error: API error"
    result = query_aiml_api(mock_api, "system prompt", "user input", 1)
    assert "Error: API error" in result

@patch("openai.OpenAI")
def test_query_aiml_api_empty_response(mock_openai_class):
    """
    Test `query_aiml_api` when the API returns an empty response.
    """
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
    """
    Test `query_aiml_api` when the API returns multiple questions.
    """
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

@patch("openai.OpenAI")
def test_query_aiml_api_no_questions(mock_openai_class):
    """
    Test `query_aiml_api` when the number of questions requested is zero.
    Should handle gracefully and return an empty string.
    """
    # If num_questions is zero (even if not logical), check behavior
    # We assume the function still tries to call the API.
    mock_api = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock(content="")
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_api.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_api

    # Even though 0 questions may not make sense, we handle gracefully
    result = query_aiml_api(mock_api, "system prompt", "user input", 0)
    assert result == ""

@patch("openai.OpenAI")
def test_query_aiml_api_special_characters(mock_openai_class):
    """
    Test `query_aiml_api` handling of special characters in user input.
    """
    # Test handling of special characters in user_input
    mock_api = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    content = "1. ¿Qué es la IA?\n2. Décrire l'apprentissage automatique?"
    mock_message = MagicMock(content=content)
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_api.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_api

    result = query_aiml_api(mock_api, "system prompt", "¿Qué es la IA? Décrire l'AA?", 2)
    assert "¿Qué es la IA?" in result
    assert "Décrire l'apprentissage automatique?" in result

### Additional Tests for Robustness ###

@patch("openai.OpenAI")
def test_query_aiml_api_empty_user_input(mock_openai_class):
    """
    Test `query_aiml_api` when the user input is empty.
    Should return an empty string or handle accordingly.
    """
    mock_api = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock(content="")
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_api.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_api

    result = query_aiml_api(mock_api, "system prompt", "", 1)
    assert result == ""

@patch("openai.OpenAI")
def test_query_aiml_api_high_num_questions(mock_openai_class):
    """
    Test `query_aiml_api` when requesting a high number of questions.
    """
    mock_api = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    # Simulate a response with 10 questions
    content = "\n".join([f"{i}. Question {i}?" for i in range(1, 11)])
    mock_message = MagicMock(content=content)
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_api.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_api

    result = query_aiml_api(mock_api, "system prompt", "user input", 10)
    for i in range(1, 11):
        assert f"{i}. Question {i}?" in result

