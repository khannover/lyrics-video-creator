1)
    Add a job queue using asyncio.Semaphore to limit concurrent FFmpeg compile jobs
    to 1 at a time in the POST /api/compile/{session_id} endpoint. Additional
    requests should wait rather than being rejected. Add a GET /api/queue endpoint
    returning the number of currently waiting compile jobs.

2)
    Add an automatic cleanup background task using FastAPI lifespan that runs every
    10 minutes and deletes session folders under /renders that are older than
    30 minutes. Use asyncio.create_task and shutil.rmtree. Start on startup,
    cancel on shutdown.

3)
    Extend or create a GET /api/health endpoint that returns the current disk usage
    of the renders directory: free_gb and used_gb via shutil.disk_usage(), plus
    the count of currently active session folders.

4)
    Add a proper README.md to the repository. Include: a short description (browser-
    rendered lyrics video creator with audio-reactive visualizers), the tech stack
    (FastAPI, Canvas API, ffmpeg, WebP frame upload), how to run with Docker Compose,
    a list of available visualizers, and a note that rendering happens client-side
    in the browser.
