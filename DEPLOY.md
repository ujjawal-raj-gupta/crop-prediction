# Deploy to Render (get a shareable public link)

Your code is on GitHub. Render will host it and give you URLs like:
- `https://smart-crop-advisor-web.onrender.com`
- `https://bihar-agriculture-portal.onrender.com`

## One-click deploy (recommended)

1. Open this link (log in with GitHub if asked):

   **https://dashboard.render.com/blueprint/new?repo=https://github.com/ujjawal-raj-gupta/crop-prediction**

2. Click **Apply** (Render reads `render.yaml` and creates 2 web services).

3. Wait ~5–10 minutes for the first build (installs packages + runs `train_model.py`).

4. Open your live URLs from the Render dashboard (**Services** → click each service → copy **URL**).

## What gets deployed

| Service | App | Public paths |
|---------|-----|----------------|
| `smart-crop-advisor-web` | Flask crop advisor (`web_app.py`) | `/` (form + prediction) |
| `bihar-agriculture-portal` | Bihar portal (FastAPI) | `/portal/` |

## Notes

- **Free plan**: services sleep after ~15 min idle; first visit may take 30–60s to wake up.
- **No secrets required** for basic crop prediction + weather (Open-Meteo).
- Twilio/SMS env vars are optional (only if you use notification features).

## After deploy

Share these links (replace with your actual Render URLs):

- Crop advisor: `https://smart-crop-advisor-web.onrender.com`
- Bihar portal: `https://bihar-agriculture-portal.onrender.com/portal/`
