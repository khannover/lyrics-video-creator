FROM python:3.11-slim

# Install native ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

WORKDIR /app

# Copy application files
COPY server.py .
COPY render.html .

# Create renders directory
RUN mkdir -p /app/renders

EXPOSE 3333

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3333"]