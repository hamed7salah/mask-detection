import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

MODEL_SERVER_URL = os.environ.get(
    "MODEL_SERVER_URL", "http://model-server:5001"
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """Proxy to model server so browser only talks to one origin."""
    data = request.get_json()
    try:
        resp = requests.post(
            f"{MODEL_SERVER_URL}/predict", json=data, timeout=10
        )
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
