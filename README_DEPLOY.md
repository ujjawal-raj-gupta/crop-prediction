# Deploy (Render) — Web + SMS Worker

This project is set up to deploy as:
- **Web service** (Flask): serves the website
- **Worker service**: runs `sms_worker.py` to send scheduled SMS in the background

Both services share the same **persistent disk** for SQLite (`DATABASE_PATH=/var/data/smart_crop.db`).

## 1) Prerequisites
- A Twilio account
- A Twilio phone number (for `TWILIO_FROM_NUMBER`)

## 2) Push code to GitHub
1. Create a GitHub repo
2. Push this project to it

## 3) Deploy on Render
1. In Render dashboard, click **New +** → **Blueprint**
2. Select your GitHub repo
3. Render will detect `render.yaml` and create:
   - `smart-crop-advisor-web`
   - `smart-crop-advisor-worker`

## 4) Set environment variables (Render)
In Render, set these for **both** services:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`

## 5) Train model artifacts (important)
This deployment is configured to **train on deploy**.

During the Render build step, it runs:
- `python train_model.py`

This generates these artifacts automatically:
- `crop_model.pkl`
- `soil_encoder.pkl`
- `feature_cols.pkl`

## 6) Confirm worker is running
On Render, open the **worker logs** and confirm it is polling and not crashing.

