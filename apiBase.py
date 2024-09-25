import streamlit as st
from openai import OpenAI

# Set your AI/ML API key and base URL
API_KEY = "5b2403d04b544fae8b4263626dbf3d49"  # Replace with your actual API key
BASE_URL = "https://api.aimlapi.com/v1"

# Initialize the OpenAI API instance
api = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# Define system and user prompts
system_prompt = "You are a helpful assistant for generating study questions."
user_prompt = ""

# Function to interact with AI/ML API (GPT-4o-mini model)
def query_aiml_api(user_input):
    try:
        completion = api.chat.completions.create(
            model="gpt-4o-mini",  # Use the correct model name from AI/ML
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Extract the response text
        response = completion.choices[0].message.content
        return response.strip()
    
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit app setup
st.title("AI/ML GPT-4o-mini Integration")

# Input text box to interact with the AI
user_input = st.text_input("Speak with the AI:", "")

# When the user presses the "Send" button, get the response from the API
if st.button("Send"):
    if user_input:
        response = query_aiml_api(user_input)
        st.text(response)
    else:
        st.text("Please enter a message to test the AI.")

if st.button("Cancel"):
    st.stop()
