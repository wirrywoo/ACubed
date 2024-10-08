"""Module to initialize and configure Streamlit app"""

import requests
from requests_toolbelt import MultipartEncoder
import streamlit as st

# # interact with FastAPI endpoint
BACKEND = "http://localhost:8000/process_stepfile"

def process(stepfile, server_url: str):
    "Processes .sm file"
    m = MultipartEncoder(
        fields={'file': ('filename', stepfile, 'text/plain')}
    )

    r = requests.post(
        server_url, data=m, headers={"Content-Type": m.content_type}, timeout=8000
    )

    return r

with open( "./ui/style.css", encoding='utf-8' ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

# construct UI layout
st.title("FFR Difficulty Model")

st.markdown(
    """A Redesigned System to Improve Skill Measurement in FlashFlashRevolution.
        This streamlit app uses a FastAPI service as backend.
        Visit this URL at `:8000/docs` for FastAPI documentation."""
)  # description and instructions

input_sm = st.file_uploader(r"$\textsf{\footnotesize Insert Stepfile (.sm)}$")  # image upload widget

# print(requests.get("http://localhost:8000/"))

if st.button("Get raw data"):

    if input_sm:
        segments = process(input_sm.read(), BACKEND)
        st.json(segments.json())
    else:
        # handle case with no image
        st.write("Insert stepfile!", unsafe_allow_html = True)
