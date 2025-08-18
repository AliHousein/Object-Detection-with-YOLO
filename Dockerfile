FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLCONFIGDIR=/tmp/matplotlib

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install CPU-only torch + torchvision
RUN pip install --no-cache-dir torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cpu

# Install ultralytics separately
RUN pip install --no-cache-dir ultralytics==8.3.0

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

RUN mkdir -p /app/weights /app/uploads /app/outputs

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "--threads", "1", "--timeout", "300", "-b", "0.0.0.0:5000", "app:app"]
