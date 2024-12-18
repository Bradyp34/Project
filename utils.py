import re
import pdfplumber

def query_aiml_api(api, system_prompt, user_input, num_questions):
    """
    Query the AIML API to generate a list of study questions or evaluate answers.

    Parameters:
        api: The OpenAI-like API client.
        system_prompt (str): The system message that provides instructions to the model.
        user_input (str): The text from which we need to generate questions.
        num_questions (int): The number of questions or outputs expected.

    Returns:
        str: The response from the model.
    """
    try:
        completion = api.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=1500  # Increased max_tokens to accommodate more detailed outputs
        )
        response = completion.choices[0].message.content
        return response.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_from_pdf(pdf_file, page_numbers):
    """
    Extract text from specified pages of a given PDF file.

    Parameters:
        pdf_file: The PDF file (uploaded through Streamlit).
        page_numbers (list of int): The specific pages to extract text from.

    Returns:
        str: Extracted text from the requested pages concatenated into a single string.
    """
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        total_pages = len(pdf.pages)
        for page_num in page_numbers:
            if 1 <= page_num <= total_pages:
                page = pdf.pages[page_num - 1]
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            else:
                # Log or handle out-of-range page numbers if necessary
                pass
    return text

def split_questions(text):
    """
    Split the generated text into individual questions.

    Assumes questions are numbered like:
    1. Question one?
    2. Question two?

    Parameters:
        text (str): The text containing the questions.

    Returns:
        list: A list of question strings.
    """
    # Regex to match numbering at the beginning of lines
    question_pattern = r'^\d+\.\s+'
    questions = []
    
    # Split the text into lines
    lines = text.split('\n')
    current_question = ""
    
    for line in lines:
        if re.match(question_pattern, line):
            if current_question:
                questions.append(current_question.strip())
            # Remove the numbering
            current_question = re.sub(question_pattern, '', line, count=1)
        else:
            current_question += ' ' + line.strip()
    
    if current_question:
        questions.append(current_question.strip())
    
    # Filter out any empty questions
    questions = [q for q in questions if q]
    
    return questions

def parse_page_numbers(page_input):
    """
    Parse page input strings (e.g. "1, 5-7, 10") into a sorted list of page numbers.

    Parameters:
        page_input (str): The string containing page specifications.

    Returns:
        list of int: A sorted list of unique page numbers.
    
    Raises:
        ValueError: If a page range is invalid (start > end).
    """
    pages = set()
    if not page_input.strip():
        return []
    
    for part in page_input.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_str, end_str = part.split("-")
            start_str, end_str = start_str.strip(), end_str.strip()
            if not (start_str.isdigit() and end_str.isdigit()):
                raise ValueError(f"Invalid page range: {part}. Both start and end must be integers.")
            start, end = int(start_str), int(end_str)
            if start > end:
                raise ValueError(f"Start page {start} cannot be greater than end page {end}.")
            pages.update(range(start, end + 1))
        else:
            # Only add if not empty and is a valid integer
            if not part.isdigit():
                raise ValueError(f"Invalid page number: {part}. Must be an integer.")
            pages.add(int(part))
    return sorted(pages)

def validate_page_input(page_input):
    """
    Validate the page input to ensure it contains valid ranges and integers.
    
    Parameters:
        page_input (str): The page input string from user.

    Returns:
        (bool, str): A tuple containing a boolean (valid or not) and an error message if invalid.
    """
    if not page_input.strip():
        return False, "Page input cannot be empty."

    # Check each segment
    for part in page_input.split(","):
        part = part.strip()
        if part:
            if "-" in part:
                split_part = part.split("-")
                if len(split_part) != 2:
                    return False, f"Invalid page range: {part}."
                start_str, end_str = split_part
                if not (start_str.isdigit() and end_str.isdigit()):
                    return False, f"Page range must contain integers only: {part}."
                if int(start_str) > int(end_str):
                    return False, f"Start page cannot be greater than end page in: {part}."
            else:
                # Single page
                if not part.isdigit():
                    return False, f"Invalid page number: {part}."
        else:
            return False, "Empty page specification found."

    return True, ""  # Valid input
