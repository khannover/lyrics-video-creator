import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Bancamp Studio V4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RENDER_DIR = Path("renders")
RENDER_DIR.mkdir(exist_ok=True)


@app.post("/api/start")
async def start_session():
    session_id = str(uuid.uuid4())[:8]
    session_dir = RENDER_DIR / session_id / "frames"
    session_dir.mkdir(parents=True, exist_ok=True)
    return {"session_id": session_id}


@app.post("/api/frame/{session_id}")
async def upload_frame(
    session_id: str,
    frame_index: int = Form(...),
    frame: UploadFile = File(...)
):
    session_dir = RENDER_DIR / session_id / "frames"
    if not session_dir.exists():
        return {"error": "Invalid session"}
    ext = Path(frame.filename or "").suffix.lower()
    mime_map = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    mime_ext = mime_map.get(frame.content_type or "", "")

    # Prefer MIME-indicated extension if it disagrees with the filename (e.g., webp sent as .jpg)
    if mime_ext and mime_ext != ext:
        ext = mime_ext
    if not ext:
        ext = mime_ext
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        return {"error": f"Unsupported frame type: {ext or 'unknown'}"}

    frame_path = session_dir / f"f{frame_index:06d}{ext}"
    with open(frame_path, "wb") as f:
        f.write(await frame.read())
    return {"status": "ok", "frame": frame_index}


@app.post("/api/audio/{session_id}")
async def upload_audio(session_id: str, audio: UploadFile = File(...)):
    audio_path = RENDER_DIR / session_id / "audio.mp3"
    with open(audio_path, "wb") as f:
        f.write(await audio.read())
    return {"status": "ok"}


@app.post("/api/compile/{session_id}")
async def compile_video(session_id: str, fps: int = Form(default=30)):
    session_dir = RENDER_DIR / session_id
    
    # Detect frame "format"
    frames = sorted((session_dir / "frames").glob("f*"))
    if not frames:
        return {"error": "No frames found"}
    
    ext = frames[0].suffix  # .jpg or .webp
    frames_pattern = str(session_dir / "frames" / f"f%06d{ext}")

    # Use the first frame index as start_number to avoid gaps killing ffmpeg
    match = re.search(r"f(\d+)", frames[0].name)
    start_number = int(match.group(1)) if match else 0

    audio_path = str(session_dir / "audio.mp3")
    output_path = str(session_dir / "output.mp4")

    # FIX: Correctly support both webp and jpg
    # The glob pattern f%06d expects exactly 6 digits (e.g., f000000.webp)
    # But if files are named f0.webp, f1.webp ..., we need f%d instead.
    # Check the first file to see if it has leading zeros.
    has_leading_zeros = frames[0].name.startswith("f00")
    frame_fmt = "%06d" if has_leading_zeros else "%d"
    frames_pattern = str(session_dir / "frames" / f"f{frame_fmt}{ext}")

    print(f"Compiling: {frames_pattern} (start: {start_number}, fps: {fps})")

    # Remove -shortest as it can cause empty output if audio stream is problematic or shorter than 1 frame
    # Instead, we rely on the frame input to determine length.
    cmd = ["ffmpeg", "-y", "-framerate", str(fps), "-start_number", str(start_number), "-i", frames_pattern]
    if os.path.exists(audio_path):
        audio_size = os.path.getsize(audio_path)
        print(f"Adding audio track: {audio_path} ({audio_size} bytes)")
        
        # We use -map 0:v so it definitely takes the video from the image sequence (input 0)
        # We use -map 1:a so it definitely takes the audio from the file (input 1)
        # We use libmp3lame which is definitely enabled in this build
        cmd.extend(["-i", audio_path, "-map", "0:v", "-map", "1:a", "-c:a", "libmp3lame", "-b:a", "192k", "-shortest"])
    
    # Add pixel format and ensure compatibility
    cmd.extend(["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", output_path])

    print("Running FFmpeg:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("FFmpeg Error:", result.stderr)
        return {"error": result.stderr[-500:]}
        
    print("FFmpeg Output:", result.stdout)
    if os.path.getsize(output_path) < 1000:
        print("Warning: Output file is very small!")
        # Force return failure if file is practically empty
        return {"error": "Output file is empty or corrupted. Check logs."}

    return {"status": "done", "download": f"/api/download/{session_id}"}


@app.get("/api/download/{session_id}")
async def download_video(session_id: str):
    output_path = RENDER_DIR / session_id / "output.mp4"
    if not output_path.exists():
        return {"error": "File not found"}
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"BANCAMP_{session_id}.mp4"
    )


@app.delete("/api/cleanup/{session_id}")
async def cleanup(session_id: str):
    session_dir = RENDER_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)
    return {"status": "cleaned"}


# Serve static files (render.html)
app.mount("/", StaticFiles(directory=".", html=True), name="static")