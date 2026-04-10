```markdown
# Mask Detection using CNN & Transfer Learning

[![CI/CD Pipeline](https://github.com/hamed7salah/mask-detection/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/hamed7salah/mask-detection/actions/workflows/ci-cd.yml)

A real-time face mask detection system built with **TensorFlow**, **MobileNetV2 (Transfer Learning)**, and deployed as a **3-server microservice architecture** using **Flask** and **Docker**.

---

## Architecture

```
┌──────────────────┐    POST /predict     ┌──────────────────┐
│  CLIENT SERVER   │ ──────────────────►  │  MODEL SERVER    │
│  (Flask :5000)   │ ◄──────────────────  │  (Flask :5001)   │
│                  │    JSON response      │  TF + MobileNetV2│
│  HTML + Canvas   │                      └────────┬─────────┘
│  Webcam capture  │                               │
└──────────────────┘                      POST /store (image + label)
                                                   │
                                                   ▼
                                          ┌──────────────────┐
                                          │  DB SERVER       │
                                          │  (Flask :5002)   │
                                          │  SQLite + Disk   │
                                          │  /app/data/      │
                                          └──────────────────┘
```

## Tech Stack

| Component | Technology |
|---|---|
| Model | TensorFlow, Keras 3, MobileNetV2 |
| Backend | Flask (Python) |
| Frontend | HTML, JavaScript, Canvas API |
| Database | SQLite + File Storage |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Registry | DockerHub |

---

## Dataset

[Face Mask 12K Images Dataset](https://www.kaggle.com/datasets/ashishjangra27/face-mask-12k-images-dataset) from Kaggle.

| Split | WithMask | WithoutMask |
|---|---|---|
| Train | 5,000 | 5,000 |
| Validation | 400 | 400 |
| Test | 483 | 509 |

---

## Model Details

- **Base Model:** MobileNetV2 (pretrained on ImageNet, frozen layers)
- **Added Layers:** GlobalAveragePooling2D → Dense(128) → Dropout(0.3) → Dense(1, sigmoid)
- **Input Size:** 128 × 128 × 3
- **Output:** Binary classification (WithMask / WithoutMask)
- **Training:** 5 epochs with Adam optimizer and binary crossentropy loss

---

## Project Structure

```
mask-detection/
├── notebook/
│   └── mask_detection.ipynb       # Training notebook (single notebook)
├── model-server/
│   ├── app.py                     # Flask API for CNN inference
│   ├── mask_detector_model.keras  # Trained model file
│   ├── requirements.txt
│   └── Dockerfile
├── client-server/
│   ├── app.py                     # Flask frontend proxy
│   ├── templates/
│   │   └── index.html             # Webcam capture UI
│   ├── requirements.txt
│   └── Dockerfile
├── db-server/
│   ├── app.py                     # Flask API for image storage
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # GitHub Actions CI/CD pipeline
└── README.md
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/hamed7salah/mask-detection.git
cd mask-detection
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

### 3. Open in Browser

```
http://localhost:5000
```

Click **"Capture & Predict"** to take a snapshot from your webcam and get a prediction.

---

## API Endpoints

### Client Server (`:5000`)

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Web UI with webcam |
| `/predict` | POST | Proxy to model server |
| `/health` | GET | Health check |

### Model Server (`:5001`)

| Endpoint | Method | Description |
|---|---|---|
| `/predict` | POST | Accepts base64 image, returns prediction |
| `/health` | GET | Health check |

### DB Server (`:5002`)

| Endpoint | Method | Description |
|---|---|---|
| `/store` | POST | Stores image + metadata |
| `/images` | GET | Lists stored captures (last 100) |
| `/count` | GET | Returns total stored image count |
| `/health` | GET | Health check |

---

## CI/CD Pipeline

The GitHub Actions workflow triggers on every push to `main`:

1. **Build** Docker images for all 3 servers
2. **Push** images to DockerHub with `latest` and commit SHA tags

### Docker Images

```
hamed7salah/mask-client:latest
hamed7salah/mask-model:latest
hamed7salah/mask-db:latest
```

---

## Run from DockerHub (Without Building)

```bash
# Pull pre-built images
docker pull hamed7salah/mask-client:latest
docker pull hamed7salah/mask-model:latest
docker pull hamed7salah/mask-db:latest

# Run with docker compose
docker compose up
```

---

## Training the Model

The notebook is located at `notebook/mask_detection.ipynb`. You can run it on:

- [Google Colab](https://colab.research.google.com/) (recommended, free GPU)
- Locally with a GPU

The notebook:
1. Downloads the dataset from Kaggle using `opendatasets`
2. Builds a MobileNetV2 transfer learning model
3. Trains for 5 epochs
4. Evaluates on the test set
5. Saves the model as `.keras`

---

## Health Checks

```bash
curl http://localhost:5000/health   # Client server
curl http://localhost:5001/health   # Model server
curl http://localhost:5002/health   # DB server
curl http://localhost:5002/count    # Stored images count
```

---

## Purpose

This project was built for **educational purposes** to demonstrate:

- CNN-based image classification with transfer learning
- Microservice architecture with Docker
- CI/CD pipelines with GitHub Actions
- Model deployment with Flask
- Data collection for model retraining

---

## License

This project is for educational purposes only.
```