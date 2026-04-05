import os
import io
import base64
import numpy as np
import requests
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from PIL import Image

app = Flask(__name__)

MODEL_PATH = os.environ.get("MODEL_PATH", "mask_detector_model.keras")

DB_SERVER_URL = os.environ.get("DB_SERVER_URL", "http://db-server:5002")

print(f"Loading model from {MODEL_PATH} ...")
model = load_model(MODEL_PATH)
print("Model loaded.")

# Class mapping (from training): WithMask=0, WithoutMask=1
CLASSES = {0: "WithMask", 1: "WithoutMask"}


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    image_b64 = data["image"]

    # Decode and preprocess
    image_bytes = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_resized = image.resize((128, 128))
    img_array = np.array(image_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    raw = float(model.predict(img_array, verbose=0)[0][0])
    label = CLASSES[int(raw > 0.5)]
    confidence = round(raw if raw > 0.5 else 1 - raw, 4)

    # Forward image to DB server asynchronously (best-effort)
    try:
        requests.post(
            f"{DB_SERVER_URL}/store",
            json={
                "image": image_b64,
                "prediction": label,
                "confidence": confidence,
            },
            timeout=3,
        )
    except Exception as e:
        print(f"DB store failed: {e}")

    return jsonify({"prediction": label, "confidence": confidence})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model": MODEL_PATH})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)