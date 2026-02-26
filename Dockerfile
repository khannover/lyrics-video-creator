FROM python:3.11-slim

# Install native ffmpeg and curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY render.html .

# Create renders directory
RUN mkdir -p /app/renders

EXPOSE 3333

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3333"]
