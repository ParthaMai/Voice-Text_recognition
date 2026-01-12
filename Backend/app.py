from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import whisper
import os
import shutil
import uuid
import subprocess

app = FastAPI()

# ===== Enable CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== FFmpeg path (self-contained) =====
FFMPEG_BIN = r"C:\ffmpeg\bin"
os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ["PATH"]

# # Patch whisper.audio to use full ffmpeg path
# import whisper.audio as wa

# wa.get_ffmpeg_exe = lambda: FFMPEG_PATH

# ===== Load Whisper model =====
model = whisper.load_model("base")

# ===== Upload folder =====
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===== Serve frontend files =====
app.mount("/static", StaticFiles(directory="./Frontend/static"), name="static")

@app.get("/")
def index():
    return FileResponse("./Frontend/index.html")

# ===== Transcribe endpoint =====
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] or ".webm"
    file_id = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_id)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"Saved file to {file_path}")

        # Transcribe with Whisper (uses patched FFMPEG_PATH)
        result = model.transcribe(file_path)
        print("Transcription result:", result["text"])
        return {"text": result["text"]}
    except Exception as e:
        print("Transcription error:", e)
        return {"error": str(e)}
    # finally:
    #     if os.path.exists(file_path):
    #         os.remove(file_path)
