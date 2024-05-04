"""Module to initialize and configure FastAPI"""

# pylint: disable=no-name-in-module

from dotenv import find_dotenv, dotenv_values
from acubed.preprocessing import FFRChartPreprocesser
from fastapi import FastAPI

app = FastAPI(
    title="ACubed",
    description="""A Redesigned System to Improve Skill Measurement in FlashFlashRevolution.
                           Visit this URL at port 8501 for the streamlit interface.""",
    version="0.1.0",
)

@app.get("/")
async def root():
    """Main FastAPI function"""
    config = {
        **dotenv_values(find_dotenv())
    }
    print(FFRChartPreprocesser)
    return config


# @app.post("/segmentation")
# def get_segmentation_map(file: bytes = File(...)):
#     """Get segmentation maps from image file"""
#     segmented_image = get_segments(model, file)
#     bytes_io = io.BytesIO()
#     segmented_image.save(bytes_io, format="PNG")
#     return Response(bytes_io.getvalue(), media_type="image/png")
