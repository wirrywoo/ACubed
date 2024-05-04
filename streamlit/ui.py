"""Module to initialize and configure Streamlit app"""

# pylint: disable=c-extension-no-member

import requests
import streamlit as st

# # interact with FastAPI endpoint
# backend = "http://fastapi:8000/segmentation"


# def process(image, server_url: str):

#     m = MultipartEncoder(fields={"file": ("filename", image, "image/jpeg")})

#     r = requests.post(
#         server_url, data=m, headers={"Content-Type": m.content_type}, timeout=8000
#     )

#     return r


# construct UI layout
st.title("ACubed Rating System")

st.write(
    """A Redesigned System to Improve Skill Measurement in FlashFlashRevolution.
         This streamlit app uses a FastAPI service as backend.
         Visit this URL at `:8000/docs` for FastAPI documentation."""
)  # description and instructions

input_image = st.file_uploader("Insert Stepfile (.sm)")  # image upload widget

print(requests.get("http://localhost:8000/"))

# if st.button("Get segmentation map"):

#     col1, col2 = st.columns(2)

#     if input_image:
#         segments = process(input_image, backend)
#         original_image = Image.open(input_image).convert("RGB")
#         segmented_image = Image.open(io.BytesIO(segments.content)).convert("RGB")
#         col1.header("Original")
#         col1.image(original_image, use_column_width=True)
#         col2.header("Segmented")
#         col2.image(segmented_image, use_column_width=True)

#     else:
#         # handle case with no image
#         st.write("Insert an image!")
