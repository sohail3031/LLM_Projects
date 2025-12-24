import io
import os
import base64

import streamlit as st

from openai import OpenAI
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv

load_dotenv(override=True)
st.set_page_config(layout="wide")

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYSTEM_PROMPT = """
You an helpful text assistance. You analyze the text from the user and answer the query or information the user asked.
Analyze the text and provide a detail explanation on it. Make no grammatical mistakes and the explanation should be in 
fun and engaging way. Provide any necessary examples or references if needed. If you are not sure about anything than 
say so instead of making assumptions.
"""

def _streamlit_ui() -> None:
    st.title("🔉 Aurora SpeakEasy 💬")
    st.subheader("Your personal AI assistant who understand your text and help you with your queries")

    audio_bytes = audio_recorder(text="Click to Give Audio Input", recording_color="#e8b12f", neutral_color="#6aa36f",
                                 icon_size="1.5rem")

    if audio_bytes:
        with open("temp_audio.wav", "wb") as audio_file:
            audio_file.write(audio_bytes)

        with open("temp_audio.wav", "rb") as audio_file:
            audio_response = openai.audio.translations.create(model="whisper-1", file=audio_file)
            user_prompt = f"""
            Analyze the text provided by the user and give a detail explanation for it. Make no grammatical mistakes and
             provide any examples or references in necessary. User Text: {audio_response.text}
            """
            messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
            text_response = openai.chat.completions.create(model="gpt-4.1-mini", messages=messages)

        st.write(text_response.choices[0].message.content)
        os.remove("temp_audio.wav")

if __name__ == '__main__':
    _streamlit_ui()
