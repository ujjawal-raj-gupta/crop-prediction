# Smart Crop Advisor

## Overview
Smart Crop Advisor is a beginner-friendly Python ML + Streamlit project that recommends a suitable crop based on soil nutrients and local conditions. It is designed around the needs of **Bihar farmers**, where crop decisions are impacted by soil type, weather, and market demand.

## Problem (Bihar farmers)
Farmers often decide crops using partial information. This project combines:
- **Soil nutrients** (N, P, K) and soil health (pH, organic matter)
- **Weather conditions** (temperature, humidity)
- **Water availability** (rainfall input)
- **Market demand** (demand/price/buyer info)

The goal is to recommend a suitable crop with a confidence score and practical market insights.

## What you will build (end-to-end)
1. **Prepare data**: extend the Kaggle crop dataset with Bihar-inspired `soil_type` and `organic_matter`, then save `data/crop_data.csv`.
2. **Explore + evaluate models**: perform EDA and compare 4 ML models using a proper train/test split.
3. **Train + export**: run a training script to generate `crop_model.pkl` and `soil_encoder.pkl`.
4. **Streamlit app**: run a UI that auto-fills temperature/humidity using a city-based weather fetch and shows market demand insights.

## Features
- **ML crop prediction**: RandomForest model trained on `data/crop_data.csv`
- **Weather integration**: city-based temperature + humidity auto-fill (with fallback)
- **Market demand panel**: demand level + price + buyer details from `data/market_demand.csv`
- **Confidence score**: uses `predict_proba()` and shows a progress bar
- **Dashboard UI option**: Flask web dashboard (HTML/CSS) for a portal-like layout

## Project structure
```
smart-crop-advisor/
├── app.py
├── prepare_data.py
├── train_model.py
├── web_app.py
├── crop_model.pkl              # generated after training
├── soil_encoder.pkl            # generated after training
├── requirements.txt
├── README.md
│
├── data/
│   ├── Crop_recommendation.csv
│   ├── crop_data.csv           # generated after data preparation
│   └── market_demand.csv
│
└── notebooks/
    └── smart_crop_advisor.ipynb
```

## Setup (Windows / PowerShell)
Create and activate a virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Quick check:
```bash
python -c "import pandas, numpy, sklearn; print('OK')"
```

## Run (strict order)
### 1) Create the prepared dataset
This generates `data/crop_data.csv` by adding Bihar-inspired `soil_type` and `organic_matter`.

```bash
python prepare_data.py
```

### 2) Train and export the model
This generates:
- `crop_model.pkl`
- `soil_encoder.pkl`

```bash
python train_model.py
```

### 3) Run the Streamlit app
```bash
streamlit run app.py
```

### (Alternative) Run the Flask dashboard (HTML/CSS)
If you prefer a portal-like dashboard UI (HTML/CSS layout), run:

```bash
python web_app.py
```

Then open: `http://127.0.0.1:5000`

### Government-grade portal (No-Node, CDN-based)

The production-style **Bihar Agriculture 4.0** web experience is served by the **FastAPI** app (Python-only) and is mounted at **`/portal/`**.

1. Run the API server:

```bash
cd bihar-agriculture-platform\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn src.main:app --reload --host 127.0.0.1 --port 8001
```

2. Open the portal UI in a browser (**do not double‑click the HTML file — use the server URL**):

- **`http://127.0.0.1:8001/`** (redirects to the portal)
- Or directly: `http://127.0.0.1:8001/portal/`

Portal files live in `bihar-agriculture-platform/backend/src/web/` and use CDNs for Tailwind + charts.

- API base: `http://127.0.0.1:8001/api/v1/...`

Key endpoints used by the portal include `POST /api/v1/market/predict`, `GET /api/v1/market/crops`, `GET /api/v1/market/mandis`, `POST /api/v1/pest/check-risk`, `POST /api/v1/crop/recommend`, `POST /api/v1/support/create-ticket`, and `GET /api/v1/support/faqs`.

## Troubleshooting
- If Streamlit says model files are missing:
  - Run `python train_model.py` first to create `crop_model.pkl` and `soil_encoder.pkl`.
- If `data/crop_data.csv` is missing:
  - Run `python prepare_data.py` first.

## Future scope ideas
- Pull rainfall estimates from a weather/climate source and engineer seasonal rainfall features.
- Add fertilizer recommendations and cost estimation.
- Add district-wise market price trends instead of static seed data.
