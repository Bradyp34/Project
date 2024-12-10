import re
import pdfplumber

def query_aiml_api(api, system_prompt, user_input, num_questions):
    try:
        completion = api.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please generate exactly {num_questions} study questions based on the following text:\n{user_input}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        response = completion.choices[0].message.content
        return response.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_from_pdf(pdf_file, page_numbers):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        total_pages = len(pdf.pages)
        for page_num in page_numbers:
            if 1 <= page_num <= total_pages:
                page = pdf.pages[page_num - 1]
                extracted = page.extract_text()
                if extracted:
                    text += extracted
            else:
                # We won't rely on Streamlit warnings during tests
                pass
    return text

def split_questions(text):
    question_pattern = r'\d+\.\s+'
    questions = re.split(question_pattern, text)
    questions = [q.strip() for q in questions if q.strip()]
    return questions

def parse_page_numbers(page_input):
    pages = set()
    for part in page_input.split(","):
        part = part.strip()
        if "-" in part:
            start, end = map(int, part.split("-"))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted(pages)
