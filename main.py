import streamlit as st
from openai import OpenAI
# Import the functions from utils
from utils import query_aiml_api, extract_text_from_pdf, split_questions, parse_page_numbers

API_KEY = "5b2403d04b544fae8b4263626dbf3d49"
BASE_URL = "https://api.aimlapi.com/v1"
api = OpenAI(api_key=API_KEY, base_url=BASE_URL)

st.title("AI/ML GPT-4o-mini Study Question Generator")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    page_input = st.text_input("Enter the page numbers (e.g., 1, 5-10, 15):")

    if page_input:
        page_numbers = parse_page_numbers(page_input)
        extracted_text = extract_text_from_pdf(uploaded_file, page_numbers)

        st.subheader("Extracted Text from Selected Pages:")
        st.text_area("Extracted Text", extracted_text, height=200)

        num_questions = st.number_input("How many questions would you like?", min_value=1, step=1)

        if st.button("Generate Questions"):
            system_prompt = f"You are a helpful assistant. Based on the following text, generate {num_questions} study questions:"
            user_input = extracted_text
            questions_text = query_aiml_api(api, system_prompt, user_input, num_questions)

            questions_list = split_questions(questions_text)
            st.session_state.questions = questions_list[:num_questions]
            st.session_state.answers = {}
            st.session_state.evaluations = {}

if st.session_state.get("questions"):
    st.subheader("Generated Questions:")
    for i, question in enumerate(st.session_state.questions):
        st.write(f"Question {i+1}: {question}")
        answer = st.text_area(f"Your Answer for Question {i+1}", value=st.session_state.answers.get(i, ""), height=100)
        st.session_state.answers[i] = answer

        if st.button(f"Submit Answer for Question {i+1}"):
            eval_prompt = (
                f"Please evaluate the following answer and provide feedback.\n\n"
                f"Question: {question}\n"
                f"Answer: {answer}\n"
                f"Provide a detailed evaluation of the answer."
            )
            evaluation = query_aiml_api(api, "You are a helpful assistant that evaluates student answers.", eval_prompt, 1)
            st.session_state.evaluations[i] = evaluation

        if i in st.session_state.evaluations:
            st.text_area(f"Evaluation for Question {i+1}", st.session_state.evaluations[i], height=100, disabled=True)
