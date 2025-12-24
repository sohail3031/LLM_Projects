import base64
import os

import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI

def encode_image(uploaded_image):
    return base64.b64encode(uploaded_image.getvalue()).decode("utf-8")

load_dotenv(override=True)
st.set_page_config(layout="wide")

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYSTEM_PROMPT = """
You are an AI Chatbot who analyze the provided image by the user and provide detail insights of the image. Analyze the 
image and explain whats there in the image in detail with examples and references if needed for the explanation. Make 
no grammatical mistakes in the response and the output should be in fun and engaging tone for the users. If you are not 
sure about the image then say so instead of making assumptions.
"""

USER_PROMPT = """
Analyze the uploaded image and provide a detail insight about it. Make no grammatical mistake in the output. Make the 
output fun and engaging for the user. The output should be in detail and user examples and references if necessary.
"""

st.title("AI Image Analyzer")

uploaded_file = st.file_uploader("Choose an image to upload", type=["png", "jpg", "jpeg", "webp"])

generate_button = st.button("Analyze")

if generate_button:
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image")

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": USER_PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{uploaded_file.type};base64,{encode_image(uploaded_file)}"
                        }
                    }
                ]
            }
        ]
        response = openai.chat.completions.create(model="gpt-4.1-mini", messages=messages, temperature=0.2)

        st.write(response.choices[0].message.content)
    else:
        st.text("Please upload an image")
