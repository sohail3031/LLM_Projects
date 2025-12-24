import os
import io

import streamlit as st

from openai import OpenAI
from dotenv import load_dotenv
from gtts import gTTS
from streamlit_carousel import carousel

load_dotenv(override=True)

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYSTEM_PROMPT = """
You are an helpful Blog Writing ChatBot and an English expert. You help users to write their blogs based on the title, 
keywords, and blog length should be no more than the given length. Your blog should contain all the keywords and 
necessary information with examples and references if needed. The blog explanation should be in a fun and engaging. Make
 no grammatical mistakes and make sure the blog should be easy to read.
"""

st.set_page_config(layout="wide")
st.title("🤖 BlogForge AI")
st.subheader("Your personal AI that writes blogs for you ✍️")

with st.sidebar:
    st.title("Enter Blog Details")

    blog_title: str = st.text_input("Enter Blog Title: ")
    blog_keywords: str = st.text_area("Enter Blog Keywords: ")
    blog_length: int = st.slider("Select Blog Length: ", min_value=100, max_value=1000, step=50)
    blog_images: int = st.number_input("Select Number of Images to be Selected: ", min_value=0, max_value=5, step=1)
    blog_audio: str = st.radio("Want Audio for Blog?", ("Yes", "No"), index=1, help="Select Yes or No")

    USER_PROMPT = f"""
    Generate a detail blog on {blog_title} using the keywords {blog_keywords} in or under {blog_length} words. The blog 
    content should be fun and engaging for the users. Provide examples and references if necessary. 
    """

    generate = st.button("Generate Blog")

if generate:
    if blog_images > 0:
        st.subheader("\n\n\nImages" if {blog_images > 1} else "\n\n\nImage")

        generated_images = []

        for i in range(blog_images):
            image = openai.images.generate(model="dall-e-2", prompt=f"Generate an image on the title {blog_title}.", size="1024x1024", n=1)
            generated_images.append(dict(title=image.data[0].url.title(), text=f"An image on {blog_title}", img=image.data[0].url))

        carousel(items=generated_images)

    st.subheader(f"\n\n\nBlog on: {blog_title}")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": USER_PROMPT}]
    response = openai.chat.completions.create(model="gpt-4.1-mini", messages=messages)

    st.write(response.choices[0].message.content)

    if blog_audio.__eq__("Yes"):
        print(f"Blog Audio: {blog_audio}")

        tts = gTTS(text=response.choices[0].message.content, lang="en")
        audio_fp = io.BytesIO()

        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)

        st.subheader("\n\n\nAudio")
        st.audio(audio_fp, format="audio/mp3")
