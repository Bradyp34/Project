import streamlit as st
from openai import OpenAI
from login import login_page, logout_user  # Importing login and logout functions from login.py
from utils import (
    query_aiml_api, 
    extract_text_from_pdf, 
    split_questions, 
    parse_page_numbers, 
    validate_page_input
)

API_KEY = "5b2403d04b544fae8b4263626dbf3d49"
BASE_URL = "https://api.aimlapi.com/v1"
api = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# Initialize session state variables if they do not exist
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'text_visible' not in st.session_state:
    st.session_state.text_visible = False
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = {}  # Initialize evaluations if not already done

# Function to handle toggling visibility of extracted text
def toggle_text_visibility():
    st.session_state.text_visible = not st.session_state.text_visible

# Main app page with PDF upload and question generation
def main_app():
    st.title(f"Welcome, {st.session_state.username}!")
    st.title("AI/ML GPT-4o-mini Study Question Generator")
    
    # Logout Button
    if st.button("Logout"):
        logout_user()
        st.rerun()  # Trigger rerun to refresh the page and go to the login page

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file:
        page_input = st.text_input("Enter the page numbers (e.g., 1, 5-10, 15):")

        if page_input:
            valid_input, error_msg = validate_page_input(page_input)
            if not valid_input:
                st.warning(error_msg)
            else:
                try:
                    page_numbers = parse_page_numbers(page_input)
                except ValueError as ve:
                    st.warning(str(ve))
                    return

                if st.session_state.extracted_text is None:
                    st.session_state.extracted_text = extract_text_from_pdf(uploaded_file, page_numbers)

                button_label = "Hide Extracted Text" if st.session_state.text_visible else "Show Extracted Text"
                st.button(button_label, on_click=toggle_text_visibility)

                if st.session_state.text_visible and st.session_state.extracted_text:
                    st.subheader("Extracted Text from Selected Pages:")
                    st.text_area("Extracted Text", st.session_state.extracted_text, height=200, disabled=True)

                num_questions = st.number_input("How many questions would you like?", min_value=1, step=1, value=5)

                if st.button("Generate Questions"):
                    system_prompt = (
                        "You are ChatGPT, a large language model trained by OpenAI. "
                        "You are tasked with generating study questions based on provided text. "
                        "Please format the questions as a numbered list, with each question on a new line, "
                        "prefixed by its number and a period (e.g., '1. What is...?'). "
                        "Ensure there are exactly {num_questions} questions."
                    ).format(num_questions=num_questions)
                    
                    user_input = st.session_state.extracted_text or ""
                    if not user_input.strip():
                        st.error("No extracted text available to generate questions from.")
                    else:
                        questions_text = query_aiml_api(api, system_prompt, user_input, num_questions)
                        questions_list = split_questions(questions_text)
                        
                        if len(questions_list) < num_questions:
                            st.warning(f"Expected {num_questions} questions, but only {len(questions_list)} were generated.")
                        
                        st.session_state.questions = questions_list[:num_questions]

    if st.session_state.get("questions"):
        st.subheader("Generated Questions:")
        for i, question in enumerate(st.session_state.questions):
            st.write(f"**Question {i+1}:** {question}")
            answer = st.text_area(
                f"Your Answer for Question {i+1}", 
                value=st.session_state.answers.get(i, ""), 
                height=100
            )
            st.session_state.answers[i] = answer

            if st.button(f"Submit Answer for Question {i+1}"):
                eval_prompt = (
                    "You are ChatGPT, a large language model trained by OpenAI. "
                    "You are tasked with evaluating student answers to study questions. "
                    "Please provide a detailed evaluation of the answer, including strengths, areas for improvement, and overall correctness.\n\n"
                    f"**Question {i+1}:** {question}\n"
                    f"**Answer:** {answer}\n\n"
                    "**Evaluation:**"
                )
                evaluation = query_aiml_api(
                    api, 
                    "You are a helpful assistant that evaluates student answers.", 
                    eval_prompt, 
                    1
                )
                st.session_state.evaluations[i] = evaluation

            if i in st.session_state.evaluations:
                st.text_area(
                    f"**Evaluation for Question {i+1}:**", 
                    st.session_state.evaluations[i], 
                    height=100, 
                    disabled=True
                )

# Main Streamlit app logic
def app():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login_page()  # Show the login page if not logged in
    else:
        main_app()  # Show the main app content if logged in

if __name__ == "__main__":
    app()  # Run the app
