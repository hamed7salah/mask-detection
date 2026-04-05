import os
import base64
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_DIR    = os.environ.get("DATA_DIR", "/app/data")
STORAGE_DIR = os.path.join(DATA_DIR, "images")
DB_PATH     = os.path.join(DATA_DIR, "captures.db")

os.makedirs(STORAGE_DIR, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


# Initialize on startup
get_db().close()


@app.route("/store", methods=["POST"])
def store():
    data = request.get_json()
    image_b64  = data["image"]
    prediction = data["prediction"]
    confidence = data["confidence"]

    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{prediction}_{ts}.jpg"
    filepath = os.path.join(STORAGE_DIR, filename)

    # Save image to disk
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(image_b64))

    # Save metadata to SQLite
    conn = get_db()
    conn.execute(
        "INSERT INTO captures (filename, prediction, confidence, timestamp) "
        "VALUES (?, ?, ?, ?)",
        (filename, prediction, confidence, ts),
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "stored", "filename": filename})


@app.route("/images", methods=["GET"])
def list_images():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, filename, prediction, confidence, timestamp "
        "FROM captures ORDER BY id DESC LIMIT 100"
    ).fetchall()
    conn.close()

    return jsonify([
        {
            "id": r[0],
            "filename": r[1],
            "prediction": r[2],
            "confidence": r[3],
            "timestamp": r[4],
        }
        for r in rows
    ])


@app.route("/count", methods=["GET"])
def count():
    conn = get_db()
    n = conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0]
    conn.close()
    return jsonify({"count": n})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "storage": STORAGE_DIR})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)