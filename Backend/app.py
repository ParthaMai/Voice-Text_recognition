from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from transformers import pipeline
from fastapi.responses import FileResponse
import whisper
import os
import shutil
import uuid
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FFMPEG_BIN = r"C:\ffmpeg\bin"
os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ["PATH"]


# Whisper model 
model = whisper.load_model("medium")
# sentiment / semantic understanding
emotion_model = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===== Serve frontend files =====
app.mount("/static", StaticFiles(directory="./Frontend/static"), name="static")

@app.get("/")
def index():
    return FileResponse("./Frontend/index.html")


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] or ".webm"
    file_id = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_id)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = model.transcribe(
            file_path,
            language="en"
        )

        text = result["text"]
        print("text:",text)
        emotions = emotion_model(text)
        print("emotions:",emotions)

        return {
            "text": text,
            "emotion": emotions
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)