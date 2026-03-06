import asyncio
import os
import re
import shutil
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

RENDER_DIR = Path("renders")
RENDER_DIR.mkdir(exist_ok=True)

# Compile job queue: only one FFmpeg process at a time; others wait.
_compile_semaphore = asyncio.Semaphore(1)
_compile_waiting: int = 0
_compile_running: bool = False

CLEANUP_INTERVAL_SECONDS = 600   # run cleanup every 10 minutes
SESSION_MAX_AGE_SECONDS = 1800   # delete sessions older than 30 minutes


async def _auto_cleanup() -> None:
    """Background task: periodically remove stale session directories."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
        now = time.time()
        if RENDER_DIR.exists():
            for entry in list(RENDER_DIR.iterdir()):
                if entry.is_dir():
                    try:
                        age = now - entry.stat().st_mtime
                        if age > SESSION_MAX_AGE_SECONDS:
                            shutil.rmtree(entry)
                            print(f"[cleanup] removed stale session {entry.name} (age={age:.0f}s)")
                    except Exception as exc:
                        print(f"[cleanup] error removing {entry}: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(_auto_cleanup())
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Bancamp Studio V4", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    global _compile_waiting, _compile_running

    session_dir = RENDER_DIR / session_id

    # Detect frame format before entering the queue so we can fail fast.
    frames = sorted((session_dir / "frames").glob("f*"))
    if not frames:
        return {"error": "No frames found"}

    ext = frames[0].suffix  # .jpg, .webp, .png …
    match = re.search(r"f(\d+)", frames[0].name)
    start_number = int(match.group(1)) if match else 0

    # Support both zero-padded (f000000.jpg) and non-padded (f0.jpg) filenames.
    has_leading_zeros = frames[0].name.startswith("f00")
    frame_fmt = "%06d" if has_leading_zeros else "%d"
    frames_pattern = str(session_dir / "frames" / f"f{frame_fmt}{ext}")

    audio_path = str(session_dir / "audio.mp3")
    output_path = str(session_dir / "output.mp4")

    print(f"Compiling: {frames_pattern} (start: {start_number}, fps: {fps})")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-start_number", str(start_number),
        "-i", frames_pattern,
    ]
    if os.path.exists(audio_path):
        audio_size = os.path.getsize(audio_path)
        print(f"Adding audio track: {audio_path} ({audio_size} bytes)")
        cmd.extend([
            "-i", audio_path,
            "-map", "0:v",
            "-map", "1:a",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            "-shortest",
        ])

    # H.264, ultrafast, web-optimised faststart for progressive download.
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path,
    ])

    print("Running FFmpeg:", " ".join(cmd))

    # Enqueue – only one FFmpeg job at a time, others wait.
    _compile_waiting += 1
    try:
        await _compile_semaphore.acquire()
    except BaseException:
        # Cancelled or other error while waiting for the semaphore.
        _compile_waiting -= 1
        raise
    # We hold the semaphore from here; decrement waiting and mark running.
    _compile_waiting -= 1
    _compile_running = True
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await proc.communicate()
        stderr_text = stderr_bytes.decode(errors="replace")
        stdout_text = stdout_bytes.decode(errors="replace")
    finally:
        _compile_running = False
        _compile_semaphore.release()

    if proc.returncode != 0:
        print("FFmpeg Error (full):\n", stderr_text)
        return {"error": stderr_text[-500:]}

    print("FFmpeg stdout:", stdout_text)
    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
        print("Warning: Output file is missing or very small!")
        return {"error": "Output file is empty or corrupted. Check logs."}

    return {"status": "done", "download": f"/api/download/{session_id}"}


@app.get("/api/queue")
async def queue_status():
    """Return current compile queue depth and running status."""
    return {
        "waiting": _compile_waiting,
        "running": _compile_running,
    }


@app.get("/api/health")
async def health():
    """Return disk usage for the renders directory and session counts."""
    try:
        usage = shutil.disk_usage(RENDER_DIR)
        free_gb = round(usage.free / 1e9, 2)
        used_gb = round(usage.used / 1e9, 2)
    except Exception:
        free_gb = used_gb = -1

    session_count = len([d for d in RENDER_DIR.iterdir() if d.is_dir()]) if RENDER_DIR.exists() else 0

    return {
        "status": "ok",
        "disk": {
            "free_gb": free_gb,
            "used_gb": used_gb,
        },
        "sessions": session_count,
        "queue": {
            "waiting": _compile_waiting,
            "running": _compile_running,
        },
    }


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