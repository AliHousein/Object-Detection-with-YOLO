# YOLOv8 Object Detection — Pen & Scissors (Flask + Docker)

![Demo Preview](static/demo_preview.gif)

This project demonstrates how to **train, package, and deploy** a custom [YOLOv8](https://github.com/ultralytics/ultralytics) object detection model to detect two everyday objects: **Pen** and **Scissors**.

The model is served through a **Flask web application**, containerized with **Docker**, and designed to be deployed on free hosting platforms **Render**.  
Users can upload an image and instantly receive detection results as an **annotated image**.

---

## 🚀 Features

-   Custom-trained YOLOv8 model for Pen & Scissors detection.
-   Flask web interface with image upload form.
-   Returns **annotated image**.
-   Containerized with Docker for easy deployment.
-   Ready for free cloud hosting (Render).

---

## 📂 Project Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container definition
├── .dockerignore       # Ignore unnecessary files in Docker build
├── weights/
│   └── best.pt         # Trained YOLOv8 weights (best.pt)
├── templates/          # HTML templates
│   └── index.html
├── static/             # CSS and demo assets
│   └── styles.css
│   └── demo_preview.gif
├── uploads/            # Temporary upload storage
└── outputs/            # Model inference results
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/yolov8-object-detection.git
cd yolov8-object-detection
```

### 2. Run Locally (without Docker)

```bash

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
```

Visit 👉 http://localhost:5000

### 4. Run with Docker

```bash
# Build Docker image
docker build -t yolo-flask .

# Run container
docker run -p 5000:5000   -e MODEL_PATH=weights/best.pt   -e CONF_THRESHOLD=0.25   yolo-flask
```

Visit 👉 http://localhost:5000

---

## 💻 Using the Interface

1. Open the app in your browser.
2. Upload an image containing a pen or scissors.
3. Receive:
    - **Annotated image** with bounding boxes

Example JSON response:

```json
{
    "uploaded_filename": "test.jpg",
    "output_image_url": "/outputs/abcd1234_pred.jpg",
    "detections": [
        {
            "class_id": 0,
            "class_name": "pen",
            "confidence": 0.73,
            "box_xyxy": [100, 50, 200, 300]
        },
        {
            "class_id": 1,
            "class_name": "scissors",
            "confidence": 0.92,
            "box_xyxy": [300, 120, 450, 400]
        }
    ],
    "timestamp": "2025-08-17T09:12:34Z"
}
```

---

## ⚠️ Known Issues / Limitations

-   The model currently detects **Scissors reliably** ✅
-   Detection of **Pens is less accurate** ⚠️ (due to object thinness & dataset limitations)
-   First request after app startup may be slower (cold-start model load)
-   Free hosting tiers have limited resources → longer inference times on large images

---

## 📈 Future Improvements

-   Expand dataset with more diverse pen images.
-   Use higher resolution & larger YOLOv8 backbone (`yolov8m.pt`)
-   Enhance UI (drag-and-drop upload, webcam support)

---
