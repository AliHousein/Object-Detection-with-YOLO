
# Use a lightweight Python base image
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_WORKERS=1 \
    MPLCONFIGDIR=/tmp/matplotlib

# System packages often required by scientific stacks
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better caching)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app
COPY . .

# Create a place for model weights (mounted or baked-in)
RUN mkdir -p /app/weights /app/uploads /app/outputs

# Expose port
EXPOSE 5000

# Use gunicorn for prod; bind 0.0.0.0:5000
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
