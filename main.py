import re
import streamlit as st
import pdfplumber  # pdfplumber for PDF text extraction
from openai import OpenAI

# Set your AI/ML API key and base URL
API_KEY = "5b2403d04b544fae8b4263626dbf3d49"  # Replace with your actual API key
BASE_URL = "https://api.aimlapi.com/v1"

# Initialize the OpenAI API instance
api = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# Function to interact with AI/ML API (GPT-4o-mini model)
def query_aiml_api(system_prompt, user_input, num_questions):
    try:
        completion = api.chat.completions.create(
            model="gpt-4o-mini",  # Use the correct model name from AI/ML
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please generate exactly {num_questions} study questions based on the following text:\n{user_input}"},
            ],
            temperature=0.7,
            max_tokens=500  # Adjust based on response length needed
        )
        response = completion.choices[0].message.content
        return response.strip()
    
    except Exception as e:
        return f"Error: {str(e)}"

# Function to extract text from specific pages of a PDF file using pdfplumber
def extract_text_from_pdf(pdf_file, page_numbers):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        total_pages = len(pdf.pages)
        # Iterate through the user-specified page numbers and extract text
        for page_num in page_numbers:
            if 1 <= page_num <= total_pages:
                page = pdf.pages[page_num - 1]  # Pages are zero-indexed in pdfplumber
                text += page.extract_text()
            else:
                st.warning(f"Page {page_num} is out of range (PDF has {total_pages} pages).")
    return text

# Function to split questions based on numbered pattern
def split_questions(text):
    # Regex pattern to split based on questions starting with numbers (1., 2., etc.)
    question_pattern = r'\d+\.\s+'
    questions = re.split(question_pattern, text)
    # Remove empty strings caused by split
    questions = [q.strip() for q in questions if q.strip()]
    return questions

# Initialize session state if not already done
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "evaluations" not in st.session_state:
    st.session_state.evaluations = {}

# Streamlit app setup
st.title("AI/ML GPT-4o-mini Study Question Generator")

# Step 1: File uploader for full-size PDFs (books)
uploaded_file = st.file_uploader("Upload a PDF file (e.g., full-size book)", type="pdf")

if uploaded_file:
    # Step 2: User specifies which pages they want to extract
    page_input = st.text_input("Enter the page numbers you want to extract (e.g., 1, 5-10, 15):")
    
    if page_input:
        # Parse the page numbers from user input (e.g., "1, 5-10, 15")
        def parse_page_numbers(page_input):
            pages = set()
            for part in page_input.split(","):
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    pages.update(range(start, end + 1))
                else:
                    pages.add(int(part))
            return sorted(pages)
        
        page_numbers = parse_page_numbers(page_input)
        
        # Extract text from the specified pages
        extracted_text = extract_text_from_pdf(uploaded_file, page_numbers)
        
        # Display the extracted text for user preview (optional)
        st.subheader("Extracted Text from Selected Pages:")
        st.text_area("Extracted Text", extracted_text, height=200)
        
        # Step 3: User inputs the number of questions they want to generate
        num_questions = st.number_input("How many questions would you like to generate?", min_value=1, step=1)

        if st.button("Generate Questions"):
            # Generate test questions based on the extracted text
            system_prompt = f"You are a helpful assistant. Based on the following text, generate {num_questions} study questions:"
            user_input = extracted_text
            questions_text = query_aiml_api(system_prompt, user_input, num_questions)
            
            # Split the generated questions
            questions_list = split_questions(questions_text)
            
            # Ensure we only display as many questions as requested
            st.session_state.questions = questions_list[:num_questions]
            st.session_state.answers = {}  # Reset answers when generating new questions
            st.session_state.evaluations = {}  # Reset evaluations when generating new questions

# Step 4: Display generated questions and collect answers
if st.session_state.questions:
    st.subheader("Generated Questions:")
    for i, question in enumerate(st.session_state.questions):
        st.write(f"Question {i+1}: {question}")
        
        # Display an auto-expanding text area for the answer
        answer = st.text_area(f"Your Answer for Question {i+1}", value=st.session_state.answers.get(i, ""), height=100)
        
        # Store the answer in session state
        st.session_state.answers[i] = answer

        # Submit button for each individual question
        if st.button(f"Submit Answer for Question {i+1}"):
            # Improved evaluation prompt
            eval_prompt = (
                f"Please evaluate the following answer and provide feedback.\n\n"
                f"Question: {question}\n"
                f"Answer: {answer}\n"
                f"Provide a detailed evaluation of the answer, including correctness and any suggestions for improvement."
            )
            
            # Get the evaluation from the AI
            evaluation = query_aiml_api(system_prompt="You are a helpful assistant that evaluates student answers.", user_input=eval_prompt, num_questions=1)
            
            # Store the evaluation in session state
            st.session_state.evaluations[i] = evaluation
        
        # Display the evaluation if it exists
        if i in st.session_state.evaluations:
            st.text_area(f"Evaluation for Question {i+1}", st.session_state.evaluations[i], height=100, disabled=True)
