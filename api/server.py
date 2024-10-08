"""Module to initialize and configure FastAPI"""

from dotenv import find_dotenv, dotenv_values
from fastapi import FastAPI, File, UploadFile

from acubed.preprocessing import FFRChartPreprocesser, SMChartPreprocesser

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

@app.post("/process_stepfile")
def upload(file: UploadFile = File(...)):
    """Upload .sm file to streamlit app"""
    # try:
    sm = SMChartPreprocesser()
    result = sm.preprocess(file.file.read().decode('utf-8'))
    # except Exception:
    #     return {"message": "There was an error uploading the file"}
    # finally:
    #     file.file.close()

    return {**result}


# @app.post("/process")
# def get_stepfile(file: bytes = File(...)):
#     """Get segmentation maps from image file"""
#     print(file)

    # segmented_image = get_segments(model, file)
    # bytes_io = io.BytesIO()
    # segmented_image.save(bytes_io, format="PNG")
    # return Response(bytes_io.getvalue(), media_type="image/png")
