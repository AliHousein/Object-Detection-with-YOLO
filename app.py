
import os
import io
import uuid
from datetime import datetime
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from ultralytics import YOLO

# ---------- Config ----------
MODEL_PATH = os.getenv("MODEL_PATH", "weights/best.pt")  # you can override via env var
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- App & Model ----------
app = Flask(__name__, static_folder="static", template_folder="templates")

try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model from {MODEL_PATH}. "
                       f"Ensure the file exists in the container. Original error: {e}")

ALLOWED_EXTS = {"jpg", "jpeg", "png", "bmp", "gif"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

def run_inference(image_path: str):
    # Use YOLOv8 predict; returns a list of Results
    results = model.predict(source=image_path, conf=CONF_THRESHOLD, verbose=False)
    res = results[0]

    # Prepare JSON
    detections = []
    if res.boxes is not None:
        for b in res.boxes:
            cls_id = int(b.cls[0].item())
            conf = float(b.conf[0].item())
            xyxy = b.xyxy[0].tolist()  # [x1, y1, x2, y2]
            name = res.names.get(cls_id, str(cls_id))
            detections.append({
                "class_id": cls_id,
                "class_name": name,
                "confidence": round(conf, 4),
                "box_xyxy": [round(float(v), 2) for v in xyxy]
            })

    # Render annotated image
    plotted = res.plot()  # numpy array with boxes/labels drawn
    # Unique filename for output
    out_name = f"{uuid.uuid4().hex}_pred.jpg"
    out_path = os.path.join(OUTPUT_FOLDER, out_name)

    # Save via PIL to ensure compatibility
    Image.fromarray(plotted[..., ::-1] if plotted.shape[-1] == 3 else plotted).save(out_path, format="JPEG")

    return detections, out_name

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No file part 'image' found in request"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    # Save upload
    unique_in = f"{uuid.uuid4().hex}_{file.filename}"
    in_path = os.path.join(UPLOAD_FOLDER, unique_in)
    file.save(in_path)

    try:
        detections, out_name = run_inference(in_path)
    except Exception as e:
        return jsonify({"error": f"Inference failed: {e}"}), 500

    return jsonify({
        "uploaded_filename": file.filename,
        "output_image_url": f"/outputs/{out_name}",
        "detections": detections,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route("/outputs/<path:filename>", methods=["GET"])
def serve_output(filename):
    # Security check
    if ".." in filename or filename.startswith("/"):
        abort(400)
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=False)

# Simple health endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # For local dev; in Docker we use gunicorn
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
