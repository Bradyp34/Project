import streamlit as st
from transformers import pipeline

# Ensure you are using the PyTorch model of bigscience/bloom
generator = pipeline('text-generation', model='bigscience/bloom', framework='pt')

# Title of the app
st.title("Study.AI")

# Read-only output textbox
output = st.empty()

# Input text box
user_input = st.text_input("Enter your message:", "")

# Function to generate a response using the transformers model
def get_transformers_response(prompt):
    try:
        # Generate a response with Hugging Face model
        response = generator(prompt, max_length=100, num_return_sequences=1)
        return response[0]['generated_text'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# When the user presses Enter or clicks the "Send" button, generate the response and display it
if st.button("Send"):
    if user_input:
        response = get_transformers_response(user_input)
        output.text(response)
    else:
        output.text("Please enter a message.")

if st.button("Cancel"):
    st.stop()
