
# YOLOv8 Object Detection (Pen & Scissors) — Flask + Docker

Minimal Flask application that serves a trained YOLOv8 model to detect **pen** and **scissors** in uploaded images.

## Project Structure
```
.
├─ app.py
├─ requirements.txt
├─ Dockerfile
├─ .dockerignore
├─ templates/
│  └─ index.html
├─ static/
│  └─ styles.css
├─ uploads/
└─ outputs/
```
> Place your trained weights at: `weights/best.pt` (create the folder if it doesn't exist).  
> Or set `MODEL_PATH` env var to the absolute/relative path of your model file.

## Run Locally (no Docker)
```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
# put your model at weights/best.pt
export MODEL_PATH=weights/best.pt
python app.py
# open http://localhost:5000
```

## Build & Run with Docker
```bash
# Copy your model file
mkdir -p weights && cp /path/to/best.pt weights/best.pt

# Build image
docker build -t yolo-flask .

# Run container
docker run -p 5000:5000 \
  -e MODEL_PATH=weights/best.pt \
  -e CONF_THRESHOLD=0.25 \
  yolo-flask
```

## API
- `GET /` — upload form
- `POST /predict` — multipart form-data with `image` field
  - Returns JSON with detections and `output_image_url`
- `GET /outputs/<file>` — serves annotated image

### Example `curl`
```bash
curl -F "image=@example.jpg" http://localhost:5000/predict | jq
```

## Notes
- This app runs CPU inference with YOLOv8 (Ultralytics). For smaller Docker images and faster cold-starts on free tiers, consider exporting to ONNX and using `onnxruntime`.
- If you trained with class names `['pen', 'scissors']`, they will appear in the JSON output.
- Set `CONF_THRESHOLD` to control detection confidence.

## Deploying to Render (Free Tier)
1. Push this repo to GitHub.
2. In Render, create **New +** → **Web Service**, and select **"Use Docker"** (Dockerfile).
3. Set **Root Directory** to the repository root.
4. Add environment variables:
   - `MODEL_PATH = weights/best.pt`
   - `CONF_THRESHOLD = 0.25`
5. Upload `weights/best.pt` to your repo (or store in a private bucket and mount at runtime).
6. Deploy. Once live, open the service URL.

## Troubleshooting
- **Model not found**: ensure `weights/best.pt` exists in the container image (commit to the repo or download during build).
- **Large image / memory**: prefer JPEG/PNG under ~5MB. Free tiers have tight RAM limits.
- **Slow cold starts**: first request after idling may be slower due to model load.
```
